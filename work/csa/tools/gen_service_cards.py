#!/usr/bin/env python3
"""Generate remaining service flip-card images with gpt-image-1 (pure JSON API, no shell quoting)."""
import json, base64, os, sys, urllib.request

ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, 'assets', 'img')

key = ''
with open(os.path.expanduser('~/Desktop/two-packaging-portal/.env.local')) as f:
    for line in f:
        if line.startswith('OPENAI_API_KEY='):
            key = line.split('=', 1)[1].strip().strip('"').strip("'")
            break
if not key:
    sys.exit('no key')

STYLE = ("Shot on a full-frame camera, professional editorial photography, bright warm natural "
         "light, crisp detail, subtle film grain, natural color grade with warm highlights, "
         "photorealistic, magazine quality.")

JOBS = {
 'svc-life-safety': "Photorealistic close-up landscape photograph inside a pristine modern commercial corridor: on the white wall, a bright red fire alarm horn-strobe notification device in sharp focus in the foreground right, and on the ceiling above, a round white smoke detector, both immaculate and newly installed. The corridor recedes with soft depth of field — polished concrete floor, clean white walls, recessed LED lighting, a glowing green exit sign far in the blurred background. Completely empty of people, unbranded devices, bright clinical clarity with warm daylight spilling from a window.",
 'svc-critical': "Photorealistic landscape photograph of a hospital isolation room anteroom: in sharp focus on the wall beside a stainless-steel door, a wall-mounted digital room pressure monitor with a small glowing display, and a magnehelic-style round pressure gauge mounted beside it. Through the door's glass vision panel, a softly blurred patient room with cool blue-white lighting. Immaculate healthcare finishes — seamless flooring, white walls, stainless door frame. Completely empty of people, no readable text, clinical and precise.",
 'svc-analysis': "Photorealistic landscape photograph, top-down three-quarter view of a work table on a commercial jobsite: a yellow handheld digital manometer with two clear pressure tubes coiled beside it, a thermal anemometer probe, a clipboard holding a printed data sheet with columns of handwritten readings (numbers only, no readable words), and a pencil. Behind the table, softly blurred exposed ceiling with silver spiral ductwork. Warm afternoon window light raking across the instruments, shallow depth of field, no people, no brand names.",
 'svc-commissioning': "Photorealistic landscape photograph of a large rooftop air-handling unit on a commercial building at golden hour: its access panel open revealing clean fans and coils, a digital tablet propped on the open panel edge showing a colorful building-systems dashboard with graphs (no readable text), pressure gauges glinting in the low sun. City skyline and desert mountains softly blurred beyond the roof edge, long warm shadows across the white roof membrane, no people, unbranded equipment.",
 'svc-kitchen': "Photorealistic landscape photograph of a pristine empty commercial restaurant kitchen: a long gleaming stainless-steel exhaust hood with baffle filters running above a professional gas range line, warm pendant light reflecting off brushed steel, tiled wall behind, everything immaculate and off-duty — burners off, counters clear. Slight low angle emphasizing the hood as the hero of the frame, shallow depth of field toward the blurred pass window, no people, no brand names.",
 'svc-duct': None,  # reference-based, handled below
 'svc-stairwell': "Photorealistic landscape photograph looking up a modern high-rise concrete emergency stairwell: switchback steel-pan stairs with yellow-striped nosings spiraling upward, a large silver supply-air grille mounted on the painted concrete wall between flights blowing visibly taut, cool even lighting from wall sconces, a glowing green exit sign one landing up. Strong geometric composition, completely empty, immaculate, slight wide-angle drama.",
 'svc-sound': "Photorealistic landscape photograph of a professional sound level meter on a black tripod standing in the center of an empty modern glass-walled conference room: the meter's small screen glowing with a decibel readout (digits only), a long wooden conference table and designer chairs softly blurred behind it, floor-to-ceiling glass showing a bright blurred office beyond, warm morning light. Quiet, precise, minimalist composition, no people, no brand names.",
}

