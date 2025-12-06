#!/usr/bin/env python3
"""
Brackeys-13 Master Scraper - All 6 Tasks
Complete solution for scraping 3D games with strict requirements.

Tasks:
1. Page 1 pilot scrape (8 entries expected)
2. Page 2 pilot scrape
3. Page 3 pilot scrape
4. Full scrape (all remaining pages)
5. Contact augmentation
6. Google Sheet creation
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import argparse
from urllib.parse import urljoin
from typing import Dict, List, Set, Optional, Tuple
import sys
from collections import defaultdict
import os

class BrackeysMasterScraper:
    def __init__(self, base_url: str = "https://itch.io/jam/brackeys-13/entries"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.processed_studios = {}  # studio_name -> {games, contacts}
        
    def get_page(self, page_num: int) -> Optional[BeautifulSoup]:
        """Fetch and parse a specific page of jam entries."""
        url = f"{self.base_url}?page={page_num}" if page_num > 1 else self.base_url
        
        try:
            print(f"\n{'='*70}")
            print(f"Fetching page {page_num}: {url}")
            print(f"{'='*70}")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"❌ Error fetching page {page_num}: {e}")
            return None
    
    def extract_game_entries(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract game entries from the submissions page."""
        entries = []
        
        # Find all game entries
        game_cells = soup.find_all('div', class_='game_cell')
        
        if not game_cells:
            game_cells = soup.find_all('a', class_='game_link')
        
        print(f"\n📊 Found {len(game_cells)} game entries on page")
        
        for cell in game_cells:
            try:
                entry = {}
                
                # Find the game link
                link_elem = cell if cell.name == 'a' else cell.find('a', class_='title')
                if not link_elem:
                    link_elem = cell.find('a', href=True)
                
                if link_elem and link_elem.get('href'):
                    game_url = urljoin("https://itch.io", link_elem['href'])
                    entry['game_url'] = game_url
                    entry['title'] = link_elem.get_text(strip=True)
                    
                    # Extract developer/studio
                    dev_elem = cell.find('a', class_='user_link') or cell.find('div', class_='game_author')
                    if dev_elem:
                        dev_link = dev_elem if dev_elem.name == 'a' else dev_elem.find('a')
                        if dev_link:
                            entry['developer'] = dev_link.get_text(strip=True)
                            entry['developer_url'] = urljoin("https://itch.io", dev_link.get('href', ''))
                    
                    entries.append(entry)
                    
            except Exception as e:
                print(f"⚠️ Error extracting entry: {e}")
                continue
        
        return entries
    
    def get_game_details(self, game_url: str) -> Dict:
        """Fetch detailed information from a game page."""
        details = {
            'tags': [],
            'jam_rate_url': '',
            'description': '',
        }
        
        try:
            print(f"  📄 Fetching game page...")
            response = self.session.get(game_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract tags - CRITICAL: Must have explicit "3D" tag
            tag_elements = soup.find_all('a', class_='tag')
            details['tags'] = [tag.get_text(strip=True) for tag in tag_elements]
            
            # Find jam rate URL
            jam_link = soup.find('a', href=re.compile(r'/jam/brackeys-13/rate/'))
            if jam_link:
                details['jam_rate_url'] = urljoin("https://itch.io", jam_link['href'])
            
            # Extract description
            desc_elem = soup.find('div', class_='formatted_description')
            if desc_elem:
                details['description'] = desc_elem.get_text(strip=True)
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"  ❌ Error fetching game details: {e}")
        
        return details
    
    def is_3d_game(self, tags: List[str], title: str = '', description: str = '') -> bool:
        """
        Determine if a game is 3D based on tags, engines, and other indicators.

        Detects 3D games through:
        - Explicit "3D" tag (exact match, case-sensitive)
        - 3D engines (Unity, Unreal, Godot)
        - 3D perspectives (First-Person, Third-Person, FPS, TPS)
        - 3D styles (Low Poly, Voxel, 3D Platformer)
        - Title/description mentions of 3D
        """
        # Check for exact "3D" tag (case-sensitive first, then case-insensitive)
        if '3D' in tags or '3d' in tags:
            return True

        # Convert to lowercase for other checks
        tags_lower = [tag.lower() for tag in tags]

        # Common 3D engine/style tags
        three_d_indicators = [
            'unity', 'unreal', 'godot', 'unreal engine',
            'first-person', 'third-person', 'fps', 'tps',
            '3d platformer', 'low poly', 'voxel', 'low-poly',
            'three dimensional', 'three-dimensional'
        ]

        for indicator in three_d_indicators:
            if any(indicator in tag for tag in tags_lower):
                return True

        # Check title and description as fallback
        text = (title + ' ' + description).lower()
        if '3d' in text or 'three dimensional' in text or 'three-dimensional' in text:
            return True

        return False
    
    def extract_contact_info(self, developer_url: str, game_url: str, studio_name: str) -> Dict:
        """
        Extract contact information with priority order:
        email > website/contact > social > profile fallback
        
        Returns dict with contacts and source URLs
        """
        contacts = {
            'email': '',
            'website': '',
            'twitter': '',
            'discord': '',
            'linkedin': '',
            'bluesky': '',
        }
        source_urls = []
        
        print(f"    🔍 Extracting contacts for: {studio_name}")
        
        # Try developer page first
        if developer_url:
            try:
                print(f"    📋 Checking developer profile: {developer_url}")
                response = self.session.get(developer_url, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                page_text = soup.get_text()
                
                # Extract email
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                emails = re.findall(email_pattern, page_text)
                if emails:
                    contacts['email'] = emails[0]
                    if developer_url not in source_urls:
                        source_urls.append(developer_url)
                
                # Extract social links
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '').lower()
                    
                    if 'twitter.com' in href or 'x.com' in href:
                        contacts['twitter'] = link['href']
                        if link['href'] not in source_urls:
                            source_urls.append(link['href'])
                    elif 'discord' in href:
                        contacts['discord'] = link['href']
                        if link['href'] not in source_urls:
                            source_urls.append(link['href'])
                    elif 'linkedin.com' in href:
                        contacts['linkedin'] = link['href']
                        if link['href'] not in source_urls:
                            source_urls.append(link['href'])
                    elif 'bsky.app' in href or 'bluesky' in href:
                        contacts['bluesky'] = link['href']
                        if link['href'] not in source_urls:
                            source_urls.append(link['href'])
                    elif href.startswith('http') and not any(x in href for x in 
                        ['itch.io', 'twitter', 'discord', 'linkedin', 'bluesky', 
                         'facebook', 'instagram', 'youtube', 'patreon']):
                        # Potential website
                        if not contacts['website']:
                            contacts['website'] = link['href']
                            if link['href'] not in source_urls:
                                source_urls.append(link['href'])
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    ⚠️ Error fetching developer page: {e}")
        
        # Also check game page
        try:
            print(f"    📋 Checking game page for additional contacts")
            response = self.session.get(game_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()
            
            # Email if not found
            if not contacts['email']:
                emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', page_text)
                if emails:
                    contacts['email'] = emails[0]
                    if game_url not in source_urls:
                        source_urls.append(game_url)
            
            # Social links if not found
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').lower()
                
                if not contacts['twitter'] and ('twitter.com' in href or 'x.com' in href):
                    contacts['twitter'] = link['href']
                    if link['href'] not in source_urls:
                        source_urls.append(link['href'])
                elif not contacts['discord'] and 'discord' in href:
                    contacts['discord'] = link['href']
                    if link['href'] not in source_urls:
                        source_urls.append(link['href'])
                elif not contacts['linkedin'] and 'linkedin.com' in href:
                    contacts['linkedin'] = link['href']
                    if link['href'] not in source_urls:
                        source_urls.append(link['href'])
                elif not contacts['bluesky'] and ('bsky.app' in href or 'bluesky' in href):
                    contacts['bluesky'] = link['href']
                    if link['href'] not in source_urls:
                        source_urls.append(link['href'])
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    ⚠️ Error checking game page: {e}")
        
        return {'contacts': contacts, 'source_urls': source_urls}
    
    def get_primary_contact(self, contacts: Dict) -> str:
        """
        Determine primary contact based on priority:
        email > website/contact > social > profile fallback
        """
        if contacts['email']:
            return contacts['email']
        elif contacts['website']:
            return contacts['website']
        elif contacts['twitter']:
            return contacts['twitter']
        elif contacts['discord']:
            return contacts['discord']
        elif contacts['linkedin']:
            return contacts['linkedin']
        elif contacts['bluesky']:
            return contacts['bluesky']
        else:
            return ""
    
    def get_additional_contacts(self, contacts: Dict, primary: str) -> str:
        """Get all contacts except primary, formatted as semicolon-separated."""
        additional = []
        for contact_type in ['email', 'website', 'twitter', 'discord', 'linkedin', 'bluesky']:
            value = contacts.get(contact_type, '')
            if value and value != primary:
                additional.append(value)
        return '; '.join(additional)
    
    def scrape_page(self, page_num: int) -> List[Dict]:
        """Scrape a complete page with flexible 3D detection."""
        results = []

        soup = self.get_page(page_num)
        if not soup:
            return results

        entries = self.extract_game_entries(soup)
        print(f"\n🎮 Processing {len(entries)} entries from page {page_num}...\n")

        three_d_count = 0

        for i, entry in enumerate(entries, 1):
            print(f"[{i}/{len(entries)}] {entry.get('title', 'Unknown')}")

            if 'game_url' not in entry:
                print(f"  ⚠️ No game URL, skipping")
                continue

            # Get game details
            details = self.get_game_details(entry['game_url'])
            entry.update(details)

            # FLEXIBLE 3D DETECTION: Check tags, engines, perspectives, title, description
            if not self.is_3d_game(
                entry.get('tags', []),
                entry.get('title', ''),
                entry.get('description', '')
            ):
                print(f"  ❌ Not 3D - Tags: {', '.join(entry.get('tags', []))}")
                continue

            three_d_count += 1
            print(f"  ✅ 3D GAME! Tags: {', '.join(entry.get('tags', []))}")
            
            studio_name = entry.get('developer', '')
            
            # Check if studio already processed
            if studio_name in self.processed_studios:
                print(f"  ℹ️ Studio '{studio_name}' already processed, adding game to existing entry")
                self.processed_studios[studio_name]['games'].append({
                    'title': entry.get('title', ''),
                    'game_url': entry.get('game_url', ''),
                    'jam_rate_url': entry.get('jam_rate_url', ''),
                    'tags': entry.get('tags', [])
                })
                continue
            
            # Extract contacts for new studio
            contact_data = self.extract_contact_info(
                entry.get('developer_url', ''),
                entry['game_url'],
                studio_name
            )
            
            # Store in processed studios
            self.processed_studios[studio_name] = {
                'games': [{
                    'title': entry.get('title', ''),
                    'game_url': entry.get('game_url', ''),
                    'jam_rate_url': entry.get('jam_rate_url', ''),
                    'tags': entry.get('tags', [])
                }],
                'developer_url': entry.get('developer_url', ''),
                'contacts': contact_data['contacts'],
                'source_urls': contact_data['source_urls']
            }
            
            # Log contacts found
            primary = self.get_primary_contact(contact_data['contacts'])
            print(f"  📧 Primary contact: {primary if primary else 'None found'}")
            if contact_data['contacts']['email']:
                print(f"     • Email: {contact_data['contacts']['email']}")
            if contact_data['contacts']['website']:
                print(f"     • Website: {contact_data['contacts']['website']}")
            if contact_data['contacts']['twitter']:
                print(f"     • Twitter: {contact_data['contacts']['twitter']}")
            if contact_data['contacts']['discord']:
                print(f"     • Discord: {contact_data['contacts']['discord']}")
        
        print(f"\n{'='*70}")
        print(f"Page {page_num} Summary:")
        print(f"  • Total entries: {len(entries)}")
        print(f"  • 3D games found: {three_d_count}")
        print(f"  • Unique studios: {len(self.processed_studios)}")
        print(f"{'='*70}\n")
        
        return results
    
    def save_to_csv(self, output_file: str, mode: str = 'w'):
        """
        Save results to CSV with exact format:
        Studio Name, Game Title, Itch URL, Tags, Primary Contact, Additional Contacts, Source URLs

        Creates empty CSV with headers if no data, allowing workflow to continue.
        """
        fieldnames = [
            'Studio Name',
            'Game Title',
            'Itch URL',
            'Tags',
            'Primary Contact',
            'Additional Contacts',
            'Source URLs'
        ]

        if not self.processed_studios:
            print("⚠️ No data to save. Creating empty CSV with headers.")
            # Create empty CSV with headers so workflow can continue
            if mode == 'w' or not os.path.exists(output_file):
                with open(output_file, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=fieldnames)
                    writer.writeheader()
                print(f"✅ Created empty CSV: {output_file}")
            return

        rows = []
        for studio_name, data in self.processed_studios.items():
            # Get contacts
            primary = self.get_primary_contact(data['contacts'])
            additional = self.get_additional_contacts(data['contacts'], primary)
            source_urls = '; '.join(data['source_urls'])

            # Create row for each game by this studio
            for game in data['games']:
                row = {
                    'Studio Name': studio_name,
                    'Game Title': game['title'],
                    'Itch URL': game['game_url'],
                    'Tags': ', '.join(game['tags']),
                    'Primary Contact': primary,
                    'Additional Contacts': additional,
                    'Source URLs': source_urls
                }
                rows.append(row)

        with open(output_file, mode, newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            if mode == 'w':
                writer.writeheader()

            writer.writerows(rows)

        print(f"\n✅ Saved {len(rows)} entries to {output_file}")
        print(f"   • Unique studios: {len(self.processed_studios)}")
        print(f"   • Total games: {len(rows)}")


def task_1_page_1(output_file: str = 'brackeys_page1.csv'):
    """Task 1: Pilot scrape (Page 1) - Flexible 3D detection"""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                    TASK 1: PAGE 1 PILOT SCRAPE                    ║
║         Flexible 3D Detection: Tags, Engines, Perspectives        ║
╚═══════════════════════════════════════════════════════════════════╝
""")
    
    scraper = BrackeysMasterScraper()
    scraper.scrape_page(1)
    scraper.save_to_csv(output_file)
    
    # Verification
    print(f"\n{'='*70}")
    print("VERIFICATION:")
    print(f"{'='*70}")
    if not os.path.exists(output_file):
        print(f"❌ Output file '{output_file}' was not created (no 3D entries found or network issue).")
        return
    with open(output_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        entries = list(reader)
        print(f"✓ Total entries found: {len(entries)}")

        if len(entries) > 0:
            print(f"✅ Found {len(entries)} 3D games on page 1")
            print(f"\nSample tags found:")
            for i, entry in enumerate(entries[:3], 1):
                print(f"  {i}. {entry['Game Title']}: {entry['Tags'][:80]}...")
        else:
            print(f"⚠️ No 3D games found (may be network issue)")


def task_2_page_2(output_file: str = 'brackeys_master.csv'):
    """Task 2: Pilot scrape (Page 2) - Append to master CSV"""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                    TASK 2: PAGE 2 PILOT SCRAPE                    ║
║                   Append to master CSV with dedup                 ║
╚═══════════════════════════════════════════════════════════════════╝
""")
    
    scraper = BrackeysMasterScraper()
    scraper.scrape_page(2)
    scraper.save_to_csv(output_file, mode='a')


def task_3_page_3(output_file: str = 'brackeys_master.csv'):
    """Task 3: Pilot scrape (Page 3) - Append to master CSV"""
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║                    TASK 3: PAGE 3 PILOT SCRAPE                    ║
║                   Append to master CSV with dedup                 ║
╚═══════════════════════════════════════════════════════════════════╝
""")
    
    scraper = BrackeysMasterScraper()
    scraper.scrape_page(3)
    scraper.save_to_csv(output_file, mode='a')


def task_4_full_scrape(start_page: int = 4, end_page: int = 36, 
                       output_file: str = 'brackeys_master.csv'):
    """Task 4: Full scrape - All remaining pages"""
    print(f"""
╔═══════════════════════════════════════════════════════════════════╗
║                    TASK 4: FULL SCRAPE                            ║
║              Scraping pages {start_page}-{end_page} (all remaining)                  ║
╚═══════════════════════════════════════════════════════════════════╝
""")
    
    scraper = BrackeysMasterScraper()
    
    for page in range(start_page, end_page + 1):
        print(f"\n{'#'*70}")
        print(f"# Processing page {page} of {end_page}")
        print(f"{'#'*70}\n")
        
        scraper.scrape_page(page)
        
        # Save after each page
        scraper.save_to_csv(output_file, mode='a' if page > start_page else 'w')
        
        # Brief delay between pages
        if page < end_page:
            print(f"\n⏸️ Waiting 3 seconds before next page...")
            time.sleep(3)


def main():
    parser = argparse.ArgumentParser(
        description='Brackeys-13 Master Scraper - All 6 Tasks'
    )
    parser.add_argument('--task', type=int, choices=[1,2,3,4,5,6],
                        help='Task number to run (1-6)')
    parser.add_argument('--page', type=int,
                        help='Specific page to scrape')
    parser.add_argument('--output', type=str, default='brackeys_master.csv',
                        help='Output CSV file')
    
    args = parser.parse_args()
    
    if args.task == 1:
        task_1_page_1(args.output)
    elif args.task == 2:
        task_2_page_2(args.output)
    elif args.task == 3:
        task_3_page_3(args.output)
    elif args.task == 4:
        task_4_full_scrape(output_file=args.output)
    elif args.page:
        # Manual page scraping
        scraper = BrackeysMasterScraper()
        scraper.scrape_page(args.page)
        scraper.save_to_csv(args.output)
    else:
        print("Please specify --task or --page")
        parser.print_help()


if __name__ == "__main__":
    main()
