#!/usr/bin/env python3
"""Generate remaining Wahl Air site images with gpt-image-1. Faces never straight-on. Trade-accurate rigging."""
import json, base64, os, sys, urllib.request, mimetypes, uuid, threading, queue

ROOT = os.path.join(os.path.dirname(__file__), '..')
OUT = os.path.join(ROOT, 'assets', 'img')

key = ''
with open(os.path.expanduser('~/Desktop/two-packaging-portal/.env.local')) as f:
    for line in f:
        if line.startswith('OPENAI_API_KEY='):
            key = line.split('=', 1)[1].strip().strip('"').strip("'"); break
if not key: sys.exit('no key')

STYLE = (" Cinema still, shot on a full-frame camera, hard directional golden-hour light, deep contrast, "
         "warm highlights against cool shadow, atmospheric haze, fine film grain, photorealistic, "
         "campaign-photography quality, no text overlay, no watermark.")

REF = lambda *n: [os.path.join(ROOT, p) for p in n]

JOBS = [
 # name, size, [reference image paths] or None, prompt
 ('owners-portrait', '1024x1536', REF('assets/img/team-three-generations.jpg','assets/brand/wahl-logo-oval.png'),
  "Using the attached photo of two men (a stocky younger man with a dark beard and ball cap, and his "
  "white-haired father) and the attached red oval company logo as references, create a NEW vertical "
  "photograph: the same two men seen FROM BEHIND at three-quarter back angle, standing shoulder to "
  "shoulder in a gravel equipment yard at golden hour, looking out toward their white box truck with a "
  "desert-sunset photo wrap parked ahead of them. Both wear navy company polos with the attached red oval "
  "logo embroidered small on the sleeve, the younger man's cap on backwards. Their faces are turned away "
  "toward the truck, at most a sliver of profile visible. Low sun floods the yard gold, long shadows run "
  "toward camera, dust hangs in the light."),
 ('install-rooftop-crew', '1536x1024', None,
  "A packaged rooftop air-conditioning unit hangs from crane slings a few inches above a prepared "
  "sheet-metal roof curb with its duct opening ready beneath, on a white commercial roof at golden hour. "
  "Two HVAC technicians stand at the SIDES of the unit, safely clear of its footprint, each with gloved "
  "hands on a side rail steadying it as the crane inches it down onto the curb — the correct, real-world "
  "way a curb set lands. Both wear scuffed white hard hats, clear safety glasses, lime-yellow hi-vis "
  "vests over navy polos, and black full-body harnesses whose yellow lanyards run back to red roof "
  "anchors bolted to the deck. Orange stanchions with yellow warning rope line the roof edge behind "
  "them. Faces in profile under hard-hat brims. Long shadows rake the white membrane, city haze beyond."),
 ('why-wahl', '1536x1024', REF('assets/img/team-three-generations.jpg'),
  "Using the attached photo of a stocky bearded man in a ball cap as a body-type reference, create a NEW "
  "photograph: the man seen ENTIRELY FROM BEHIND, standing on a commercial rooftop at dusk, hard hat "
  "held at his side, black safety harness still on with its yellow lanyard clipped to a red deck anchor "
  "beside him, looking out over a desert city as its lights come on. A massive dark rooftop AC unit sits "
  "landed on its curb behind his shoulder. The last orange band of sunset burns along the horizon under "
  "a deep violet sky; amber rim light edges his shoulders and cap. Wide negative space of sky, quiet "
  "epic tone."),
 ('service-gauges', '1536x1024', None,
  "Extreme close-up macro: a refrigerant manifold gauge set clamped to the service ports of a running "
  "outdoor condenser, shot through the soft blur of its own red and blue hoses. Brass fittings blaze "
  "with hard specular sunlight; both needle dials are knife-sharp in a razor-thin focal plane while "
  "everything else melts into amber and steel bokeh. A worn leather work glove enters frame "
  "mid-adjustment. Heat shimmer rises off the compressor behind, bending the backlight."),
 ('service-coil-clean', '1536x1024', None,
  "A fine pressure rinse hits the aluminium fins of an outdoor condenser coil directly into the low "
  "setting sun, the spray exploding into a backlit halo of thousands of frozen droplets with a faint "
  "rainbow ghost in the mist. The technician is a half-silhouette at the frame edge, gloved hand steady "
  "on the spray wand, ball cap brim dripping, face fully in shadow. Coil fins glow amber where the light "
  "rakes them and fall to black in the gaps. Sun star bursting through the spray."),
 ('service-furnace', '1536x1024', None,
  "Seen from behind and over his shoulder, a technician in a navy company polo kneels at an open gas "
  "furnace in a clean residential utility closet, headlamp beam and the warm glow of the burner "
  "inspection port lighting his gloved hands as he checks the burner assembly with a combustion analyser "
  "probe clipped in the flue. His face is turned away into the cabinet. Warm pool of task light against "
  "cool ambient shadow, labelled ductwork rising into darkness above."),
 ('service-heatpump', '1536x1024', None,
  "A brand-new modern heat pump outdoor unit beside a stuccoed desert home on a cool bright winter "
  "morning, light frost haze in the air, its fan blades crisp behind the grille, copper line-set neatly "
  "insulated and strapped. Low angled morning sun rakes long blue shadows across gravel landscaping; a "
  "barrel cactus and agave frame the corner; distant mountains stack in soft haze. No people, hero "
  "product angle from low three-quarter."),
 ('commercial-mechanical-room', '1536x1024', None,
  "Inside a commercial mechanical room shot like a ship's engine bay: a corridor of stainless "
  "air-handling units and insulated piping compressing into deep one-point perspective, hard specular "
  "streaks from caged work lights, thin steam curling through a shaft of cool daylight from a high "
  "window. In the middle distance a technician in a navy polo kneels at an open control cabinet with "
  "his BACK to camera, lit by the glow of the panel. Wet-look reflective floor doubling the lights, "
  "teal-and-steel palette with one warm pool at the technician."),
 ('area-west-valley', '1536x1024', None,
  "High-altitude aerial at golden hour over a wide desert-suburb valley: tile rooftops with visible "
  "AC condensers, curving palm-lined streets, a canal catching the low sun as a ribbon of fire, distant "
  "mountain ranges layered in warm haze, monsoon clouds stacking gold and violet on the horizon. Gentle "
  "atmospheric depth, no people."),
]

