# Setup Guide - Brackeys-13 Complete Scraper

Complete setup instructions for all 6 tasks.

---

## 🔧 Prerequisites

### Required
- **Python 3.7+** - Check with `python3 --version`
- **pip** - Check with `pip --version`
- **Internet connection** - For scraping itch.io

### Optional (Task 6 only)
- **Google Cloud Account** - For Google Sheets API
- **Google Sheets API enabled** - In Google Cloud Console

---

## 📥 Installation

### Step 1: Install Core Dependencies

```bash
# Install required packages
pip install requests beautifulsoup4 lxml
```

### Step 2: Install Google Sheets API (Optional - Task 6)

```bash
# Only needed if creating actual Google Sheets
pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

**OR install everything at once:**
```bash
pip install -r requirements.txt
```

---

## 🔑 Google Sheets API Setup (Task 6)

### Option 1: Service Account (Recommended)

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/

2. **Create New Project**
   - Click "Select a project" → "New Project"
   - Name: "Brackeys Scraper" 
   - Click "Create"

3. **Enable Google Sheets API**
   - Go to "APIs & Services" → "Library"
   - Search for "Google Sheets API"
   - Click "Enable"

4. **Create Service Account**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "Service Account"
   - Name: "brackeys-scraper-bot"
   - Click "Create and Continue"

5. **Download Credentials**
   - Click on the service account you created
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key"
   - Choose "JSON" format
   - Click "Create"
   - Save as `credentials.json` in the same folder as scripts

6. **Test Setup**
   ```bash
   python3 google_sheet_creator.py test.csv
   ```

### Option 2: Skip Google Sheets (Use CSV Export)

If you don't want to set up Google Sheets API:

```bash
# This creates a formatted CSV instead
python3 google_sheet_creator.py brackeys_master.csv --csv-only
```

You can then manually import the CSV to Google Sheets.

---

## 🚦 Quick Test

### Test 1: Basic Scraping Works

```bash
# Test scraping a single page
python3 brackeys_master_scraper.py --page 1 --output test.csv

# Check output
cat test.csv
```

**Expected**: CSV file with some 3D game entries

### Test 2: Full Workflow (Pilot Only)

```bash
# Run pilot tasks (1-3) without Google Sheets
python3 complete_workflow.py --pilot-only

# Check outputs
ls -lh brackeys*.csv
```

**Expected**: 
- `brackeys_page1.csv` (~8 entries)
- `brackeys_master.csv` (combined pages 1-3)

### Test 3: Google Sheets (If Setup)

```bash
# Create test data
head -n 10 brackeys_master.csv > test_small.csv

# Try creating Google Sheet
python3 google_sheet_creator.py test_small.csv
```

**Expected**: Google Sheet URL or formatted CSV

---

## 📁 File Structure

After setup, your directory should look like:

```
brackeys-scraper/
├── brackeys_master_scraper.py      # Main scraper
├── contact_augmentation.py         # Task 5
├── google_sheet_creator.py         # Task 6
├── complete_workflow.py            # Automated workflow
├── requirements.txt                # Dependencies
├── ALL_TASKS_README.md             # Full documentation
├── SETUP_GUIDE.md                  # This file
└── credentials.json                # (Optional) Google API credentials
```

---

## ⚙️ Configuration

### Adjusting Rate Limits

In `brackeys_master_scraper.py`, look for:
```python
time.sleep(0.5)  # Delay between requests
```

Change to:
```python
time.sleep(1.0)  # Slower, more polite
```

### Changing Output File Names

```bash
# Use custom output file
python3 brackeys_master_scraper.py --task 1 --output my_results.csv
```

### Modifying 3D Detection

Edit `brackeys_master_scraper.py`, function `has_explicit_3d_tag()` (line ~150)

Current (strict):
```python
def has_explicit_3d_tag(self, tags: List[str]) -> bool:
    tags_lower = [tag.lower() for tag in tags]
    return '3d' in tags_lower
```

More lenient (if needed):
```python
def has_explicit_3d_tag(self, tags: List[str]) -> bool:
    tags_lower = [tag.lower() for tag in tags]
    # Also accept games tagged with engines or perspectives
    return ('3d' in tags_lower or 
            any(x in tags_lower for x in ['unity', 'unreal', 'godot', 
                                           'first-person', 'third-person']))
```

---

## 🔍 Verification

### Verify Task 1 Output

```bash
# Run task 1
python3 brackeys_master_scraper.py --task 1

