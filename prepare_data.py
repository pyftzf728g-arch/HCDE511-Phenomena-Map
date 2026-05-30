"""
prepare_data.py — Run this whenever you update your source Excel files.
Generates all data tiles consumed by index.html.

Usage (run from the repo root folder in your terminal):
    python prepare_data.py

Source files expected in:
    Update UFO Bigfoot Dafa File/
        Cleaned_UFO_Sightings_US_Only-2.xlsx
        Til_2014_Bigfoot_data_with_cities.xlsx
        Cleaned_US_Nuclear_Facilities-4.xlsx
        Cleaned_US_UFO_Crashes-2.xlsx
        Cleaned_US_National_Parks-2.xlsx
        Cleaned_UFO_Films-3.xlsx
        Cleaned_Bigfoot_Films-2.xlsx
        Cleaned_UFO_Books_1900_2014.xlsx
        Cleaned_Bigfoot_Books_1900_2014.xlsx
        Technology.xlsx
"""
import json, os
from collections import defaultdict
import pandas as pd

# ------------------------------------------------------------------
# FOLDER SETUP
# ------------------------------------------------------------------
DATA_FOLDER = os.path.join("Update UFO Bigfoot Dafa File")

os.makedirs("data/ufo_sightings", exist_ok=True)
os.makedirs("data/bigfoot",       exist_ok=True)
os.makedirs("data/static",        exist_ok=True)

# ------------------------------------------------------------------
# HELPER FUNCTIONS
# ------------------------------------------------------------------

def src(filename):
    return os.path.join(DATA_FOLDER, filename)

def safe_year(v):
    try:
        return int(pd.to_datetime(v, errors='coerce').year)
    except:
        return 0

def write_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, separators=(',', ':'))
    kb = os.path.getsize(path) / 1024
    print(f"  -> {path} ({kb:.0f} KB)")


# ── 1. UFO Sightings (large dataset) ──────────────────────────────────────────
print("\n[1/7] UFO Sightings...")

ufo = pd.read_excel(src("Cleaned_UFO_Sightings_US_Only-2.xlsx"))
ufo['year'] = pd.to_datetime(ufo['Date'], errors='coerce').dt.year.fillna(0).astype(int)
ufo = ufo[ufo['year'] > 0]

