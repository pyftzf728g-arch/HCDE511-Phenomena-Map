#!/usr/bin/env python3
"""
apply_nuclear_patch.py
Copy this file AND radiation_b64.txt into your project root, then run:
    python apply_nuclear_patch.py
"""

import re, os

# Read the base64 from the separate file
with open("radiation_b64.txt") as fh:
    b64 = fh.read().strip()

DATA_URI = "data:image/png;base64," + b64

with open("index.html", "r", encoding="utf-8") as fh:
    html = fh.read()

original = html
errors = 0

# ── Patch 1: replace mkNukeIcon with radiation PNG ───────────────────────────
old_fn = r"""function mkNukeIcon(color){
  return L.divIcon({
    html:'<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 20 20">'
        +'<circle cx="10" cy="10" r="8" fill="'+color+'" fill-opacity=".85" stroke="#fff" stroke-width="1"/>'
        +'<text x="10" y="14" text-anchor="middle" font-size="8" fill="#fff">&#9762;</text></svg>',
    className:'',iconSize:[20,20],iconAnchor:[10,10]
  });
}"""

new_fn = (
    "function mkNukeIcon(color){\n"
    "  return L.divIcon({\n"
    "    html:'<img src=\"' + DATA_URI + '\" width=\"22\" height=\"22\" "
    'style=\"display:block;filter:drop-shadow(0 0 2px rgba(0,0,0,.7))\"/>\',\n'
    "    className:'',iconSize:[22,22],iconAnchor:[11,11]\n"
    "  });\n"
    "}"
)

if old_fn in html:
    html = html.replace(old_fn, new_fn)
    print("Patch 1 OK: map icons -> radiation PNG")
else:
    print("WARN Patch 1: mkNukeIcon block not matched")
    errors += 1

# ── Patch 2: simplify legend nuclear row ─────────────────────────────────────
old_leg = """      <strong>&#9762; Nuclear Facilities</strong><br>
      <span class="ld" style="background:#3B8BD4"></span>Power Plant &nbsp;
      <span class="ld" style="background:#E24B4A"></span>Weapons Lab<br>
      <span class="ld" style="background:#BA7517"></span>Research Lab &nbsp;
      <span class="ld" style="background:#D85A30"></span>Testing<br>
      <span class="ld" style="background:#185FA5"></span>Enrichment &nbsp;
      <span class="ld" style="background:#993C1D"></span>Weapons/Waste<br>"""

new_leg = (
    '      <img src=\"' + DATA_URI + '\" width=\"16\" height=\"16\" '
    'style=\"vertical-align:middle;margin-right:5px;filter:drop-shadow(0 0 1px rgba(0,0,0,.5))\"/>'
    '<strong>Nuclear Facilities</strong><br>'
)

if old_leg in html:
    html = html.replace(old_leg, new_leg)
    print("Patch 2 OK: legend simplified")
else:
    print("WARN Patch 2: legend block not matched")
    errors += 1

with open("index.html", "w", encoding="utf-8") as fh:
    fh.write(html)

print(f"\nDone. {errors} warning(s). Reload index.html in your browser.")