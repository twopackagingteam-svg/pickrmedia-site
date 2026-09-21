#!/bin/bash
# Generate the 9 service flip-card images with gpt-image-1.
# Key is read at runtime from two-packaging-portal/.env.local — never echoed.
set -euo pipefail
cd "$(dirname "$0")/.."

KEY=$(grep -m1 '^OPENAI_API_KEY=' ~/Desktop/two-packaging-portal/.env.local | cut -d= -f2- | tr -d '"' | tr -d "'")
[ -z "$KEY" ] && { echo "no key found"; exit 1; }

LOGO="/Users/nickwahl/Downloads/CSA LOGO.png"
HOOD="/Users/nickwahl/Downloads/Tech Flow Hood.png"   # our best hood reference (already CSA-branded)
OUT="assets/img"
SIZE="1536x1024"

STYLE="Shot on a full-frame camera, professional editorial photography, bright warm natural light, crisp detail, subtle film grain, natural color grade with warm highlights, photorealistic, magazine quality."

gen () { # name, prompt  (pure generation)
  local name="$1"; local prompt="$2"
  echo "── generating $name (text-only)…"
  curl -sS https://api.openai.com/v1/images/generations \
    -H "Authorization: Bearer $KEY" -H "Content-Type: application/json" \
    -d "$(python3 -c "import json,sys;print(json.dumps({'model':'gpt-image-1','prompt':sys.argv[1],'size':'$SIZE','quality':'high'}))" "$prompt $STYLE")" \
    | python3 -c "import json,sys,base64;d=json.load(sys.stdin);open('$OUT/$name','wb').write(base64.b64decode(d['data'][0]['b64_json'])) if 'data' in d else print('ERROR:',json.dumps(d)[:400])"
  ls -la "$OUT/$name" 2>/dev/null || true
}

edit () { # name, prompt (uses logo + hood references)
  local name="$1"; local prompt="$2"
  echo "── generating $name (with logo+hood references)…"
  curl -sS https://api.openai.com/v1/images/edits \
    -H "Authorization: Bearer $KEY" \
    -F "model=gpt-image-1" \
    -F "image[]=@$LOGO" \
    -F "image[]=@$HOOD" \
    -F "size=$SIZE" -F "quality=high" \
    -F "prompt=$prompt $STYLE" \
    | python3 -c "import json,sys,base64;d=json.load(sys.stdin);open('$OUT/$name','wb').write(base64.b64decode(d['data'][0]['b64_json'])) if 'data' in d else print('ERROR:',json.dumps(d)[:400])"
  ls -la "$OUT/$name" 2>/dev/null || true
}

# 01 — HVAC Test & Balance (CSA TECH, uses references)
edit svc-tab.png "Using the two attached references — the first is a black-and-white company logo reading COMMERCIAL SYSTEMS ANALYSIS with a circular spiral-arrow mark, the second shows a technician holding a red fabric airflow capture hood with a black digital meter base against a white ceiling — create a NEW photorealistic landscape photograph: a technician seen from behind at a three-quarter angle, standing in a bright modern office lobby with a white suspended ceiling grid, arms raised, seating that exact red capture hood flat against a ceiling air diffuser. He wears a white hard hat and a high-visibility orange safety vest with the attached logo reproduced exactly, large across the upper back. Floor-to-ceiling windows at the left show a softly blurred sunny desert city skyline. His face is fully hidden by the angle and hard hat. Tack-sharp on the vest logo and the red hood fabric."

# 02 — Life Safety Testing (no people)
gen svc-life-safety.png "Photorealistic close-up landscape photograph inside a pristine modern commercial corridor: on the white wall, a bright red fire alarm horn-strobe notification device in sharp focus in the foreground right, and on the ceiling above, a round white smoke detector, both immaculate and newly installed. The corridor recedes with soft depth of field — polished concrete floor, clean white walls, recessed LED lighting, a glowing green exit sign far in the blurred background. Completely empty of people, unbranded devices, bright clinical clarity with warm daylight spilling from a window."