decades = defaultdict(list)
for _, r in ufo.iterrows():
    decade = (int(r['year']) // 10) * 10
    decades[decade].append({
        "lat":      round(float(r['Latitude']),  2),
        "lng":      round(float(r['Longitude']), 2),
        "year":     int(r['year']),
        "city":     str(r['City'])     if pd.notna(r['City'])           else '',
        "state":    str(r['State'])    if pd.notna(r['State'])          else '',
        "shape":    str(r['Shape'])    if pd.notna(r['Shape'])          else '',
        "duration": str(r['Duration (sec)']) if pd.notna(r['Duration (sec)']) else '',
    })

for decade, records in sorted(decades.items()):
    write_json(f"data/ufo_sightings/{decade}.json", records)
    print(f"     {decade}s: {len(records):>6} records")

write_json("data/ufo_sightings/manifest.json", {
    "decades": sorted(decades.keys()),
    "total":   len(ufo)
})


# ── 2. Bigfoot Sightings ──────────────────────────────────────────────────────
print("\n[2/7] Bigfoot Sightings...")

bf = pd.read_excel(src("Til_2014_Bigfoot_data_with_cities.xlsx"), header=None)
bf.columns = ['City', 'State', 'County', 'Latitude', 'Longitude',
              'Date', 'Classification', 'Temp', 'Precip',
              'Weather', 'Moon', 'Report']
bf['year'] = pd.to_datetime(bf['Date'], errors='coerce').dt.year.fillna(0).astype(int)
bf = bf[bf['year'] > 0]

decades = defaultdict(list)
for _, r in bf.iterrows():
    decade = (int(r['year']) // 10) * 10
    decades[decade].append({
        "lat":   round(float(r['Latitude']),  4),
        "lng":   round(float(r['Longitude']), 4),
        "year":  int(r['year']),
        "cls":   str(r['Classification']),
        "county": str(r['County']),
        "state": str(r['State']),
    })

for decade, records in sorted(decades.items()):
    write_json(f"data/bigfoot/{decade}.json", records)
    print(f"     {decade}s: {len(records):>6} records")

write_json("data/bigfoot/manifest.json", {
    "decades": sorted(decades.keys()),
    "total":   len(bf)
})


# ── 3. Nuclear Facilities ─────────────────────────────────────────────────────
print("\n[3/7] Nuclear Facilities...")

nf = pd.read_excel(src("Cleaned_US_Nuclear_Facilities-4.xlsx"))
data = []
for _, r in nf.iterrows():
    try:
        data.append({
            "name":  str(r['Facility']),
            "type":  str(r['Type']),
            "city":  str(r['City']),
            "state": str(r['State']),
            "lat":   round(float(r['Latitude']),  5),
            "lng":   round(float(r['Longitude']), 5),
            "year":  int(r['Year Opened'])
        })
    except:
        pass

write_json("data/static/nuclear.json", data)
print(f"     {len(data)} facilities")


# ── 4. UFO Crashes ────────────────────────────────────────────────────────────
print("\n[4/7] UFO Crashes...")

ufc = pd.read_excel(src("Cleaned_US_UFO_Crashes-2.xlsx"))
data = []
for _, r in ufc.iterrows():
    y = safe_year(r['Date of Crash'])
    if y:
        data.append({
            "name":  str(r['Name']),
            "city":  str(r['City']),
            "state": str(r['State']),
            "lat":   round(float(r['Latitude']),  5),
            "lng":   round(float(r['Longitude']), 5),
            "year":  y
        })

write_json("data/static/ufo_crashes.json", data)
print(f"     {len(data)} crashes")


# ── 5. National Parks ─────────────────────────────────────────────────────────
print("\n[5/7] National Parks...")

parks = pd.read_excel(src("Cleaned_US_National_Parks-2.xlsx"))
data = []
for _, r in parks.iterrows():
    try:
        data.append({
            "name":  str(r['National Park']),
            "state": str(r['State']),
            "lat":   round(float(r['Latitude']),  4),
            "lng":   round(float(r['Longitude']), 4)
        })
    except:
        pass

write_json("data/static/parks.json", data)
print(f"     {len(data)} parks")


# ── 6. Cultural Events (films + books) ────────────────────────────────────────
print("\n[6/7] Cultural Events...")

events = []

# UFO Films
ufo_films = pd.read_excel(src("Cleaned_UFO_Films-3.xlsx"))
for _, r in ufo_films.iterrows():
    y = safe_year(r.iloc[1])
    if y:
        events.append({"title": str(r.iloc[0]), "year": y, "cat": "UFO Film"})

# Bigfoot Films
bf_films = pd.read_excel(src("Cleaned_Bigfoot_Films-2.xlsx"), header=None)
for _, r in bf_films.iterrows():
    y = safe_year(r.iloc[1])
    if y:
        events.append({"title": str(r.iloc[0]), "year": y, "cat": "Bigfoot Film"})

# UFO Books
ufo_books = pd.read_excel(src("Cleaned_UFO_Books_1900_2014.xlsx"))
for _, r in ufo_books.iterrows():
    try:
        events.append({
            "title":  str(r['Book Title']),
            "author": str(r['Author']),
            "year":   int(r['Date']),
            "cat":    "UFO Book"
        })
    except:
        pass

# Bigfoot Books
bf_books = pd.read_excel(src("Cleaned_Bigfoot_Books_1900_2014.xlsx"), header=None)
for _, r in bf_books.iterrows():
    try:
        events.append({
            "title":  str(r.iloc[0]),
            "author": str(r.iloc[1]),
            "year":   int(r.iloc[2]),
            "cat":    "Bigfoot Book"
        })
    except:
        pass


# ── 7. Technology Events ──────────────────────────────────────────────────────
print("\n[7/7] Technology Events...")

tech = pd.read_excel(src("Technology.xlsx"), header=1)
tech.columns = ['title', 'date']
tech = tech.dropna(subset=['title', 'date'])
tech['year'] = pd.to_datetime(tech['date'], errors='coerce').dt.year
tech = tech.dropna(subset=['year'])
tech['year'] = tech['year'].astype(int)

for _, r in tech.iterrows():
    events.append({"title": str(r['title']), "year": int(r['year']), "cat": "New Technology"})

print(f"     {len(tech)} technology events")

events.sort(key=lambda x: x['year'])
write_json("data/static/cultural_events.json", events)
print(f"     {len(events)} total events")


print("\n✓ All data tiles generated successfully.")
print("  Push the data/ folder and index.html to GitHub Pages.")