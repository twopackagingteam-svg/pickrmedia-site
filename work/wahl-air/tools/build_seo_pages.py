#!/usr/bin/env python3
"""Programmatic search-term pages: {service} x {city} with differentiated content,
rotating verbatim reviews, FAQs, and full per-page schema."""
import os, json, hashlib
ROOT = os.path.join(os.path.dirname(__file__), '..')
DOMAIN = 'https://wahlair.com'
idx = open(os.path.join(ROOT,'index.html')).read()
CHROME = idx[idx.find('<div class="progress"'): idx.find('</header>')+len('</header>')]
FOOTER = idx[idx.find('<!-- ▸ footer -->'): idx.find('<script src=')]
def ab(s):
    return s.replace('src="assets/','src="/assets/').replace('href="assets/','href="/assets/').replace('href="index.html"','href="/"')
CHROME, FOOTER = ab(CHROME), ab(FOOTER)
REVIEWS = json.load(open(os.path.join(ROOT,'reviews.json')))['reviews']

CITIES = [('phoenix','Phoenix'),('scottsdale','Scottsdale'),('tempe','Tempe'),('glendale','Glendale'),
 ('peoria','Peoria'),('sun-city','Sun City'),('surprise','Surprise'),('youngtown','Youngtown'),
 ('tolleson','Tolleson'),('goodyear','Goodyear'),('avondale','Avondale'),('verrado','Verrado'),('wittmann','Wittmann')]

AR='<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'
STAR='<svg viewBox="0 0 24 24" fill="currentColor" style="width:13px;height:13px;color:var(--accent)"><path d="M12 2l2.9 6.3 6.9.8-5.1 4.7 1.4 6.8L12 17.3 5.9 20.6l1.4-6.8L2.2 9.1l6.9-.8z"/></svg>'

