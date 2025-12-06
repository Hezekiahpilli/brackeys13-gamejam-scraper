# Brackeys-13 Game Jam Scraper

A comprehensive Python scraper for the Brackeys Game Jam 2025.1, specifically designed to:
- Extract game entries from the jam submissions
- Filter for 3D games based on tags and indicators
- Collect developer/studio contact information
- Deduplicate entries by studio
- Export to CSV format

## Features

### 🎮 Game Detection
- Scrapes paginated jam entries from itch.io
- Extracts: title, developer, game URL, jam rating URL, tags
- Visits individual game pages for detailed information

### 🎯 3D Game Filtering
Identifies 3D games using multiple signals:
- **Direct tags**: "3D", "3d"
- **Engine indicators**: Unity, Unreal, Godot references
- **Perspective tags**: First-person, Third-person, FPS, TPS
- **Style tags**: Low poly, Voxel, 3D Platformer
- **Text analysis**: Checks title and description for "3D" mentions

### 📧 Contact Extraction
Automatically extracts from developer and game pages:
- Email addresses
- Twitter/X profiles
- Discord links
- Personal websites
- Other social/contact links

### 🔄 Deduplication
- Tracks processed studios to avoid duplicates
- Single entry per unique developer/studio

## Installation

### Prerequisites
- Python 3.7 or higher
- pip package manager

### Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Or install manually
pip install requests beautifulsoup4 lxml
```

## Usage

### Basic Usage - Scrape Page 2
```bash
python brackeys_scraper.py --page 2
```

### Custom Output File
```bash
python brackeys_scraper.py --page 2 --output my_results.csv
```

### Append to Existing CSV
```bash
python brackeys_scraper.py --page 3 --output brackeys_3d_games.csv --append
```

### Scrape Multiple Pages
```bash
# Scrape pages 2-5 and combine into one CSV
python brackeys_scraper.py --page 2 --output results.csv
python brackeys_scraper.py --page 3 --output results.csv --append
python brackeys_scraper.py --page 4 --output results.csv --append
python brackeys_scraper.py --page 5 --output results.csv --append
```

## Command-Line Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--page` | Page number to scrape | 2 |
| `--output` | Output CSV filename | brackeys_3d_games.csv |
| `--append` | Append to existing file instead of overwriting | False |

## Output Format

The CSV file contains the following columns:

| Column | Description |
|--------|-------------|
| `title` | Game title |
| `developer` | Developer/Studio name |
| `game_url` | Direct link to game page |
| `developer_url` | Developer profile URL |
| `jam_rate_url` | Jam rating/submission URL |
| `tags` | Comma-separated game tags |
| `email` | Contact email (if found) |
| `twitter` | Twitter/X profile URL |
| `discord` | Discord invite/profile link |
| `website` | Personal/studio website |
| `other_links` | Additional contact/social links |

## How It Works

### 1. Page Fetching
```python
# Fetches: https://itch.io/jam/brackeys-13/entries?page=2
soup = scraper.get_page(2)
```

### 2. Entry Extraction
Parses HTML to extract game cards with:
- Game title and URL
- Developer name and profile link

### 3. Detail Gathering
For each entry, visits the game page to collect:
- Tags (for 3D detection)
- Jam rating URL
- Game description

### 4. 3D Filtering
Applies multi-criteria check:
```python
is_3d = is_3d_game(tags=['Unity', 'First-Person', '3D'])
# Returns: True
```

### 5. Contact Extraction
If 3D game detected and studio not yet processed:
- Visits developer profile page
- Scans for email, social links, website
- Also checks game page for additional contacts

### 6. CSV Export
Writes filtered results to CSV with all contact info

## Rate Limiting & Etiquette

The scraper includes built-in delays:
- 0.5 seconds between game page requests
- 0.5 seconds between developer page requests
- Proper User-Agent headers

**Be respectful**: Don't hammer the server. The built-in delays are intentional.

## Example Output

```csv
title,developer,game_url,developer_url,jam_rate_url,tags,email,twitter,discord,website,other_links
"Gravity Shift","Pixel Studios","https://pixelstudios.itch.io/gravity-shift","https://pixelstudios.itch.io","https://itch.io/jam/brackeys-13/rate/3348230","Unity, 3D, First-Person, Puzzle","contact@pixelstudios.com","https://twitter.com/pixelstudios","","https://pixelstudios.dev",""
```

## Troubleshooting

### No entries found
- Check if the page number exists (jam had ~2,168 entries, ~36 pages)
- Verify internet connection
- itch.io structure may have changed

### Permission errors
- Ensure you have write permissions in the directory
- Try a different output path

### Connection timeouts
- Check your internet connection
- itch.io may be temporarily unavailable
- Try again later

### No 3D games found
- Some pages may genuinely have fewer 3D games
- Check the console output to see what tags were detected

## Advanced: Batch Processing Script

Create a shell script to process multiple pages:

```bash
#!/bin/bash
# scrape_all_pages.sh

for page in {2..10}
do
    echo "Processing page $page..."
    python brackeys_scraper.py --page $page --output all_3d_games.csv --append
    sleep 2  # Extra delay between pages
done

echo "Done! Check all_3d_games.csv"
```

Make it executable and run:
```bash
chmod +x scrape_all_pages.sh
./scrape_all_pages.sh
```

## 3D Detection Rules (Reference)

The scraper considers a game as 3D if it has any of these:

**Direct indicators:**
- Tag: "3D" or "3d"

**Engine/Framework tags:**
- Unity, Unreal, Godot

**Perspective tags:**
- First-Person, Third-Person, FPS, TPS

**Style tags:**
- 3D Platformer, Low Poly, Voxel

**Text mentions:**
- "3D", "three dimensional", "three-dimensional" in title/description

## Limitations

1. **Contact Info Completeness**: Not all developers list public contact information
2. **Tag Reliability**: Depends on developers correctly tagging their games
3. **Rate Limits**: Intentionally slow to respect server resources
4. **Structure Changes**: itch.io may update their HTML structure

## Future Enhancements

Potential improvements:
- Screenshot download
- Genre classification
- Play count/rating scraping
- Export to JSON format
- Parallel processing (with careful rate limiting)
- GUI interface

## License

This scraper is for educational and research purposes. Respect itch.io's terms of service and robots.txt.

## Support

For issues or questions about this scraper, check:
1. The error message in console output
2. The troubleshooting section above
3. Verify itch.io is accessible in your browser

---

**Note**: This tool was created for the Tendem project to help identify 3D game developers from the Brackeys Game Jam 2025.1 for potential collaboration and outreach purposes.