# Check entry count (should be 8 + 1 header = 9 lines)
wc -l brackeys_page1.csv

# Verify all have 3D tag
grep -i "3d" brackeys_page1.csv | wc -l
```

### Verify Contact Priority

```bash
# Check primary contacts
cut -d',' -f5 brackeys_page1.csv
```

Expected: Email addresses first, then websites, then social

### Verify Source URLs

```bash
# Check source URLs column
cut -d',' -f7 brackeys_page1.csv
```

Expected: Only developer profiles, websites, and social profile URLs

---

## 🛠️ Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'requests'"

**Solution:**
```bash
pip install requests beautifulsoup4 lxml
```

### Issue: "Permission denied" when running scripts

**Solution:**
```bash
chmod +x *.py
# OR run with python3 explicitly
python3 brackeys_master_scraper.py --task 1
```

### Issue: "Connection timeout" or "403 Forbidden"

**Possible causes:**
1. Network restriction
2. itch.io temporarily blocking
3. Rate limit hit

**Solutions:**
1. Check internet connection
2. Wait 5-10 minutes and retry
3. Increase delay in code (see Configuration section)

### Issue: Google Sheets API "404 Not Found"

**Solutions:**
1. Verify API is enabled in Google Cloud Console
2. Check credentials.json is in correct location
3. Verify service account has Sheets API access

### Issue: "Expected 8 entries, got 6"

This is normal if:
- Some page 1 games don't have explicit "3D" tag
- Jam entries changed since PDF was created

**Verification:**
Manually check page 1 on itch.io: https://itch.io/jam/brackeys-13/entries

Count games with explicit "3D" tag.

---

## 🔐 Security Notes

### credentials.json
- **Do NOT commit to Git**
- Add to `.gitignore`
- Keep private and secure
- Contains API access keys

```bash
# Add to .gitignore
echo "credentials.json" >> .gitignore
```

### CSV Files
- May contain email addresses
- Respect privacy and GDPR
- Use only for intended outreach
- Don't publish publicly without consent

---

## 📊 Performance Optimization

### For Faster Scraping (Use with Caution)

```python
# In brackeys_master_scraper.py
# Reduce delays (may risk IP blocking)
time.sleep(0.3)  # Instead of 0.5
```

### For Slower, More Polite Scraping

```python
# Increase delays
time.sleep(1.0)  # Instead of 0.5
```

### For Large-Scale Scraping

Consider:
1. Running overnight (full scrape takes 6-8 hours)
2. Using VPN if rate limited
3. Splitting pages across multiple runs

---

## 🔄 Update & Maintenance

### Keep Dependencies Updated

```bash
# Update all packages
pip install --upgrade requests beautifulsoup4 lxml

# Or update from requirements.txt
pip install --upgrade -r requirements.txt
```

### Check for Script Updates

The scripts are static, but itch.io structure may change.

If scraping fails:
1. Check if itch.io changed HTML structure
2. Update selectors in code (search for `find_all` calls)
3. Test with single page first

---

## 📱 Platform-Specific Notes

### Windows
```bash
# Use python instead of python3
python brackeys_master_scraper.py --task 1

# Path separators
python3 google_sheet_creator.py brackeys_master.csv
```

### macOS
```bash
# May need to install certificates
/Applications/Python*/Install\ Certificates.command

# Or:
pip install --upgrade certifi
```

### Linux
```bash
# Should work out of the box
python3 brackeys_master_scraper.py --task 1
```

---

## ✅ Setup Checklist

Before starting scraping:

- [ ] Python 3.7+ installed and working
- [ ] pip working and updated
- [ ] Core dependencies installed (`requests`, `beautifulsoup4`, `lxml`)
- [ ] Scripts downloaded to a folder
- [ ] Test run completed successfully
- [ ] (Optional) Google Sheets API setup completed
- [ ] (Optional) credentials.json in correct location

---

## 🎯 Ready to Start!

Once setup is complete:

### For Pilot Only (Fast, ~30-40 minutes)
```bash
python3 complete_workflow.py --pilot-only
```

### For Complete Workflow (Slow, ~8-10 hours)
```bash
python3 complete_workflow.py
```

### For Individual Tasks
See `ALL_TASKS_README.md` for detailed task commands.

---

**Setup complete!** 🎉

For detailed usage instructions, see `ALL_TASKS_README.md`

For troubleshooting, refer to the Troubleshooting section above.

Good luck with your Brackeys-13 developer outreach! 🎮
