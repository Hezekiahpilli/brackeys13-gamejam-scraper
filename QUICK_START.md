# 🚀 QUICK START GUIDE

Get started scraping Brackeys-13 jam entries in 3 steps!

## ⚡ Fast Track (3 minutes)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Run the Scraper
```bash
python brackeys_scraper.py --page 2
```

### Step 3: Check Your Results
```bash
# View the CSV
cat brackeys_3d_games.csv

# Or open in Excel/Google Sheets
```

**Done!** You now have a CSV with 3D games and developer contacts from page 2.

---

## 📋 Common Tasks

### Scrape a Different Page
```bash
python brackeys_scraper.py --page 3
```

### Save to Custom File
```bash
python brackeys_scraper.py --page 2 --output my_games.csv
```

### Scrape Multiple Pages (Automatically)
```bash
# Edit batch_scrape.sh to set START_PAGE and END_PAGE
./batch_scrape.sh
```

### Append to Existing CSV
```bash
# First page (creates file)
python brackeys_scraper.py --page 2 --output results.csv

# Additional pages (appends)
python brackeys_scraper.py --page 3 --output results.csv --append
python brackeys_scraper.py --page 4 --output results.csv --append
```

---

## 🔍 What Gets Scraped?

For each 3D game, the scraper collects:

| Data | Example |
|------|---------|
| **Game Info** | Title, URL, Tags, Rating URL |
| **Developer** | Name, Profile URL |
| **Contacts** | Email, Twitter, Discord, Website |

**3D Detection** looks for tags like:
- "3D", "Unity", "Godot", "Unreal"
- "First-Person", "Third-Person", "FPS"
- "Low Poly", "Voxel", "3D Platformer"

---

## ⏱️ How Long Does It Take?

| Task | Time |
|------|------|
| Single page (60 games) | ~8-12 minutes |
| Batch 5 pages | ~40-60 minutes |
| Finding ~10-15 3D games/page | Normal |

The scraper includes delays to be respectful to itch.io servers.

---

## 🐛 Quick Troubleshooting

### "No module named 'requests'"
**Fix**: Run `pip install -r requirements.txt`

### "No data to save"
**Causes**:
- Page number too high (jam only has ~36 pages)
- No 3D games on that particular page (try another)
- Connection issue

**Fix**: Try a different page number

### Can't connect to itch.io
**Fix**: Check your internet connection

### CSV file not opening properly
**Fix**: Use UTF-8 encoding when opening in Excel

---

## 📊 Expected Results (Page 2)

| Metric | Typical Range |
|--------|---------------|
| Games on page | ~60 |
| 3D games found | 10-15 (15-25%) |
| Emails found | 40-50% of 3D games |
| Social links | 60-70% of 3D games |

---

## 💡 Pro Tips

1. **Start with page 2**: Page 1 has the most popular games (often already contacted)

2. **Batch process efficiently**:
   ```bash
   ./batch_scrape.sh  # Processes pages 2-5 automatically
   ```

3. **Check results periodically**: Open CSV after each page to verify quality

4. **Respect rate limits**: Don't modify the built-in delays

5. **Track your outreach**: Add columns to CSV:
   - "contacted" (date)
   - "responded" (yes/no)
   - "interested" (yes/no)

---

## 📁 File Structure

```
brackeys-scraper/
├── brackeys_scraper.py      # Main scraper script
├── requirements.txt         # Python dependencies
├── batch_scrape.sh          # Batch processing script
├── README.md                # Full documentation
├── DEMO_OUTPUT.md           # Example output
└── QUICK_START.md           # This file
```

---

## 🎯 Your Page 2 Mission

Run this now:
```bash
python brackeys_scraper.py --page 2
```

Then check `brackeys_3d_games.csv` for your results!

---

## 🆘 Need Help?

1. Check **README.md** for detailed documentation
2. Read **DEMO_OUTPUT.md** for expected output examples
3. Review error messages in console output
4. Verify itch.io is accessible in your browser

---

## Next Steps

After scraping page 2:

✅ **Review CSV**: Check data quality  
✅ **Scrape more pages**: Use `--append` flag  
✅ **Deduplicate**: Remove any studio duplicates  
✅ **Start outreach**: Contact developers!  

---

**Ready?** Just run:
```bash
pip install -r requirements.txt && python brackeys_scraper.py --page 2
```

That's it! Good luck with your outreach! 🎮
