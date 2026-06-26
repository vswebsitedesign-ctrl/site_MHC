#!/usr/bin/env python3
import json, os, shutil, sys, hashlib

def build():
    # Related Services index — built once from real pages.json relationships, not guessed URL patterns
    by_town_index = {}

    pages_path = 'data/pages.json'
    if not os.path.exists(pages_path):
        print("ERROR: pages.json not found")
        sys.exit(1)
    with open(pages_path, 'r') as f:
        pages = json.load(f)
    with open('theme/base.html', 'r') as f:
        template = f.read()
    for _p in pages:
        _svc = _p.get('service_title', '')
        _town = _p.get('town_name', '')
        _slug = _p.get('slug', '')
        if _svc and _town and _slug:
            by_town_index.setdefault(_town, []).append((_svc, _slug))

    if os.path.exists('build'):
        shutil.rmtree('build')
    os.makedirs('build')
    BUILD_EXCLUDE = ['README']
    for page in pages:
        slug = page['slug']
        if slug in BUILD_EXCLUDE:
            continue
        title = page.get('title', '')
        meta_description = page.get('meta_description') or page.get('description', '')
        content = page.get('body_content', '')
        # Rich content generation — overrides legacy body_content for enriched location pages
        _town = page.get('town_name', '')
        _service = page.get('service_title', '')
        _intro = page.get('location_intro', '')
        _era = page.get('property_era', '')
        _landmark = page.get('landmark', '')
        _nearby = page.get('nearby_areas', [])
        _p1 = page.get('service_paragraph_1', '')
        _p2 = page.get('service_paragraph_2', '')
        _p3 = page.get('service_paragraph_3', '')
        if _town and _service and (_intro or _p1):
            _nearby_links = ''
            if _nearby:
                _nearby_links = '<p class="nearby-areas"><strong>Also serving:</strong> ' + ', '.join(_nearby) + '</p>'
            _era_html = '<p class="property-era"><strong>Local property types:</strong> ' + _era + '</p>' if _era else ''
            content = (
                '<section class="service-body">'
                '<h2>' + _service + ' in ' + _town + (' — ' + page.get('town_postcode','') if page.get('town_postcode') else '') + '</h2>'
                + ('<p class="location-intro">' + _intro + '</p>' if _intro else '')
                + _era_html
                + ('<p>' + _p1 + '</p>' if _p1 else '')
                + ('<p>' + _p2 + '</p>' if _p2 else '')
                + ('<p>' + _p3 + '</p>' if _p3 else '')
                + _nearby_links
                + '<div class="loc-prop-services__btns"><a href="tel:07347300798" class="btn-primary">Ring Mike: 07347300798</a><a href="/contact-us/" class="btn-primary">Free Quote</a></div>'
                '</section>'
            )


        # Title + meta_description generation (rotating patterns for SEO uniqueness)
        service_title_tm = page.get('service_title', '')
        town_name_tm = page.get('town_name', '')
        if service_title_tm and town_name_tm:
            title_patterns = [
                service_title_tm + chr(32) + chr(8211) + chr(32) + town_name_tm,
                town_name_tm + ' ' + service_title_tm,
                service_title_tm + ' | ' + town_name_tm,
            ]
            meta_patterns = [
                'Need ' + service_title_tm + ' in ' + town_name_tm + '? Mike' + chr(39) + 's House Clearance offers fast, fully insured local service. Free, no-obligation quotes.',
                'Professional ' + service_title_tm + ' in ' + town_name_tm + '. Licensed waste carrier, fully insured, trusted locally. Call Mike for a free quote.',
            ]
            title_idx = int(hashlib.md5((slug + '-title').encode()).hexdigest(), 16) % len(title_patterns)
            meta_idx = int(hashlib.md5((slug + '-meta').encode()).hexdigest(), 16) % len(meta_patterns)
            title = title_patterns[title_idx]
            meta_description = meta_patterns[meta_idx]

        # Hero generation (rotating H1 patterns for SEO uniqueness)
        service_title_h = page.get('service_title', '')
        town_name_h = page.get('town_name', '')
        town_county_h = page.get('town_county', '')
        hero = ''
        if service_title_h and town_name_h:
            h1_patterns = []
            if town_county_h:
                h1_patterns.append(service_title_h + ' in ' + town_name_h + ', ' + town_county_h)
            else:
                h1_patterns.append(service_title_h + ' in ' + town_name_h)
            h1_patterns.append('Professional ' + service_title_h + chr(32) + chr(8212) + chr(32) + town_name_h)
            h1_patterns.append(town_name_h + ' ' + service_title_h + ' Services')
            if town_county_h:
                h1_patterns.append('Need ' + service_title_h + ' in ' + town_name_h + '? We Cover ' + town_county_h + '.')
            else:
                h1_patterns.append('Need ' + service_title_h + ' in ' + town_name_h + '?')
            pattern_index = int(hashlib.md5(slug.encode()).hexdigest(), 16) % len(h1_patterns)
            hero_h1 = h1_patterns[pattern_index]
            hero = (
                '<section class="hero-banner" aria-label="Hero">'
                '<div class="hero-inner">'
                '<h1>' + hero_h1 + '</h1>'
                '<p class="hero-tagline"><strong>Don' + chr(39) + 't Worry! Mike Will Sort it Out!</strong></p>'
                '<div class="hero-cta-buttons">'
                '<a href="/contact-us/" class="btn btn-outline">Contact Mike</a>'
                '<a href="tel:07347300798" class="btn btn-outline" aria-label="Ring Mike on 07347300798">Ring Mike</a>'
                '</div></div></section>'
            )
        # FAQ generation (rotating Q&A patterns for SEO uniqueness, reused from homepage FAQ content)
        service_title_faq = page.get('service_title', '')
        town_name_faq = page.get('town_name', '')
        town_county_faq = page.get('town_county', '')
        faq = ''
        faq_schema = ''
        if service_title_faq and town_name_faq:
            area_faq = town_name_faq + ', ' + town_county_faq if town_county_faq else town_name_faq
            q1_variants = [
                'Are you fully licensed for ' + service_title_faq + ' in ' + town_name_faq + '?',
                'Is your ' + town_name_faq + ' team fully licensed?',
            ]
            a1_variants = [
                'Absolutely. We are an Environment Agency Licensed Waste Carrier and fully insured for all residential and commercial work in ' + area_faq + '.',
                'Yes. We' + chr(39) + 're an Environment Agency Licensed Waste Carrier, fully insured for every job we take on across ' + area_faq + '.',
            ]
            q2_variants = [
                'Do I need to be at the property during the ' + service_title_faq + '?',
                'Can you carry out ' + service_title_faq + ' in ' + town_name_faq + ' if I' + chr(39) + 'm not there?',
            ]
            a2_variants = [
                'No. We regularly work with solicitors, estate agents, and landlords in ' + area_faq + '. We can collect keys and provide before and after photos.',
                'No problem. We work closely with solicitors, estate agents, and landlords across ' + area_faq + ', and can collect keys and send before and after photos.',
            ]
            q3_variants = [
                'How much does ' + service_title_faq + ' cost in ' + town_name_faq + '?',
                'What' + chr(39) + 's the cost of ' + service_title_faq + ' in ' + town_name_faq + '?',
            ]
            a3_variants = [
                'Every ' + service_title_faq + ' job in ' + area_faq + ' is unique. We provide free local site visits to give you an exact price with no hidden fees or add-ons later.',
                'It depends on the job. We offer free, no-obligation quotes for ' + service_title_faq + ' in ' + area_faq + ', with no hidden fees added later.',
            ]
            i1 = int(hashlib.md5((slug + '-faq1').encode()).hexdigest(), 16) % len(q1_variants)
            i2 = int(hashlib.md5((slug + '-faq2').encode()).hexdigest(), 16) % len(q2_variants)
            i3 = int(hashlib.md5((slug + '-faq3').encode()).hexdigest(), 16) % len(q3_variants)
            faq_pairs = [
                (q1_variants[i1], a1_variants[i1]),
                (q2_variants[i2], a2_variants[i2]),
                (q3_variants[i3], a3_variants[i3]),
            ]
            faq_cards = ''
            for q_text, a_text in faq_pairs:
                faq_cards += '<div class="faq-card"><h3>' + q_text + '</h3><p>' + a_text + '</p></div>'
            faq = '<section class="faq-section" aria-label="Frequently asked questions"><h2>Common Questions</h2><div class="faq-grid">' + faq_cards + '</div></section>'
            faq_schema_obj = {
                "@context": "https://schema.org",
                "@type": "FAQPage",
                "mainEntity": [
                    {
                        "@type": "Question",
                        "name": q_text,
                        "acceptedAnswer": {"@type": "Answer", "text": a_text}
                    } for q_text, a_text in faq_pairs
                ]
            }
            faq_schema = '<script type="application/ld+json">' + json.dumps(faq_schema_obj, separators=(',', ':')) + '</script>'
        # Related Services index — direct lookup against real sibling pages, no URL string-guessing
        town_name_rs = page.get('town_name', '')
        related_services = ''
        if town_name_rs:
            siblings = [(svc, sl) for svc, sl in by_town_index.get(town_name_rs, []) if sl != slug]
            siblings.sort(key=lambda x: x[0])
            if siblings:
                cards = ''
                for svc_title_rs, sib_slug in siblings:
                    cards += '<li class="mikes-grid-card"><a href="/' + sib_slug + '/">' + svc_title_rs + ' in ' + town_name_rs + '</a></li>'
                related_services = '<section class="related-services" aria-label="Related services"><h2>Related Services in ' + town_name_rs + '</h2><ul class="mikes-grid">' + cards + '</ul></section>'
        # Gallery generation — 1 before/after pair per page, cycled across all pages
        gallery = ''
        if slug != 'index':
            _pairs = [('alley', 'Alley Clearance'), ('bedroom', 'Bedroom Clearance'), ('closet', 'Closet Clearance'), ('furniture', 'Furniture Removal'), ('garage', 'Garage Clearance'), ('garden', 'Garden Clearance'), ('living-room', 'Living Room Clearance'), ('room', 'Room Clearance'), ('rubbish', 'Rubbish Removal'), ('shed', 'Shed Clearance'), ('spare-room', 'Spare Room Clearance'), ('unit', 'Unit Clearance')]
            _idx = int(hashlib.md5((slug + '-gallery').encode()).hexdigest(), 16) % len(_pairs)
            _name, _label = _pairs[_idx]
            gallery = (
                '<section class="gallery-section" aria-label="Before and after photos">'
                '<h2>Before &amp; After</h2>'
                '<p class="gallery-intro">Real jobs, real results &mdash; every property left clean and cleared.</p>'
                '<div class="gallery-grid">'
                '<div class="gallery-card">'
                '<img src="/assets/images/' + _name + '-before.webp" alt="' + _label + ' before" loading="lazy" width="600" height="400">'
                '<span class="gallery-label">Before</span>'
                '</div>'
                '<div class="gallery-card">'
                '<img src="/assets/images/' + _name + '-after.webp" alt="' + _label + ' after" loading="lazy" width="600" height="400">'
                '<span class="gallery-label">After</span>'
                '</div>'
                '</div>'
                '</section>'
            )
        canonical_slug = '' if slug == 'index' else slug + '/'
        # Guard: only inject static sections on real location pages (have town_name + service_title)
        is_location_page = bool(page.get('town_name') and page.get('service_title'))
        location_sections = '''<section class="trust-credentials" aria-label="Trust and credentials"><ul class="trust-credentials-list"><li>Environment Agency Licensed Waste Carrier</li><li>Fully Insured &amp; Professional Team</li><li>5-Star Rated Local Service</li><li>Free, No-Obligation Quotes</li><li>Registered in England &amp; Wales</li></ul><p class="trust-credentials-tagline">Trusted across Devon, Cornwall, and Somerset &mdash; every job handled with care, every item disposed of responsibly.</p></section><section class="process-section" aria-label="How it works"><h2>How It Works</h2><div class="process-grid"><div class="process-card"><div class="process-icon">📷</div><h3>Free Valuation</h3><p>Simply call Mike or send photos via WhatsApp. We provide a fair, transparent estimate within hours.</p></div><div class="process-card"><div class="process-icon">🚚</div><h3>Expert Clearance</h3><p>Our team arrives on time, handles all the heavy lifting, and clears the property with total care and respect.</p></div><div class="process-card"><div class="process-icon">♻️</div><h3>Eco-Finish</h3><p>We leave the property tidy, prioritising charity donations and responsible recycling.</p></div></div></section><section class="whats-included" aria-label="What's included"><h2>What's Included</h2><ul class="whats-included-list"><li>Full or partial property clearance — every room, or just the areas you need</li><li>Single-item and bulk rubbish removal</li><li>Heavy lifting and manual handling — we do the hard work</li><li>Responsible disposal, recycling, and charity donation wherever possible</li><li>Sweeping and tidying after every job — left clean and ready</li><li>No hidden fees — your free quote is the price you pay</li></ul></section><section class="sensitive-clearances" aria-label="Sensitive and specialist clearances"><h2>Sensitive &amp; Specialist Clearances</h2><p>We understand that some clearances come at difficult times — bereavement, probate, or supporting a loved one through hoarding. Mike's House Clearance handles these situations with patience, discretion, and genuine care.</p><ul class="sensitive-clearances-list"><li><strong>Bereavement &amp; Probate</strong> — We work closely with families, solicitors, and executors, often without needing anyone present, to clear a property with dignity and respect.</li><li><strong>Hoarder Clearances</strong> — A judgement-free, compassionate approach. We work at whatever pace feels right, treating every home and its history with care.</li></ul><p>If you're going through a difficult time, please get in touch — we're happy to talk things through before any commitment.</p></section>''' if is_location_page else ''

        # Pricing section — per-service tiers, South West England 2026 market rates
        pricing = ''
        if is_location_page:
            _pr_svc = page.get('service_title', '')
            _pr_town = page.get('town_name', '')
            _pricing_data = {
                'House Clearance': [
                    ('Single Room', '£125', 'One room cleared, bagged, and removed. Ideal for a bedroom, living room, or box room.'),
                    ('Half House', '£325', 'Up to half a property cleared. Perfect for part-clearance ahead of a sale or move.'),
                    ('Full Property', '£550', 'Complete house clearance top to bottom. Every room, every item, left clean and ready.'),
                ],
                'Attic Clearance': [
                    ('Light Attic', '£100', 'A few boxes and loose items. In and out quickly, no fuss.'),
                    ('Packed Attic', '£225', 'A fully loaded loft cleared and carried down. All waste removed and disposed of responsibly.'),
                    ('Full Attic + Boarding', '£375', 'Heavy clearance including old furniture, white goods, or decades of stored items.'),
                ],
                'Bereavement & Probate Clearance': [
                    ('Single Room', '£125', 'One room handled with care and discretion. We work at your pace, no pressure.'),
                    ('Half Property', '£350', 'Partial estate clearance. We liaise directly with solicitors or executors if needed.'),
                    ('Full Estate', '£600', 'Complete probate clearance handled with dignity. Property left clean and ready for sale or handover.'),
                ],
                'Garage & Shed Clearance': [
                    ('Single Shed', '£85', 'Garden shed emptied and contents removed. Recycled or donated wherever possible.'),
                    ('Garage', '£175', 'Full garage clearance including tools, tyres, and bulky items. All disposed of legally.'),
                    ('Garage + Shed', '£295', 'Both cleared in a single visit. Everything removed, space left empty and swept out.'),
                ],
                'Garden Clearance': [
                    ('Light Tidy', '£85', 'Green waste, bags, and loose rubbish removed. Ideal for a seasonal clear-out.'),
                    ('Full Garden', '£195', 'Full garden clearance including furniture, waste, and overgrowth. Left tidy and clear.'),
                    ('Large or Overgrown', '£350', 'Heavily overgrown plots, large volumes of green waste, or gardens with outbuildings included.'),
                ],
                'Hoarder Clearance': [
                    ('Single Room', '£175', 'One room cleared compassionately, at whatever pace feels right. Judgement-free throughout.'),
                    ('Half Property', '£400', 'Partial hoarder clearance across multiple rooms. We work sensitively and at your pace.'),
                    ('Full Property', '£700', 'Complete hoarder clearance handled with care, discretion, and genuine compassion.'),
                ],
                'Home Removals': [
                    ('1-Bed', '£225', 'Full contents of a one-bedroom property moved. Carefully loaded, transported, and unloaded.'),
                    ('2–3 Bed', '£400', 'Family home removal across Devon, Cornwall, and Somerset. Fully insured, no hidden fees.'),
                    ('4-Bed+', '£650', 'Large property removal handled by an experienced team. Everything moved safely and on time.'),
                ],
                'Rubbish Clearance': [
                    ('Single Load', '£85', 'A van load of mixed rubbish collected and disposed of legally. Fast and hassle-free.'),
                    ('Half Van', '£150', 'Half a van of mixed waste cleared from your home or garden. Same-day slots available.'),
                    ('Full Van', '£275', 'A full van of rubbish removed in one visit. All waste taken to licensed disposal facilities.'),
                ],
            }
            _tiers = _pricing_data.get(_pr_svc, _pricing_data['House Clearance'])
            _tier_html = ''
            _tier_classes = ['pricing-card', 'pricing-card pricing-card--featured', 'pricing-card']
            for _i, (_tier_name, _tier_price, _tier_desc) in enumerate(_tiers):
                _tier_html += '<div class="' + _tier_classes[_i] + '"><h3>' + _tier_name + '</h3><p class="pricing-price">From ' + _tier_price + '</p><p>' + _tier_desc + '</p></div>'
            pricing = (
                '<section class="pricing-section" aria-label="Pricing guide">'
                '<h2>' + _pr_svc + ' Prices in ' + _pr_town + '</h2>'
                '<p class="pricing-intro">Every job is different, so we always visit and quote for free. The guide below gives you a realistic idea of what to expect.</p>'
                '<div class="pricing-grid">' + _tier_html + '</div>'
                '<p class="pricing-footnote">Prices vary by volume, access, and location. <a href="/contact-us/">Get your free quote</a> — no hidden fees, ever.</p>'
                '</section>'
            )

        # Recent Local Jobs — per-service hash-rotated job summaries
        recent_jobs = ''
        if is_location_page:
            _rj_town = page.get('town_name', '')
            _rj_svc = page.get('service_title', '')
            _all_job_pools = {
                'House Clearance': [
                    [
                        ('3-bed semi-detached', 'Full contents cleared in a single day. Family delighted with how quickly and carefully everything was handled.'),
                        ('end-of-tenancy terrace', 'Landlord needed a full clear-out between tenants. Completed same week, property left broom-clean.'),
                        ('4-bed detached', 'Pre-sale clearance completed in one visit. Every room emptied and swept out ready for viewings.'),
                    ],
                    [
                        ('Victorian terrace', 'Three generations of belongings cleared respectfully over two days. Nothing left behind.'),
                        ('2-bed bungalow', 'Quick turnaround needed for a probate sale. Cleared and ready for the estate agent within 48 hours.'),
                        ('5-bed farmhouse', 'Large rural property cleared top to bottom. Charity donations arranged for usable furniture.'),
                    ],
                    [
                        ('3-bed semi', 'Family moving abroad needed everything gone fast. Cleared in a single visit, no stress.'),
                        ('end-of-tenancy flat', 'Letting agent called Monday, cleared by Wednesday. Landlord said it was the fastest turnaround they' + chr(39) + 'd had.'),
                        ('detached bungalow', 'Executors instructed us directly. Property cleared and keys handed back to solicitor same day.'),
                    ],
                    [
                        ('4-bed detached', 'Full contents removed ahead of a house sale. Garden outbuildings included at no extra charge.'),
                        ('terraced house', 'Tenant left a full house of belongings. Landlord back on the rental market within the week.'),
                        ('2-bed cottage', 'Remote rural property cleared with care. All waste taken to licensed facilities, nothing fly-tipped.'),
                    ],
                ],
                'Attic Clearance': [
                    [
                        ('packed loft, 3-bed semi', 'Decades of stored items carried down and cleared in a single morning. Customer couldn' + chr(39) + 't believe how fast it went.'),
                        ('loft with old furniture', 'Heavy items including a wardrobe and chest of drawers removed safely. No damage to the hatch or landing.'),
                        ('loft full of boxes', 'Sorted, bagged, and cleared in one visit. Several boxes donated to a local charity shop.'),
                    ],
                    [
                        ('boarded loft, 4-bed', 'Fully boarded loft with years of accumulated items. Cleared top to bottom, boarding left intact.'),
                        ('loft with old white goods', 'Fridge freezer and washing machine removed from loft space. Disposed of via licensed facility.'),
                        ('two lofts, semi-detached', 'Both lofts cleared on the same visit. Customer said it was the best money they' + chr(39) + 'd spent all year.'),
                    ],
                    [
                        ('cluttered loft, bungalow', 'Low headroom made it tricky but the team got everything out without a scratch on the ceilings.'),
                        ('loft full of old tools', 'Tools, paint tins, and old timber cleared and disposed of responsibly. Space completely empty afterwards.'),
                        ('loft conversion prep', 'Full loft clear ahead of a conversion. Builder said it was ready to go when they arrived.'),
                    ],
                    [
                        ('packed loft, Victorian terrace', 'Narrow hatch, steep stairs, and a loft rammed full. Cleared safely in under three hours.'),
                        ('loft with old carpets and boards', 'Old carpets and underlay removed along with general stored items. Skipped on site.'),
                        ('holiday let loft', 'End-of-season clearance for a holiday property owner. Loft empty and ready for off-season storage.'),
                    ],
                ],
                'Bereavement & Probate Clearance': [
                    [
                        ('3-bed semi, probate', 'Worked directly with the family solicitor. Property cleared with care and handed back on schedule.'),
                        ('bungalow, bereavement', 'Family couldn' + chr(39) + 't face doing it themselves. We handled everything with discretion and left the property spotless.'),
                        ('4-bed detached, estate clearance', 'Executors instructed us remotely. Keys collected, property cleared, report sent to solicitor same day.'),
                    ],
                    [
                        ('terraced house, probate', 'Solicitor needed the property cleared before exchange. Completed in one visit, on time.'),
                        ('2-bed flat, bereavement', 'Sensitive clearance handled at the family' + chr(39) + 's pace. Sentimental items set aside carefully before anything was removed.'),
                        ('farmhouse, full estate', 'Large rural estate cleared over two days. Everything documented and disposed of responsibly.'),
                    ],
                    [
                        ('bungalow, sudden bereavement', 'Family called us within days of losing their mother. We were there within the week, no pressure applied.'),
                        ('3-bed semi, executor-led', 'Executor managing from out of area. We liaised directly, sent photos, and cleared without needing anyone present.'),
                        ('cottage, probate', 'Remote property cleared ahead of auction. Estate agent said it was presented better than expected.'),
                    ],
                    [
                        ('detached house, probate', 'Full clearance including outbuildings. Charity donations arranged, remainder disposed of legally.'),
                        ('flat, bereavement', 'Respectful, quiet team. Family said they felt genuinely supported throughout the process.'),
                        ('4-bed house, contested estate', 'Worked carefully under solicitor instruction. Inventory provided before any items were removed.'),
                    ],
                ],
                'Garage & Shed Clearance': [
                    [
                        ('double garage, 4-bed detached', 'Thirty years of tools, tyres, and timber cleared in a morning. Space left completely empty.'),
                        ('garden shed and summerhouse', 'Both structures emptied and contents removed. Old white goods taken to licensed disposal facility.'),
                        ('single garage, terrace', 'Packed floor to ceiling. Cleared in under two hours, everything disposed of responsibly.'),
                    ],
                    [
                        ('garage with old motorbike parts', 'Tools, parts, and scrap metal cleared. Customer said they' + chr(39) + 'd been putting it off for years.'),
                        ('two sheds, rural property', 'Both sheds emptied including old paint tins, pesticides, and garden machinery. All handled correctly.'),
                        ('garage conversion prep', 'Full garage clear ahead of a conversion. Builder arrived to an empty, swept space.'),
                    ],
                    [
                        ('detached garage, bungalow', 'Old furniture, carpet rolls, and boxes cleared in one visit. Nothing left behind.'),
                        ('shed full of garden tools', 'Tools sorted, donated where possible, remainder disposed of legally. Job done in an hour.'),
                        ('garage with old appliances', 'Fridge, freezer, and washing machine removed along with general clutter. Disposed of via licensed facility.'),
                    ],
                    [
                        ('large shed, smallholding', 'Agricultural shed cleared of old equipment and waste. Took a full day but left completely empty.'),
                        ('garage and lean-to', 'Both structures cleared in a single visit. Customer delighted with how much space they' + chr(39) + 'd reclaimed.'),
                        ('shed, end-of-tenancy', 'Tenant left a full shed behind. Landlord had it cleared and property re-let within the week.'),
                    ],
                ],
                'Garden Clearance': [
                    [
                        ('overgrown rear garden, terrace', 'Waist-high grass, brambles, and a collapsed fence panel all cleared. Customer said it transformed the space.'),
                        ('front and rear garden, bungalow', 'Green waste, old furniture, and a broken trampoline removed. Both gardens left tidy and clear.'),
                        ('large garden, detached', 'Full clearance including a rotting shed and years of accumulated green waste. Skipped on site.'),
                    ],
                    [
                        ('neglected garden, rental property', 'Landlord needed it cleared before new tenants moved in. Done in a day, garden left presentable.'),
                        ('garden with old decking', 'Decking lifted and removed along with green waste and old furniture. Space ready for landscaping.'),
                        ('coastal garden, holiday let', 'End-of-season garden clear. Salt-damaged furniture removed, green waste bagged and taken away.'),
                    ],
                    [
                        ('rear garden, Victorian terrace', 'Years of green waste and junk cleared. Neighbour asked for our number before we' + chr(39) + 'd finished.'),
                        ('large rural garden', 'Overgrown plot with old outbuildings cleared over two visits. Disposed of responsibly throughout.'),
                        ('garden and greenhouse', 'Greenhouse emptied and garden cleared in one visit. All waste taken to licensed facilities.'),
                    ],
                    [
                        ('estate garden, probate', 'Large mature garden cleared ahead of property sale. Estate agent said it made a real difference to viewings.'),
                        ('garden with pond clearance', 'Overgrowth around pond cleared and old garden furniture removed. Customer very happy with the result.'),
                        ('front garden, end-of-tenancy', 'Tenant left rubbish bags and old furniture outside. Cleared same day the landlord called.'),
                    ],
                ],
                'Hoarder Clearance': [
                    [
                        ('3-bed semi, single occupant', 'Compassionate clearance carried out over two days at the customer' + chr(39) + 's pace. Judgement-free throughout.'),
                        ('bungalow, referred by social worker', 'Worked alongside a social worker to clear the property safely. Tenant remained in the home throughout.'),
                        ('2-bed flat, council referral', 'Council-referred clearance completed sensitively. Property left safe and habitable.'),
                    ],
                    [
                        ('4-bed house, family-instructed', 'Family instructed us after years of worry. We worked carefully, set aside sentimental items, and cleared the rest.'),
                        ('terraced house, long-term hoarding', 'Floor-to-ceiling in every room. Cleared over three visits with patience and no pressure.'),
                        ('bungalow, elderly resident', 'Elderly customer felt embarrassed. Team put them at ease immediately and worked at their pace throughout.'),
                    ],
                    [
                        ('ground floor flat', 'Narrow hallways and blocked rooms cleared safely. Fire exits cleared first as a priority.'),
                        ('3-bed semi, post-bereavement hoarding', 'Hoarding developed after a bereavement. Handled with genuine compassion and care throughout.'),
                        ('cottage, rural property', 'Remote location with no skip access. Everything bagged and removed by van over two days.'),
                    ],
                    [
                        ('2-bed flat, landlord referral', 'Landlord couldn' + chr(39) + 't enter the property. We cleared it safely and sent a full photo report afterwards.'),
                        ('detached house, self-referral', 'Customer called us themselves. We kept everything confidential and worked discreetly throughout.'),
                        ('bungalow, NHS referral', 'NHS team requested urgent clearance. Property made safe within 48 hours of the call.'),
                    ],
                ],
                'Home Removals': [
                    [
                        ('1-bed flat to 2-bed terrace', 'Local move completed in under four hours. Everything wrapped, loaded, and placed exactly where the customer wanted.'),
                        ('3-bed semi, cross-county move', 'Move from Devon to Somerset completed in a day. Not a scratch on anything.'),
                        ('4-bed detached, downsizing', 'Large family home to a smaller bungalow. Took care of everything including the shed and garage contents.'),
                    ],
                    [
                        ('2-bed flat, student move', 'End-of-term move completed quickly. Customer said it was stress-free from start to finish.'),
                        ('3-bed terrace, chain move', 'Tight completion deadline. We coordinated with both ends of the chain and delivered on time.'),
                        ('5-bed rural farmhouse', 'Large rural move with difficult access. Every item moved safely, nothing left behind.'),
                    ],
                    [
                        ('1-bed flat, elderly customer', 'Careful, patient move for an elderly customer moving closer to family. Furniture arranged exactly as requested.'),
                        ('3-bed semi to new build', 'New build move with snagging concerns. We waited while the customer checked rooms before unloading.'),
                        ('4-bed detached, probate move', 'Estate contents moved into storage ahead of property sale. Fully inventoried on arrival.'),
                    ],
                    [
                        ('2-bed cottage, coastal move', 'Narrow lanes and no parking. We planned the route in advance and got it done without issue.'),
                        ('3-bed semi, last-minute move', 'Customer called Friday, moved Saturday. Full load, no damage, customer delighted.'),
                        ('4-bed house, office contents included', 'Home and home office moved in one visit. IT equipment handled with extra care throughout.'),
                    ],
                ],
                'Rubbish Clearance': [
                    [
                        ('mixed household waste, 3-bed semi', 'Full van of mixed rubbish cleared from garage and garden. Disposed of at a licensed facility same day.'),
                        ('builder' + chr(39) + 's waste, renovation project', 'Rubble, old timber, and plasterboard removed after a kitchen renovation. Site left clear and safe.'),
                        ('end-of-tenancy rubbish', 'Tenant left bags and bulky items throughout the property. Cleared in a single visit.'),
                    ],
                    [
                        ('garage waste, detached house', 'Old tyres, paint tins, and general rubbish removed. All hazardous items disposed of correctly.'),
                        ('garden waste and furniture', 'Broken garden furniture and green waste bags collected and taken away. Job done in an hour.'),
                        ('flat clearance, mixed waste', 'Moving-out rubbish including old appliances and furniture removed quickly and legally.'),
                    ],
                    [
                        ('post-clearance rubbish', 'Bagged waste left after a DIY clearance collected and taken to a licensed tip. No skip needed.'),
                        ('commercial premises, mixed waste', 'Old office equipment and general waste cleared from a small business premises. Waste transfer note provided.'),
                        ('loft waste bags', 'Twenty bags of loft waste carried down and taken away. Customer had been putting it off for months.'),
                    ],
                    [
                        ('kitchen renovation waste', 'Old units, worktops, and appliances removed after a full kitchen refit. Site left spotless.'),
                        ('garden rubbish, large plot', 'Multiple van loads of green waste and junk cleared from a large rural garden. All disposed of responsibly.'),
                        ('mixed waste, rental property', 'Landlord needed a full rubbish clear between tenants. Done same week, property back on the market fast.'),
                    ],
                ],
            }
            _pool = _all_job_pools.get(_rj_svc, _all_job_pools['House Clearance'])
            _rj_idx = int(__import__('hashlib').md5((slug + '-jobs').encode()).hexdigest(), 16) % len(_pool)
            _rj_jobs = _pool[_rj_idx]
            _rj_cards = ''
            for _rj_prop, _rj_desc in _rj_jobs:
                _rj_cards += '<div class="job-card"><h3>' + _rj_svc + ' — ' + _rj_prop + ' in ' + _rj_town + '</h3><p>' + _rj_desc + '</p></div>'
            recent_jobs = '<section class="recent-jobs" aria-label="Recent local jobs"><h2>Recent Jobs Near ' + _rj_town + '</h2><div class="recent-jobs-grid">' + _rj_cards + '</div></section>' 

        if not is_location_page:
            hero = ''
            gallery = ''
            faq = ''
            faq_schema = ''
            related_services = ''
        html = template.replace('{{ content }}', content)
        html = html.replace('{{ location_sections }}', location_sections)
        html = html.replace('{{ hero }}', hero)
        html = html.replace('{{ gallery }}', gallery)
        html = html.replace('{{ faq }}', faq)
        html = html.replace('{{ pricing }}', pricing)
        html = html.replace('{{ recent_jobs }}', recent_jobs)
        html = html.replace('{{ related_services }}', related_services)
        html = html.replace('{{ faq_schema }}', faq_schema)
        html = html.replace('{{ title }}', title)
        html = html.replace('{{ meta_description }}', meta_description)
        html = html.replace('{{ canonical_slug }}', canonical_slug)

        # OG tags
        og_title = title
        og_description = meta_description
        og_type = 'website'
        if slug == 'index':
            og_url = 'https://mikes-house-clearance.co.uk/'
        else:
            og_url = f'https://mikes-house-clearance.co.uk/{canonical_slug}'
        html = html.replace('{{ og_title }}', og_title)
        html = html.replace('{{ og_description }}', og_description)
        html = html.replace('{{ og_url }}', og_url)
        html = html.replace('{{ og_type }}', og_type)

        # Schema markup
        SITE = 'https://mikes-house-clearance.co.uk'
        service_title = page.get('service_title', '')
        town_name = page.get('town_name', '')
        town_county = page.get('town_county', '')
        town_postcode = page.get('town_postcode', '')

        if slug == 'index':
            schema = json.dumps({
                "@context": "https://schema.org",
                "@type": "LocalBusiness",
                "name": "Mike's House Clearance",
                "url": SITE + "/",
                "telephone": "+447347300798",
                "image": SITE + "/assets/images/hero-image.webp",
                "description": meta_description,
                "address": {
                    "@type": "PostalAddress",
                    "addressRegion": "Devon, Cornwall, Somerset",
                    "addressCountry": "GB"
                },
                "areaServed": ["Devon", "Cornwall", "Somerset"],
                "priceRange": "££"
            }, separators=(',', ':'))
        elif town_name and service_title:
            area = f"{town_name}, {town_county}" if town_county else town_name
            schema = json.dumps({
                "@context": "https://schema.org",
                "@type": "Service",
                "name": f"{service_title} in {town_name}",
                "description": meta_description,
                "url": og_url,
                "provider": {
                    "@type": "LocalBusiness",
                    "name": "Mike's House Clearance",
                    "telephone": "+447347300798",
                    "url": SITE + "/"
                },
                "areaServed": {
                    "@type": "Place",
                    "name": area
                }
            }, separators=(',', ':'))
        else:
            schema = json.dumps({
                "@context": "https://schema.org",
                "@type": "WebPage",
                "name": title,
                "description": meta_description,
                "url": og_url,
                "isPartOf": {
                    "@type": "WebSite",
                    "name": "Mike's House Clearance",
                    "url": SITE + "/"
                }
            }, separators=(',', ':'))

        html = html.replace('{{ schema }}', schema)
        out_dir = os.path.join('build', slug) if slug else 'build'
        os.makedirs(out_dir, exist_ok=True)
        with open(os.path.join(out_dir, 'index.html'), 'w') as f:
            f.write(html)
    if os.path.exists('assets'):
        shutil.copytree('assets', 'build/assets', dirs_exist_ok=True)
        if os.path.exists('send.php'):
            shutil.copy('send.php', 'build/send.php')
    # Generate robots.txt
    robots = "User-agent: *\nAllow: /\nSitemap: https://mikes-house-clearance.co.uk/sitemap.xml\n"
    with open('build/robots.txt', 'w') as f:
        f.write(robots)
    # Generate sitemap.xml
    SITEMAP_EXCLUDE = ['README', 'thank-you', 'footer', 'header', 'hero', 'location', 'service', 'google-tag', 'location-hero', 'location-info', 'location-map', 'location-pricing', 'location-process-reviews-faq', 'location-service-card', 'location-before-after', 'location-more-services', 'location-trust-banner', 'location-finder', 'location-property-services', 'location-hero-content', 'location-footer-cta', 'process-reviews-faq', 'professional-property-services', 'cookie-consent', 'before-after-gallery', 'top-banner']
    sitemap_urls = ''
    BUILD_EXCLUDE = ['README']
    for page in pages:
        slug = page['slug']
        if slug in BUILD_EXCLUDE:
            continue
        if slug in SITEMAP_EXCLUDE:
            continue
        if slug == 'index':
            url = 'https://mikes-house-clearance.co.uk/'
        elif slug:
            url = f'https://mikes-house-clearance.co.uk/{slug}/'
        else:
            continue
        sitemap_urls += f'  <url>\n    <loc>{url}</loc>\n    <changefreq>monthly</changefreq>\n    <priority>0.7</priority>\n  </url>\n'
    sitemap = f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sitemap_urls}</urlset>'
    with open('build/sitemap.xml', 'w') as f:
        f.write(sitemap)
    # Homepage slug fix
    homepage_src = 'build/index/index.html'
    if os.path.exists(homepage_src):
        shutil.copy(homepage_src, 'build/index.html')
        print('Homepage copied: build/index/index.html -> build/index.html')
    print(f"Built {len(pages)} pages")
    print("Generated robots.txt")
    print("Generated sitemap.xml")

if __name__ == '__main__':
    build()
