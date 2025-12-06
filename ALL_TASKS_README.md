# Brackeys-13 Game Jam Scraper - Complete 6-Task Solution

**Complete solution for extracting 3D game studio contacts from Brackeys-13 Game Jam**

## 📋 Overview

This package implements all 6 tasks from the project specification:

1. **Pilot scrape (Page 1)** - Identify 3D games and collect studio contacts (8 expected)
2. **Pilot scrape (Page 2)** - Append to master CSV with deduplication  
3. **Pilot scrape (Page 3)** - Append to master CSV with deduplication
4. **Full scrape** - Cover all remaining pages (4-36)
5. **Contact augmentation** - Find missing emails and standardize contacts
6. **Google Sheet creation** - Deliver final formatted Google Sheet

---

## 🎯 Key Requirements

### Strict 3D Filtering
- **CRITICAL**: Only games with an **explicit "3D" tag** are included
- No inference from engines (Unity/Unreal/Godot) or perspectives (FPS/TPS)
- Tag must be exactly "3D" or "3d" in the game's tag list

### CSV Format
```
Studio Name | Game Title | Itch URL | Tags | Primary Contact | Additional Contacts | Source URLs
```

### Contact Priority Order
1. **Email** (highest priority)
2. **Website/Contact page**
3. **Social media** (Twitter/X, Discord, LinkedIn, Bluesky)
4. **Profile fallback** (developer itch.io profile)

### Source URLs
- Only include pages where contacts were actually found
- Exclude: assets, devlogs, stores, non-contact pages
- Format: Semicolon-separated list

### Deduplication
- One entry per unique studio
- If studio has multiple games, consolidate contacts
- All games listed for each studio

---

## 📦 Files Included

### Core Scripts
1. **brackeys_master_scraper.py** - Main scraper (Tasks 1-4)
2. **contact_augmentation.py** - Find missing emails (Task 5)  
3. **google_sheet_creator.py** - Create Google Sheet (Task 6)
4. **complete_workflow.py** - Automated workflow for all tasks

### Documentation
5. **ALL_TASKS_README.md** - This file
6. **requirements.txt** - Python dependencies
7. **SETUP_GUIDE.md** - Detailed setup instructions

---

## 🚀 Quick Start

### Installation
```bash
# Install core dependencies
pip install requests beautifulsoup4 lxml

# Optional: For Google Sheets (Task 6)
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

### Run All Tasks (Automated)
```bash
# Pilot only (Tasks 1-3)
python3 complete_workflow.py --pilot-only

# Full workflow (all 6 tasks, skipping long full scrape)
python3 complete_workflow.py --skip-full-scrape

# Everything including full scrape (6+ hours)
python3 complete_workflow.py
```

### Run Individual Tasks
```bash
# Task 1: Page 1 pilot (8 entries expected)
python3 brackeys_master_scraper.py --task 1

# Task 2: Page 2 pilot
python3 brackeys_master_scraper.py --task 2

# Task 3: Page 3 pilot
python3 brackeys_master_scraper.py --task 3

# Task 4: Full scrape (pages 4-36)
python3 brackeys_master_scraper.py --task 4

# Task 5: Augment contacts
python3 contact_augmentation.py brackeys_master.csv

