"""Seed data — articles, comments, trends, notifications."""
import json
import time
from db import get_db, now

ARTICLES = [
    {
        'id': 'a1', 'category': 'POLITICS', 'tag': 'politics', 'source': "Editor's Pick",
        'title': 'Federal budget marks hydropower pivot, pegs Rs 180B for transmission corridors',
        'title_np': 'संघीय बजेटले जलविद्युत्मा जोड दिँदै रू १८० अर्ब प्रसारणका लागि छुट्यायो',
        'dek': 'Finance Ministry frames the year as one of "energy independence." Provinces will share half the new revenue from cross-border electricity sales.',
        'icon': 'building', 'img_label': 'BUDGET / KATHMANDU / FILE',
        'bias': 42, 'bias_label': 'Center-Left',
        'verified': 1, 'verified_count': 4, 'comments_count': 84, 'likes': 1240,
        'developing': 0, 'is_video': 0,
        'body': [
            'The federal budget tabled in parliament today commits Rs 1.75 trillion for the coming fiscal year, with hydropower and digital infrastructure presented as the two anchor priorities for what the Finance Minister called a "decade of cross-border export."',
            'Energy receives the largest single allocation — Rs 180 billion — directed primarily at high-voltage transmission corridors linking generation clusters in Karnali and Koshi to substations near the Indian border. Officials say the goal is to add 3 GW of exportable capacity by 2030.',
            'A separate Rs 42 billion is earmarked for a "national digital corridor" connecting Kathmandu, Pokhara, Biratnagar and four secondary cities with metro-grade fibre. Education and health each see roughly 12% increases.',
            'Opposition leaders described the targets as ambitious but executable only if the budget is matched by procurement reform. A new public-disclosure rule for contracts above Rs 500 million was announced but the operational details were deferred to a finance ordinance.',
        ],
        'key_points': [
            'Rs 180B for hydropower — the largest-ever single-sector allocation.',
            'Digital corridor links 7 cities with metro-grade fibre by 2027.',
            'Provinces to receive 50% of new cross-border electricity revenue.',
            'Education + health budgets up 12%; defence flat year-on-year.',
        ],
        'why_matters': 'For households the immediate signal is load-shedding: Energy Ministry models suggest 30-40% fewer outage hours in valley wards within two years if transmission timelines hold.',
        'time_label': '2H AGO', 'age_seconds': 7200,
    },
    {
        'id': 'a2', 'category': 'HYPERLOCAL', 'tag': 'hyperlocal', 'source': 'Ward 5 Reporter',
        'title': 'Pulchowk footpath project begins — three-month timeline, four businesses affected',
        'dek': 'Ward office confirms pedestrian safety scheme with traffic rerouting along Sanepa side roads. Compensation package under review.',
        'icon': 'pin', 'img_label': 'PULCHOWK ROAD / FIELD PHOTO',
        'verified': 1, 'verified_count': 2, 'comments_count': 18, 'likes': 240,
        'body': [
            'Ward 5 office began the long-promised Pulchowk-to-Jhamsikhel footpath upgrade this morning, with workers laying initial barricades from the Patan Hospital side at 6 AM.',
            'Four businesses on the stretch — two tea shops, a tailor and a stationery store — will see reduced footfall during the three-month works. The ward chair confirmed that a compensation framework is "under active review with the municipality" but stopped short of committing to dates.',
            'Traffic from Kupondole is being rerouted via Sanepa side roads between 7 AM and 10 AM each weekday. Two-wheelers are exempt outside peak hours.',
        ],
        'key_points': [
            'Three-month timeline · completion target August 14',
            'Four businesses affected · compensation pending',
            'Traffic rerouted via Sanepa · 7-10 AM weekdays',
            'Pedestrian crossings added at four junctions',
        ],
        'why_matters': 'If you walk this stretch daily, expect dust and noise but a properly kerbed footpath by August. Ward office says the design includes drainage that should eliminate monsoon flooding on the Pulchowk dip.',
        'time_label': '1H AGO', 'age_seconds': 3600,
    },
    {
        'id': 'a3', 'category': 'BUSINESS', 'tag': 'business', 'source': 'Markets Desk',
        'title': 'NEPSE closes up 2.3% — banking subindex carries the rally on FDI sentiment',
        'dek': 'Mid-cap commercial banks lead gains after IMF assessment signals a stable external position into Q2.',
        'icon': 'chart', 'img_label': 'NEPSE INDEX CHART',
        'bias': 64, 'bias_label': 'Pro-market',
        'verified': 1, 'verified_count': 3, 'comments_count': 41, 'likes': 890,
        'body': [
            'The NEPSE closed at 2,184.6 today, up 2.3% on heavier-than-usual volume of Rs 6.2 billion. The banking subindex led the rally with a 3.8% gain.',
            'Mid-cap commercial banks were the standout: Prabhu Bank, Nabil Bank and NIC Asia each closed above their 50-day moving average for the first time in six weeks.',
            'The move came hours after the IMF Article IV consultation flagged Nepal\'s external position as "broadly stable into Q2," with reserves covering 11.3 months of imports.',
        ],
        'key_points': [
            'NEPSE +2.3% to 2,184.6 · highest close in 6 weeks',
            'Banking subindex +3.8% · volume 35% above 30-day avg',
            'IMF Article IV: reserves at 11.3 months of imports',
            'Hydropower IPOs queue lengthens · 3 new filings',
        ],
        'why_matters': 'If you hold a banking SIP through any commercial bank, today\'s rally probably nudged your portfolio 1.5-2% higher. The IMF signal also reduces the near-term odds of an NRB rate hike.',
        'time_label': '5H AGO', 'age_seconds': 18000,
    },
    {
        'id': 'a4', 'category': 'TECHNOLOGY', 'tag': 'tech', 'source': 'Tech Samachar',
        'title': 'eSewa vs Khalti — what the new RBI cross-border rule actually changes',
        'dek': 'AI explainer breakdown of inter-operability requirements and what it means for ride-share and merchant fees.',
        'icon': 'sparkle', 'img_label': 'WALLET ICONS / FILE',
        'developing': 1, 'is_video': 1, 'comments_count': 212, 'likes': 3400,
        'verified': 1, 'verified_count': 2,
        'body': [
            'The Reserve Bank of India\'s new cross-border interoperability rule takes effect August 1 and changes how Nepali wallets — eSewa, Khalti, IME Pay — handle Indian merchants.',
            'In practice: a tourist in Pokhara can now scan an Indian QR with eSewa directly, with the FX cleared via NRB\'s overnight window rather than a SWIFT hop.',
            'Merchant fees for cross-border acceptance drop from 2.1% to 1.4%. Ride-share platforms with cross-border drivers (Pathao, Indrive) are the immediate winners.',
        ],
        'key_points': [
            'Cross-border QR acceptance · effective Aug 1',
            'Merchant fees drop 2.1% to 1.4%',
            'FX cleared via NRB overnight window',
            'Pathao + Indrive get fee relief on cross-border trips',
        ],
        'why_matters': 'If you regularly visit India, your wallet will work at most Indian shops with the next app update. Receive money from family in India? Expect arrival in minutes rather than hours.',
        'time_label': '3H AGO', 'age_seconds': 10800,
    },
    {
        'id': 'a5', 'category': 'AGRICULTURE', 'tag': 'agri', 'source': 'AgriDesk',
        'title': 'Winter wheat prices soften 4% as imports arrive at Birgunj',
        'dek': 'Trade Ministry data shows arrivals tracking 8% above the five-year average; millers expect retail flour prices to follow within two weeks.',
        'icon': 'plant', 'img_label': 'WHEAT / BIRGUNJ DEPOT',
        'verified': 1, 'verified_count': 2, 'comments_count': 28, 'likes': 620,
        'body': [
            'Wholesale wheat prices at the Birgunj depot dropped 4% week-on-week as 38,000 tonnes of imported grain cleared customs this morning.',
            'Trade Ministry data shows total arrivals running 8% ahead of the five-year seasonal average. Millers in Bara and Parsa say retail flour prices should follow within ten to fourteen days.',
        ],
        'key_points': [
            'Wholesale wheat -4% w/w at Birgunj depot',
            '38,000 tonnes cleared customs today',
            'Arrivals 8% above 5-year seasonal average',
            'Retail flour expected to drop in 10-14 days',
        ],
        'why_matters': 'A 20kg flour sack should cost Rs 60-90 less by month-end if millers pass through. Roti-shop margins improve immediately.',
        'time_label': '6H AGO', 'age_seconds': 21600,
    },
    {
        'id': 'a6', 'category': 'REMITTANCE', 'tag': 'nepal', 'source': 'Diaspora Desk',
        'title': 'Gulf-to-Nepal transfers hit record Q1 — and what the rate gap means for receivers',
        'dek': 'Formal channel inflows up 11%; informal channel hawala spread has narrowed for the third consecutive quarter.',
        'icon': 'globe', 'img_label': 'FX BOARD / KATHMANDU',
        'bias': 50, 'bias_label': 'Center',
        'verified': 1, 'verified_count': 3, 'comments_count': 67, 'likes': 1100,
        'body': [
            'Formal-channel remittances from the Gulf hit Rs 312 billion in Q1, an 11% year-on-year increase and the highest single quarter on record.',
            'The hawala spread — the gap between informal and formal exchange rates — narrowed to 0.4% from 1.2% a year ago, signalling that formal channels are now competitive on price as well as compliance.',
        ],
        'key_points': [
            'Q1 formal remittances: Rs 312B (+11% YoY)',
            'Hawala spread narrowed to 0.4% from 1.2%',
            'UAE and Qatar lead inflow growth',
            'Reserves boost · 11.3 months import cover',
        ],
        'why_matters': 'If family sends money from Doha or Dubai, the formal channel is now within paisa of the street rate — and safer. Wise, Remitly and IME all offer same-day clearance.',
        'time_label': '8H AGO', 'age_seconds': 28800,
    },
    {
        'id': 'a7', 'category': 'CLIMATE', 'tag': 'nepal', 'source': 'Climate Desk',
        'title': 'Glacial lake monitoring expands to 47 sites — Imja and Tsho Rolpa get hourly sensors',
        'dek': 'ICIMOD and DHM commission new IoT array following last monsoon\'s near-breach scare at Hongu valley.',
        'icon': 'mountain', 'img_label': 'IMJA LAKE / GLACIER',
        'verified': 1, 'verified_count': 3, 'comments_count': 34, 'likes': 480,
        'body': [
            'A joint ICIMOD-DHM project commissioned hourly water-level sensors at 47 glacial lakes this week, doubling the previous network.',
            'Imja and Tsho Rolpa — the two most-watched lakes for outburst risk — now have redundant satellite uplinks and battery backups rated for 30-day outages.',
        ],
        'key_points': [
            'Sensor count doubled · 23 to 47 lakes',
            'Hourly readings · 30-day battery backup',
            'Early warning lead time: 2-6 hours downstream',
            'Imja, Tsho Rolpa get redundant satellite uplinks',
        ],
        'why_matters': 'Communities in Solukhumbu and Dolakha now get a 2-6 hour warning window for outburst floods. The system pushes SMS in Nepali and Sherpa to registered ward numbers.',
        'time_label': '4H AGO', 'age_seconds': 14400,
    },
    {
        'id': 'a8', 'category': 'POLITICS', 'tag': 'politics', 'source': 'Parliament Desk',
        'title': 'Local-government bill clears committee — ward chiefs gain procurement authority up to Rs 5M',
        'dek': 'Cross-party amendment raises threshold from Rs 2M while tightening disclosure rules and adding a public-objection window.',
        'icon': 'building', 'img_label': 'PARLIAMENT / SINGHA DURBAR',
        'bias': 38, 'bias_label': 'Center-Left',
        'verified': 1, 'verified_count': 3, 'comments_count': 56, 'likes': 720,
        'body': [
            "Parliament's State Affairs committee cleared the local government amendment bill yesterday after a six-hour cross-party negotiation.",
            'Ward chairs gain direct procurement authority up to Rs 5 million for road repair, drainage and street-lighting work — up from Rs 2 million previously.',
            'The trade-off: all contracts above Rs 1 million now require a 14-day public-objection window and ward-level expenditure portals.',
        ],
        'key_points': [
            'Ward procurement ceiling: Rs 2M to Rs 5M',
            'Mandatory 14-day public-objection window',
            'Ward expenditure portals · live by Aug 30',
            'Final-reading vote scheduled for next week',
        ],
        'why_matters': 'Ward 5 alone has an estimated Rs 18M of drainage work that has been stuck waiting for municipality sign-off. This bill, if it passes, lets the ward chair commission it directly.',
        'time_label': '9H AGO', 'age_seconds': 32400,
    },
    {
        'id': 'a9', 'category': 'SPORTS', 'tag': 'nepal', 'source': 'Sports Desk',
        'title': "Nepal U-19 cricket squad books Asia Cup semifinal — Gulshan Jha's 87 carries chase",
        'dek': 'Bangladesh defeated by 5 wickets at Premadasa with 12 balls to spare; Jha named player of the match.',
        'icon': 'star', 'img_label': 'CRICKET / PREMADASA',
        'verified': 1, 'verified_count': 2, 'comments_count': 145, 'likes': 2800,
        'body': [
            "Nepal's under-19 team booked their first ever U-19 Asia Cup semifinal with a five-wicket win over Bangladesh in Colombo.",
            'Captain Gulshan Jha\'s 87 off 71 balls anchored the chase of 234. He fell with 14 still needed but his stand of 92 with Hemant Dhami had broken the back of the target.',
        ],
        'key_points': [
            'Bangladesh beaten by 5 wickets · 12 balls to spare',
            'Gulshan Jha 87(71) · player of the match',
            'Semifinal vs India · Saturday 14:30 NPT',
            "Nepal's first U-19 Asia Cup semi",
        ],
        'why_matters': "The Saturday semifinal will be on Star Sports + free YouTube stream. India have not lost an U-19 Asia Cup semifinal since 2018 — but Nepal's bowling has been the tournament's tightest by economy.",
        'time_label': '7H AGO', 'age_seconds': 25200,
    },
    {
        'id': 'a10', 'category': 'HEALTH', 'tag': 'nepal', 'source': 'Health Desk',
        'title': 'Free cervical screening expands to 22 districts — HPV self-test kits available at ward level',
        'dek': 'Health Ministry programme reaches 180,000 women in year one; new districts include Mugu, Humla and Bajura.',
        'icon': 'shield-check', 'img_label': 'HEALTH POST / KARNALI',
        'verified': 1, 'verified_count': 2, 'comments_count': 22, 'likes': 540,
        'body': [
            'The Ministry of Health is expanding its free cervical-cancer screening programme to 22 districts from August, including the remote Karnali districts of Mugu, Humla and Bajura.',
            'HPV self-test kits — first piloted in Kavre last year — will be available free at any ward health post for women aged 30-49.',
        ],
        'key_points': [
            'Programme expands · 8 to 22 districts',
            'HPV self-test kits free at ward health posts',
            'Target: 500,000 women screened in year two',
            'Eligibility: women 30-49 · no referral needed',
        ],
        'why_matters': "Cervical cancer remains Nepal's most common cancer in women under 50. Self-test takes 10 minutes; results in 7 days; treatment subsidies for positive cases.",
        'time_label': '12H AGO', 'age_seconds': 43200,
    },
    {
        'id': 'a11', 'category': 'TECHNOLOGY', 'tag': 'tech', 'source': 'Tech Samachar',
        'title': 'Nepali language LLM crosses 70% on standard benchmarks — KU and CMU collaboration',
        'dek': 'NepaliBERT-3 outperforms multilingual baselines on news classification, summarisation and code-switched dialogue.',
        'icon': 'sparkles', 'img_label': 'AI LAB / DHULIKHEL',
        'verified': 1, 'verified_count': 2, 'comments_count': 88, 'likes': 1450,
        'body': [
            'Researchers at Kathmandu University, in collaboration with Carnegie Mellon, have released NepaliBERT-3, a 7-billion-parameter language model trained primarily on Nepali text.',
            'The model crossed 70% on the standard XNLI-Nepali benchmark — the first open model to do so — and outperforms GPT-4 on code-switched Nepali-English dialogue tasks.',
        ],
        'key_points': [
            '70%+ on XNLI-Nepali benchmark · first open model',
            '7B parameters · trained on 80GB Nepali text',
            'Beats GPT-4 on code-switched dialogue',
            'Weights released under Apache 2.0',
        ],
        'why_matters': "If you build an app for Nepali users, you now have a free, on-device-capable model that does not require sending data to OpenAI. Samachar's AI chat will switch to NepaliBERT-3 in the next release.",
        'time_label': '14H AGO', 'age_seconds': 50400,
    },
    {
        'id': 'a12', 'category': 'HYPERLOCAL', 'tag': 'hyperlocal', 'source': 'Ward 5 Reporter',
        'title': 'Jhamsikhel power cut Wednesday 10 AM-2 PM — substation maintenance',
        'dek': 'NEA confirms scheduled outage covering Sanepa, Pulchowk and Lower Jhamsikhel. Hospital wing exempt.',
        'icon': 'pin', 'img_label': 'SUBSTATION / PULCHOWK',
        'verified': 1, 'verified_count': 2, 'comments_count': 8, 'likes': 120,
        'body': [
            'NEA has scheduled a four-hour power cut covering Sanepa, Pulchowk and Lower Jhamsikhel from 10 AM to 2 PM next Wednesday.',
            'The substation transformer is being replaced as part of the valley reliability upgrade. Patan Hospital and the police post are on a separate feeder and unaffected.',
        ],
        'key_points': [
            'Wednesday 10 AM - 2 PM · Sanepa + Pulchowk + Jhamsikhel',
            'Patan Hospital + police post exempt',
            'Transformer replacement · part of reliability upgrade',
            'NEA helpline: 1150',
        ],
        'why_matters': 'Charge phones and laptops the night before. Wifi will be out unless you have a UPS or mobile hotspot. Restaurants are pre-warning customers.',
        'time_label': '18H AGO', 'age_seconds': 64800,
    },
    {
        'id': 'a13', 'category': 'BUSINESS', 'tag': 'business', 'source': 'Markets Desk',
        'title': 'Hydropower IPO queue grows — three new filings push pipeline past Rs 24B',
        'dek': 'SEBON receives three fresh prospectuses; 27 MW Upper Tamor leads on size with Rs 9.2B raise target.',
        'icon': 'chart', 'img_label': 'HYDRO PROJECT / TAMOR',
        'bias': 58, 'verified': 1, 'verified_count': 3, 'comments_count': 39, 'likes': 680,
        'body': [
            'SEBON has received three new IPO prospectuses from hydropower developers in the past two weeks, bringing the total pipeline to Rs 24.3 billion.',
            'The 27 MW Upper Tamor project is the largest of the three with a Rs 9.2B raise target. The other two — Khimti-3 and Modi Khola Upper — are 14 MW and 11 MW respectively.',
        ],
        'key_points': [
            'Three new prospectuses · pipeline at Rs 24.3B',
            'Upper Tamor (27 MW) · Rs 9.2B target',
            'Subscription windows expected Q3-Q4',
            'Sector ROE average · 12.4% trailing five years',
        ],
        'why_matters': 'If you have an unused IPO quota and trust hydropower fundamentals, this quarter is likely to give you several allocation chances. Subscribe via TMS once windows open.',
        'time_label': '20H AGO', 'age_seconds': 72000,
    },
    {
        'id': 'a14', 'category': 'CULTURE', 'tag': 'nepal', 'source': 'Culture Desk',
        'title': 'Indra Jatra preparations begin — chariot pulling routes finalised after ward consultation',
        'dek': 'Kathmandu Metropolitan finalises three-day procession map; live streams arranged for diaspora viewers.',
        'icon': 'star', 'img_label': 'INDRA JATRA / BASANTAPUR',
        'verified': 1, 'verified_count': 2, 'comments_count': 67, 'likes': 2100,
        'body': [
            'Preparations for Indra Jatra began at Basantapur this week. The Kathmandu Metropolitan Office finalised the chariot pulling routes after a three-week ward consultation.',
            'Live streams will be arranged on the metropolitan YouTube channel for the diaspora viewers, with English commentary on day one and Newari on days two and three.',
        ],
        'key_points': [
            'Procession dates: Aug 30 - Sept 1',
            'Live stream · KMC YouTube channel',
            'English commentary day 1 · Newari days 2-3',
            'Road closures: Basantapur-Naradevi 9 AM-6 PM',
        ],
        'why_matters': "If you live in the old city, plan around the road closures. If you're abroad, the live stream link will be in this app on day one — no VPN needed.",
        'time_label': '1D AGO', 'age_seconds': 86400,
    },
    {
        'id': 'a15', 'category': 'EDUCATION', 'tag': 'nepal', 'source': 'Education Desk',
        'title': 'SEE results out — pass rate climbs to 47.8% with Karnali showing biggest gain',
        'dek': 'NEB releases secondary education exam results; girls outperform boys for the seventh consecutive year.',
        'icon': 'shield-check', 'img_label': 'SCHOOL / EXAM HALL',
        'verified': 1, 'verified_count': 3, 'comments_count': 198, 'likes': 3200,
        'body': [
            'The National Examination Board released the Secondary Education Examination results this morning. The overall pass rate climbed to 47.8% from 46.2% last year.',
            'Karnali province showed the largest year-on-year improvement at 7.4 percentage points, driven mainly by gains in Surkhet and Jumla districts. Girls outperformed boys for the seventh consecutive year.',
        ],
        'key_points': [
            'Overall pass rate: 47.8% (+1.6pp YoY)',
            'Karnali biggest gainer · +7.4pp',
            'Girls outperform · 7th consecutive year',
            'Results portal: see.gov.np · SMS via 1090',
        ],
        'why_matters': "If you or family appeared, check the portal — it's less loaded than the website. Counselling helpline for students dealing with results runs free until Aug 15.",
        'time_label': '1D AGO', 'age_seconds': 90000,
    },
]

