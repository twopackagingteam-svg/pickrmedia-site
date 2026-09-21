#!/usr/bin/env python3
"""Enhance three existing gallery photos with gpt-image-1 edits — same scene, better light/sky/clarity."""
import json, base64, os, sys, urllib.request, mimetypes, uuid

ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, 'assets', 'img')
key = ''
with open(os.path.expanduser('~/Desktop/two-packaging-portal/.env.local')) as f:
    for line in f:
        if line.startswith('OPENAI_API_KEY='):
            key = line.split('=',1)[1].strip().strip('"').strip("'"); break
if not key: sys.exit('no key')

KEEP = ("Recreate this exact photograph as a flawless professional version of itself: identical "
        "composition, identical subjects, identical framing and camera angle. ")
STYLE = (" Render it cleaner and crisper — tack-sharp detail, noise-free, true blacks, rich "
         "dynamic range, professional color grade with warm golden highlights and clean cool "
         "shadows, fine film grain, campaign-photography quality.")

JOBS = [
 ('install-new-pad', 'install-new-pad.jpg', KEEP +
  "The technician kneeling at the outdoor AC unit beside the desert home stays exactly as he is — "
  "same pose, same uniform, same tools. Upgrade the light to rich late-golden-hour: low warm sun "
  "raking across the stucco, long soft shadows, and replace the plain sky with a luminous desert "
  "evening sky — high golden cirrus streaks over deep blue. Landscaping crisp, gravel texture sharp."),
 ('commercial-rtu-row', 'commercial-rtu-row.jpg', KEEP +
  "The white box truck with its desert-sunset photo wrap, the red crane behind the building, the "
  "building and bushes all stay exactly in place — and every piece of lettering on the truck wrap "
  "is preserved EXACTLY as it appears in the source photo, stroke for stroke, unchanged and "
  "undistorted. Upgrade the light to dramatic: monsoon clouds towering gold and slate above, low "
  "sun breaking under the cloud shelf to flood the truck and building in warm directional light, "
  "crisp shadows, the wrap colors rich and saturated."),
 ('team-truck-lineup', 'team-truck-lineup.jpg', KEEP +
  "The white service truck door with its script company lettering and phone number stays exactly "
  "as photographed — every letter, number and flourish preserved EXACTLY as in the source, "
  "unchanged and undistorted, including the small license numbers below. Upgrade the image "
  "quality: tack-sharp, noise-free, the sunset reflection on the door paint glowing rich amber "
  "and pink, deep clean shadows in the window glass, chrome and ladder rack crisp."),
]

def save_b64(name, b64):
    raw = os.path.join(OUT, name + '.new.png')
    with open(raw,'wb') as f: f.write(base64.b64decode(b64))
    os.system('sips -Z 1800 -s format jpeg -s formatOptions 80 "%s" --out "%s" >/dev/null 2>&1' % (raw, os.path.join(OUT, name + '.new.jpg')))
    os.remove(raw)
    print('saved', name + '.new.jpg', flush=True)

def edit(name, src, prompt):
    boundary = uuid.uuid4().hex
    parts=[]
    def field(k,v):
        parts.append(('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n'%(boundary,k,v)).encode())
    field('model','gpt-image-1'); field('prompt',prompt+STYLE); field('size','1536x1024'); field('quality','high')
    field('input_fidelity','high')
    p=os.path.join(OUT,src)
    parts.append(('--%s\r\nContent-Disposition: form-data; name="image[]"; filename="%s"\r\nContent-Type: image/jpeg\r\n\r\n'%(boundary,src)).encode())
    parts.append(open(p,'rb').read()); parts.append(b'\r\n')
    parts.append(('--%s--\r\n'%boundary).encode())
    req=urllib.request.Request('https://api.openai.com/v1/images/edits', data=b''.join(parts),
        headers={'Authorization':'Bearer '+key,'Content-Type':'multipart/form-data; boundary='+boundary})
    with urllib.request.urlopen(req, timeout=900) as r: d=json.load(r)
    save_b64(name, d['data'][0]['b64_json'])

for name, src, prompt in JOBS:
    try: edit(name, src, prompt)
    except Exception as e:
        msg=getattr(e,'read',lambda:b'')()
        print('FAILED', name, str(e), (msg[:300] if isinstance(msg,bytes) else b'').decode('utf-8','replace'), flush=True)
print('DONE')
