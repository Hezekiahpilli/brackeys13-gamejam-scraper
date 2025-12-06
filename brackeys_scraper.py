#!/usr/bin/env python3
"""
Brackeys-13 Game Jam Scraper
Scrapes game entries, filters for 3D games, and extracts contact information.

Usage:
    python brackeys_scraper.py --page 2
    python brackeys_scraper.py --page 2 --output results.csv
"""

import requests
from bs4 import BeautifulSoup
import csv
import time
import re
import argparse
from urllib.parse import urljoin, urlparse
from typing import Dict, List, Set, Optional
import sys

class BrackeysScraper:
    def __init__(self, base_url: str = "https://itch.io/jam/brackeys-13/entries"):
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        self.processed_studios = set()
        
    def get_page(self, page_num: int) -> Optional[BeautifulSoup]:
        """Fetch and parse a specific page of jam entries."""
        url = f"{self.base_url}?page={page_num}" if page_num > 1 else self.base_url
        
        try:
            print(f"Fetching page {page_num}...")
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Error fetching page {page_num}: {e}")
            return None
    
    def extract_game_entries(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract game entries from the submissions page."""
        entries = []
        
        # Find all game entries - they're in divs with class 'game_cell'
        game_cells = soup.find_all('div', class_='game_cell')
        
        if not game_cells:
            # Try alternative structure
            game_cells = soup.find_all('a', class_='game_link')
        
        print(f"Found {len(game_cells)} game entries on page")
        
        for cell in game_cells:
            try:
                entry = {}
                
                # Try to find the game link
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
                print(f"Error extracting entry: {e}")
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
            print(f"  Fetching game details: {game_url}")
            response = self.session.get(game_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Extract tags
            tag_elements = soup.find_all('a', class_='tag')
            details['tags'] = [tag.get_text(strip=True) for tag in tag_elements]
            
            # Find jam rate URL
            jam_link = soup.find('a', href=re.compile(r'/jam/brackeys-13/rate/'))
            if jam_link:
                details['jam_rate_url'] = urljoin("https://itch.io", jam_link['href'])
            
            # Extract description (first paragraph)
            desc_elem = soup.find('div', class_='formatted_description')
            if desc_elem:
                details['description'] = desc_elem.get_text(strip=True)[:200]
            
            time.sleep(0.5)  # Be nice to the server
            
        except Exception as e:
            print(f"  Error fetching game details: {e}")
        
        return details
    
    def is_3d_game(self, tags: List[str], title: str = '', description: str = '') -> bool:
        """Determine if a game is 3D based on tags and other indicators."""
        # Tag-based detection
        tags_lower = [tag.lower() for tag in tags]
        
        # Explicit 3D tags
        if '3d' in tags_lower:
            return True
        
        # Common 3D engine/style tags
        three_d_indicators = [
            'unity', 'unreal', 'godot',
            'first-person', 'third-person', 'fps', 'tps',
            '3d platformer', 'low poly', 'voxel',
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
    
    def extract_contact_info(self, developer_url: str, game_url: str) -> Dict:
        """Extract contact information from developer and game pages."""
        contacts = {
            'email': '',
            'twitter': '',
            'discord': '',
            'website': '',
            'other_links': []
        }
        
        # Try developer page first
        if developer_url:
            try:
                print(f"    Checking developer page: {developer_url}")
                response = self.session.get(developer_url, timeout=30)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Look for social links
                social_links = soup.find_all('a', class_='user_link')
                for link in social_links:
                    href = link.get('href', '')
                    if 'twitter.com' in href or 'x.com' in href:
                        contacts['twitter'] = href
                    elif 'discord' in href.lower():
                        contacts['discord'] = href
                    elif href and not href.startswith('#'):
                        contacts['other_links'].append(href)
                
                # Look for email
                email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
                page_text = soup.get_text()
                emails = re.findall(email_pattern, page_text)
                if emails:
                    contacts['email'] = emails[0]
                
                # Look for website link
                profile_links = soup.find_all('a', href=True)
                for link in profile_links:
                    href = link.get('href', '')
                    if href and not any(x in href for x in ['itch.io', 'twitter.com', 'discord']):
                        if href.startswith('http') and 'website' not in contacts:
                            contacts['website'] = href
                            break
                
                time.sleep(0.5)
                
            except Exception as e:
                print(f"    Error fetching developer page: {e}")
        
        # Also check game page for additional contacts
        try:
            print(f"    Checking game page for contacts")
            response = self.session.get(game_url, timeout=30)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for contact section
            page_text = soup.get_text()
            
            # Email
            if not contacts['email']:
                emails = re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', page_text)
                if emails:
                    contacts['email'] = emails[0]
            
            # Social links
            for link in soup.find_all('a', href=True):
                href = link.get('href', '')
                if not contacts['twitter'] and ('twitter.com' in href or 'x.com' in href):
                    contacts['twitter'] = href
                elif not contacts['discord'] and 'discord' in href.lower():
                    contacts['discord'] = href
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"    Error checking game page: {e}")
        
        return contacts
    
    def scrape_page(self, page_num: int) -> List[Dict]:
        """Scrape a complete page and return filtered 3D game entries with contacts."""
        results = []
        
        # Fetch the page
        soup = self.get_page(page_num)
        if not soup:
            return results
        
        # Extract all entries
        entries = self.extract_game_entries(soup)
        print(f"\nProcessing {len(entries)} entries...")
        
        for i, entry in enumerate(entries, 1):
            print(f"\n[{i}/{len(entries)}] Processing: {entry.get('title', 'Unknown')}")
            
            # Get game details
            if 'game_url' in entry:
                details = self.get_game_details(entry['game_url'])
                entry.update(details)
                
                # Check if it's a 3D game
                is_3d = self.is_3d_game(
                    entry.get('tags', []),
                    entry.get('title', ''),
                    entry.get('description', '')
                )
                
                if is_3d:
                    print(f"  ✓ 3D game detected! Tags: {', '.join(entry.get('tags', []))}")
                    
                    # Extract contact info
                    developer = entry.get('developer', '')
                    if developer and developer not in self.processed_studios:
                        contacts = self.extract_contact_info(
                            entry.get('developer_url', ''),
                            entry['game_url']
                        )
                        entry.update(contacts)
                        self.processed_studios.add(developer)
                        
                        results.append(entry)
                    elif developer in self.processed_studios:
                        print(f"  ! Studio '{developer}' already processed, skipping")
                else:
                    print(f"  ✗ Not a 3D game. Tags: {', '.join(entry.get('tags', []))}")
        
        return results
    
    def save_to_csv(self, data: List[Dict], output_file: str, mode: str = 'w'):
        """Save results to CSV file."""
        if not data:
            print("No data to save.")
            return
        
        fieldnames = [
            'title', 'developer', 'game_url', 'developer_url', 'jam_rate_url',
            'tags', 'email', 'twitter', 'discord', 'website', 'other_links'
        ]
        
        with open(output_file, mode, newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            
            if mode == 'w':
                writer.writeheader()
            
            for row in data:
                # Convert lists to strings for CSV
                row_copy = row.copy()
                row_copy['tags'] = ', '.join(row_copy.get('tags', []))
                row_copy['other_links'] = '; '.join(row_copy.get('other_links', []))
                
                # Ensure all fields exist
                for field in fieldnames:
                    if field not in row_copy:
                        row_copy[field] = ''
                
                writer.writerow(row_copy)
        
        print(f"\n✓ Saved {len(data)} entries to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Scrape Brackeys-13 jam entries for 3D games with contact info'
    )
    parser.add_argument('--page', type=int, default=2,
                        help='Page number to scrape (default: 2)')
    parser.add_argument('--output', type=str, default='brackeys_3d_games.csv',
                        help='Output CSV file (default: brackeys_3d_games.csv)')
    parser.add_argument('--append', action='store_true',
                        help='Append to existing CSV instead of overwriting')
    
    args = parser.parse_args()
    
    print(f"""
╔═══════════════════════════════════════════════════════════╗
║        Brackeys-13 Game Jam Scraper (Page {args.page})         ║
║  Filtering for 3D games and extracting contact info      ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    scraper = BrackeysScraper()
    results = scraper.scrape_page(args.page)
    
    mode = 'a' if args.append else 'w'
    scraper.save_to_csv(results, args.output, mode)
    
    print(f"\n{'='*60}")
    print(f"Summary:")
    print(f"  • Page scraped: {args.page}")
    print(f"  • 3D games found: {len(results)}")
    print(f"  • Unique studios: {len(scraper.processed_studios)}")
    print(f"  • Output file: {args.output}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()
