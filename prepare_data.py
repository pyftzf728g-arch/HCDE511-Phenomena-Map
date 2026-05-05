"""
prepare_data.py — Run this whenever you update your source Excel files.
Generates all data tiles consumed by index.html.

Usage:
    python prepare_data.py

Source files expected in the same folder:
    Cleaned_US_Nuclear_Facilities.xlsx
    Cleaned_US_UFO_Crashes.xlsx
    Cleaned_UFO_Sightings_US_Only.xlsx
    Til_2014_Bigfoot_data_with_cities.xlsx
    Cleaned_US_National_Parks.xlsx
    Cleaned_UFO_Films.xlsx
    Cleaned_Bigfoot_Films.xlsx
    Cleaned_UFO_Books_1900_2026.xlsx
    Cleaned_Bigfoot_Books_1900_2026.xlsx
"""
import json, os
from collections import defaultdict
import pandas as pd

os.makedirs("data/ufo_sightings", exist_ok=True)
os.makedirs("data/bigfoot",       exist_ok=True)
os.makedirs("data/static",        exist_ok=True)

def safe_year(v):
    try: return int(pd.to_datetime(v, errors='coerce').year)
    except: return 0

def write_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, separators=(',', ':'))
    kb = os.path.getsize(path) / 1024
    print(f"  -> {path} ({kb:.0f} KB)")

# ── 1. UFO Sightings (large) ───────────────────────────────────────────────────
print("\n[1/6] UFO Sightings...")
ufo = pd.read_excel("Cleaned_UFO_Sightings_US_Only.xlsx")
ufo['year'] = pd.to_datetime(ufo['Date'], errors='coerce').dt.year.fillna(0).astype(int)
ufo = ufo[ufo['year'] > 0]
decades = defaultdict(list)
for _, r in ufo.iterrows():
    decade = (int(r['year']) // 10) * 10
    decades[decade].append([round(float(r['Latitude']),2), round(float(r['Longitude']),2), int(r['year'])])
for decade, records in sorted(decades.items()):
    write_json(f"data/ufo_sightings/{decade}.json", records)
    print(f"     {decade}s: {len(records):>6} records")
write_json("data/ufo_sightings/manifest.json", {"decades": sorted(decades.keys()), "total": len(ufo)})

# ── 2. Bigfoot Sightings ──────────────────────────────────────────────────────
print("\n[2/6] Bigfoot Sightings...")
bf = pd.read_excel("Til_2014_Bigfoot_data_with_cities.xlsx")
bf['year'] = pd.to_datetime(bf['Date'], errors='coerce').dt.year.fillna(0).astype(int)
bf = bf[bf['year'] > 0]
decades = defaultdict(list)
for _, r in bf.iterrows():
    decade = (int(r['year']) // 10) * 10
    decades[decade].append({
        "lat":  round(float(r['Latitude']), 4),
        "lng":  round(float(r['Longitude']), 4),
        "year": int(r['year']),
        "cls":  str(r['Classification']),
        "city": str(r['City']),
        "state":str(r['State']),
    })
for decade, records in sorted(decades.items()):
    write_json(f"data/bigfoot/{decade}.json", records)
    print(f"     {decade}s: {len(records):>6} records")
write_json("data/bigfoot/manifest.json", {"decades": sorted(decades.keys()), "total": len(bf)})

# ── 3. Nuclear Facilities ─────────────────────────────────────────────────────
print("\n[3/6] Nuclear Facilities...")
nf = pd.read_excel("Cleaned_US_Nuclear_Facilities.xlsx")
data = [{"name":str(r['Facility']),"type":str(r['Type']),"city":str(r['City']),
          "state":str(r['State']),"lat":round(float(r['Latitude']),5),
          "lng":round(float(r['Longitude']),5),"year":int(r['Year Opened'])}
         for _, r in nf.iterrows()]
write_json("data/static/nuclear.json", data)
print(f"     {len(data)} facilities")

# ── 4. UFO Crashes ────────────────────────────────────────────────────────────
print("\n[4/6] UFO Crashes...")
ufc = pd.read_excel("Cleaned_US_UFO_Crashes.xlsx")
data = []
for _, r in ufc.iterrows():
    y = safe_year(r['Date of Crash'])
    if y: data.append({"name":str(r['Name']),"city":str(r['City']),"state":str(r['State']),
                        "lat":round(float(r['Latitude']),5),"lng":round(float(r['Longitude']),5),"year":y})
write_json("data/static/ufo_crashes.json", data)
print(f"     {len(data)} crashes")

# ── 5. National Parks ─────────────────────────────────────────────────────────
print("\n[5/6] National Parks...")
parks = pd.read_excel("Cleaned_US_National_Parks.xlsx")
data = []
for _, r in parks.iterrows():
    try:
        data.append({"name":str(r['National Park']),"state":str(r['State']),
                     "lat":round(float(r['Latitude']),4),"lng":round(float(r['Longitude']),4)})
    except: pass
write_json("data/static/parks.json", data)
print(f"     {len(data)} parks")

# ── 6. Cultural Events (films + books) ────────────────────────────────────────
print("\n[6/6] Cultural Events...")
events = []

# UFO Films
ufo_films = pd.read_excel("Cleaned_UFO_Films.xlsx")
for _, r in ufo_films.iterrows():
    y = safe_year(r.iloc[1])
    if y: events.append({"title":str(r.iloc[0]),"year":y,"cat":"UFO Film"})

# Bigfoot Films
bf_films = pd.read_excel("Cleaned_Bigfoot_Films.xlsx", header=None)
for _, r in bf_films.iterrows():
    y = safe_year(r.iloc[1])
    if y: events.append({"title":str(r.iloc[0]),"year":y,"cat":"Bigfoot Film"})

# UFO Books
ufo_books = pd.read_excel("Cleaned_UFO_Books_1900_2026.xlsx")
for _, r in ufo_books.iterrows():
    try: events.append({"title":str(r['Book Title']),"author":str(r['Author']),"year":int(r['Date']),"cat":"UFO Book"})
    except: pass

# Bigfoot Books
bf_books = pd.read_excel("Cleaned_Bigfoot_Books_1900_2026.xlsx", header=None)
for _, r in bf_books.iterrows():
    try: events.append({"title":str(r.iloc[0]),"author":str(r.iloc[1]),"year":int(r.iloc[2]),"cat":"Bigfoot Book"})
    except: pass

events.sort(key=lambda x: x['year'])
write_json("data/static/cultural_events.json", events)
print(f"     {len(events)} events")

print("\n✓ All data tiles generated successfully.")
print("  Push the data/ folder and index.html to GitHub Pages.")