DUCT_PROMPT = ("Using the two attached references — the first is a black-and-white company logo reading "
 "COMMERCIAL SYSTEMS ANALYSIS with a circular spiral-arrow mark, the second shows a technician in an "
 "orange hi-vis vest with that logo on the back holding a red capture hood — create a NEW photorealistic "
 "landscape photograph: an unfinished commercial interior with exposed silver spiral ductwork running "
 "along the ceiling. A technician seen from behind, standing on the concrete slab, white hard hat, "
 "high-visibility orange safety vest with the attached logo reproduced exactly across the back, reaching "
 "up to connect a clear pressure tube from a yellow duct-leakage testing fan rig on the floor to a sealed "
 "test port on the duct. Work lights mixing with daylight from unfinished window openings, his face fully "
 "hidden, tack-sharp on the vest logo and the duct. " + STYLE)


def save_b64(name, b64):
    path = os.path.join(OUT, name + '.png')
    with open(path, 'wb') as f:
        f.write(base64.b64decode(b64))
    print('saved', path, os.path.getsize(path) // 1024, 'KB', flush=True)


def generate(name, prompt):
    body = json.dumps({'model': 'gpt-image-1', 'prompt': prompt + ' ' + STYLE,
                       'size': '1536x1024', 'quality': 'high'}).encode()
    req = urllib.request.Request('https://api.openai.com/v1/images/generations', data=body,
                                 headers={'Authorization': 'Bearer ' + key,
                                          'Content-Type': 'application/json'})
    with urllib.request.urlopen(req, timeout=600) as r:
        d = json.load(r)
    save_b64(name, d['data'][0]['b64_json'])


def edit_with_refs(name, prompt, refs):
    boundary = '----csaform7391'
    parts = []
    def field(k, v):
        parts.append(('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n' % (boundary, k, v)).encode())
    field('model', 'gpt-image-1')
    field('size', '1536x1024')
    field('quality', 'high')
    field('prompt', prompt)
    for p in refs:
        fn = os.path.basename(p)
        parts.append(('--%s\r\nContent-Disposition: form-data; name="image[]"; filename="%s"\r\nContent-Type: image/png\r\n\r\n' % (boundary, fn)).encode())
        parts.append(open(p, 'rb').read())
        parts.append(b'\r\n')
    parts.append(('--%s--\r\n' % boundary).encode())
    body = b''.join(parts)
    req = urllib.request.Request('https://api.openai.com/v1/images/edits', data=body,
                                 headers={'Authorization': 'Bearer ' + key,
                                          'Content-Type': 'multipart/form-data; boundary=' + boundary})
    with urllib.request.urlopen(req, timeout=600) as r:
        d = json.load(r)
    save_b64(name, d['data'][0]['b64_json'])


for name, prompt in JOBS.items():
    if os.path.exists(os.path.join(OUT, name + '.png')) or os.path.exists(os.path.join(OUT, name + '.jpg')):
        print('skip (exists)', name, flush=True)
        continue
    print('generating', name, flush=True)
    try:
        if name == 'svc-duct':
            edit_with_refs(name, DUCT_PROMPT, [
                '/Users/nickwahl/Downloads/CSA LOGO.png',
                '/Users/nickwahl/Downloads/Tech Flow Hood.png'])
        else:
            generate(name, prompt)
    except Exception as e:
        print('ERROR', name, repr(e)[:300], flush=True)

# convert every svc-*.png (incl. svc-tab from the first run) to optimized jpg
from PIL import Image
import glob
for p in glob.glob(os.path.join(OUT, 'svc-*.png')):
    im = Image.open(p).convert('RGB')
    dst = p[:-4] + '.jpg'
    im.save(dst, 'JPEG', quality=84, optimize=True, progressive=True)
    os.remove(p)
    print('converted', dst, os.path.getsize(dst) // 1024, 'KB', flush=True)
print('ALL DONE', flush=True)
