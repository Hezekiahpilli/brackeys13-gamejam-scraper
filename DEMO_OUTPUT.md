# DEMONSTRATION OUTPUT - Page 2 Scraping

This file shows what you can expect when running the scraper on page 2 of Brackeys-13 entries.

## Expected Console Output:

```
╔═══════════════════════════════════════════════════════════╗
║        Brackeys-13 Game Jam Scraper (Page 2)              ║
║  Filtering for 3D games and extracting contact info      ║
╚═══════════════════════════════════════════════════════════╝

Fetching page 2...
Found 60 game entries on page

Processing 60 entries...

[1/60] Processing: Pixel Warriors
  Fetching game details: https://gamestudio.itch.io/pixel-warriors
  ✗ Not a 3D game. Tags: 2D, Pixel Art, Action

[2/60] Processing: Cube Runner 3D
  Fetching game details: https://devteam.itch.io/cube-runner-3d
  ✓ 3D game detected! Tags: 3D, Unity, First-Person, Puzzle
    Checking developer page: https://devteam.itch.io
    Checking game page for contacts
  ✓ Contacts extracted: email, twitter

[3/60] Processing: Retro Adventure
  Fetching game details: https://retrodev.itch.io/retro-adventure
  ✗ Not a 3D game. Tags: 2D, Retro, Platformer

[4/60] Processing: Gravity Shift
  Fetching game details: https://pixelstudios.itch.io/gravity-shift
  ✓ 3D game detected! Tags: Unity, Third-Person, Physics
    Checking developer page: https://pixelstudios.itch.io
    Checking game page for contacts
  ✓ Contacts extracted: email, twitter, website

[5/60] Processing: Maze Explorer
  Fetching game details: https://indiegames.itch.io/maze-explorer
  ✓ 3D game detected! Tags: 3D, Godot, FPS
    Checking developer page: https://indiegames.itch.io
    Checking game page for contacts
  ✓ Contacts extracted: discord

...

[60/60] Processing: Final Game
  Fetching game details: https://lastdev.itch.io/final-game
  ✗ Not a 3D game. Tags: Visual Novel, Story

✓ Saved 12 entries to brackeys_3d_games.csv

============================================================
Summary:
  • Page scraped: 2
  • 3D games found: 12
  • Unique studios: 12
  • Output file: brackeys_3d_games.csv
============================================================
```

## Expected CSV Output Sample:

```csv
title,developer,game_url,developer_url,jam_rate_url,tags,email,twitter,discord,website,other_links
"Cube Runner 3D","DevTeam","https://devteam.itch.io/cube-runner-3d","https://devteam.itch.io","https://itch.io/jam/brackeys-13/rate/3348500","3D, Unity, First-Person, Puzzle","contact@devteam.com","https://twitter.com/devteam","","",""
"Gravity Shift","Pixel Studios","https://pixelstudios.itch.io/gravity-shift","https://pixelstudios.itch.io","https://itch.io/jam/brackeys-13/rate/3348501","Unity, Third-Person, Physics","hello@pixelstudios.dev","https://twitter.com/pixelstudios","","https://pixelstudios.dev",""
"Maze Explorer","IndieGames","https://indiegames.itch.io/maze-explorer","https://indiegames.itch.io","https://itch.io/jam/brackeys-13/rate/3348502","3D, Godot, FPS","","","https://discord.gg/indiegames","",""
"Voxel Voyage","CubeCreators","https://cubecreators.itch.io/voxel-voyage","https://cubecreators.itch.io","https://itch.io/jam/brackeys-13/rate/3348503","3D, Voxel, Adventure","team@cubecreators.net","","","https://cubecreators.net",""
"Parkour Pro","MotionStudios","https://motionstudios.itch.io/parkour-pro","https://motionstudios.itch.io","https://itch.io/jam/brackeys-13/rate/3348504","Unity, 3D Platformer, Third-Person","info@motionstudios.com","https://twitter.com/motionstudios","https://discord.gg/motion","",""
```

## Statistics to Expect:

Based on typical game jam distributions:
- **Total entries on page 2**: ~60 games
- **3D games**: ~10-15 games (15-25% are typically 3D)
- **Contacts found**:
  - Email: ~40% of 3D games
  - Twitter: ~60% of 3D games
  - Discord: ~30% of 3D games
  - Website: ~20% of 3D games

## Processing Time Estimate:

- Basic page fetch: 1-2 seconds
- Per game detail fetch: 0.5-1 second
- Per developer page: 0.5-1 second
- **Total for page 2**: ~8-12 minutes
  - 60 games × 1 second = ~1 minute for initial fetch
  - ~12 3D games × 3 seconds each = ~40 seconds for details
  - ~12 developer pages × 1 second = ~12 seconds
  - Plus rate limiting delays

## 3D Game Detection Examples:

### DETECTED as 3D:
✓ Tags: ["3D", "Unity", "First-Person"]
✓ Tags: ["Godot", "Third-Person", "Adventure"]
✓ Tags: ["Low Poly", "3D Platformer"]
✓ Tags: ["Unreal Engine", "FPS"]
✓ Title: "My Amazing 3D Game"

### NOT DETECTED as 3D:
✗ Tags: ["2D", "Pixel Art", "Platformer"]
✗ Tags: ["Visual Novel", "Story"]
✗ Tags: ["Puzzle", "Strategy"]
✗ Tags: ["Top-Down", "Roguelike"]

## Contact Extraction Examples:

### From Developer Profile:
- Bio text containing email: contact@studio.com
- Social links section: Twitter, Discord
- External links: Personal website

### From Game Page:
- Description mentioning: "Contact us at..."
- Footer links: Social media profiles
- About section: Email addresses

## Error Scenarios:

### Possible Issues:
1. **No 3D games on page**: Some pages may have fewer or no 3D games
   - Output: "No data to save."
   
2. **Connection timeout**: Network issues
   - Output: "Error fetching page 2: ..."
   
3. **Missing contacts**: Not all developers provide public contact info
   - Output: Empty fields in CSV (still saved)

## Deduplication Example:

```
[5/60] Processing: Another Game
  ✓ 3D game detected!
    ! Studio 'DevTeam' already processed, skipping
```

This means "DevTeam" already had a 3D game earlier in the same page,
so only their first 3D game is included in the results.

## Next Steps After Scraping:

1. **Open the CSV** in Excel/Google Sheets
2. **Verify 3D detection** - Check if tags make sense
3. **Contact developers** - Use the extracted contact info
4. **Append more pages** - Run with --append flag for pages 3, 4, etc.
5. **Deduplicate across pages** - Remove any studio duplicates manually or with a script

## Pro Tips:

1. **Save raw data**: Keep the CSV as your master source
2. **Track outreach**: Add columns for "contacted", "responded", "interested"
3. **Multiple pages**: Use the batch script to process pages 2-10
4. **Backup**: Git commit your CSV after each page

---

This demonstration shows the typical workflow and output you'll see
when running the scraper on page 2 of the Brackeys-13 jam entries.
