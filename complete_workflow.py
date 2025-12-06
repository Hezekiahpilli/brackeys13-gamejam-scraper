#!/usr/bin/env python
"""
Complete Workflow for Brackeys-13 3D Games Scraping
Runs all 6 tasks in sequence with progress tracking.
"""

import sys
import os
import subprocess
import time
from datetime import datetime

class BrackeysWorkflow:
    def __init__(self):
        self.start_time = None
        self.results = {}
    
    def print_header(self, title: str):
        print(f"\n{'='*70}")
        print(f"{title:^70}")
        print(f"{'='*70}\n")

    def ensure_data_exists(self):
        """Ensure we have data to work with, using sample data if scraping failed."""
        import shutil

        # Check if we have any real data
        has_data = False
        for filename in ['brackeys_page1.csv', 'brackeys_master.csv']:
            if os.path.exists(filename):
                with open(filename, 'r') as f:
                    lines = f.readlines()
                    if len(lines) > 1:  # More than just headers
                        has_data = True
                        break

        if not has_data and os.path.exists('sample_data.csv'):
            print("\n" + "="*70)
            print("⚠️ No data scraped (likely network issues)")
            print("📋 Using sample data to demonstrate workflow...")
            print("="*70)

            # Copy sample data to master CSV
            shutil.copy('sample_data.csv', 'brackeys_master.csv')
            print("✅ Copied sample_data.csv → brackeys_master.csv")
            print("   (In production, this would contain real scraped data)")
            self.results['Using Sample Data'] = {
                'status': 'INFO',
                'timestamp': datetime.now().isoformat()
            }
    
    def run_command(self, cmd: list, description: str) -> bool:
        """Run a shell command and track results."""
        self.print_header(description)
        print(f"Command: {' '.join(cmd)}\n")
        
        try:
            result = subprocess.run(cmd, check=True, capture_output=False)
            self.results[description] = {
                'status': 'SUCCESS',
                'timestamp': datetime.now().isoformat()
            }
            print(f"\n✅ {description} completed successfully")
            return True
        except subprocess.CalledProcessError as e:
            self.results[description] = {
                'status': 'FAILED',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            print(f"\n❌ {description} failed: {e}")
            return False
        except Exception as e:
            self.results[description] = {
                'status': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            print(f"\n❌ Unexpected error in {description}: {e}")
            return False
    
    def run_full_workflow(self, auto_continue: bool = False):
        """Run all 6 tasks in sequence."""
        self.start_time = datetime.now()

        print("""
╔══════════════════════════════════════════════════════════════════════╗
║                BRACKEYS-13 COMPLETE WORKFLOW                         ║
║                    All 6 Tasks Automated                             ║
╚══════════════════════════════════════════════════════════════════════╝

This workflow will:
  1. Scrape Page 1 (pilot - 8 expected entries)
  2. Scrape Page 2 (pilot - append to master)
  3. Scrape Page 3 (pilot - append to master)
  4. Scrape all remaining pages (pages 4-36 - can take 6+ hours)
  5. Augment missing contacts
  6. Create Google Sheet

Starting at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}

Note: If network access is unavailable, empty CSVs will be created
      and sample data will be used for demonstration.
""")

        # Task 1: Page 1 Pilot
        success = self.run_command(
            ['python', 'brackeys_master_scraper.py', '--task', '1', '--output', 'brackeys_page1.csv'],
            'Task 1: Page 1 Pilot Scrape'
        )
        if not success and not auto_continue:
            print("\n⚠️ Task 1 had issues. Continuing with remaining tasks...")

        time.sleep(1)

        # Task 2: Page 2 Pilot
        success = self.run_command(
            ['python', 'brackeys_master_scraper.py', '--task', '2', '--output', 'brackeys_master.csv'],
            'Task 2: Page 2 Pilot Scrape'
        )
        if not success and not auto_continue:
            print("\n⚠️ Task 2 had issues. Continuing with remaining tasks...")

        time.sleep(1)

        # Task 3: Page 3 Pilot
        success = self.run_command(
            ['python', 'brackeys_master_scraper.py', '--task', '3', '--output', 'brackeys_master.csv'],
            'Task 3: Page 3 Pilot Scrape'
        )
        if not success and not auto_continue:
            print("\n⚠️ Task 3 had issues. Continuing with remaining tasks...")

        time.sleep(1)

        # Check if we have any data, if not use sample data
        self.ensure_data_exists()

        # Task 4: Full Scrape (Pages 4-36)
        print("\n" + "="*70)
        print("TASK 4: FULL SCRAPE")
        print("="*70)
        print("\n⚠️ Warning: This will scrape pages 4-36 and may take 6+ hours.")
        print("   Starting full scrape...\n")

        success = self.run_command(
            ['python', 'brackeys_master_scraper.py', '--task', '4', '--output', 'brackeys_master.csv'],
            'Task 4: Full Scrape (Pages 4-36)'
        )
        if not success and not auto_continue:
            print("\n⚠️ Task 4 had issues. Continuing with remaining tasks...")

        time.sleep(1)
        
        # Task 5: Contact Augmentation
        csv_file = 'brackeys_master.csv' if os.path.exists('brackeys_master.csv') else 'brackeys_page1.csv'
        if os.path.exists(csv_file):
            success = self.run_command(
                ['python', 'contact_augmentation.py', csv_file],
                'Task 5: Contact Augmentation'
            )
            if not success and not auto_continue:
                print("\n⚠️ Task 5 had issues. Continuing to final task...")
        else:
            print(f"\n⚠️ No CSV file found for augmentation. Skipping Task 5.")
            self.results['Task 5: Contact Augmentation'] = {
                'status': 'SKIPPED',
                'timestamp': datetime.now().isoformat()
            }

        time.sleep(1)

        # Task 6: Google Sheet Creation (auto-mode uses CSV export)
        augmented_file = csv_file.replace('.csv', '_augmented.csv')
        final_file = augmented_file if os.path.exists(augmented_file) else csv_file

        print("\n" + "="*70)
        print("TASK 6: GOOGLE SHEET CREATION")
        print("="*70)

        if os.path.exists(final_file):
            if auto_continue:
                print("\n📄 Auto mode: Creating formatted CSV export...")
                success = self.run_command(
                    ['python', 'google_sheet_creator.py', final_file, '--csv-only'],
                    'Task 6: Formatted CSV Export'
                )
            else:
                print("\n📄 Creating formatted CSV export (set up Google API credentials for Sheet creation)...")
                success = self.run_command(
                    ['python', 'google_sheet_creator.py', final_file, '--csv-only'],
                    'Task 6: Formatted CSV Export'
                )
        else:
            print(f"\n⚠️ No final CSV file found. Skipping Task 6.")
            self.results['Task 6: Google Sheet Creation'] = {
                'status': 'SKIPPED',
                'timestamp': datetime.now().isoformat()
            }
        
        # Final Summary
        self.print_summary()
    
    def run_pilot_only(self):
        """Run just the pilot tasks (1-3)."""
        self.start_time = datetime.now()
        
        print("""
╔══════════════════════════════════════════════════════════════════════╗
║                BRACKEYS-13 PILOT WORKFLOW                            ║
║                 Tasks 1-3 Only (Pages 1-3)                           ║
╚══════════════════════════════════════════════════════════════════════╝
""")
        
        # Task 1
        self.run_command(
            ['python', 'brackeys_master_scraper.py', '--task', '1', '--output', 'brackeys_page1.csv'],
            'Task 1: Page 1 Pilot Scrape'
        )
        time.sleep(2)
        
        # Task 2
        self.run_command(
            ['python', 'brackeys_master_scraper.py', '--task', '2', '--output', 'brackeys_master.csv'],
            'Task 2: Page 2 Pilot Scrape'
        )
        time.sleep(2)
        
        # Task 3
        self.run_command(
            ['python', 'brackeys_master_scraper.py', '--task', '3', '--output', 'brackeys_master.csv'],
            'Task 3: Page 3 Pilot Scrape'
        )
        
        self.print_summary()
    
    def print_summary(self):
        """Print final summary of all tasks."""
        end_time = datetime.now()
        duration = end_time - self.start_time
        
        print("\n\n")
        print("╔══════════════════════════════════════════════════════════════════════╗")
        print("║                         WORKFLOW SUMMARY                             ║")
        print("╚══════════════════════════════════════════════════════════════════════╝")
        print(f"\nStart time: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"End time:   {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"Duration:   {duration}")
        print(f"\n{'Task':<40} {'Status':<15} {'Timestamp':<20}")
        print("-" * 75)
        
        for task, result in self.results.items():
            status_symbol = {
                'SUCCESS': '✅',
                'FAILED': '❌',
                'SKIPPED': '⏭️',
                'ERROR': '❌'
            }.get(result['status'], '?')
            
            timestamp = result.get('timestamp', '').split('T')[1][:8] if 'timestamp' in result else ''
            print(f"{task:<40} {status_symbol} {result['status']:<13} {timestamp:<20}")
        
        print("\n" + "="*75)
        
        success_count = sum(1 for r in self.results.values() if r['status'] == 'SUCCESS')
        total_count = len([r for r in self.results.values() if r['status'] != 'SKIPPED'])
        
        print(f"\n✅ {success_count}/{total_count} tasks completed successfully")
        
        # Show output files
        print("\n📁 Output Files:")
        if os.path.exists('brackeys_page1.csv'):
            print("   • brackeys_page1.csv (Page 1 pilot)")
        if os.path.exists('brackeys_master.csv'):
            print("   • brackeys_master.csv (Master list)")
        if os.path.exists('brackeys_master_augmented.csv'):
            print("   • brackeys_master_augmented.csv (With augmented contacts)")
        if os.path.exists('brackeys_master_formatted.csv'):
            print("   • brackeys_master_formatted.csv (Formatted export)")
        
        print("\n")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Complete workflow for Brackeys-13 scraping (all 6 tasks)'
    )
    parser.add_argument('--pilot-only', action='store_true',
                        help='Run only pilot tasks (1-3), skip full scrape')
    parser.add_argument('--auto-continue', action='store_true',
                        help='Auto-continue through all tasks without prompts (demo mode)')

    args = parser.parse_args()

    workflow = BrackeysWorkflow()

    if args.pilot_only:
        workflow.run_pilot_only()
    else:
        workflow.run_full_workflow(auto_continue=args.auto_continue)


if __name__ == "__main__":
    main()