SEED_COMMENTS = [
    ('a1', 'Priya Karmacharya', 'PK', 'Ward 5 · Kathmandu',
     'Finally a budget that names digital infrastructure as a line item. The seven-city corridor plan is ambitious — execution is the only question that matters now.', 47, 3, 1),
    ('a1', 'Bijaya Tamang', 'BT', 'Pokhara',
     'Rs 180B for hydropower reads well on paper. But who is on the technical evaluation committee? Without transparent tendering we have heard this story before.', 89, 7, 0),
    ('a1', 'Sita Rana', 'SR', 'Chitwan · Farmer',
     'The wheat import figure matters more for us than any number in this budget. Please follow what happens at the Birgunj depot next week.', 34, 1, 1),
    ('a2', 'Ramesh Thapa', 'RT', 'Pulchowk',
     'They started works without finalising compensation. Same story every time. The tea shop at the corner has been there 22 years.', 28, 1, 0),
    ('a2', 'Manish Adhikari', 'MA', 'Sanepa',
     'Drainage in this design is good. The monsoon flooding at the Pulchowk dip ruins my shoes twice a week.', 41, 0, 1),
    ('a9', 'Anil Shrestha', 'AS', 'Kathmandu',
     "Gulshan Jha is a generational talent. Saturday will be his biggest test — India's spinners read pitches better than anyone at this level.", 122, 3, 1),
]