HEAD = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta name="robots" content="index, follow">
<meta property="og:type" content="website">
<meta property="og:site_name" content="Wahl Air Conditioning Inc.">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{domain}/assets/img/hero-poster.jpg">
<meta property="og:locale" content="en_US">
<meta name="twitter:card" content="summary_large_image">
<meta name="geo.region" content="US-AZ">
<meta name="geo.placename" content="{city}, Arizona">
<link rel="icon" href="/assets/brand/favicon-270.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wdth,wght@0,100..125,400..900;1,100..125,400..900&family=Inter:wght@400;500;600&family=Jost:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/main.css?v=5">
{schema}
</head>
<body>
'''
TAIL = '<script src="/js/main.js?v=5"></script>\n</body>\n</html>\n'

def biz_schema():
    return {
      "@type":"HVACBusiness","@id":DOMAIN+"/#organization",
      "name":"Wahl Air Conditioning Inc.",
      "alternateName":["Wahl Air","Wahl Air Conditioning"],
      "url":DOMAIN+"/", "logo":DOMAIN+"/assets/brand/wahl-logo-new.png",
      "image":DOMAIN+"/assets/img/hero-poster.jpg",
      "slogan":"Serving The Valley Since 1957",
      "foundingDate":"1957",
      "telephone":"+1-602-242-2353","email":"info@wahlair.com","priceRange":"$$",
      "address":{"@type":"PostalAddress","streetAddress":"9802 N 91st Ave, Suite 104",
        "addressLocality":"Peoria","addressRegion":"AZ","postalCode":"85345","addressCountry":"US"},
      "geo":{"@type":"GeoCoordinates","latitude":33.5745,"longitude":-112.2540},
      "openingHoursSpecification":[{"@type":"OpeningHoursSpecification",
        "dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday"],
        "opens":"08:00","closes":"17:00"}],
      "areaServed":[{"@type":"City","name":c[1]+", AZ"} for c in CITIES],
      "aggregateRating":{"@type":"AggregateRating","ratingValue":"4.9","reviewCount":"218",
        "bestRating":"5","worstRating":"1"},
      "sameAs":["https://www.facebook.com/profile.php?id=61550313643205",
        "https://www.instagram.com/wahlair_az",
        "https://www.yelp.com/biz/wahl-air-conditioning-peoria-4"]}

def page_schema(url, name, desc, city, service_name, faqs, revs):
    graph=[biz_schema(),
     {"@type":"WebPage","@id":url+"#webpage","url":url,"name":name,"description":desc,
      "isPartOf":{"@id":DOMAIN+"/#website"},"about":{"@id":DOMAIN+"/#organization"},"inLanguage":"en-US"},
     {"@type":"Service","name":service_name,"serviceType":service_name,
      "provider":{"@id":DOMAIN+"/#organization"},
      "areaServed":{"@type":"City","name":city+", AZ"},
      "availableChannel":{"@type":"ServiceChannel","servicePhone":"+1-602-242-2353","serviceUrl":url}},
     {"@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Home","item":DOMAIN+"/"},
        {"@type":"ListItem","position":2,"name":service_name,"item":url}]}]
    if faqs:
        graph.append({"@type":"FAQPage","mainEntity":[
          {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":a}} for q,a in faqs]})
    for r in revs:
        graph.append({"@type":"Review","itemReviewed":{"@id":DOMAIN+"/#organization"},
          "reviewRating":{"@type":"Rating","ratingValue":"5","bestRating":"5"},
          "author":{"@type":"Person","name":r['name']},"reviewBody":r['text']})
    return '<script type="application/ld+json">%s</script>' % json.dumps(
        {"@context":"https://schema.org","@graph":graph}, separators=(',',':'))

def pick_reviews(slug, n=3):
    h=int(hashlib.md5(slug.encode()).hexdigest(),16) % len(REVIEWS)
    return [REVIEWS[(h+i*5) % len(REVIEWS)] for i in range(n)]

def esc(s): return s.replace('&','&amp;').replace('<','&lt;').replace('>','&gt;').replace('"','&quot;')

def review_block(revs, city):
    cards=''.join('<div class="rcard reveal" style="width:auto">'
      '<div class="rcard-top"><div class="stars">%s</div></div>'
      '<blockquote>&ldquo;%s&rdquo;</blockquote><p>%s</p>'
      '<footer><span><b>%s</b><small>%s &middot; Google review</small></span></footer></div>'
      % (STAR*5, esc(r['pull']), esc(r['text']), esc(r['name']), esc(r['when'])) for r in revs)
    return ('<section class="section hairline"><div class="wrap">'
      '<div class="sec-head-row reveal"><div><span class="kicker">Real Google Reviews</span>'
      '<h2 class="h2" style="margin-top:.7rem">4.9 stars.<br><span class="accent">218 reviews.</span></h2></div>'
      '<p class="lede">What Valley homeowners say about Wahl Air &mdash; verbatim, from our public Google profile.</p></div>'
      '<div class="grid-2" style="grid-template-columns:repeat(auto-fit,minmax(300px,1fr));display:grid;gap:1rem">%s</div>'
      '<div class="mt"><a class="btn btn-ghost" href="https://share.google/2r1OJS3nVcB6s8mbk" target="_blank" rel="noopener"><span class="mag">Read all 218 reviews on Google</span></a></div>'
      '</div></section>' % cards)

def faq_block(faqs):
    items=''.join('<div class="reason reveal"><span class="n">Q</span><div><h4>%s</h4><p>%s</p></div></div>'
                  % (q,a) for q,a in faqs)
    return ('<section class="section hairline"><div class="wrap">'
      '<div class="section-head reveal"><span class="kicker">Questions We Hear Every Day</span>'
      '<h2 class="h2">Straight answers</h2></div>'
      '<div class="reasons">%s</div></div></section>' % items)

def cross_links(city_slug, city, self_key):
    svc=''.join('<a class="sib" href="/%s-%s-az/">%s</a>' % (k, city_slug, lbl)
        for k,lbl in [('ac-repair','AC Repair'),('emergency-ac-repair','Emergency AC'),
                      ('ac-installation','AC Installation'),('hvac-company','AC Company'),
                      ('heating-repair','Heating Repair')] if k!=self_key)
    cities=''.join('<a class="city" href="/%s-%s-az/">%s</a>' % (self_key,cs,cn)
        for cs,cn in CITIES if cs!=city_slug)
    return ('<section class="section hairline"><div class="wrap">'
      '<div class="reveal"><span class="kicker">More in %s</span><div class="sibs" style="margin-top:1rem">%s</div></div>'
      '<div class="reveal mt"><span class="kicker">Nearby Cities</span><div class="cities" style="margin-top:1rem">%s</div></div>'
      '</div></section>' % (city, svc, cities))

def cta():
    return ('<section class="cta"><div class="wrap cta-inner">'
      '<div class="reveal"><span class="kicker">Ready When You Are</span>'
      '<h2 class="h2" style="margin-top:.7rem">Let\'s get your air <span class="accent">handled.</span></h2></div>'
      '<div class="cta-actions reveal" data-d="1">'
      '<a class="btn btn-solid" href="/contact/"><span class="mag">Request Service Online %s</span></a>'
      '<span class="tiny" style="margin-top:.6rem">Or call us right now</span>'
      '<a class="cta-tel" href="tel:+16022422353">(602) 242-2353</a></div></div></section>' % AR)

def hero(kick, h1, lede):
    return ('<section class="p-hero"><div class="wrap">'
      '<nav class="crumb"><a href="/">Home</a> <i>›</i> %s</nav>'
      '<h1 class="reveal in">%s</h1><p class="lede reveal in">%s</p>'
      '<div class="hero-ctas reveal in">'
      '<a class="btn btn-solid" href="/contact/"><span class="mag">Request a Free Estimate %s</span></a>'
      '<a class="btn btn-ghost" href="tel:+16022422353"><span class="mag">Call (602) 242-2353</span></a></div>'
      '</div></section>' % (kick, h1, lede, AR))

def split_block(kick,h2,paras,checks,img,alt,tag):
    ps=''.join('<p class="lede" style="font-size:1rem;margin-bottom:1rem">%s</p>'%p for p in paras)
    cl=''.join('<li>%s</li>'%c for c in checks)
    return ('<section class="section"><div class="wrap"><div class="split">'
      '<div class="reveal"><span class="kicker">%s</span>'
      '<h2 class="h2" style="margin:.7rem 0 1rem">%s</h2>%s<ul class="check">%s</ul></div>'
      '<div class="split-media reveal" data-d="1" data-slot-wrap>'
      '<img src="/assets/img/%s" alt="%s" data-slot loading="lazy"><span class="tagchip"><i></i>%s</span>'
      '</div></div></div></section>' % (kick,h2,ps,cl,img,alt,tag))

# ── the five templates (service-differentiated content) ──
def T(key,c_slug,city):
    trust=("Wahl Air Conditioning is a family-owned and operated company based in nearby Peoria, serving "
      f"{city} and the West Valley since 1957. Three generations of the Wahl family, 4.9 stars across 218 "
      "Google reviews, NATE-certified technicians, and a same-day guarantee for no-air calls.")
    if key=='ac-repair':
        return dict(service='AC Repair',
         title=f'AC Repair {city}, AZ — Same-Day No-Air Service | Wahl Air Conditioning',
         desc=f'Honest AC repair in {city}, AZ from a family-owned company serving the Valley since 1957. Same-day no-air service, 4.9 stars on Google. Call (602) 242-2353.',
         crumb=f'AC Repair {city}', h1=f'AC repair in {city}, <span class="accent">done right.</span>',
         lede=f'When your AC quits in {city} heat, you need a company that answers, shows up, and fixes it honestly. '+trust,
         split=('Why %s Calls Wahl'%city,'Diagnosed honestly,<br>fixed <span class="accent">once</span>',
          [f'Our technicians repair every major brand and every common failure — refrigerant leaks, failed capacitors, tripped breakers, frozen coils, dead compressors, weak airflow. We carry common parts on our trucks so most {city} repairs finish the same visit.',
           'No upsells and no inflated repair bills — the reviews below say it better than we can.'],
          ['Same-day service for no-air calls','All major brands repaired','Upfront estimate before any work','Trucks stocked with common parts','Financing for qualifying repairs','Backed by a workmanship guarantee'],
          'owner-service-call.jpg','Wahl Air technician repairing an AC unit','The owner still runs calls'),
         faqs=[('How fast can you get to my house in %s?'%city,'Same day for most no-air calls — it is a written guarantee for service-agreement members, and we prioritize every emergency. We are based in Peoria, minutes from %s.'%city),
          ('How much does AC repair cost?','You get a clear, upfront estimate after diagnosis and before any work begins. No hidden fees, no bait-and-switch — and financing is available for qualifying repairs.'),
          ('Do you repair all brands?','Yes — our technicians work on all major brands and systems, from home units and ductless systems to large commercial HVAC equipment.'),
          ('Is it worth repairing, or should I replace?','We tell you straight. If a repair makes sense we repair it; if the math favors replacement we show you why — without sales pressure. It is how we have kept customers for 40+ years.')])
    if key=='emergency-ac-repair':
        return dict(service='Emergency AC Repair',
         title=f'Emergency AC Repair {city}, AZ — Fix My AC Today | Wahl Air Conditioning',
         desc=f'AC out in {city}? We answer 24/7 and guarantee same-day service for no-air calls. Family-owned since 1957, 4.9 stars. Call (602) 242-2353 now.',
         crumb=f'Emergency AC {city}', h1=f'AC out in {city}? We can fix it <span class="accent">today.</span>',
         lede=f'No air in the middle of a desert summer is an emergency, and we treat it like one. Call (602) 242-2353 — we answer 7 days a week and are on call 24/7. '+trust,
         split=('When It Cannot Wait','Same-day no-air<br><span class="accent">guarantee</span>',
          [f'A no-air call in {city} goes to the front of the line. Our trucks carry the parts that fail most in extreme heat — capacitors, contactors, fan motors — so most emergency repairs finish on the first visit.',
           'One of our reviews tells the story: our senior tech took a 6:00 pm Friday call, climbed into an attic in extreme heat, and had the failed capacitor swapped from parts on his van.'],
          ['24/7 emergency response, 365 days','Same-day guarantee for no-air calls','No after-hours fees for agreement members','Emergency parts stocked on every truck','Clear pricing even under pressure','Family-owned accountability since 1957'],
          'why-wahl.jpg','After-hours AC repair','On call around the clock'),
         faqs=[('My AC just died — what do I do right now?','Call (602) 242-2353. Set your thermostat fan to ON, close blinds on the sun side, and skip the oven. We will get a technician moving and give you an honest arrival window.'),
          ('Do you really answer at night and on weekends?','Yes — we are open 8AM–5PM seven days a week and on call for emergencies 24/7.'),
          ('Do emergency calls cost extra?','Service-agreement members pay no after-hours or weekend overtime fees. Everyone gets a clear, upfront estimate before work begins.'),
          ('What breaks most often in extreme heat?','Run capacitors, contactors, and fan motors — heat is brutal on electrical components. We stock all three on our trucks.')])
    if key=='ac-installation':
        return dict(service='AC Installation',
         title=f'AC Installation {city}, AZ — Carrier Factory-Authorized | Wahl Air Conditioning',
         desc=f'New AC installation in {city}, AZ — properly sized, professionally installed, backed by a 12-month replacement guarantee on Carrier units. Financing available.',
         crumb=f'AC Installation {city}', h1=f'A new system for your {city} home, <span class="accent">sized right.</span>',
         lede=f'A new AC is a 15-year decision. We evaluate your {city} home\'s size, layout, insulation and sun exposure, run a real load calculation, and install the right system — never oversized equipment you don\'t need. '+trust,
         split=('Factory-Authorized Dealer','Carrier systems.<br><span class="accent">12-month</span> replacement guarantee.',
          ['Every Carrier unit we install is backed by a 12-month replacement guarantee — if the unit fails within the first 12 months, we replace it completely.',
           f'From load calculation and equipment selection through removal, install, testing and cleanup, the whole {city} job is handled by our own team — no subcontractors.'],
          ['Free replacement estimates','Real load calculations, not guesses','Carrier factory-authorized dealer','12-month replacement guarantee on Carrier units','Financing plans through GreenSky','Old system removed and hauled away'],
          'install-crane-set.jpg','New AC system installation','Installed by our own crew'),
         faqs=[('How do I know what size AC my house needs?','We calculate it — square footage, insulation, window exposure, ceiling height and ductwork all factor in. Wrong-sized systems waste energy or fail to keep up; ours are load-calculated.'),
          ('How long does an installation take?','Most residential replacements are done in a day. One recent review: both units replaced, started early morning, complete by midday.'),
          ('Can I finance a new system?','Yes — GreenSky plans including 6-month and 15-month no-interest promotional options and 120-month fixed-rate terms, subject to credit approval.'),
          ('What is the 12-month replacement guarantee?','If a Carrier unit we install fails within its first 12 months, we replace the unit completely — not just repair it.')])
    if key=='hvac-company':
        return dict(service='HVAC Company',
         title=f'AC Company in {city}, AZ — Family-Owned Since 1957 | Wahl Air Conditioning',
         desc=f'Looking for a trustworthy AC company in {city}? Wahl Air Conditioning — three generations, 4.9 stars across 218 Google reviews, BBB A+ since 1972.',
         crumb=f'AC Company {city}', h1=f'The AC company {city} has trusted for <span class="accent">three generations.</span>',
         lede=f'Plenty of companies can fix an air conditioner. Fewer can say families in {city} have trusted them since 1957 — grandparents, parents, and now their kids. '+trust,
         split=('Not a Chain. Your Neighbors.','Same family.<br>Same <span class="accent">standard.</span>',
          ['Founded in 1957. Led today by Chris Wahl — third generation — with Dennis Wahl, the founder\'s eldest son, still involved. The owner still runs service calls himself.',
           'BBB A+ accredited since 1972. Licensed Arizona contractor (ROC R39R-055930 and C39-075896). NATE-certified. Factory-authorized Carrier dealer. And 218 Google reviews averaging 4.9 stars.'],
          ['Family-owned and operated since 1957','BBB A+ accredited since 1972','Licensed & insured Arizona contractor','NATE-certified technicians','No subcontractors — our own crew','Honest pricing, no sales pressure'],
          'owners-portrait.jpg','The Wahl family','Chris & Dennis Wahl'),
         faqs=[('What makes Wahl different from the big AC chains?','We answer to neighbors, not shareholders. Three generations of one family, technicians customers request by name, and no commission-driven upselling — our reviews repeat the phrase "no upsell" over and over.'),
          ('Are you licensed and insured?','Yes — Arizona ROC R39R-055930 and C39-075896, fully insured, BBB A+ accredited since 1972.'),
          ('Do you serve both homes and businesses?','Both. Residential AC and heating across the West Valley, plus commercial HVAC for offices, retail, restaurants, medical offices, warehouses, schools and churches.'),
          ('Do you offer maintenance plans?','Yes — service agreements from $154/year residential with two yearly system checks, 15% off labor and materials, priority scheduling and no after-hours fees.')])
    if key=='heating-repair':
        return dict(service='Heating Repair',
         title=f'Heating Repair {city}, AZ | Wahl Air Conditioning',
         desc=f'Furnace and heat pump heating repair in {city}, AZ from a family-owned company serving the Valley since 1957. Honest diagnostics, fair prices.',
         crumb=f'Heating Repair {city}', h1=f'Heating repair in {city} for those <span class="accent">cold desert nights.</span>',
         lede=f'Desert winters bite harder than people expect. When your furnace or heat pump quits in {city}, we diagnose it honestly and fix it properly — gas, electric, or heat pump. '+trust,
         split=('Warm Again, Fast','Every heating system,<br><span class="accent">handled</span>',
          [f'We repair gas and electric furnaces and heat pump heating for {city} homes — ignition failures, blower problems, thermostat faults, weak airflow, and systems that will not start at all.',
           'Every repair ends with a full test and a walkthrough of what was done, backed by our workmanship guarantee.'],
          ['Gas & electric furnace repair','Heat pump heating specialists','Safety-first burner inspections','Honest repair-versus-replace advice','Financing for qualifying repairs','Workmanship guarantee'],
          'service-furnace.jpg','Furnace repair','Gas, electric & heat pumps'),
         faqs=[('My heat pump runs but the house stays cold — why?','Often a refrigerant issue, a failing reversing valve, or airflow restriction. We diagnose the actual cause rather than guessing at parts.'),
          ('Do you work on gas furnaces?','Yes — gas and electric furnaces and heat pump heating, all major brands, with combustion safety checks on every gas repair.'),
          ('Should I repair or replace my old furnace?','We show you the honest math. If your system is 10–15+ years old with rising bills and repeated repairs, replacement may win — but we never pressure the decision.'),
          ('Do you do heating tune-ups?','Yes — seasonal heating tune-ups that verify safe operation before winter. Agreement members get two yearly system checks included.')])

def write_page(key,c_slug,city):
    t=T(key,c_slug,city)
    slug=f'{key}-{c_slug}-az'
    url=f'{DOMAIN}/{slug}/'
    revs=pick_reviews(slug)
    schema=page_schema(url,t['title'],t['desc'],city,f"{t['service']} in {city}, AZ",t['faqs'],revs)
    body = hero(t['crumb'],t['h1'],t['lede'])
    body += split_block(*t['split'])
    body += review_block(revs,city)
    body += faq_block(t['faqs'])
    body += cross_links(c_slug,city,key)
    body += cta()
    d=os.path.join(ROOT,slug); os.makedirs(d,exist_ok=True)
    open(os.path.join(d,'index.html'),'w').write(
        HEAD.format(title=esc(t['title']),desc=esc(t['desc']),url=url,domain=DOMAIN,city=city,schema=schema)
        +CHROME+body+FOOTER+TAIL)
    return slug

built=[]
for key in ['ac-repair','emergency-ac-repair','ac-installation','hvac-company','heating-repair']:
    for c_slug,city in CITIES:
        built.append(write_page(key,c_slug,city))

# ── near-me page ──
url=DOMAIN+'/ac-repair-near-me/'
revs=pick_reviews('near-me')
faqs=[('Is Wahl Air actually near me?','If you are anywhere in the West Valley, yes. We are based at 9802 N 91st Ave in Peoria and dispatch across Phoenix, Scottsdale, Tempe, Glendale, Peoria, Sun City, Surprise, Youngtown, Tolleson, Goodyear, Avondale, Verrado, and Wittmann.'),
 ('How fast can a technician reach me?','Same day for most no-air calls — guaranteed for service-agreement members. We are open 7 days a week and on call 24/7 for emergencies.'),
 ('Why choose a local company over a national chain?','A local, family-owned company answers to its neighbors. We have been doing exactly that since 1957 — three generations, 218 Google reviews at 4.9 stars, and technicians customers ask for by name.')]
schema=page_schema(url,'AC Repair Near Me — West Valley','Searching "AC repair near me" in the West Valley? Wahl Air Conditioning is based in Peoria and dispatches across the Valley — same-day no-air service since 1957.','Peoria','AC Repair Near Me',faqs,revs)
body = hero('AC Repair Near Me','Searching &ldquo;AC repair near me&rdquo;? <span class="accent">Found us.</span>',
 'Wahl Air Conditioning is based in Peoria and dispatches across the entire West Valley, 7 days a week, on call 24/7. Family-owned since 1957 — 4.9 stars across 218 Google reviews, and a same-day guarantee for no-air calls.')
body += split_block('Minutes Away','Based in Peoria.<br>Serving the whole <span class="accent">Valley.</span>',
 ['When you search "near me," what you want is a real local company that can actually get to you today. Our trucks roll from 9802 N 91st Ave in Peoria across every West Valley community below.',
  'Call (602) 242-2353 and tell us where you are — we will give you an honest arrival window on the spot.'],
 ['Same-day service for no-air calls','7 days a week, 24/7 emergencies','Trucks stocked with common parts','Upfront pricing before any work','All major brands','Family-owned since 1957'],
 'area-west-valley.jpg','The West Valley from above','Dispatching Valley-wide')
body += ('<section class="section hairline"><div class="wrap"><div class="reveal">'
 '<span class="kicker">Pick Your City</span><h2 class="h2" style="margin:.7rem 0 1.2rem">AC repair,<br>wherever you are</h2>'
 '<div class="cities">'+''.join('<a class="city" href="/ac-repair-%s-az/">%s</a>'%(cs,cn) for cs,cn in CITIES)+'</div></div></div></section>')
body += review_block(revs,'the West Valley') + faq_block(faqs) + cta()
d=os.path.join(ROOT,'ac-repair-near-me'); os.makedirs(d,exist_ok=True)
open(os.path.join(d,'index.html'),'w').write(
 HEAD.format(title='AC Repair Near Me — West Valley | Wahl Air Conditioning',
   desc='Searching AC repair near me? Wahl Air Conditioning dispatches across the West Valley from Peoria — same-day no-air service, family-owned since 1957.',
   url=url,domain=DOMAIN,city='Peoria',schema=schema)+CHROME+body+FOOTER+TAIL)
built.append('ac-repair-near-me')
print('built %d SEO pages' % len(built))
