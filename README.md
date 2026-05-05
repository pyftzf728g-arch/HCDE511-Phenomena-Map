# US Phenomena Timeline Map

Interactive timeline map overlaying Nuclear Facilities, UFO Crashes, UFO Sightings,
Bigfoot Sightings, and National Parks across North America (1869–2019).

## Live site
`https://YOUR-USERNAME.github.io/phenomena-map`

## Layers
| Layer | Dataset | Strategy |
|---|---|---|
| ☢ Nuclear Facilities | 34 facilities | Individual markers, appears when opened |
| ★ UFO Crashes | 11 events | Individual markers |
| ★ UFO Sightings | 70,747 records | Heatmap, decade tiles fetched on demand |
| 🐾 Bigfoot Sightings | 3,475 records | Heatmap, decade tiles fetched on demand |
| 🌲 National Parks | 63 parks | Static markers, always visible |
| 📽📚 Films & Books | 77 events | Sidebar, no map coordinates |

## Deploy to GitHub Pages

```bash
git init
git add .
git commit -m "Initial deploy"
git remote add origin https://github.com/YOUR-USERNAME/phenomena-map.git
git push -u origin main
```

Then: **GitHub repo → Settings → Pages → Deploy from branch: main / (root)**

## Update data
If you get new Excel files, update the filenames in `prepare_data.py` and run:
```bash
python prepare_data.py
git add data/
git commit -m "Update data tiles"
git push
```

## File structure
```
phenomena-map/
├── index.html
├── prepare_data.py
├── README.md
└── data/
    ├── ufo_sightings/      ← one JSON per decade (fetched on demand)
    │   ├── manifest.json
    │   ├── 1910.json ... 2010.json
    ├── bigfoot/            ← one JSON per decade (fetched on demand)
    │   ├── manifest.json
    │   ├── 1860.json ... 2010.json
    └── static/             ← small files, fetched once on load
        ├── nuclear.json
        ├── ufo_crashes.json
        ├── parks.json
        └── cultural_events.json
```
