#!/usr/bin/env python3
"""
Task 5: Contact Augmentation
Identifies studios lacking email addresses and attempts to find them
from websites or social profiles.
"""

import csv
import requests
from bs4 import BeautifulSoup
import re
import time
from typing import Dict, List

class ContactAugmenter:
    def __init__(self, csv_file: str):
        self.csv_file = csv_file
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def load_csv(self) -> List[Dict]:
        """Load the master CSV file."""
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            return list(csv.DictReader(f))
    
    def identify_missing_emails(self, data: List[Dict]) -> List[Dict]:
        """Identify studios without email addresses."""
        missing = []
        studios_seen = set()
        
        for row in data:
            studio = row['Studio Name']
            primary = row.get('Primary Contact', '')
            
            # Skip if already processed this studio
            if studio in studios_seen:
                continue
            studios_seen.add(studio)
            
            # Check if email is missing
            if not primary or '@' not in primary:
                missing.append(row)
        
        return missing
    
    def extract_email_from_url(self, url: str) -> str:
        """Try to extract email from a URL."""
        try:
            print(f"      🌐 Checking: {url}")
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            page_text = soup.get_text()
            
            # Look for email patterns
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = re.findall(email_pattern, page_text)
            
            # Filter out common generic emails
            filtered = [e for e in emails if not any(
                x in e.lower() for x in ['noreply', 'example', 'test', 'spam']
            )]
            
            if filtered:
                print(f"      ✅ Found email: {filtered[0]}")
                return filtered[0]
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"      ⚠️ Error: {e}")
        
        return ""
    
    def find_contact_form(self, url: str) -> str:
        """Check if URL has a contact form."""
        try:
            response = self.session.get(url, timeout=15)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Look for contact page links
            for link in soup.find_all('a', href=True):
                href = link.get('href', '').lower()
                text = link.get_text(strip=True).lower()
                
                if 'contact' in href or 'contact' in text:
                    contact_url = href if href.startswith('http') else url.rstrip('/') + '/' + href.lstrip('/')
                    print(f"      📧 Found contact form: {contact_url}")
                    return contact_url
            
            time.sleep(0.5)
            
        except Exception as e:
            print(f"      ⚠️ Error: {e}")
        
        return ""
    
    def get_best_social_contact(self, row: Dict) -> str:
        """Get the most suitable social contact channel."""
        additional = row.get('Additional Contacts', '')
        
        if not additional:
            return ""
        
        # Split additional contacts
        contacts = [c.strip() for c in additional.split(';')]
        
        # Priority: Twitter/X > Discord > LinkedIn > Bluesky
        for contact in contacts:
            if 'twitter.com' in contact or 'x.com' in contact:
                return contact
        
        for contact in contacts:
            if 'discord' in contact.lower():
                return contact
        
        for contact in contacts:
            if 'linkedin.com' in contact:
                return contact
        
        for contact in contacts:
            if 'bsky.app' in contact or 'bluesky' in contact:
                return contact
        
        # Return first available
        return contacts[0] if contacts else ""
    
    def augment_contacts(self) -> Dict:
        """Main augmentation process."""
        print("""
╔═══════════════════════════════════════════════════════════════════╗
║               TASK 5: CONTACT AUGMENTATION                        ║
║          Finding missing emails and standardizing contacts        ║
╚═══════════════════════════════════════════════════════════════════╝
""")
        
        data = self.load_csv()
        missing = self.identify_missing_emails(data)
        
        print(f"\n📊 Analysis:")
        print(f"   • Total studios: {len(set(r['Studio Name'] for r in data))}")
        print(f"   • Studios missing emails: {len(missing)}\n")
        
        if not missing:
            print("✅ All studios have email addresses!")
            return {'updated': 0, 'found_emails': 0}
        
        updates = {}
        found_emails = 0
        
        for i, row in enumerate(missing, 1):
            studio = row['Studio Name']
            print(f"\n[{i}/{len(missing)}] {studio}")
            print(f"   Current primary: {row.get('Primary Contact', 'None')}")
            
            new_email = ""
            new_contact_form = ""
            source_urls = row.get('Source URLs', '').split('; ')
            
            # Try to extract from additional contacts (websites)
            additional = row.get('Additional Contacts', '')
            if additional:
                for contact in additional.split(';'):
                    contact = contact.strip()
                    if contact.startswith('http') and not any(x in contact.lower() for x in 
                        ['twitter', 'discord', 'linkedin', 'bluesky', 'facebook']):
                        # Looks like a website
                        email = self.extract_email_from_url(contact)
                        if email:
                            new_email = email
                            found_emails += 1
                            break
                        else:
                            # Try to find contact form
                            form_url = self.find_contact_form(contact)
                            if form_url:
                                new_contact_form = form_url
            
            # Determine new primary contact
            if new_email:
                updates[studio] = {
                    'primary': new_email,
                    'note': 'Email found from website'
                }
                print(f"   ✅ New primary: {new_email} (email)")
            elif new_contact_form:
                updates[studio] = {
                    'primary': new_contact_form,
                    'note': 'Contact form found'
                }
                print(f"   ✅ New primary: {new_contact_form} (contact form)")
            else:
                # Use best social contact
                social = self.get_best_social_contact(row)
                if social:
                    updates[studio] = {
                        'primary': social,
                        'note': 'Social contact (best available)'
                    }
                    print(f"   ℹ️ New primary: {social} (social)")
                else:
                    print(f"   ❌ No additional contacts found")
        
        # Apply updates to CSV
        if updates:
            self.apply_updates(data, updates)
        
        print(f"\n{'='*70}")
        print(f"Summary:")
        print(f"   • Studios processed: {len(missing)}")
        print(f"   • Emails found: {found_emails}")
        print(f"   • Contact forms found: {sum(1 for u in updates.values() if 'contact form' in u['note'])}")
        print(f"   • Social fallbacks: {sum(1 for u in updates.values() if 'Social' in u['note'])}")
        print(f"{'='*70}\n")
        
        return {'updated': len(updates), 'found_emails': found_emails}
    
    def apply_updates(self, data: List[Dict], updates: Dict):
        """Apply updates to the CSV file."""
        output_file = self.csv_file.replace('.csv', '_augmented.csv')
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            fieldnames = data[0].keys()
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for row in data:
                studio = row['Studio Name']
                if studio in updates:
                    # Update primary contact
                    old_primary = row.get('Primary Contact', '')
                    new_primary = updates[studio]['primary']
                    
                    row['Primary Contact'] = new_primary
                    
                    # Update additional contacts
                    if old_primary and old_primary not in row.get('Additional Contacts', ''):
                        additional = row.get('Additional Contacts', '')
                        row['Additional Contacts'] = f"{old_primary}; {additional}" if additional else old_primary
                
                writer.writerow(row)
        
        print(f"\n✅ Updated CSV saved to: {output_file}")


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python contact_augmentation.py <master_csv_file>")
        print("Example: python contact_augmentation.py brackeys_master.csv")
        sys.exit(1)
    
    csv_file = sys.argv[1]
    augmenter = ContactAugmenter(csv_file)
    augmenter.augment_contacts()


if __name__ == "__main__":
    main()
