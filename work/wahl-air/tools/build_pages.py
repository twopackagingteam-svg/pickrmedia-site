#!/usr/bin/env python3
"""Stamp all interior pages from the homepage chrome + verbatim wahlair.com copy."""
import os, re
ROOT = os.path.join(os.path.dirname(__file__), '..')
idx = open(os.path.join(ROOT,'index.html')).read()

# ── shared chrome, absolutized for subfolder pages ──
head_start = idx.find('<div class="progress"')
head_end   = idx.find('</header>') + len('</header>')
CHROME = idx[head_start:head_end]
foot_start = idx.find('<!-- ▸ footer -->')
FOOTER = idx[foot_start: idx.find('<script src=')]
def absolutize(s):
    s = s.replace('src="assets/','src="/assets/').replace('href="assets/','href="/assets/')
    s = s.replace('href="index.html"','href="/"')
    return s
CHROME, FOOTER = absolutize(CHROME), absolutize(FOOTER)

HEAD = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="icon" href="/assets/brand/favicon-270.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Archivo:ital,wdth,wght@0,100..125,400..900;1,100..125,400..900&family=Inter:wght@400;500;600&family=Jost:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/css/main.css?v=3">
</head>
<body>
'''
TAIL = '<script src="/js/main.js?v=3"></script>\n</body>\n</html>\n'

ARROW = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'

def hero(crumb, h1, lede):
    crumbs = ' <i>›</i> '.join('<a href="%s">%s</a>' % c if isinstance(c,tuple) else c for c in crumb)
    return ('<section class="p-hero"><div class="wrap">'
        '<nav class="crumb">%s</nav>'
        '<h1 class="reveal in">%s</h1>'
        '<p class="lede reveal in">%s</p>'
        '<div class="hero-ctas reveal in">'
        '<a class="btn btn-solid" href="/contact/"><span class="mag">Request a Free Estimate %s</span></a>'
        '<a class="btn btn-ghost" href="tel:+16022422353"><span class="mag">Call (602) 242-2353</span></a>'
        '</div></div></section>' % (crumbs, h1, lede, ARROW))

def cards(kicker, heading, items):
    cell = ''.join('<div class="svc reveal" style="min-height:0"><div class="svc-body">'
        '<h3>%s</h3><p>%s</p></div><span class="svc-bar"></span></div>' % (t,d) for t,d in items)
    return ('<section class="section"><div class="wrap">'
        '<div class="section-head reveal"><span class="kicker">%s</span><h2 class="h2">%s</h2></div>'
        '<div class="svc-grid">%s</div></div></section>' % (kicker, heading, cell))

def body_split(img, alt, tag, heading, paras, quote, why):
    ps = ''.join('<p class="lede" style="font-size:1rem;margin-bottom:1rem">%s</p>' % p for p in paras)
    whyl = ''.join('<li>%s</li>' % w for w in why)
    return ('<section class="section hairline"><div class="wrap"><div class="split">'
        '<div class="reveal"><span class="kicker">Why Choose Wahl Air</span>'
        '<h2 class="h2" style="margin:.7rem 0 1.1rem">%s</h2>%s'
        '<div class="pull">%s</div>'
        '<ul class="check">%s</ul></div>'
        '<div class="split-media reveal" data-d="1" data-slot-wrap>'
        '<img src="/assets/img/%s" alt="%s" data-slot><span class="tagchip"><i></i>%s</span>'
        '</div></div></div></section>' % (heading, ps, quote, whyl, img, alt, tag))

STEPS = [
 ('01','Schedule Your Service',"Call us at (602) 242-2353 or submit a request online. We'll get you on the schedule as quickly as possible — often same day or next day."),
 ('02','Diagnosis & Estimate',"Our technician thoroughly inspects your system, identifies the problem, and gives you a clear, upfront estimate before any work begins."),
 ('03','Repair & Testing',"Once you approve, we get to work. We carry common residential parts on our trucks to minimize delays, then test the system to make sure everything runs properly."),
 ('04','Follow-Up',"We walk you through what was done and any recommendations for keeping your system running well. Our work is backed by a workmanship guarantee."),
]
def steps():
    cell = ''.join('<div class="step reveal"><span class="n">%s</span><h4>%s</h4><p>%s</p></div>' % s for s in STEPS)
    return ('<section class="section hairline"><div class="wrap">'
        '<div class="section-head reveal"><span class="kicker">What to Expect</span>'
        '<h2 class="h2">Simple, honest,<br>start to finish</h2></div>'
        '<div class="steps">%s</div></div></section>' % cell)

def pricing(label, rows):
    cell = ''.join('<div class="price reveal"><span class="u">%s</span><div class="v"><sup>$</sup>%s</div><small>per year</small></div>' % r for r in rows)
    return ('<section class="section hairline"><div class="wrap">'
        '<div class="section-head reveal"><span class="kicker">Membership Pricing</span>'
        '<h2 class="h2">%s</h2></div><div class="price-grid">%s</div>'
        '<p class="lede" style="margin-top:1.4rem;font-size:.95rem">Protect your comfort with Peoria\'s award-winning HVAC team.</p>'
        '</div></section>' % (label, cell))

def cta():
    return ('<section class="cta"><div class="wrap cta-inner">'
        '<div class="reveal"><span class="kicker">Ready to Book Service?</span>'
        '<h2 class="h2" style="margin-top:.7rem">Let\'s get your air <span class="accent">handled.</span></h2></div>'
        '<div class="cta-actions reveal" data-d="1">'
        '<a class="btn btn-solid" href="/contact/"><span class="mag">Request Service Online %s</span></a>'
        '<span class="tiny" style="margin-top:.6rem">Or call us right now</span>'
        '<a class="cta-tel" href="tel:+16022422353">(602) 242-2353</a>'
        '</div></div></section>' % ARROW)

def write(slug, title, desc, body):
    d = os.path.join(ROOT, slug); os.makedirs(d, exist_ok=True)
    open(os.path.join(d,'index.html'),'w').write(HEAD.format(title=title,desc=desc)+CHROME+body+FOOTER+TAIL)
    print('built /'+slug+'/')

SV=[('/','Home')]
# ══ SERVICE PAGES ══
P=[]
P.append(dict(slug='ac-repair', title='AC Repair in Phoenix, AZ | Wahl Air Conditioning',
 desc='Professional AC diagnostics and repair throughout Phoenix and the West Valley. Family-owned since 1957. Same-day no-air service.',
 crumb=[SV[0],'Cooling','AC Repair'], h1='AC Repair,<br>done <span class="accent">right.</span>',
 lede='When you need reliable AC repair, Wahl Air provides professional air conditioning diagnostics and repair for cooling systems throughout the West Valley. Our experienced technicians identify the source of the problem and provide dependable solutions to restore comfort to your home.',
 ck='We Repair Issues Including', ch='Every cooling failure,<br>diagnosed honestly',
 cards=[('Not Cooling',"System runs but won't keep up; we diagnose refrigerant, airflow, electrical, or component failure."),
  ('Frozen Coil','Ice buildup signals an underlying issue; we find and correct the cause.'),
  ('Breaker Tripping','May point to electrical, compressor, or motor issues; safe diagnostics to find the source.'),
  ('Strange Noises','Grinding, buzzing, rattling, banging, squealing are early warning signs.'),
  ('Emergency Repairs','No air in desert heat? We prioritize urgent calls.'),
  ('Short Cycling & High Bills','Constant running and higher-than-normal energy bills point to performance problems we can fix.')],
 img='owner-service-call.jpg', alt='Wahl Air technician repairing a condenser', tag='The owner still runs calls',
 bh='Reliable repair when cooling <span class="accent">can\'t wait</span>',
 paras=['When your air conditioning system breaks down, you need a company that responds fast, diagnoses the problem honestly, and gets the job done right the first time. Wahl Air has been providing trusted residential and commercial AC repair throughout the West Valley since 1957.',
  'No unnecessary upsells, no inflated repair bills — just dependable service from a family-owned and operated company trusted for over 65 years.'],
 quote='Our experienced technicians work on all major brands and systems — from home units and ductless systems to large commercial HVAC equipment.',
 why=['Same-day service available for no-air calls','Experienced, highly trained technicians','Locally owned and serving the Valley','Honest recommendations, no pressure sales','Financing available for qualifying repairs','Repairs focused on long-term reliability'], steps=True))
P.append(dict(slug='ac-installation-and-replacement', title='AC Installation & Replacement | Wahl Air Conditioning',
 desc='Professional AC installation and replacement across the West Valley — proper sizing, energy savings, financing. Carrier factory-authorized dealer.',
 crumb=[SV[0],'Cooling','Installation & Replacement'], h1='Upgrade your comfort with a system <span class="accent">built for the heat.</span>',
 lede='Whether your current system is constantly breaking down, struggling to keep up, or reaching the end of its life, Wahl Air makes replacing your system simple and stress-free. Every home deserves a properly designed system — not a one-size-fits-all approach.',
 ck='Our Installation Process', ch='Handled end to end,<br>done right the first time',
 cards=[('New System Installs','We handle everything from removal of your old unit to full installation of your new system.'),
  ('System Sizing','Wrong size means wasted energy or poor comfort; we calculate the exact unit your space needs.'),
  ('Energy Savings','Modern systems use significantly less power; we help you choose equipment that lowers your monthly bills.'),
  ('Financing Options',"Don't let upfront costs hold you back; flexible payment plans to fit your budget."),
  ('Carrier 12-Month Guarantee','Every Carrier unit we install is backed by a 12-month replacement guarantee.'),
  ('Permits, Testing & Cleanup','From load calculations to final testing, every step handled with precision.')],
 img='install-rooftop-crew.jpg', alt='Wahl crew setting a new unit', tag='Crane sets done safely',
 bh='Built for <span class="accent">long-term</span> comfort',
 paras=['Installing a new air conditioning system is a major investment, and choosing the right HVAC company makes all the difference. We take the time to properly evaluate your property\'s size, layout, insulation, and cooling demands to recommend the right system for your needs and budget — never oversized equipment you don\'t need.'],
 quote='Our experienced team designs and installs AC systems for homes, retail spaces, office buildings, and industrial facilities — with comfort, efficiency, and long-term performance in mind.',
 why=['Free replacement estimates','Proper system sizing and design','Professional installation standards','Financing options available','Clean, respectful install teams','Ongoing support after installation'], steps=True))
P.append(dict(slug='ac-maintenance-tuneups', title='AC Maintenance & Tune-Ups | Wahl Air Conditioning',
 desc='Seasonal AC tune-ups, coil cleaning and performance checks that prevent breakdowns before desert summer peaks.',
 crumb=[SV[0],'Cooling','Maintenance / Tune-Ups'], h1='Protect your investment with <span class="accent">preventative maintenance.</span>',
 lede='Routine maintenance helps your system run efficiently, lowers the chance of unexpected breakdowns, and identifies concerns before they become costly. Wahl Air maintenance is designed to keep your system performing through the toughest seasons.',
 ck='Maintenance Services', ch='Ready before<br>peak demand',
 cards=[('Seasonal Inspections','Stay ahead of breakdowns with scheduled tune-ups before peak heating and cooling seasons.'),
  ('Coil Cleaning','Dirty coils reduce efficiency and strain your system; we clean them to restore full performance.'),
  ('Performance Checks','We test airflow, refrigerant levels, and electrical components to make sure your system runs at its best.')],
 img='service-coil-clean.jpg', alt='Condenser coil cleaning at golden hour', tag='Coil cleaning, done properly',
 bh='Small problems caught <span class="accent">early</span>',
 paras=['Regular air conditioning maintenance helps your system perform better during the hottest months of the year. A seasonal tune-up can identify small problems before they become expensive breakdowns — keeping your cooling system clean, efficient, and ready for desert heat.'],
 quote='Our experienced technicians work on all major brands and systems — from home units and ductless systems to large commercial HVAC equipment.',
 why=['Extend equipment life','Improve energy efficiency','Reduce unexpected breakdowns','Priority scheduling options available','Thorough system evaluations','Trusted local HVAC professionals'], steps=True))
P.append(dict(slug='heat-pumps', title='Heat Pump Repair, Replacement & Maintenance | Wahl Air Conditioning',
 desc='Heat pump installation, repair and maintenance for energy-efficient year-round comfort across the West Valley.',
 crumb=[SV[0],'Cooling','Heat Pumps'], h1='Efficient heat pump cooling, <span class="accent">year-round.</span>',
 lede='Heat pumps provide reliable cooling while using less energy than many traditional systems. Whether you need a new installation, replacement, or service, Wahl Air keeps your home comfortable and efficient through the long cooling season.',
 ck='Heat Pump Services', ch='One system,<br>every season',
 cards=[('Repairs','From poor cooling performance to unusual noises and airflow issues, we diagnose and repair heat pump problems quickly.'),
  ('Replacement','Replace an aging or inefficient system with a modern heat pump that delivers improved performance and lower operating costs.'),
  ('Maintenance','Keep your heat pump dependable with seasonal service tuned to desert demand.')],
 img='service-heatpump.jpg', alt='Modern heat pump installed by Wahl Air', tag='Energy-efficient comfort',
 bh='Comfort that costs <span class="accent">less to run</span>',
 paras=['Heat pumps are an excellent cooling solution for homeowners looking for energy-efficient comfort. Modern systems move heat out of your home while using less electricity than many conventional cooling systems — helping you stay comfortable even during extreme summer temperatures.'],
 quote='Our experienced technicians install, repair, and service heat pumps from all major manufacturers, helping homeowners maximize comfort, efficiency, and long-term performance.',
 why=['Energy-efficient cooling solutions','Professional heat pump installation','Expert repairs for all major brands','Improved indoor comfort & performance','Honest recommendations with no pressure','Trusted local HVAC professionals'], steps=True))
P.append(dict(slug='heating-repair', title='Heating Repair | Wahl Air Conditioning',
 desc='Prompt heating repair for gas and electric furnaces and heat pumps across the West Valley.',
 crumb=[SV[0],'Heating','Heating Repair'], h1='Fast, reliable heating repairs <span class="accent">when you need them most.</span>',
 lede="A heating system breakdown can leave your home uncomfortable when temperatures drop. Whether your system won't turn on, isn't producing enough heat, or is making unusual noises, Wahl Air provides prompt heating repair to restore comfort as quickly as possible.",
 ck='We Repair', ch='Warm again,<br>fast',
 cards=[('Furnace Repairs','We diagnose and repair heating issues for gas and electric furnaces of all major brands.'),
  ('Heat Pump Heating Repairs','When a heat pump stops keeping up in winter, we find the cause and fix it properly.'),
  ('Airflow & Thermostat Issues','Weak airflow, cold spots, and control problems traced to the source.')],
 img='service-furnace.jpg', alt='Furnace inspection by headlamp', tag='Gas & electric systems',
 bh='Cold desert nights, <span class="accent">handled</span>',
 paras=['Dependable heating service for those cold desert nights — honest diagnostics, clear estimates, and repairs that keep your system running safely.'],
 quote='Show up, inspect the system properly, explain the options clearly, and do the work right.',
 why=['Prompt response when heat is out','Experienced with furnaces and heat pumps','Honest recommendations, no pressure sales','Financing available for qualifying repairs','Family-owned and operated since 1957','Workmanship guarantee'], steps=True))
P.append(dict(slug='heating-installation', title='Heating Installation | Wahl Air Conditioning',
 desc='Expert heating installation — properly sized, efficient systems for reliable winter comfort.',
 crumb=[SV[0],'Heating','Heating Installation'], h1='Professional heating installation for <span class="accent">reliable winter comfort.</span>',
 lede="A properly installed heating system is essential for long-term comfort, efficiency, and safety. Whether you're building a new home or replacing an outdated unit, Wahl Air provides expert heating installation designed to keep your home warm and energy efficient through every winter season.",
 ck='Installation Services', ch='Sized right,<br>installed right',
 cards=[('Furnace Installation','High-efficiency gas and electric furnaces, installed to professional standards.'),
  ('Heat Pump Systems','One efficient system for both heating and cooling, matched to your home.'),
  ('System Replacement','Retire an aging heater for a modern system that costs less to run.')],
 img='install-new-pad.jpg', alt='New system installed on a fresh pad', tag='Clean, professional installs',
 bh='An investment done <span class="accent">once, properly</span>',
 paras=['We evaluate your home\'s size, layout, and heating demands to recommend the right system for your needs and budget — then handle equipment, installation, testing, and cleanup with precision.'],
 quote='Every home deserves a properly designed system, not a one-size-fits-all approach.',
 why=['Free replacement estimates','Proper sizing and design','Professional installation standards','Financing options available','Clean, respectful install teams','Ongoing support after installation'], steps=True))
P.append(dict(slug='heat-pump-heating', title='Heat Pump Heating | Wahl Air Conditioning',
 desc='Efficient heat pump heating service, replacement and repair for comfortable desert winters.',
 crumb=[SV[0],'Heating','Heat Pump Heating'], h1='Reliable heat pump heating for <span class="accent">comfortable winters.</span>',
 lede='Heat pumps provide efficient, dependable heating when temperatures drop. Whether you need a new system, a replacement, or repairs, Wahl Air delivers expert heat pump heating service to keep your home warm, comfortable, and energy efficient all season long.',
 ck='Heat Pump Heating', ch='Efficient warmth,<br>all season',
 cards=[('Heat Pump Installation','High-efficiency heat pumps that deliver reliable heating and cooling from one system.'),
  ('Heating Repairs','Diagnostics and repair when your heat pump stops keeping up.'),
  ('Seasonal Service','Winter-readiness checks that protect performance and efficiency.')],
 img='service-heatpump.jpg', alt='Heat pump outdoor unit', tag='Heating + cooling in one',
 bh='One system, <span class="accent">both seasons</span>',
 paras=['Modern heat pumps heat your home efficiently in winter and cool it in summer — a single system matched to desert demand, installed and serviced by technicians who know it inside and out.'],
 quote='Our experienced technicians install, repair, and service heat pumps from all major manufacturers.',
 why=['Energy-efficient heating solutions','Professional installation','Expert repairs for all major brands','Honest recommendations with no pressure','Family-owned and operated since 1957','Trusted local HVAC professionals'], steps=True))
P.append(dict(slug='seasonal-heating-tune-ups', title='Seasonal Heating Tune-Ups | Wahl Air Conditioning',
 desc='Seasonal heating tune-ups that prepare your system for winter — safe, efficient, reliable.',
 crumb=[SV[0],'Heating','Seasonal Tune-Ups'], h1='Seasonal tune-ups for <span class="accent">reliable winter comfort.</span>',
 lede="Your heating system works hard during the colder months, and regular maintenance helps ensure it runs safely, efficiently, and reliably. Wahl Air's seasonal heating tune-ups prepare your system for winter, reduce the risk of breakdowns, and improve overall performance.",
 ck='Tune-Up Services', ch='Safe and ready<br>before the cold',
 cards=[('Heating System Inspection','A full system inspection to identify wear, safety concerns, and efficiency losses.'),
  ('Burner & Component Checks','Burners, ignition, and electrical components tested and verified.'),
  ('Performance Verification','Airflow and output confirmed so the system is ready before you need it.')],
 img='service-gauges.jpg', alt='System performance check', tag='Checked before the season',
 bh='Breakdowns prevented, <span class="accent">not repaired</span>',
 paras=['A seasonal tune-up catches small issues while they are still small — protecting your equipment, your safety, and your energy bill through the heating season.'],
 quote='Regular maintenance helps ensure your system runs safely, efficiently, and reliably.',
 why=['Reduce the risk of winter breakdowns','Verify safe operation','Improve efficiency and performance','Extend equipment life','Priority scheduling options available','Trusted local HVAC professionals'], steps=True))
P.append(dict(slug='emergency-repairs', title='Emergency AC Repair | Wahl Air Conditioning',
 desc='24/7 emergency AC repair with same-day no-air service across the West Valley.',
 crumb=[SV[0],'Cooling',('/ac-repair/','AC Repair'),'Emergency Repairs'], h1='Emergency AC repair, <span class="accent">24/7.</span>',
 lede='An unexpected AC failure can leave your home uncomfortable fast. We respond quickly, diagnose the problem, and perform reliable repairs to restore your cooling as soon as possible — with same-day no-air service and no after-hours surprises for agreement members.',
 ck='Signs You Need Emergency Repair', ch='Call now if you see<br>any of these',
 cards=[("System won't turn on",'No response at the thermostat or the unit — we trace power, controls, and components fast.'),
  ('No cool air in extreme heat','A running system blowing warm air is an emergency in desert summer.'),
  ('Burning smell or electrical signs','Shut the system down and call — electrical faults are safety issues.'),
  ('Breaker trips repeatedly','A breaker that trips when the AC runs points to a fault that needs safe diagnostics.'),
  ('Loud banging or grinding','Mechanical failure in progress — stopping early prevents bigger damage.'),
  ('Water where it should not be','Leaks and overflow signal drainage or freeze problems worth urgent attention.')],
 img='why-wahl.jpg', alt='After-hours rooftop service', tag='On call for emergencies',
 bh='When the heat won\'t wait, <span class="accent">neither do we</span>',
 paras=['We are on call for emergencies every day of the year. Call (602) 242-2353 and we will prioritize your no-air call — often same day.'],
 quote='Same-Day Service Guarantee for no-air calls — that is the standard our customers count on.',
 why=['24/7 emergency response','Same-day no-air service','Trucks stocked with common parts','Honest diagnostics under pressure','Family-owned and operated since 1957','Workmanship guarantee'], steps=True))
P.append(dict(slug='residential', title='Residential Service Agreements | Wahl Air Conditioning',
 desc='Wahl Air residential service agreements — 2 yearly system checks, 15% off labor and materials, priority scheduling, no after-hours fees.',
 crumb=[SV[0],'Agreements','Residential'], h1='Protect your comfort. Save money. <span class="accent">Get priority service.</span>',
 lede='Your HVAC system works hard year-round — especially here. The Wahl Air Service Agreement reduces unexpected breakdowns, improves system performance, and gives you priority when you need service most.',
 ck='Membership Benefits', ch='What you get,<br>every year',
 cards=[('2 Yearly Services & System Checks','Scheduled before each peak season, so problems get caught early.'),
  ('15% Off All Labor & Materials','Member pricing on every repair, all year.'),
  ('Up to $1,000 Off a New System','$500 off install, plus $100 per consecutive renewal year, up to $1,000.'),
  ('Priority Scheduling','Same-day when weather and schedule permit.'),
  ('No After-Hours or Weekend Overtime Fees','Emergencies without the surcharge.'),
  ('Same-Day Service Guarantee','Guaranteed same-day response for no-air calls.')],
 img='area-west-valley.jpg', alt='The West Valley at golden hour', tag='Priority across the Valley',
 bh='Membership that <span class="accent">pays for itself</span>',
 paras=['Discounted maintenance services are included too — coil cleaning, duct cleaning, filter replacement, lubrication of moving parts, and other qualifying maintenance.'],
 quote="Protect your comfort with Peoria's award-winning HVAC team.",
 why=['Lower repair costs','Priority scheduling benefits','Reduce unexpected breakdowns','Extend equipment life','Exclusive member savings','Peace of mind year-round'],
 pricing=('Residential Service Agreement',[('1 unit','154'),('2 units','239'),('3 units','324'),('4 units','409')]), steps=False))
P.append(dict(slug='commercial', title='Commercial Service Agreements | Wahl Air Conditioning',
 desc='Commercial HVAC service agreements — priority scheduling, 15% off labor and materials, preventative maintenance that protects uptime.',
 crumb=[SV[0],'Agreements','Commercial'], h1='Protect your business. Reduce downtime. <span class="accent">Keep operations running.</span>',
 lede="Commercial HVAC systems are essential to comfortable operations. Wahl Air's Commercial Service Agreement improves system reliability, reduces unexpected repairs, and keeps your equipment operating efficiently — with priority service when you need it most.",
 ck='Agreement Benefits', ch='Built for buildings<br>that can\'t go down',
 cards=[('2 Yearly Services & System Checks','Preventative visits scheduled around your operations.'),
  ('15% Off All Labor & Materials','Member pricing on every commercial repair.'),
  ('Up to $1,000 Off a New System','$500 off install, plus $100 per consecutive renewal year, up to $1,000.'),
  ('Priority Commercial Scheduling','Same-day when weather and schedule permit.'),
  ('No After-Hours or Weekend Overtime Fees','Downtime handled without the surcharge.'),
  ('Same-Day Service Guarantee','Guaranteed same-day response for no-air calls.')],
 img='commercial-mechanical-room.jpg', alt='Commercial mechanical room service', tag='Commercial-grade coverage',
 bh='Downtime is the <span class="accent">real cost</span>',
 paras=['Discounted maintenance services included — coil cleaning, duct cleaning, filter replacement, lubrication of moving parts, and other qualifying maintenance.'],
 quote="Protect your comfort with Peoria's award-winning HVAC team.",
 why=['Fast response times','Priority commercial scheduling','Experienced commercial HVAC team','Preventative maintenance programs','Reduced repair costs through membership','Long-term equipment protection'],
 pricing=('Commercial Service Agreement',[('1 unit','210'),('2 units','320'),('3 units','430'),('4 units','540'),('5 units','650'),('6 units','760'),('7 units','870')]), steps=False))
P.append(dict(slug='commercial-hvac-services', title='Commercial HVAC Services | Wahl Air Conditioning',
 desc='Commercial HVAC repair, installation, replacement and maintenance for West Valley businesses — offices, retail, restaurants, medical, warehouses.',
 crumb=[SV[0],'Commercial HVAC'], h1='Commercial HVAC that keeps your <span class="accent">business running.</span>',
 lede='Wahl Air provides commercial HVAC repair, installation, replacement, and maintenance for businesses and commercial properties across the West Valley. From urgent cooling issues to planned system upgrades, our team keeps your building comfortable and your equipment reliable.',
 ck='Commercial Solutions', ch='Complete commercial<br>HVAC services',
 cards=[('Commercial AC Repair','Fast diagnosis and clear explanations, with work planned to minimize disruption.'),
  ('Commercial Installation','Properly sized, efficient systems designed for desert heat and commercial demands.'),
  ('Commercial Replacement','Aging, inefficient equipment replaced after an honest repair-versus-replace comparison.'),
  ('Commercial Maintenance','Routine care that protects equipment and reduces expensive peak-season downtime.'),
  ('Light Commercial','Offices, small businesses, and retail spaces supported throughout the West Valley.'),
  ('Emergency Commercial Service','When cooling problems affect your business, fast response matters.')],
 img='commercial-mechanical-room.jpg', alt='Commercial mechanical room', tag='Since 1957, commercial too',
 bh='Serving businesses <span class="accent">since 1957</span>',
 paras=["When your commercial HVAC system goes down, it's not just uncomfortable — it can cost you customers, productivity, and revenue. We understand the urgency of commercial service, and we respond accordingly.",
  "We've worked on everything from small retail shops to large industrial facilities, and we bring the same professionalism to every job. Our technicians carry commercial-grade parts on our trucks and work efficiently to minimize disruption."],
 quote='Industries we serve: office buildings, retail stores, restaurants, medical offices, warehouses, industrial facilities, schools, and churches.',
 why=['Experienced with commercial systems of all types','Commercial-grade parts on our trucks','Minimal disruption to your operations','Priority response for downtime','Service agreements for planned maintenance','Family-owned accountability since 1957'], steps=False))

for p in P:
    body = hero(p['crumb'], p['h1'], p['lede'])
    body += cards(p['ck'], p['ch'], p['cards'])
    body += body_split(p['img'], p['alt'], p['tag'], p['bh'], p['paras'], p['quote'], p['why'])
    if p.get('pricing'): body += pricing(*p['pricing'])
    if p.get('steps'): body += steps()
    body += cta()
    write(p['slug'], p['title'], p['desc'], body)

# ══ ABOUT ══
about = hero([SV[0],'About'],
 'Three generations of keeping the <span class="accent">Valley cool.</span>',
 "Three generations of the Wahl family have been keeping the West Valley cool since 1957. We're not just a business — we're your neighbors.")
about += ('<section class="section"><div class="wrap"><div class="split">'
 '<div class="reveal"><span class="kicker">Over 65 Years of Trusted Service</span>'
 '<h2 class="h2" style="margin:.7rem 0 1.1rem">Founded 1957.<br>Still <span class="accent">family.</span></h2>'
 '<p class="lede" style="font-size:1rem;margin-bottom:1rem">Wahl Air Conditioning was founded in 1957 by the Wahl family with a simple mission: provide honest, reliable air conditioning service to families and businesses throughout the West Valley.</p>'
 '<p class="lede" style="font-size:1rem;margin-bottom:1rem">Today the company is led by Chris Wahl — the third generation of the Wahl family — who grew up in the business and has spent his career carrying on his father and grandfather\'s commitment to quality and integrity. Dennis Wahl, the founder\'s eldest son, remains involved, and together Chris and Dennis continue to build Wahl Air\'s reputation as one of the most trusted names in West Valley HVAC service.</p>'
 '<p class="lede" style="font-size:1rem">We\'re not a national chain. We\'re a local, family-owned and operated company that answers to our neighbors — not corporate shareholders. Over the years, the majority of founder Elmer\'s twelve children contributed their talents to the company, and even today four members of the Wahl family remain active in the industry. Many of our customers are second-generation patrons.</p></div>'
 '<div><div class="split-media reveal" data-d="1" data-slot-wrap>'
 '<img src="/assets/img/owners-portrait.jpg" alt="Chris and Dennis Wahl" data-slot>'
 '<span class="tagchip"><i></i>Chris &amp; Dennis Wahl</span></div>'
 '<div class="stats mt reveal" data-d="1">'
 '<div class="stat"><span class="v"><span data-count="65">0</span>+</span><span class="l">Years in business</span></div>'
 '<div class="stat"><span class="v"><span data-count="3">0</span></span><span class="l">Generations</span></div>'
 '<div class="stat"><span class="v"><span data-count="218">0</span>+</span><span class="l">Five-star reviews</span></div>'
 '<div class="stat"><span class="v">A+</span><span class="l">BBB since 1972</span></div>'
 '</div></div></div></div></section>')
about += cards('What Sets Us Apart','Why the Valley<br>keeps calling',
 [('Three Generations of Excellence',"Founded in 1957 and still family-owned and operated. We've been doing this longer than most companies have existed."),
  ('Experienced Technicians','Decades of combined experience. No subcontractors — just skilled professionals who know their craft.'),
  ('West Valley Specialists','We live and work in the communities we serve, and we understand cooling homes in desert heat.'),
  ('24/7 Emergency Service',"AC emergencies don't wait for business hours. We're available around the clock, every day of the year."),
  ('Licensed & Insured','Fully licensed (ROC R39R-055930 and C39-075896) and insured for your protection and peace of mind.'),
  ('Honest, Fair Pricing','No hidden fees, no bait-and-switch tactics. Upfront pricing and honest recommendations.')])
about += ('<section class="section hairline"><div class="wrap">'
 '<div class="sec-head-row reveal"><div><span class="kicker">Recognized for Our Service</span>'
 '<h2 class="h2" style="margin-top:.7rem">Awarded. Accredited.<br><span class="accent">Authorized.</span></h2></div>'
 '<p class="lede">Best HVAC Contractor in Peoria (2024), BBB A+ accredited since 1972, and a factory-authorized Carrier dealer.</p></div>'
 '<div class="gal"><figure class="g-a reveal"><img src="/assets/img/award-2024.jpg" alt="Best Business Award 2024" data-slot><figcaption>Best HVAC Contractor in Peoria · 2024</figcaption></figure>'
 '<figure class="g-b reveal" data-d="1"><img src="/assets/img/team-truck-lineup.jpg" alt="Wahl service truck" data-slot><figcaption>The fleet</figcaption></figure></div>'
 '</div></section>')
about += cta()
write('about','About Wahl Air Conditioning | Family-Owned Since 1957',
 'Three generations of the Wahl family serving the West Valley since 1957 — the story of Wahl Air Conditioning.', about)

# ══ CONTACT ══
contact = hero([SV[0],'Contact'],
 'Let\'s get you <span class="accent">scheduled.</span>',
 'Need AC repair, installation, replacement, maintenance, or emergency service? Contact Wahl Air Conditioning to schedule service or request an estimate. 4.9 on Google across 218 reviews.')
contact += ('<section class="section"><div class="wrap"><div class="split" style="align-items:start">'
 '<div class="reveal"><span class="kicker">Request an Estimate</span>'
 '<h2 class="h2" style="margin:.7rem 0 1.4rem">Tell us what\'s<br>going on</h2>'
 '<form id="contact-form" class="form" action="/contact.php" method="post">'
 '<div class="field"><label for="cf-first">First name</label><input id="cf-first" name="first" required autocomplete="given-name"></div>'
 '<div class="field"><label for="cf-last">Last name</label><input id="cf-last" name="last" required autocomplete="family-name"></div>'
 '<div class="field"><label for="cf-email">Email</label><input id="cf-email" type="email" name="email" required autocomplete="email"></div>'
 '<div class="field"><label for="cf-phone">Phone</label><input id="cf-phone" type="tel" name="phone" required autocomplete="tel"></div>'
 '<div class="field full"><label for="cf-svc">Service needed</label><select id="cf-svc" name="service">'
 '<option>AC Repair</option><option>AC Installation / Replacement</option><option>Maintenance / Tune-Up</option>'
 '<option>Heat Pumps</option><option>Heating</option><option>Commercial HVAC</option><option>Service Agreement</option><option>Emergency — no air</option></select></div>'
 '<div class="field full"><label for="cf-msg">Message</label><textarea id="cf-msg" name="message" placeholder="Let us know what type of service you need."></textarea></div>'
 '<input type="text" name="company" style="display:none" tabindex="-1" autocomplete="off">'
 '<div id="form-status" class="form-status" role="status"></div>'
 '<div class="field full"><button class="btn btn-solid" type="submit"><span class="mag">Send Request %s</span></button></div>'
 '</form></div>'
 '<div class="reveal" data-d="1"><span class="kicker">Contact Information</span>'
 '<div class="reasons" style="margin-top:1.2rem">'
 '<div class="reason"><span class="n">☎</span><div><h4>Phone</h4><p><a href="tel:+16022422353"><b>(602) 242-2353</b></a> — call today, 7 days a week</p></div></div>'
 '<div class="reason"><span class="n">✉</span><div><h4>Email</h4><p><a href="mailto:info@wahlair.com">info@wahlair.com</a></p></div></div>'
 '<div class="reason"><span class="n">⌂</span><div><h4>Location</h4><p>9802 N 91st Ave, Suite 104<br>Peoria, AZ 85345</p></div></div>'
 '<div class="reason"><span class="n">◔</span><div><h4>Hours</h4><p>8AM–5PM, 7 days a week<br>On call for emergencies 24/7</p></div></div>'
 '</div>'
 '<div class="mt"><span class="kicker">Service Area</span><div class="cities" style="margin-top:1rem">' +
 ''.join('<a class="city" href="/%s/">%s</a>' % c for c in [('phoenix-az','Phoenix'),('scottsdale-az','Scottsdale'),('tempe-az','Tempe'),('glendale-az','Glendale'),('peoria-az','Peoria'),('sun-city-az','Sun City'),('surprise-az','Surprise'),('youngtown-az','Youngtown'),('tolleson-az','Tolleson'),('goodyear-az','Goodyear'),('avondale-az','Avondale'),('verrado-az','Verrado'),('wittmann-az','Wittmann')]) +
 '</div></div></div></div></div></section>') % ARROW
contact += cta()
write('contact','Contact Wahl Air Conditioning | (602) 242-2353',
 'Schedule service or request a free estimate — Wahl Air Conditioning, Peoria AZ. 8AM-5PM 7 days, 24/7 emergency.', contact)

# ══ CITY PAGES ══
CITIES=[('phoenix-az','Phoenix'),('scottsdale-az','Scottsdale'),('tempe-az','Tempe'),('glendale-az','Glendale'),
 ('peoria-az','Peoria'),('sun-city-az','Sun City'),('surprise-az','Surprise'),('youngtown-az','Youngtown'),
 ('tolleson-az','Tolleson'),('goodyear-az','Goodyear'),('avondale-az','Avondale'),('verrado-az','Verrado'),('wittmann-az','Wittmann')]
for slug, city in CITIES:
    b = hero([SV[0],'Service Area',city],
     'AC repair &amp; HVAC service in <span class="accent">%s, AZ.</span>' % city,
     'Whether you need AC repair, installation, replacement, or maintenance in %s, Wahl Air Conditioning is ready to help — a family-owned and operated company serving the West Valley since 1957, with 4.9 stars across 218 Google reviews.' % city)
    b += cards('Services in %s' % city,'Everything your<br>system needs',
     [('AC Repair','Fast, honest cooling repair for %s homes — from weak airflow to full system failures.' % city),
      ('Installation & Replacement','Properly sized, energy-efficient systems built for desert heat, with financing available.'),
      ('Maintenance / Tune-Ups','Seasonal service that prevents breakdowns before peak summer demand.'),
      ('Heat Pumps','Repair, replacement, and maintenance for efficient year-round comfort.'),
      ('Heating Services','Repairs, installs, and tune-ups for those cold desert nights.'),
      ('Commercial HVAC','Repair and maintenance that keeps %s businesses running.' % city)])
    b += body_split('area-west-valley.jpg','The West Valley from above','Serving %s since 1957' % city,
     'Your neighbors, <span class="accent">not a chain</span>',
     ['Wahl Air is based in Peoria and deeply rooted in the communities we serve. Many of our customers have been with us for decades — that\'s the kind of trust you only earn by doing the job right, every single time.'],
     'Family-owned and operated, honest recommendations, same-day no-air service.',
     ['Family-owned and operated since 1957','4.9 stars across 218 Google reviews','Same-day no-air service','NATE-certified technicians','Licensed & insured (ROC R39R-055930 · C39-075896)','Financing available for qualifying work'])
    b += cta()
    write(slug,'AC Repair & HVAC Services in %s, AZ | Wahl Air Conditioning' % city,
     'Trusted AC repair, installation and maintenance in %s, AZ from Wahl Air Conditioning — family-owned since 1957.' % city, b)
print('ALL PAGES BUILT')
