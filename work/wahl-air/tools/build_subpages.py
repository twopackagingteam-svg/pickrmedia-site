#!/usr/bin/env python3
"""Stamp the leaf sub-pages (symptoms → causes → process) from verbatim wahlair.com copy."""
import os
ROOT = os.path.join(os.path.dirname(__file__), '..')
idx = open(os.path.join(ROOT,'index.html')).read()
CHROME = idx[idx.find('<div class="progress"'): idx.find('</header>')+len('</header>')]
FOOTER = idx[idx.find('<!-- ▸ footer -->'): idx.find('<script src=')]
def ab(s):
    return s.replace('src="assets/','src="/assets/').replace('href="assets/','href="/assets/').replace('href="index.html"','href="/"')
CHROME, FOOTER = ab(CHROME), ab(FOOTER)
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
<link rel="stylesheet" href="/css/main.css?v=4">
</head>
<body>
'''
TAIL = '<script src="/js/main.js?v=4"></script>\n</body>\n</html>\n'
AR = '<svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><path d="M5 12h14M13 6l6 6-6 6"/></svg>'

def page(p):
    crumb = ' <i>›</i> '.join(('<a href="%s">%s</a>'%c if isinstance(c,tuple) else c) for c in p['crumb'])
    sigs = ''.join('<li>%s</li>'%s for s in p['signs'])
    causes = ''.join('<div class="cause reveal"><span class="n">%02d</span><div><b>%s</b><p>%s</p></div></div>'
                     % (i+1, t, d) for i,(t,d) in enumerate(p['causes']))
    flow = ''.join('<div class="flow-step reveal"><div class="fn">%d</div><span>%s</span></div>'
                   % (i+1, s) for i,s in enumerate(p['flow']))
    sibs = ''.join('<a class="sib%s" href="%s">%s</a>' % (' on' if s[0]==p['slug'] else '', '/%s/'%s[0], s[1]) for s in p['sibs'])
    b = ('<section class="p-hero"><div class="wrap">'
     '<nav class="crumb">%s</nav><h1 class="reveal in">%s</h1>'
     '<p class="lede reveal in">%s</p>'
     '<div class="hero-ctas reveal in">'
     '<a class="btn btn-solid" href="/contact/"><span class="mag">Request a Free Estimate %s</span></a>'
     '<a class="btn btn-ghost" href="tel:+16022422353"><span class="mag">Call (602) 242-2353</span></a></div>'
     '<div class="sibs reveal in">%s</div></div></section>' % (crumb, p['h1'], p['lede'], AR, sibs))
    b += ('<section class="section"><div class="wrap"><div class="split">'
     '<div class="reveal"><span class="kicker">%s</span>'
     '<h2 class="h2" style="margin:.7rem 0 .4rem">%s</h2>'
     '<ul class="check">%s</ul></div>'
     '<div class="split-media reveal" data-d="1" data-slot-wrap>'
     '<img src="/assets/img/%s" alt="%s" data-slot><span class="tagchip"><i></i>%s</span>'
     '</div></div></div></section>' % (p['sk'], p['sh'], sigs, p['img'], p['alt'], p['tag']))
    b += ('<section class="section hairline"><div class="wrap">'
     '<div class="section-head reveal"><span class="kicker">%s</span><h2 class="h2">%s</h2></div>'
     '<div class="causes">%s</div></div></section>' % (p['ck'], p['ch'], causes))
    b += ('<section class="section hairline"><div class="wrap">'
     '<div class="section-head reveal"><span class="kicker">%s</span><h2 class="h2">Our five-step<br>process</h2></div>'
     '<div class="flow">%s</div>'
     '<p class="lede reveal" style="margin-top:1.4rem;font-size:.95rem">%s</p></div></section>'
     % (p['fk'], flow, p.get('note','Call us now or request a free estimate online. Flexible financing is also available for qualifying repairs.')))
    b += ('<section class="cta"><div class="wrap cta-inner">'
     '<div class="reveal"><span class="kicker">Ready to Schedule?</span>'
     '<h2 class="h2" style="margin-top:.7rem">Let\'s get your air <span class="accent">handled.</span></h2></div>'
     '<div class="cta-actions reveal" data-d="1">'
     '<a class="btn btn-solid" href="/contact/"><span class="mag">Request Service Online %s</span></a>'
     '<span class="tiny" style="margin-top:.6rem">Or call us right now</span>'
     '<a class="cta-tel" href="tel:+16022422353">(602) 242-2353</a></div></div></section>' % AR)
    d = os.path.join(ROOT, p['slug']); os.makedirs(d, exist_ok=True)
    open(os.path.join(d,'index.html'),'w').write(HEAD.format(title=p['title'],desc=p['desc'])+CHROME+b+FOOTER+TAIL)
    print('built /%s/' % p['slug'])

HOME=('/','Home')
REPAIR=[('not-cooling','Not Cooling'),('frozen-coil','Frozen Coil'),('breaker-tripping','Breaker Tripping'),
        ('strange-noises','Strange Noises'),('emergency-repairs','Emergency Repairs')]
INSTALL=[('new-system-installs','New System Installs'),('system-sizing','System Sizing'),
         ('energy-savings','Energy Savings'),('financing','Financing')]
MAINT=[('seasonal-inspections','Seasonal Inspections'),('coil-cleaning','Coil Cleaning'),('performance-checks','Performance Checks')]
HP=[('repair','Repair'),('replacement','Replacement'),('maintenance','Maintenance')]
CB_R=[HOME,'Cooling',('/ac-repair/','AC Repair')]
CB_I=[HOME,'Cooling',('/ac-installation-and-replacement/','AC Installation')]
CB_M=[HOME,'Cooling',('/ac-maintenance-tuneups/','AC Maintenance')]
CB_H=[HOME,'Cooling',('/heat-pumps/','Heat Pumps')]

P=[
dict(slug='not-cooling', sibs=REPAIR, crumb=CB_R+['Not Cooling'],
 title="AC Not Cooling? | Wahl Air Conditioning", desc="AC running but not cooling? We diagnose the root cause fast — dirty filters, low refrigerant, dirty coils, thermostat or compressor issues.",
 h1="AC not cooling? We'll find the problem <span class=\"accent\">fast.</span>",
 lede="When your AC is running but your home stays warm, something isn't working as it should. We diagnose the root cause and restore reliable cooling so your system performs the way it should.",
 sk="Signs Your AC Isn't Cooling", sh="What you're<br>noticing",
 signs=["Warm air coming from the vents","Indoor temperature won't reach the thermostat setting","Weak or inconsistent airflow","AC runs constantly without cooling the home","Hot and cold spots throughout the house","Higher-than-normal energy bills"],
 img='service-gauges.jpg', alt='Diagnosing a cooling failure', tag='Root-cause diagnostics',
 ck="What Causes It", ch="Five reasons an AC<br>stops cooling",
 causes=[("Dirty air filter","A clogged filter restricts airflow, making it harder for your system to circulate cool air."),
  ("Low refrigerant or a leak","Without the proper refrigerant charge, your AC can't remove heat from your home effectively."),
  ("Dirty condenser coil","Dirt and debris on the outdoor unit prevent heat from escaping, reducing cooling performance."),
  ("Thermostat or electrical issue","Incorrect thermostat operation or a failing electrical component can prevent your system from cooling properly."),
  ("A failing compressor","The compressor is the heart of your AC. When it begins to fail, cooling performance drops or stops completely.")],
 fk="How We Fix It", flow=["Inspect the System","Check Airflow","Test Refrigerant","Repair the Issue","Test & Verify"]),

dict(slug='frozen-coil', sibs=REPAIR, crumb=CB_R+['Frozen Coil'],
 title="Frozen AC Coil Repair | Wahl Air Conditioning", desc="Ice on your evaporator coil means your system is fighting itself. We diagnose the real cause and fix it before it damages your compressor.",
 h1="Frozen coil? We find the cause and <span class=\"accent\">fix it right.</span>",
 lede="Ice on your evaporator coil means your system is fighting itself. We diagnose the real reason it's freezing — and fix it before it damages your compressor.",
 sk="Signs Your Coil Is Frozen", sh="What you're<br>noticing",
 signs=["Ice or frost on the refrigerant lines","Water pooling around the air handler","Higher-than-usual energy bills","Warm or weak air from the vents","Runs constantly, never hits the set temp","Hissing or bubbling near the unit"],
 img='service-coil-clean.jpg', alt='Coil service', tag='Fixed before compressor damage',
 ck="What Causes It", ch="Five reasons a coil<br>freezes up",
 causes=[("Restricted airflow","A dirty filter, closed registers, or a blocked return starves the coil of warm air."),
  ("Low refrigerant or a leak","Low charge drops coil pressure and temperature until ice builds up."),
  ("A dirty evaporator coil","Grime insulates the coil so it can't absorb heat from your home's air."),
  ("A failing blower motor","Weak airflow from a worn blower lets the coil drop below freezing."),
  ("Running it when it's too cool out","Cooling on a cool desert night can push the coil past freezing.")],
 fk="How We Fix It", flow=["Thaw & Inspect","Airflow Check","Leak Test","Clean / Repair","Test & Verify"]),

dict(slug='breaker-tripping', sibs=REPAIR, crumb=CB_R+['Breaker Tripping'],
 title="AC Breaker Keeps Tripping | Wahl Air Conditioning", desc="If your AC keeps tripping the breaker, something is overloading the circuit. We diagnose it safely and make the repair.",
 h1="Breaker keeps tripping? We'll find it <span class=\"accent\">safely.</span>",
 lede="If your AC keeps tripping the breaker, it's a sign that something is overloading the electrical system. We diagnose the underlying issue and make the necessary repairs to restore safe, reliable operation.",
 sk="Signs Your AC Is Tripping the Breaker", sh="What you're<br>noticing",
 signs=["Breaker trips whenever the AC starts","System shuts off unexpectedly during operation","Outdoor unit won't stay running","Breaker won't reset or trips repeatedly","Burning smell near the unit or electrical panel","Cooling stops without warning"],
 img='owner-service-call.jpg', alt='Electrical diagnostics at the condenser', tag='Safe electrical diagnostics',
 ck="What Causes It", ch="Five reasons a breaker<br>keeps tripping",
 causes=[("Dirty condenser coil","A clogged outdoor coil forces the system to work harder, increasing electrical demand and causing the breaker to trip."),
  ("Failing capacitor","A weak or damaged capacitor makes it difficult for the compressor or fan motor to start, drawing excessive current."),
  ("Compressor problems","A failing or locked compressor can overload the circuit and repeatedly trip the breaker."),
  ("Damaged wiring or connections","Loose, worn, or shorted wiring can create unsafe electrical conditions that trigger the breaker."),
  ("Faulty fan motor","An overworked or failing indoor or outdoor fan motor can draw more power than the circuit is designed to handle.")],
 fk="How We Fix It", flow=["Electrical Inspection","Test Components","Repair the Fault","Replace Failed Parts","Test & Verify"]),

dict(slug='strange-noises', sibs=REPAIR, crumb=CB_R+['Strange Noises'],
 title="Strange AC Noises? | Wahl Air Conditioning", desc="Banging, buzzing, squealing or grinding from your AC is an early warning. We find the source and repair it before it becomes a breakdown.",
 h1="Strange noises? We'll find the source and <span class=\"accent\">fix it.</span>",
 lede="Unusual sounds are often an early warning that something inside your AC needs attention. We identify the source of the noise and make the necessary repairs before a small problem turns into a major breakdown.",
 sk="Signs Your AC Needs Attention", sh="What you're<br>hearing",
 signs=["Banging or clanking sounds during operation","Buzzing or humming that wasn't there before","Squealing or screeching when the system starts","Rattling from the indoor or outdoor unit","Clicking that continues after startup","Grinding or scraping noises while running"],
 img='service-furnace.jpg', alt='Component inspection', tag='Caught before breakdown',
 ck="What Causes It", ch="Five sources of<br>unusual noise",
 causes=[("Loose or damaged parts","Screws, panels, or internal components can vibrate or rattle as the system operates."),
  ("Worn blower motor or fan","Failing bearings or damaged fan blades can create squealing, grinding, or scraping noises."),
  ("Failing compressor","A compressor nearing the end of its life may produce loud buzzing, knocking, or clanking sounds."),
  ("Debris in the outdoor unit","Leaves, twigs, or other debris can strike the fan blades and create rattling or clicking noises."),
  ("Electrical component issues","A failing contactor, capacitor, or relay can cause persistent buzzing or repeated clicking.")],
 fk="How We Fix It", flow=["Locate the Noise","Inspect Components","Repair or Tighten Parts","Replace Worn Components","Test & Verify"]),

dict(slug='new-system-installs', sibs=INSTALL, crumb=CB_I+['New System Installs'],
 title="New AC System Installation | Wahl Air Conditioning", desc="New AC installation done right from day one — proper sizing, ductwork inspection, professional install, startup and calibration.",
 h1="New system installation, done right from <span class=\"accent\">day one.</span>",
 lede="A properly installed air conditioning system is key to long-term comfort, efficiency, and reliability. We help you choose the right system for your home and install it with precision so it performs exactly as it should.",
 sk="Signs You May Need a New System", sh="When replacement<br>beats repair",
 signs=["AC is more than 10–15 years old","Frequent and costly repairs","Rising energy bills despite normal use","Uneven cooling throughout the home","System struggles to keep up on hot days","Uses outdated or discontinued refrigerant"],
 img='install-crane-set.jpg', alt='New system installation', tag='Carrier 12-month guarantee',
 ck="What Goes Into It", ch="Five stages of<br>a proper install",
 causes=[("Proper system sizing","We calculate the correct capacity for your home to ensure balanced cooling and efficiency."),
  ("Old system removal","We safely disconnect and remove your existing unit and components."),
  ("Ductwork inspection","We check existing ductwork for leaks, restrictions, or design issues that affect performance."),
  ("Professional installation","We install the new indoor and outdoor units according to manufacturer specifications."),
  ("Startup & calibration","We test, charge, and fine-tune the system for optimal performance and efficiency.")],
 fk="How We Install", flow=["Home Evaluation","System Selection","Removal of Old Equipment","Installation","Test & Verify"],
 note="Call us now or request a free estimate online. We serve Peoria, Glendale, Surprise, Sun City, and Phoenix."),

dict(slug='system-sizing', sibs=INSTALL, crumb=CB_I+['System Sizing'],
 title="AC System Sizing & Load Calculations | Wahl Air Conditioning", desc="Detailed load calculations so your new AC is neither too big nor too small — the foundation of an efficient, reliable system.",
 h1="The right size system for maximum <span class=\"accent\">comfort.</span>",
 lede="Proper system sizing is the foundation of a reliable and efficient air conditioning system. We perform detailed load calculations to ensure your new AC is neither too big nor too small — just right for your home.",
 sk="Signs Your AC May Be the Wrong Size", sh="What the wrong size<br>feels like",
 signs=["Uneven temperatures between rooms","AC short cycles (turns on and off frequently)","System runs constantly without reaching set temperature","High humidity indoors","Excessively high energy bills","Weak comfort despite a newer system"],
 img='install-new-pad.jpg', alt='Properly sized system installed', tag='Load-calculated, not guessed',
 ck="What Affects Sizing", ch="Five factors in<br>a load calculation",
 causes=[("Home square footage","The overall size of your home is the starting point for determining cooling capacity."),
  ("Insulation levels","Poor insulation increases heat gain and requires a larger capacity system."),
  ("Window size and sun exposure","Large windows and direct sunlight increase cooling demand significantly."),
  ("Ceiling height and layout","Open spaces and high ceilings change how air circulates through your home."),
  ("Ductwork condition","Leaks, restrictions, or poor design can affect airflow and system performance.")],
 fk="How We Size It", flow=["Home Assessment","Load Calculation","Evaluate Existing Ductwork","System Recommendation","Confirm & Plan Installation"],
 note="Call us now or request a free estimate online. We serve Peoria, Glendale, Surprise, Sun City, and Phoenix."),

dict(slug='energy-savings', sibs=INSTALL, crumb=CB_I+['Energy Savings'],
 title="HVAC Energy Savings | Wahl Air Conditioning", desc="Lower your energy bills without sacrificing comfort — we identify inefficiencies and optimize your system's performance.",
 h1="Lower bills without sacrificing <span class=\"accent\">comfort.</span>",
 lede="Improving your system's efficiency can significantly reduce monthly energy costs while keeping your home comfortable. We identify opportunities in your HVAC system and optimize performance so you get more cooling for less energy.",
 sk="Signs Your System Is Wasting Energy", sh="Where the money<br>is going",
 signs=["Higher-than-usual electricity bills","AC runs longer than normal to cool the home","Uneven or inconsistent temperatures","System frequently turning on and off","Weak airflow from vents","Home struggles to stay cool during peak heat"],
 img='service-heatpump.jpg', alt='Energy-efficient system', tag='More cooling, less energy',
 ck="What Impacts Efficiency", ch="Five drivers of<br>energy waste",
 causes=[("System age and condition","Older or poorly maintained systems naturally consume more energy to deliver less cooling."),
  ("Dirty filters and coils","Restricted airflow forces the system to work harder, increasing energy use."),
  ("Incorrect system sizing","Oversized or undersized units reduce efficiency and increase operating costs."),
  ("Poor insulation or duct leaks","Conditioned air loss makes your system run longer than necessary."),
  ("Outdated components","Worn capacitors, motors, or controls reduce system efficiency over time.")],
 fk="How We Improve It", flow=["System Evaluation","Performance Testing","Identify Energy Loss Points","Optimize or Repair Components","Test & Verify"],
 note="Call us now or request a free estimate online. We serve Peoria, Glendale, Surprise, Sun City, and Phoenix."),

dict(slug='seasonal-inspections', sibs=MAINT, crumb=CB_M+['Seasonal Inspections'],
 title="Seasonal AC Inspections | Wahl Air Conditioning", desc="Seasonal inspections catch small issues before they become costly repairs — filters, coils, refrigerant, electrical, full system test.",
 h1="Seasonal inspections that keep your system <span class=\"accent\">running.</span>",
 lede="Regular seasonal inspections help catch small issues before they turn into costly repairs. We check, clean, and test your system to make sure it's ready for peak cooling performance when you need it most.",
 sk="Signs You Need an Inspection", sh="When to book<br>a check",
 signs=["Reduced cooling performance compared to last season","Rising energy bills without increased usage","Weak or inconsistent airflow","Strange smells when the AC starts","Unusual noises during operation","System hasn't been serviced in over a year"],
 img='service-gauges.jpg', alt='Seasonal system inspection', tag='Before peak season',
 ck="What We Check", ch="Five checks in every<br>seasonal inspection",
 causes=[("Air filter and airflow","We inspect and evaluate airflow restrictions that can reduce efficiency and comfort."),
  ("Coils and condenser unit","We check for dirt buildup and debris that can impact heat transfer and performance."),
  ("Refrigerant levels","We verify proper charge to ensure efficient and reliable cooling."),
  ("Electrical components","We test capacitors, contactors, wiring, and safety controls for proper operation."),
  ("Overall system performance","We run a full system test to confirm everything is operating safely and efficiently.")],
 fk="How It Works", flow=["Schedule Service","Full Inspection","Clean & Test","Report Findings","Recommendations"],
 note="Call us now or request a free estimate online. We serve Peoria, Glendale, Surprise, Sun City, and Phoenix."),

dict(slug='coil-cleaning', sibs=MAINT, crumb=CB_M+['Coil Cleaning'],
 title="AC Coil Cleaning | Wahl Air Conditioning", desc="Professional evaporator and condenser coil cleaning to restore heat transfer, improve performance and prevent system strain.",
 h1="Coil cleaning for better cooling and <span class=\"accent\">efficiency.</span>",
 lede="Dirty evaporator and condenser coils reduce your AC's ability to cool your home efficiently. We thoroughly clean your coils to restore proper heat transfer, improve performance, and help prevent system strain and breakdowns.",
 sk="Signs Your Coils Need Cleaning", sh="What dirty coils<br>look like",
 signs=["Reduced cooling performance","Higher-than-usual energy bills","AC runs longer than normal","Warm air from vents despite running system","System struggles during peak heat","Ice or frost forming on components"],
 img='service-coil-clean.jpg', alt='Professional coil cleaning', tag='Restored heat transfer',
 ck="Why It Matters", ch="Five things dirty<br>coils cost you",
 causes=[("Reduced heat transfer","Dirt buildup acts as insulation, preventing coils from absorbing and releasing heat effectively."),
  ("Increased energy usage","A dirty system works harder to achieve the same cooling, raising energy consumption."),
  ("System strain","Restricted performance puts extra stress on the compressor and other key components."),
  ("Poor indoor comfort","Reduced efficiency leads to uneven temperatures and longer cooling cycles."),
  ("Higher risk of breakdowns","Neglected coils can contribute to overheating and premature system failure.")],
 fk="How We Clean", flow=["System Inspection","Power Down & Access","Coil Cleaning","Rinse & Clear Drainage","Test & Verify"],
 note="Call us now or request a free estimate online. We serve Peoria, Glendale, Surprise, Sun City, and Phoenix."),

dict(slug='performance-checks', sibs=MAINT, crumb=CB_M+['Performance Checks'],
 title="AC Performance Checks | Wahl Air Conditioning", desc="We test airflow, temperature output, refrigerant operation and electrical performance to catch hidden issues before they become breakdowns.",
 h1="Performance checks that keep your system at its <span class=\"accent\">best.</span>",
 lede="A performance check ensures your air conditioning system is operating efficiently, safely, and at full capacity. We test key components and system output to catch hidden issues before they turn into breakdowns.",
 sk="Signs You Need a Performance Check", sh="When output<br>slips",
 signs=["AC is running but cooling feels weaker than usual","Rising energy bills without changes in usage","System runs longer cycles to cool the home","Uneven temperatures between rooms","AC struggles during hot afternoons","No recent professional system evaluation"],
 img='service-gauges.jpg', alt='Measuring system performance', tag='Measured, not guessed',
 ck="What We Evaluate", ch="Five measurements<br>in every check",
 causes=[("Airflow performance","We measure airflow to ensure your system is moving air properly through your home."),
  ("Temperature output","We check supply and return air temperatures to confirm proper cooling performance."),
  ("Refrigerant operation","We evaluate system pressures and performance to ensure correct cooling efficiency."),
  ("Electrical performance","We test capacitors, motors, and controls for proper and safe operation."),
  ("Overall system efficiency","We assess how effectively your system is cooling relative to energy use.")],
 fk="How It Works", flow=["Schedule Service","Measure Airflow","Test Output","Check Electrical","Report & Recommend"],
 note="Call us now or request a free estimate online. We serve Peoria, Glendale, Surprise, Sun City, and Phoenix."),

dict(slug='repair', sibs=HP, crumb=CB_H+['Repair'],
 title="Heat Pump Repair | Wahl Air Conditioning", desc="Heat pump repair you can rely on — refrigerant, electrical, reversing valve, airflow and compressor issues diagnosed and fixed.",
 h1="Heat pump repair you can <span class=\"accent\">rely on.</span>",
 lede="When your heat pump stops working properly, it affects both heating and cooling comfort. We quickly diagnose the issue and perform precise repairs to restore efficient, reliable operation year-round.",
 sk="Signs Your Heat Pump Needs Repair", sh="What you're<br>noticing",
 signs=["System not heating or cooling properly","Heat pump running but not changing indoor temperature","Frequent cycling on and off","Weak airflow from vents","Strange noises during operation","Higher energy bills without increased usage"],
 img='service-heatpump.jpg', alt='Heat pump repair', tag='Both seasons covered',
 ck="What Causes It", ch="Five common heat<br>pump failures",
 causes=[("Refrigerant problems","Low refrigerant or leaks reduce the system's ability to transfer heat effectively."),
  ("Electrical or control failures","Faulty capacitors, contactors, or control boards can prevent proper operation."),
  ("Reversing valve issues","A malfunctioning reversing valve can stop the system from switching between heating and cooling modes."),
  ("Airflow restrictions","Dirty filters, blocked coils, or duct issues can significantly reduce performance."),
  ("Compressor or motor wear","Aging components can lead to reduced efficiency or complete system failure.")],
 fk="How We Fix It", flow=["Inspect the System","Test Components","Diagnose the Fault","Repair or Replace","Test & Verify"]),

dict(slug='replacement', sibs=HP, crumb=CB_H+['Replacement'],
 title="Heat Pump Replacement | Wahl Air Conditioning", desc="Heat pump replacement for better comfort and efficiency — evaluation, proper sizing, safe removal, professional install and calibration.",
 h1="Heat pump replacement for better comfort and <span class=\"accent\">efficiency.</span>",
 lede="When your heat pump is no longer reliable or cost-effective to repair, a full replacement can restore consistent comfort and significantly improve energy efficiency. We help you choose the right system and install it with precision.",
 sk="Signs You Need a Replacement", sh="When repair stops<br>paying off",
 signs=["System is 10–15+ years old","Frequent breakdowns and costly repairs","Inconsistent heating or cooling performance","Rising energy bills despite normal usage","System struggles in extreme temperatures","Uses outdated or discontinued refrigerant"],
 img='install-new-pad.jpg', alt='New heat pump installed', tag='Sized and calibrated',
 ck="What Goes Into It", ch="Five stages of<br>a replacement",
 causes=[("System evaluation","We assess your current setup to determine the right replacement options for your home."),
  ("Proper system sizing","We calculate the correct capacity to ensure balanced comfort and efficiency year-round."),
  ("Safe removal of old unit","We disconnect and remove the existing heat pump and related components."),
  ("Professional installation","We install the new indoor and outdoor units according to manufacturer specifications."),
  ("Startup & calibration","We test, charge, and fine-tune the system for optimal performance.")],
 fk="How We Replace It", flow=["System Evaluation","Select the Right Unit","Remove Old Equipment","Professional Install","Test & Verify"]),

dict(slug='maintenance', sibs=HP, crumb=CB_H+['Maintenance'],
 title="Heat Pump Maintenance | Wahl Air Conditioning", desc="Heat pump maintenance to prevent breakdowns, improve performance and extend system life — both heating and cooling seasons.",
 h1="Heat pump maintenance, <span class=\"accent\">year-round.</span>",
 lede="Regular maintenance is key to keeping your heat pump efficient, reliable, and ready for both heating and cooling seasons. We service your system to prevent breakdowns, improve performance, and extend its lifespan.",
 sk="Signs Your Heat Pump Needs Service", sh="When to book<br>maintenance",
 signs=["Reduced heating or cooling performance","Higher energy bills than usual","System runs longer to reach set temperature","Weak or inconsistent airflow","Unusual noises during operation","It's been over a year since last service"],
 img='service-coil-clean.jpg', alt='Heat pump maintenance', tag='Ready both seasons',
 ck="What We Check", ch="Five checks in every<br>maintenance visit",
 causes=[("Airflow system","We inspect filters, vents, and airflow paths to ensure proper circulation."),
  ("Indoor and outdoor coils","We check for dirt and buildup that can reduce efficiency."),
  ("Refrigerant levels","We verify correct charge for optimal heating and cooling performance."),
  ("Electrical components","We test capacitors, contactors, wiring, and safety controls."),
  ("Reversing valve and operation","We ensure smooth switching between heating and cooling modes.")],
 fk="How It Works", flow=["System Inspection","Clean Components","Verify Refrigerant","Test Electrical","Confirm Operation"]),
]
for p in P: page(p)

# ── FINANCING (unique layout: GreenSky plans) ──
PLANS=[("6 Months No Interest","Plan 4069","No Interest if Paid in Full in 6 Months, with Payments Required. Fixed rate of 9.99% APR.","For every $1,000 financed at 9.99% APR, 108 monthly payments of $14.07.","Interest is billed but waived if paid in full before the 6 month promo period expires. Monthly payments required during promo period.","POPULAR"),
 ("15 Months No Interest","Plan 4158","No Interest if Paid in Full in 15 Months, with Payments Required. Rates range from 17.99%–24.99% APR based on creditworthiness.","For every $1,000 financed at 24.99% APR, 84 monthly payments of $25.30.","Interest is billed but waived if paid in full before the 15 month promo period expires. Monthly payments required during promo period.",None),
 ("120 Months Fixed Rate","Plan 9992 &middot; 7.99%–19.99% APR","Fixed rate financing for 120 months. Rates from 7.99%–19.99% APR based on income and creditworthiness. Only well-qualified applicants receive the lowest rate.","For every $1,000 financed at 19.99% APR, 120 monthly payments of $19.32.","",None),
 ("120 Months Fixed Rate","Plan 9991 &middot; 9.99%–22.99% APR","Fixed rate financing for 120 months. Rates from 9.99%–22.99% APR based on income and creditworthiness. Only well-qualified applicants receive the lowest rate.","For every $1,000 financed at 22.99% APR, 120 monthly payments of $21.35.","",None)]
cards=''.join('<div class="fin reveal">%s<h3>%s</h3><span class="plan">%s</span><p>%s</p>'
  '<div class="ex"><b>Example:</b> %s</div>%s</div>'
  % (('<span class="tag">%s</span>'%tag) if tag else '', title, plan, desc, ex,
     ('<p style="font-size:.78rem">%s</p>'%fine) if fine else '')
  for title,plan,desc,ex,fine,tag in PLANS)
sibs=''.join('<a class="sib%s" href="/%s/">%s</a>' % (' on' if s[0]=='financing' else '', s[0], s[1]) for s in INSTALL)
crumb=' <i>›</i> '.join(('<a href="%s">%s</a>'%c if isinstance(c,tuple) else c) for c in CB_I+['Financing'])
b=('<section class="p-hero"><div class="wrap"><nav class="crumb">%s</nav>'
 '<h1 class="reveal in">Don\'t let cost stand in the way of <span class="accent">comfort.</span></h1>'
 '<p class="lede reveal in">We offer flexible financing options to make your new AC system or major repair affordable. '
 'We partner with GreenSky&reg; to offer multiple financing plans — choose the option that works best for your budget.</p>'
 '<div class="hero-ctas reveal in">'
 '<a class="btn btn-solid" href="/contact/"><span class="mag">Request a Free Estimate %s</span></a>'
 '<a class="btn btn-ghost" href="tel:+16022422353"><span class="mag">Call (602) 242-2353</span></a></div>'
 '<div class="sibs reveal in">%s</div></div></section>' % (crumb, AR, sibs))
b+=('<section class="section"><div class="wrap">'
 '<div class="section-head reveal"><span class="kicker">Flexible Financing Options</span>'
 '<h2 class="h2">Four plans.<br>Pick your <span class="accent">budget.</span></h2></div>'
 '<div class="fin-grid">%s</div>'
 '<p class="fin-legal reveal">Subject to credit approval. These examples are estimates based on amount and timing of purchases. '
 'Call 866-936-0602 for financing costs and terms. Loans for the GreenSky&reg; consumer loan program are offered and made by '
 'federally insured, federal or state chartered financial institutions providing credit without regard to age, race, color, '
 'national origin, gender, disability, or familial status. A list of financial institutions currently providing loans through '
 'the GreenSky&reg; Program is available at greensky.com/bank-partners. GreenSky Servicing, LLC services the loans on behalf of '
 'your lender, NMLS #1416362. GreenSky&reg; is a registered trademark of GreenSky, LLC and is licensed to banks and other '
 'financial institutions for their use in connection with consumer loan programs. GreenSky, LLC and GreenSky Servicing, LLC are '
 'lenders. All credit decisions and loan terms are determined by program lenders.</p></div></section>' % cards)
b+=('<section class="section hairline"><div class="wrap"><div class="split">'
 '<div class="reveal"><span class="kicker">Why Finance</span>'
 '<h2 class="h2" style="margin:.7rem 0 1.1rem">Comfort now,<br>paid over <span class="accent">time.</span></h2>'
 '<p class="lede" style="font-size:1rem">Financing your AC system gives you the flexibility to upgrade your comfort without '
 'the stress of a large upfront expense. Whether you need a full system replacement, emergency repair, or a new high-efficiency '
 'installation, financing allows you to get the service you need now while making manageable monthly payments over time.</p>'
 '<ul class="check" style="margin-top:1.2rem"><li>No large upfront expense</li><li>Manageable monthly payments</li>'
 '<li>Available for qualifying repairs</li><li>Available for full system replacement</li>'
 '<li>Promotional no-interest periods</li><li>Apply before the work begins</li></ul></div>'
 '<div class="split-media reveal" data-d="1" data-slot-wrap>'
 '<img src="/assets/img/carrier-unit.jpg" alt="New system installed by Wahl Air" data-slot>'
 '<span class="tagchip"><i></i>Financing available</span></div></div></div></section>')
b+=('<section class="cta"><div class="wrap cta-inner">'
 '<div class="reveal"><span class="kicker">Ready to Schedule?</span>'
 '<h2 class="h2" style="margin-top:.7rem">Let\'s get your air <span class="accent">handled.</span></h2></div>'
 '<div class="cta-actions reveal" data-d="1">'
 '<a class="btn btn-solid" href="/contact/"><span class="mag">Request Service Online %s</span></a>'
 '<span class="tiny" style="margin-top:.6rem">Or call us right now</span>'
 '<a class="cta-tel" href="tel:+16022422353">(602) 242-2353</a></div></div></section>' % AR)
d=os.path.join(ROOT,'financing'); os.makedirs(d,exist_ok=True)
open(os.path.join(d,'index.html'),'w').write(
 HEAD.format(title='AC Financing Options | Wahl Air Conditioning',
   desc='Flexible GreenSky financing for a new AC system or major repair — no-interest promo plans and fixed-rate options.')
 +CHROME+b+FOOTER+TAIL)
print('built /financing/')
print('SUBPAGES DONE')