SEED_TRENDS = [
    (1, 'Budget 2081/82', '48.2k discussions', 'hot'),
    (2, 'Valley flood warning · Ward 5', '32.1k mentions', 'breaking'),
    (3, 'Pulchowk road works', '4.8k local', 'rising'),
    (4, 'NEPSE banking rally', '14.2k discussions', 'rising'),
    (5, 'Q1 remittance data', '9.8k readers', 'new'),
    (6, 'U-19 cricket semi vs India', '24.5k discussions', 'hot'),
    (7, 'SEE results released', '38.1k searches', 'rising'),
]

SEED_NOTIFICATIONS = [
    ('n1', 'alert',     'live',   'Flash flood warning — Ward 5', 'Avoid Pulchowk Road until 18:00 · now'),
    ('n2', 'sparkle',   'info',   'Your morning brief is ready',  '5 min audio · personalised · 2h ago'),
    ('n3', 'thumb-up',  'verify', 'Priya liked your comment',     'On Budget 2081 · 3h ago'),
    ('n4', 'star',      'warn',   'You earned a "Local Hero" badge', 'Three verified contributions · 1d ago'),
    ('n5', 'chart',     'info',   'NEPSE closed up 2.3%',         'Market alert you enabled · 4h ago'),
]


def seed_articles():
    """Insert seed articles if articles table is empty."""
    conn = get_db()
    try:
        existing = conn.execute('SELECT COUNT(*) FROM articles').fetchone()[0]
        if existing:
            return False
        now_ts = int(time.time())
        for a in ARTICLES:
            conn.execute("""
                INSERT INTO articles (id, category, tag, source, title, title_np, dek,
                  icon, img_label, bias, bias_label, verified, verified_count,
                  comments_count, likes, developing, is_video,
                  body, key_points, why_matters, published_at, time_label)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                a['id'], a['category'], a.get('tag'), a['source'], a['title'],
                a.get('title_np'), a.get('dek'),
                a.get('icon'), a.get('img_label'),
                a.get('bias'), a.get('bias_label'),
                a.get('verified', 0), a.get('verified_count', 0),
                a.get('comments_count', 0), a.get('likes', 0),
                a.get('developing', 0), a.get('is_video', 0),
                json.dumps(a.get('body', [])),
                json.dumps(a.get('key_points', [])),
                a.get('why_matters'),
                now_ts - a.get('age_seconds', 0),
                a.get('time_label'),
            ))
        for c in SEED_COMMENTS:
            article_id, name, initials, place, text, likes, dislikes, verified = c
            conn.execute("""
                INSERT INTO comments (article_id, user_id, name, initials, place, text,
                  likes, dislikes, verified, created_at)
                VALUES (?, NULL, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (article_id, name, initials, place, text, likes, dislikes, verified, now_ts - 1800))
        for t in SEED_TRENDS:
            conn.execute("""
                INSERT OR REPLACE INTO trends (rank, title, sub, heat)
                VALUES (?, ?, ?, ?)
            """, t)
        for n in SEED_NOTIFICATIONS:
            conn.execute("""
                INSERT OR REPLACE INTO notifications (id, icon, tone, title, sub, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, n + (now_ts,))
        conn.commit()
    finally:
        conn.close()
    return True


if __name__ == '__main__':
    from db import init_db
    init_db()
    result = seed_articles()
    print('Seeded.' if result else 'Already populated — nothing to seed.')