def save_b64(name, b64):
    raw = os.path.join(OUT, name + '.png')
    with open(raw, 'wb') as f: f.write(base64.b64decode(b64))
    os.system('sips -Z 1800 -s format jpeg -s formatOptions 80 "%s" --out "%s" >/dev/null 2>&1' % (raw, os.path.join(OUT, name + '.jpg')))
    os.remove(raw)
    print('saved', name + '.jpg', flush=True)

def generations(name, size, prompt):
    body = json.dumps({'model':'gpt-image-1','prompt':prompt+STYLE,'size':size,'quality':'high'}).encode()
    req = urllib.request.Request('https://api.openai.com/v1/images/generations', data=body,
        headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
    with urllib.request.urlopen(req, timeout=900) as r: d = json.load(r)
    save_b64(name, d['data'][0]['b64_json'])

def edits(name, size, refs, prompt):
    boundary = uuid.uuid4().hex
    parts = []
    def field(k, v):
        parts.append(('--%s\r\nContent-Disposition: form-data; name="%s"\r\n\r\n%s\r\n' % (boundary,k,v)).encode())
    field('model','gpt-image-1'); field('prompt',prompt+STYLE); field('size',size); field('quality','high')
    for p in refs:
        ct = mimetypes.guess_type(p)[0] or 'image/png'
        parts.append(('--%s\r\nContent-Disposition: form-data; name="image[]"; filename="%s"\r\nContent-Type: %s\r\n\r\n' % (boundary, os.path.basename(p), ct)).encode())
        parts.append(open(p,'rb').read()); parts.append(b'\r\n')
    parts.append(('--%s--\r\n' % boundary).encode())
    body = b''.join(parts)
    req = urllib.request.Request('https://api.openai.com/v1/images/edits', data=body,
        headers={'Authorization':'Bearer '+key,'Content-Type':'multipart/form-data; boundary='+boundary})
    with urllib.request.urlopen(req, timeout=900) as r: d = json.load(r)
    save_b64(name, d['data'][0]['b64_json'])

q = queue.Queue()
for j in JOBS: q.put(j)
errs = []
def worker():
    while True:
        try: name, size, refs, prompt = q.get_nowait()
        except queue.Empty: return
        try:
            (edits if refs else generations)(*( (name,size,refs,prompt) if refs else (name,size,prompt) ))
        except Exception as e:
            msg = getattr(e,'read',lambda: b'')()
            errs.append((name, str(e), (msg[:300] if isinstance(msg,bytes) else b'').decode('utf-8','replace')))
            print('FAILED', name, str(e), flush=True)
        q.task_done()
ts = [threading.Thread(target=worker) for _ in range(3)]
[t.start() for t in ts]; [t.join() for t in ts]
print('DONE. failures:', len(errs))
for e in errs: print(e)
