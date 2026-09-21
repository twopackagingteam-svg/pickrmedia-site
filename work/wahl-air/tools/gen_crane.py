#!/usr/bin/env python3
import json, base64, os, sys, urllib.request, uuid
ROOT = os.path.join(os.path.dirname(__file__), '..'); OUT = os.path.join(ROOT,'assets','img')
key=''
with open(os.path.expanduser('~/Desktop/two-packaging-portal/.env.local')) as f:
    for line in f:
        if line.startswith('OPENAI_API_KEY='): key=line.split('=',1)[1].strip().strip('"').strip("'"); break
if not key: sys.exit('no key')
prompt = ("Using this photograph as the reference for the scene — the red boom crane with its white "
 "lettering, the packaged AC unit hanging from the hook, the brown shingle residential roof and "
 "surrounding trees — create a NEW, far more dramatic cinema still of the same lift. Camera drops "
 "low and wide so the red boom towers diagonally across the full frame, the unit swinging high "
 "against the sky. Replace the flat blue sky with a monsoon spectacle: towering gold-and-slate "
 "thunderheads with the low evening sun breaking underneath, torching the crane's red paint and "
 "rim-lighting the hanging unit, long warm shadows raking the shingles. On the roof ridge, two "
 "technicians in white hard hats and lime-yellow hi-vis vests wait for the load, standing clear of "
 "its path, faces small and in profile. Dust and a faint heat shimmer drift through the sunbeam. "
 "Hard contrast, warm highlights against cool storm shadow, fine film grain, campaign-photography "
 "quality, tack-sharp detail on the crane and unit.")
boundary=uuid.uuid4().hex; parts=[]
def field(k,v): parts.append(('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n'%(boundary,k,v)).encode())
field('model','gpt-image-1'); field('prompt',prompt); field('size','1536x1024'); field('quality','high'); field('input_fidelity','high')
p=os.path.join(OUT,'install-crane-set.jpg')
parts.append(('--%s\r\nContent-Disposition: form-data; name="image[]"; filename="install-crane-set.jpg"\r\nContent-Type: image/jpeg\r\n\r\n'%boundary).encode())
parts.append(open(p,'rb').read()); parts.append(b'\r\n'); parts.append(('--%s--\r\n'%boundary).encode())
req=urllib.request.Request('https://api.openai.com/v1/images/edits', data=b''.join(parts),
    headers={'Authorization':'Bearer '+key,'Content-Type':'multipart/form-data; boundary='+boundary})
try:
    with urllib.request.urlopen(req, timeout=900) as r: d=json.load(r)
    raw=os.path.join(OUT,'install-crane-set.new.png')
    open(raw,'wb').write(base64.b64decode(d['data'][0]['b64_json']))
    os.system('sips -Z 1800 -s format jpeg -s formatOptions 80 "%s" --out "%s" >/dev/null 2>&1'%(raw,os.path.join(OUT,'install-crane-set.new.jpg')))
    os.remove(raw); print('saved install-crane-set.new.jpg')
except Exception as e:
    msg=getattr(e,'read',lambda:b'')()
    print('FAILED', str(e), (msg[:300] if isinstance(msg,bytes) else b'').decode('utf-8','replace'))