# Task 6: Create Google Sheet
python3 google_sheet_creator.py brackeys_master_augmented.csv
```

---

## 📊 Task Details

### Task 1: Page 1 Pilot Scrape

**Objective**: Scrape page 1, filter for explicit 3D tag, collect contacts

**Expected Output**: 8 entries (as per PDF specification)

**Verification Criteria**:
- ✅ Exactly 8 entries
- ✅ All entries have explicit "3D" tag
- ✅ Only actionable contact channels (email, website, social)
- ✅ Primary Contact follows priority order
- ✅ Source URLs only include pages where contacts found
- ✅ No non-contact links (assets, devlogs, stores)

**Command**:
```bash
python3 brackeys_master_scraper.py --task 1 --output brackeys_page1.csv
```

**Output File**: `brackeys_page1.csv`

**Processing Time**: ~10-15 minutes

---

### Task 2: Page 2 Pilot Scrape

**Objective**: Scrape page 2, filter for 3D, append to master CSV

**Key Points**:
- Appends to master CSV (doesn't overwrite)
- Deduplicates studios automatically
- If studio from page 1 appears, consolidates contacts

**Command**:
```bash
python3 brackeys_master_scraper.py --task 2 --output brackeys_master.csv
```

**Output File**: `brackeys_master.csv`

**Processing Time**: ~10-15 minutes

---

### Task 3: Page 3 Pilot Scrape

**Objective**: Scrape page 3, filter for 3D, append to master CSV

**Same process as Task 2**

**Command**:
```bash
python3 brackeys_master_scraper.py --task 3 --output brackeys_master.csv
```

**Output File**: `brackeys_master.csv` (updated)

**Processing Time**: ~10-15 minutes

---

### Task 4: Full Scrape (All Remaining Pages)

**Objective**: Scrape pages 4-36, complete the dataset

**Scope**: 
- ~2,168 total entries in jam
- ~60 entries per page  
- 36 pages total
- Pages 4-36 = 33 pages remaining

**Command**:
```bash
python3 brackeys_master_scraper.py --task 4 --output brackeys_master.csv
```

**Output File**: `brackeys_master.csv` (final master list)

**Processing Time**: ~6-8 hours
- ~10-12 minutes per page
- 33 pages × 12 minutes = ~6.6 hours
- Plus rate limiting delays

**Note**: Can be interrupted and resumed by tracking last processed page

---

### Task 5: Contact Augmentation

**Objective**: Find missing emails and standardize contacts

**Process**:
1. Identify studios without email in Primary Contact
2. Visit studio websites to search for emails
3. Look for contact form URLs
4. If no email/form, standardize to best social channel
5. Update CSV with new primary contacts

**Priority for Missing Emails**:
1. Search website for email address
2. Find contact form URL
3. Use Twitter/X profile
4. Use Discord invite
5. Use LinkedIn profile
6. Use Bluesky profile

**Command**:
```bash
python3 contact_augmentation.py brackeys_master.csv
```

**Input**: `brackeys_master.csv`
**Output**: `brackeys_master_augmented.csv`

**Processing Time**: ~5-10 minutes per 10 studios

---

### Task 6: Google Sheet Creation

**Objective**: Create formatted Google Sheet with final data

**Features**:
- Groups games by studio
- Formatted headers
- Frozen header row
- Auto-resized columns
- Shareable link

**Prerequisites**:
1. Google Cloud Project created
2. Google Sheets API enabled
3. Service account credentials (credentials.json)

**Command (with Google Sheets API)**:
```bash
python3 google_sheet_creator.py brackeys_master_augmented.csv
```

**Command (CSV export only)**:
```bash
python3 google_sheet_creator.py brackeys_master_augmented.csv --csv-only
```

**Output**: 
- Google Sheet URL (if API setup)
- OR `brackeys_master_formatted.csv` (if CSV export)

**Processing Time**: ~1-2 minutes

---

## 📄 CSV Format Specifications

### Columns

1. **Studio Name** - Developer/studio name from itch.io
2. **Game Title** - Name of the game
3. **Itch URL** - Direct link to game page
4. **Tags** - All game tags (comma-separated)
5. **Primary Contact** - Best contact (priority order)
6. **Additional Contacts** - Other contacts (semicolon-separated)
7. **Source URLs** - Where contacts were found (semicolon-separated)

### Example Row

```csv
"Pixel Studios","Gravity Shift","https://pixelstudios.itch.io/gravity-shift","3D, Unity, Physics","contact@pixelstudios.com","https://twitter.com/pixelstudios; https://pixelstudios.dev","https://pixelstudios.itch.io; https://pixelstudios.dev"
```

---

## 🔍 Strict Filtering Rules

### What Counts as 3D?

**✅ INCLUDED** (has explicit 3D tag):
```python
Tags: ["3D", "Unity", "First-Person"]  # Has "3D" tag
Tags: ["3d", "Puzzle"]                 # Has "3d" tag
Tags: ["Unity", "3D", "Action"]        # Has "3D" tag
```

**❌ EXCLUDED** (no explicit 3D tag):
```python
Tags: ["Unity", "First-Person", "Puzzle"]  # No "3D" tag
Tags: ["Godot", "FPS", "Shooter"]          # No "3D" tag
Tags: ["Low Poly", "Platformer"]           # No "3D" tag
```

### What Counts as Actionable Contact?

**✅ ACTIONABLE**:
- Email addresses
- Websites with contact pages
- Contact form URLs
- Twitter/X profiles
- Discord invites
- LinkedIn profiles
- Bluesky profiles

**❌ NOT ACTIONABLE**:
- Asset store pages
- Devlog pages
- YouTube channels (unless primary contact)
- Patreon pages (unless primary contact)
- Generic social media without profile

---

## 🔄 Deduplication Logic

### Studio-Level Deduplication

**Scenario**: Same studio has multiple 3D games

**Action**:
1. Keep first occurrence of studio
2. Add additional games to same studio entry
3. Consolidate contacts (use best available)
4. Don't duplicate contact searches

**Example**:
```
Page 2, Entry 5:  "Pixel Studios" - "Gravity Shift"  → Added to CSV
Page 2, Entry 23: "Pixel Studios" - "Moon Walker"     → Game added, no new contact search
Page 3, Entry 8:  "Pixel Studios" - "Space Explorer"  → Game added, no new contact search
```

**Result**: One studio entry with 3 games listed

---

## ⚙️ Advanced Usage

### Custom Page Range
```bash
# Scrape specific pages
python3 brackeys_master_scraper.py --page 5 --output results.csv
python3 brackeys_master_scraper.py --page 6 --output results.csv --append
```

### Resume Interrupted Scrape
```bash
# If scrape stopped at page 15, resume from page 16
# Note: Script doesn't auto-resume, track manually
python3 brackeys_master_scraper.py --task 4
# Edit script to set start_page=16 if needed
```

### Verify Page 1 Results
```bash
# Run task 1, then check the CSV
python3 brackeys_master_scraper.py --task 1
wc -l brackeys_page1.csv  # Should show 9 lines (8 entries + header)
grep "3D\|3d" brackeys_page1.csv  # All should have 3D tag
```

---

## 🛠️ Troubleshooting

### Common Issues

**Issue**: "Only got 6 entries from page 1, expected 8"
- **Cause**: Strict 3D filtering
- **Solution**: Verify game tags on itch.io manually
- **Note**: Count may vary if jam entries change

**Issue**: "No email found for studio X"
- **Cause**: Studio has no public email
- **Solution**: Task 5 will find best alternative contact
- **Expected**: ~40-60% of studios have public emails

**Issue**: "Google Sheets authentication failed"
- **Cause**: Missing credentials.json
- **Solution**: Follow Google Sheets API setup guide
- **Workaround**: Use `--csv-only` flag

**Issue**: "Connection timeout"
- **Cause**: Network issues or rate limiting
- **Solution**: Wait and retry, script has built-in delays

**Issue**: "Duplicate studios in output"
- **Cause**: CSV append mode without loading existing data
- **Solution**: Use the workflow script which handles this

---

## 📈 Expected Statistics

### Per Page
- Total games: ~60
- 3D games: ~10-15 (15-25%)
- Contact success:
  - Email: ~40-50% of 3D games
  - Website: ~20-30%
  - Social: ~60-70%

### Full Jam (All Pages)
- Total entries: ~2,168
- Expected 3D games: ~325-450 (15-25%)
- Expected unique studios: ~300-400
- With emails: ~150-200
- Processing time: ~8-10 hours total

---

## 🎓 Best Practices

### 1. Start with Pilot
```bash
# Always run pilot first to verify approach
python3 complete_workflow.py --pilot-only
```

### 2. Verify Quality
```bash
# Check page 1 results before proceeding
# Expected: 8 entries, all with 3D tag
cat brackeys_page1.csv
```

### 3. Save Incrementally
```bash
# Full scrape saves after each page
# Safe to interrupt and resume
```

### 4. Backup Data
```bash
# Copy CSVs before augmentation
cp brackeys_master.csv brackeys_master_backup.csv
```

### 5. Test Google Sheets
```bash
# Test with small dataset first
head -n 20 brackeys_master.csv > test.csv
python3 google_sheet_creator.py test.csv
```

---

## 📞 Support & Modifications

### Modifying 3D Detection
Edit `brackeys_master_scraper.py`, function `has_explicit_3d_tag()`:
```python
def has_explicit_3d_tag(self, tags: List[str]) -> bool:
    tags_lower = [tag.lower() for tag in tags]
    # Change this to add more acceptable tags
    return '3d' in tags_lower or 'three-d' in tags_lower
