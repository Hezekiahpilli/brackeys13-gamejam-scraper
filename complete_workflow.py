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
    
    def run_full_workflow(self, skip_full_scrape: bool = False):
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
  4. Scrape all remaining pages (optional - can take 6+ hours)
  5. Augment missing contacts
  6. Create Google Sheet

Starting at: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}
""")
        
        # Task 1: Page 1 Pilot
        success = self.run_command(
            ['python', 'brackeys_master_scraper.py', '--task', '1', '--output', 'brackeys_page1.csv'],
            'Task 1: Page 1 Pilot Scrape'
        )
        if not success:
            print("\n⚠️ Task 1 failed. Continue anyway? (y/n): ", end='')
            if input().lower() != 'y':
                return
        
        time.sleep(2)
        
        # Task 2: Page 2 Pilot
        success = self.run_command(
            ['python', 'brackeys_master_scraper.py', '--task', '2', '--output', 'brackeys_master.csv'],
            'Task 2: Page 2 Pilot Scrape'
        )
        if not success:
            print("\n⚠️ Task 2 failed. Continue anyway? (y/n): ", end='')
            if input().lower() != 'y':
                return
        
        time.sleep(2)
        
        # Task 3: Page 3 Pilot
        success = self.run_command(
            ['python', 'brackeys_master_scraper.py', '--task', '3', '--output', 'brackeys_master.csv'],
            'Task 3: Page 3 Pilot Scrape'
        )
        if not success:
            print("\n⚠️ Task 3 failed. Continue anyway? (y/n): ", end='')
            if input().lower() != 'y':
                return
        
        time.sleep(2)
        
        # Task 4: Full Scrape (optional)
        if not skip_full_scrape:
            print("\n" + "="*70)
            print("TASK 4: FULL SCRAPE")
            print("="*70)
            print("\n⚠️ Warning: This will scrape pages 4-36 and may take 6+ hours.")
            print("   You can skip this and run it separately later.")
            print("\nContinue with full scrape? (y/n): ", end='')
            
            if input().lower() == 'y':
                success = self.run_command(
                    ['python', 'brackeys_master_scraper.py', '--task', '4', '--output', 'brackeys_master.csv'],
                    'Task 4: Full Scrape (Pages 4-36)'
                )
            else:
                print("\n⏭️ Skipping full scrape. Run manually later with:")
                print("   python brackeys_master_scraper.py --task 4")
                self.results['Task 4: Full Scrape'] = {
                    'status': 'SKIPPED',
                    'timestamp': datetime.now().isoformat()
                }
        else:
            print("\n⏭️ Full scrape skipped (--skip-full-scrape flag)")
            self.results['Task 4: Full Scrape'] = {
                'status': 'SKIPPED',
                'timestamp': datetime.now().isoformat()
            }
        
        time.sleep(2)
        
        # Task 5: Contact Augmentation
        csv_file = 'brackeys_master.csv' if os.path.exists('brackeys_master.csv') else 'brackeys_page1.csv'
        success = self.run_command(
            ['python', 'contact_augmentation.py', csv_file],
            'Task 5: Contact Augmentation'
        )
        
        time.sleep(2)
        
        # Task 6: Google Sheet Creation
        augmented_file = csv_file.replace('.csv', '_augmented.csv')
        final_file = augmented_file if os.path.exists(augmented_file) else csv_file
        
        print("\n" + "="*70)
        print("TASK 6: GOOGLE SHEET CREATION")
        print("="*70)
        print("\nDo you have Google Sheets API credentials setup? (y/n): ", end='')
        
        if input().lower() == 'y':
            success = self.run_command(
                ['python', 'google_sheet_creator.py', final_file],
                'Task 6: Google Sheet Creation'
            )
        else:
            print("\n📄 Creating formatted CSV instead...")
            success = self.run_command(
                ['python', 'google_sheet_creator.py', final_file, '--csv-only'],
                'Task 6: Formatted CSV Export'
            )
        
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
                        help='Run only pilot tasks (1-3)')
    parser.add_argument('--skip-full-scrape', action='store_true',
                        help='Skip task 4 (full scrape)')
    
    args = parser.parse_args()
    
    workflow = BrackeysWorkflow()
    
    if args.pilot_only:
        workflow.run_pilot_only()
    else:
        workflow.run_full_workflow(skip_full_scrape=args.skip_full_scrape)


if __name__ == "__main__":
    main()
