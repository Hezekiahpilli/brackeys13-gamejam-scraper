#!/usr/bin/env python3
"""
Task 6: Google Sheet Creation
Creates a formatted Google Sheet from the finalized CSV.

NOTE: Requires Google Sheets API credentials.
Setup instructions included in comments.
"""

import csv
from collections import defaultdict
from typing import List, Dict

# Google Sheets API will be imported only when needed
GOOGLE_AVAILABLE = None  # Will be checked lazily


class GoogleSheetCreator:
    """
    Creates and formats a Google Sheet from CSV data.
    
    Setup instructions:
    1. Go to https://console.cloud.google.com/
    2. Create a new project
    3. Enable Google Sheets API
    4. Create service account credentials
    5. Download credentials.json
    6. Place credentials.json in the same directory as this script
    """
    
    def __init__(self, csv_file: str, credentials_file: str = 'credentials.json'):
        self.csv_file = csv_file
        self.credentials_file = credentials_file
        self.service = None
    
    def authenticate(self):
        """Authenticate with Google Sheets API."""
        global GOOGLE_AVAILABLE

        # Lazy import of Google libraries
        if GOOGLE_AVAILABLE is None:
            try:
                from google.oauth2.credentials import Credentials
                from google.oauth2 import service_account
                from googleapiclient.discovery import build
                from googleapiclient.errors import HttpError
                GOOGLE_AVAILABLE = True
            except ImportError as e:
                GOOGLE_AVAILABLE = False
                print(f"⚠️ Google API libraries not installed: {e}")
                print("   Run: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
                return False

        if not GOOGLE_AVAILABLE:
            print("❌ Google API libraries not available")
            return False
        
        try:
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            self.service = build('sheets', 'v4', credentials=creds)
            print("✅ Authenticated with Google Sheets API")
            return True
        except Exception as e:
            print(f"❌ Authentication error: {e}")
            return False
    
    def load_and_group_data(self) -> Dict:
        """Load CSV and group games by studio."""
        studios = defaultdict(lambda: {
            'games': [],
            'primary_contact': '',
            'additional_contacts': '',
            'source_urls': ''
        })
        
        with open(self.csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                studio = row['Studio Name']
                studios[studio]['games'].append({
                    'title': row['Game Title'],
                    'url': row['Itch URL'],
                    'tags': row['Tags']
                })
                
                # Use first occurrence for contacts
                if not studios[studio]['primary_contact']:
                    studios[studio]['primary_contact'] = row.get('Primary Contact', '')
                    studios[studio]['additional_contacts'] = row.get('Additional Contacts', '')
                    studios[studio]['source_urls'] = row.get('Source URLs', '')
        
        return studios
    
    def create_sheet_data(self, studios: Dict) -> List[List]:
        """Format data for Google Sheets."""
        rows = [
            ['Studio Name', 'Game Title', 'Itch URL', 'Tags', 'Primary Contact', 
             'Additional Contacts', 'Source URLs']
        ]
        
        for studio_name, data in sorted(studios.items()):
            # Create row for each game
            for i, game in enumerate(data['games']):
                row = [
                    studio_name if i == 0 else '',  # Studio name only on first row
                    game['title'],
                    game['url'],
                    game['tags'],
                    data['primary_contact'] if i == 0 else '',
                    data['additional_contacts'] if i == 0 else '',
                    data['source_urls'] if i == 0 else ''
                ]
                rows.append(row)
        
        return rows
    
    def create_google_sheet(self, title: str = "Brackeys-13 3D Games Contact List") -> str:
        """Create and format a Google Sheet."""
        if not self.service:
            print("❌ Not authenticated. Call authenticate() first.")
            return ""
        
        print(f"\n📊 Creating Google Sheet: '{title}'")
        
        try:
            # Load and format data
            studios = self.load_and_group_data()
            sheet_data = self.create_sheet_data(studios)
            
            # Create spreadsheet
            spreadsheet = {
                'properties': {
                    'title': title
                },
                'sheets': [{
                    'properties': {
                        'title': '3D Games',
                        'gridProperties': {
                            'frozenRowCount': 1
                        }
                    }
                }]
            }
            
            spreadsheet = self.service.spreadsheets().create(
                body=spreadsheet,
                fields='spreadsheetId,spreadsheetUrl'
            ).execute()
            
            spreadsheet_id = spreadsheet.get('spreadsheetId')
            spreadsheet_url = spreadsheet.get('spreadsheetUrl')
            
            print(f"✅ Spreadsheet created: {spreadsheet_id}")
            
            # Write data
            body = {'values': sheet_data}
            self.service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id,
                range='3D Games!A1',
                valueInputOption='RAW',
                body=body
            ).execute()
            
            print(f"✅ Data written: {len(sheet_data) - 1} rows")
            
            # Format the sheet
            self.format_sheet(spreadsheet_id)
            
            # Make it shareable
            self.make_shareable(spreadsheet_id)
            
            print(f"\n{'='*70}")
            print(f"✅ Google Sheet created successfully!")
            print(f"{'='*70}")
            print(f"\n🔗 URL: {spreadsheet_url}")
            print(f"\n📊 Stats:")
            print(f"   • Studios: {len(studios)}")
            print(f"   • Total games: {len(sheet_data) - 1}")
            print(f"\n")
            
            return spreadsheet_url
            
        except HttpError as err:
            print(f"❌ Error creating sheet: {err}")
            return ""
    
    def format_sheet(self, spreadsheet_id: str):
        """Apply formatting to the sheet."""
        requests = [
            # Header row formatting
            {
                'repeatCell': {
                    'range': {
                        'sheetId': 0,
                        'startRowIndex': 0,
                        'endRowIndex': 1
                    },
                    'cell': {
                        'userEnteredFormat': {
                            'backgroundColor': {'red': 0.2, 'green': 0.2, 'blue': 0.2},
                            'textFormat': {
                                'foregroundColor': {'red': 1, 'green': 1, 'blue': 1},
                                'fontSize': 11,
                                'bold': True
                            }
                        }
                    },
                    'fields': 'userEnteredFormat(backgroundColor,textFormat)'
                }
            },
            # Auto-resize columns
            {
                'autoResizeDimensions': {
                    'dimensions': {
                        'sheetId': 0,
                        'dimension': 'COLUMNS',
                        'startIndex': 0,
                        'endIndex': 7
                    }
                }
            }
        ]
        
        body = {'requests': requests}
        self.service.spreadsheets().batchUpdate(
            spreadsheetId=spreadsheet_id,
            body=body
        ).execute()
        
        print("✅ Formatting applied")
    
    def make_shareable(self, spreadsheet_id: str):
        """Make the sheet viewable by anyone with the link."""
        try:
            # This requires Drive API, which might not be enabled
            # If it fails, manual sharing is needed
            print("ℹ️ To make sheet shareable:")
            print("   1. Open the sheet URL")
            print("   2. Click 'Share' button")
            print("   3. Change to 'Anyone with the link can view'")
        except Exception as e:
            pass
    
    def export_formatted_csv(self, output_file: str = None):
        """Export a nicely formatted CSV (alternative to Google Sheets)."""
        if not output_file:
            output_file = self.csv_file.replace('.csv', '_formatted.csv')
        
        print(f"\n📄 Creating formatted CSV: {output_file}")
        
        studios = self.load_and_group_data()
        sheet_data = self.create_sheet_data(studios)
        
        with open(output_file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerows(sheet_data)
        
        print(f"✅ Formatted CSV created: {output_file}")
        print(f"   • Studios: {len(studios)}")
        print(f"   • Total rows: {len(sheet_data) - 1}")


def main():
    import sys
    import argparse
    
    print("""
╔═══════════════════════════════════════════════════════════════════╗
║              TASK 6: GOOGLE SHEET CREATION                        ║
║         Creates formatted Google Sheet from CSV data              ║
╚═══════════════════════════════════════════════════════════════════╝
""")
    
    parser = argparse.ArgumentParser(description='Create Google Sheet from CSV')
    parser.add_argument('csv_file', help='Input CSV file')
    parser.add_argument('--credentials', default='credentials.json',
                        help='Google credentials file')
    parser.add_argument('--title', default='Brackeys-13 3D Games Contact List',
                        help='Sheet title')
    parser.add_argument('--csv-only', action='store_true',
                        help='Create formatted CSV instead of Google Sheet')
    
    args = parser.parse_args()
    
    creator = GoogleSheetCreator(args.csv_file, args.credentials)
    
    if args.csv_only or not GOOGLE_AVAILABLE:
        print("\n📄 Creating formatted CSV (no Google Sheets)...")
        creator.export_formatted_csv()
    else:
        if creator.authenticate():
            creator.create_google_sheet(args.title)
        else:
            print("\n❌ Failed to authenticate. Creating formatted CSV instead...")
            creator.export_formatted_csv()


if __name__ == "__main__":
    main()