```

### Changing Contact Priority
Edit `get_primary_contact()` function:
```python
def get_primary_contact(self, contacts: Dict) -> str:
    # Reorder this to change priority
    if contacts['email']:
        return contacts['email']
    # ... etc
```

### Adjusting Rate Limits
Look for `time.sleep()` calls and modify delay duration:
```python
time.sleep(0.5)  # Change to 1.0 for slower, more polite scraping
```

---

## 📊 Output Examples

### Task 1 Output (brackeys_page1.csv)
```csv
Studio Name,Game Title,Itch URL,Tags,Primary Contact,Additional Contacts,Source URLs
"Pixel Studios","Gravity Shift","https://pixelstudios.itch.io/gravity-shift","3D, Unity, Physics","contact@pixelstudios.com","https://twitter.com/pixelstudios","https://pixelstudios.itch.io"
"Cube Games","Voxel World","https://cubegames.itch.io/voxel-world","3D, Voxel, Adventure","https://twitter.com/cubegames","https://cubegames.dev","https://twitter.com/cubegames"
```

### Task 5 Output (brackeys_master_augmented.csv)
Same format, but with enhanced Primary Contact:
```csv
"Cube Games","Voxel World","https://cubegames.itch.io/voxel-world","3D, Voxel, Adventure","info@cubegames.dev","https://twitter.com/cubegames","https://cubegames.dev"
```

---

## ✅ Success Criteria

Your scraping is successful if:

### Task 1 ✓
- [ ] Exactly 8 entries (or confirmed variance)
- [ ] All have explicit "3D" tag
- [ ] Primary contacts follow priority order
- [ ] Source URLs only show where contacts found

### Task 2-3 ✓
- [ ] Entries appended to master CSV
- [ ] No duplicate studios
- [ ] Deduplication working correctly

### Task 4 ✓
- [ ] All 36 pages processed
- [ ] ~300-400 unique studios
- [ ] Master CSV complete

### Task 5 ✓
- [ ] Missing emails identified
- [ ] Alternative contacts found
- [ ] Augmented CSV created

### Task 6 ✓
- [ ] Google Sheet created (or formatted CSV)
- [ ] Data properly grouped by studio
- [ ] Shareable link provided

---

## 🎉 Final Deliverables

After completing all tasks, you'll have:

1. ✅ `brackeys_page1.csv` - Page 1 pilot (8 entries)
2. ✅ `brackeys_master.csv` - Complete master list
3. ✅ `brackeys_master_augmented.csv` - With enhanced contacts
4. ✅ `brackeys_master_formatted.csv` - Formatted export
5. ✅ Google Sheet URL - Final deliverable (if API setup)

**Total Studios**: ~300-400  
**Total 3D Games**: ~325-450  
**With Email Contacts**: ~150-200  
**Ready for Outreach**: 100%  

---

## 📝 Notes

- All scripts include rate limiting (0.5s delays)
- Respectful to itch.io servers
- Can be interrupted and resumed
- Deduplication is automatic
- Source code is well-commented
- Follows exact PDF specifications

---

**Created for**: Tendem Project - Brackeys-13 Game Jam Developer Outreach  
**Version**: 2.0 - Complete 6-Task Solution  
**Date**: December 2025

For questions or issues, refer to inline code comments or create a GitHub issue.

---

## License

Educational and research purposes. Respect itch.io's terms of service and robots.txt.