# 03 — Critical Room Certification (no people)
gen svc-critical.png "Photorealistic landscape photograph of a hospital isolation room anteroom: in sharp focus on the wall beside a stainless-steel door, a wall-mounted digital room pressure monitor with a small glowing display, and a magnehelic-style round pressure gauge mounted beside it. Through the door's glass vision panel, a softly blurred patient room with cool blue-white lighting. Immaculate healthcare finishes — seamless flooring, white walls, stainless door frame. Completely empty of people, no readable text, clinical and precise."

# 04 — HVAC Analysis Reports (no people)
gen svc-analysis.png "Photorealistic landscape photograph, top-down three-quarter view of a work table on a commercial jobsite: a yellow handheld digital manometer with two clear pressure tubes coiled beside it, a thermal anemometer probe, a clipboard holding a printed data sheet with columns of handwritten readings (numbers only, no readable words), and a pencil. Behind the table, softly blurred exposed ceiling with silver spiral ductwork. Warm afternoon window light raking across the instruments, shallow depth of field, no people, no brand names."

# 05 — Commissioning & Retro-Cx (no people)
gen svc-commissioning.png "Photorealistic landscape photograph of a large rooftop air-handling unit on a commercial building at golden hour: its access panel open revealing clean fans and coils, a digital tablet propped on the open panel edge showing a colorful building-systems dashboard with graphs (no readable text), pressure gauges glinting in the low sun. City skyline and desert mountains softly blurred beyond the roof edge, long warm shadows across the white roof membrane, no people, unbranded equipment."

# 06 — Kitchen Hood Certification (no people)
gen svc-kitchen.png "Photorealistic landscape photograph of a pristine empty commercial restaurant kitchen: a long gleaming stainless-steel exhaust hood with baffle filters running above a professional gas range line, warm pendant light reflecting off brushed steel, tiled wall behind, everything immaculate and off-duty — burners off, counters clear. Slight low angle emphasizing the hood as the hero of the frame, shallow depth of field toward the blurred pass window, no people, no brand names."

# 07 — Duct Leak Testing (CSA TECH, uses references)
edit svc-duct.png "Using the two attached references — the first is a black-and-white company logo reading COMMERCIAL SYSTEMS ANALYSIS with a circular spiral-arrow mark, the second shows a technician in an orange hi-vis vest with that logo on the back holding a red capture hood — create a NEW photorealistic landscape photograph: an unfinished commercial interior with exposed silver spiral ductwork running along the ceiling. A technician seen from behind, standing on the concrete slab, white hard hat, high-visibility orange safety vest with the attached logo reproduced exactly across the back, reaching up to connect a clear pressure tube from a yellow duct-leakage testing fan rig on the floor to a sealed test port on the duct. Work lights mixing with daylight from unfinished window openings, his face fully hidden, tack-sharp on the vest logo and the duct."

# 08 — Stairwell Pressurization (no people)
gen svc-stairwell.png "Photorealistic landscape photograph looking up a modern high-rise concrete emergency stairwell: switchback steel-pan stairs with yellow-striped nosings spiraling upward, a large silver supply-air grille mounted on the painted concrete wall between flights blowing visibly taut, cool even lighting from wall sconces, a glowing green exit sign one landing up. Strong geometric composition, completely empty, immaculate, slight wide-angle drama."

# 09 — Sound Testing (no people)
gen svc-sound.png "Photorealistic landscape photograph of a professional sound level meter on a black tripod standing in the center of an empty modern glass-walled conference room: the meter's small screen glowing with a decibel readout (digits only), a long wooden conference table and designer chairs softly blurred behind it, floor-to-ceiling glass showing a bright blurred office beyond, warm morning light. Quiet, precise, minimalist composition, no people, no brand names."

echo "ALL DONE"
