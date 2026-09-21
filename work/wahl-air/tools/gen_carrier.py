#!/usr/bin/env python3
import json, base64, os, sys, urllib.request, uuid
ROOT = os.path.join(os.path.dirname(__file__), '..'); OUT = os.path.join(ROOT,'assets','img')
key=''
with open(os.path.expanduser('~/Desktop/two-packaging-portal/.env.local')) as f:
    for line in f:
        if line.startswith('OPENAI_API_KEY='): key=line.split('=',1)[1].strip().strip('"').strip("'"); break
if not key: sys.exit('no key')
prompt = ("Using this photograph as the reference for the air-conditioning unit itself — keep the same "
 "Carrier condenser model with its round oval Carrier badge on the front panel, same proportions, "
 "same louvered coil guard — create a NEW, far more beautiful photograph of that unit freshly "
 "installed. Place it on a clean poured concrete pad beside a freshly stuccoed desert-modern home "
 "wall in warm cream tone, the copper line-set and electrical whip neatly insulated, strapped and "
 "dressed, crushed white-grey decorative rock landscaping raked flat around the pad with one "
 "sculptural blue agave nearby. Golden-hour light rakes softly across the stucco from the side, "
 "giving the unit a gentle warm rim light and long clean shadows; the sky above the wall glows soft "
 "amber into blue. Everything immaculate, showroom-fresh, magazine-quality: tack-sharp on the unit "
 "and badge, shallow depth of field melting the background, warm filmic grade, fine grain.")
boundary=uuid.uuid4().hex; parts=[]
def field(k,v): parts.append(('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n'%(boundary,k,v)).encode())
field('model','gpt-image-1'); field('prompt',prompt); field('size','1536x1024'); field('quality','high'); field('input_fidelity','high')
p=os.path.join(OUT,'carrier-unit.jpg')
parts.append(('--%s\r\nContent-Disposition: form-data; name="image[]"; filename="carrier-unit.jpg"\r\nContent-Type: image/jpeg\r\n\r\n'%boundary).encode())
parts.append(open(p,'rb').read()); parts.append(b'\r\n'); parts.append(('--%s--\r\n'%boundary).encode())
req=urllib.request.Request('https://api.openai.com/v1/images/edits', data=b''.join(parts),
    headers={'Authorization':'Bearer '+key,'Content-Type':'multipart/form-data; boundary='+boundary})
try:
    with urllib.request.urlopen(req, timeout=900) as r: d=json.load(r)
    raw=os.path.join(OUT,'carrier-unit.new.png'); open(raw,'wb').write(base64.b64decode(d['data'][0]['b64_json']))
    os.system('sips -Z 1800 -s format jpeg -s formatOptions 80 "%s" --out "%s" >/dev/null 2>&1'%(raw,os.path.join(OUT,'carrier-unit.new.jpg')))
    os.remove(raw); print('saved carrier-unit.new.jpg')
except Exception as e:
    msg=getattr(e,'read',lambda:b'')()
    print('FAILED', str(e), (msg[:300] if isinstance(msg,bytes) else b'').decode('utf-8','replace'))
