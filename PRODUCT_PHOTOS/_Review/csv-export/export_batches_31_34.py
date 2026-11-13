"""Export the frozen 70 approved products from queue2416–2517, price1."""
import csv, hashlib, json, re, zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[2]
REVIEW = ROOT / '_Review'
OUT = Path(__file__).resolve().parent / 'batches'
HEADERS = 'name,description,price,sku,stock_qty,category,brand,image_url,group,variant_name,variant_value,currency,seo_title,seo_description,gallery_urls'.split(',')
NAMES = ['01_White-Background.png', '02_Styled-Background.png', '03_Lifestyle.png', '04_Detail.png', '05_Promotional.png']
OVERRIDES = {
 '2513': 'Contact Lens Travel Case Set', '2512': 'Printed Contact Lens Travel Kit Assortment',
 '2506': 'Coloured Contact Lens Shade Guide', '2505': 'Coloured Contact Lens Box Assortment',
 '2499': 'Party Snow Spray', '2495': 'Textured Hair Barrette Card Assortment',
 '2494': 'Textured Hair Barrette Assortment',
 '2491': 'Bright Textured Hair Barrette Assortment', '2490': 'Floral Print Hair Barrette Assortment',
 '2485': 'Mixed Fragrance Bottle and Box Assortment', '2484': 'Colourful Fragrance Bottle and Box Assortment',
 '2483': 'Fragrance Bottle Assortment with Outer Carton', '2482': 'Boxed Fragrance Bottle Collection',
 '2475': 'Fantasy Plush Toy Assortment', '2474': 'Pink and Magenta Plush Bear Pair',
 '2465': 'White Pearl Butterfly Jewellery Set Assortment', '2463': 'Daisy Print Drinking Bottle Assortment',
 '2459': 'Gold-Tone Ball Nose Stud Assortment', '2451': 'Black Marbled Hair Barrette Card',
 '2450': 'Warm Woodgrain Hair Barrette Card Assortment', '2441': 'Unicorn Pencil Pouch Assortment',
 '2440': 'Bright Velvet Scrunchie Assortment', '2437': 'Black Dot Bindi Card Assortment',
}
DESCRIPTIONS = {
 '2513': 'Six contact lens travel cases, shown with the blue paired pot and two white tools.',
 '2512': 'Eight closed printed contact lens travel kit boxes in the photographed designs.',
 '2506': 'A twelve-variant coloured contact lens reference chart. View the product photos for the shade guide.',
 '2505': 'The photographed lens carton assortment with opened carton and blister packaging.',
 '2504': 'Two seated blue and pink plush toys holding smaller dolls.',
 '2503': 'Six plush tote bags in the photographed colours and designs.',
 '2502': 'Four colourful cat plush toys shown together as one assortment.',
 '2499': 'Party snow spray can, shown capped and in a spraying demonstration.',
 '2497': 'Four distinct spiral notebook cover designs shown as one assortment.',
 '2496': 'Two six-clip cards with bow and oval shapes, twelve clips in total.',
 '2493': 'Six distinct cards of black barrettes, six clips per card.',
 '2492': 'Six distinct cards of warm marbled barrettes, six clips per card.',
 '2491': 'Five six-clip cards with textured coral, green and blue barrettes.',
 '2490': 'Six six-clip cards with floral prints and assorted shapes.',
 '2489': 'Three six-clip cards with pastel star and glitter designs.',
 '2488': 'Three six-clip cards with floral prints and assorted shapes.',
 '2475': 'Four fantasy plush toys in the photographed colours and orientations.',
 '2474': 'Two pink and deep magenta plush bears with white belly and muzzle details.',
 '2471': 'A pair of white cat plush toys with plaid bow details.',
 '2470': 'Three rabbit-eared plush toys in yellow, mint and pink.',
 '2468': 'Twelve distinct necklace and matching stud-earring sets from the photographed assortment.',
 '2465': 'Six white pearl and coloured butterfly jewellery sets with matching stud pairs.',
 '2463': 'Four daisy-print drinking bottles in pink, white, light blue and yellow.',
 '2462': 'Three bead bracelets with the photographed charm and colour details.',
 '2461': 'A case of forty star-gem nose studs in an eight-by-five arrangement.',
 '2460': 'Twenty-five gem-accent nose hoops in the photographed five-by-five case.',
 '2459': 'Forty gold-tone ball nose studs in the photographed case.',
 '2458': 'Twenty-five slender curved gold-tone nose hoops in a five-by-five case.',
 '2457': 'Two silver-tone double-wire bangles with blue eye and black bead details.',
 '2455': 'Twelve plush character hair ties arranged as six matched pairs.',
 '2451': 'One card of six black marbled curved rectangular barrettes.',
 '2450': 'Two distinct six-clip cards of warm woodgrain and marbled barrettes.',
 '2447': 'One card of six neutral textured rectangular barrettes.',
 '2446': 'Two six-clip cards of bright textured oval and rectangular barrettes.',
 '2443': 'Four sports bottles with phone-holder lids, shown with four phone props.',
 '2442': 'Four gradient drinking bottles with the photographed printed designs.',
 '2441': 'Six translucent unicorn pencil pouches: two blue, two purple and two pink.',
 '2440': 'Six visible velvet scrunchies in blue, yellow, red, green, purple and pink.',
 '2439': 'Six velvet scrunchies in the photographed rich colours.',
 '2438': 'Six velvet scrunchies in the photographed pastel colours.',
 '2437': 'A twelve-card display of small black dot bindis.',
 '2433': 'Three cards of black snap hair clips in small, medium and large sizes, twelve clips per card.',
}

def category(name):
    low = name.lower()
    if 'tote' in low: return 'Bags'
    if any(w in low for w in ('notebook', 'pencil', 'pouch')): return 'Stationery'
    if 'fragrance' in low: return 'Fragrances'
    if 'lens' in low or 'bindi' in low: return 'Beauty Accessories'
    if 'snow spray' in low: return 'Party Supplies'
    if 'fan' in low: return 'Home & Living'
    if 'bottle' in low: return 'Drinkware'
    if 'plush' in low and 'hair' not in low: return 'Toys'
    if any(w in low for w in ('jewellery', 'bracelet', 'bangle', 'nose')): return 'Jewellery'
    return 'Hair Accessories'

progress = json.loads((REVIEW / 'END100_2416_2517_PROGRESS.json').read_text())
approved = [r for r in progress['products'] if r['status'] == 'complete']
assert len(approved) == 70, 'This export is frozen to70products; make a new batch if inventory changes.'
web = json.loads((REVIEW / 'END100_2416_2517_WEB_VERIFICATION.json').read_text())
verified = {r['url'] for r in web['results'] if r.get('status') == 200 and r.get('content_type', '').startswith('image/')}
prior = set()
for file in OUT.glob('mytradevia-batch-*.csv'):
    match = re.fullmatch(r'mytradevia-batch-(\d+)\.csv', file.name)
    if match and int(match[1]) <= 30:
        prior.update(r['sku'] for r in csv.DictReader(file.open(encoding='utf-8-sig', newline='')))

rows, evidence, skus = [], [], set()
for product in approved:
    pid = product['product_id']; folder = ROOT / product['folder']
    notes = json.loads((folder / 'GENERATION_NOTES.json').read_text())
    prompts = ' '.join(r.get('prompt') or '' for r in notes.get('records', []) if r.get('saved_file') == 'New/05_Promotional.png')
    headings = re.findall(r'(?i)heading\s*[:=]?\s*["\u201c\u2018\x27]([^"\u201d\u2019\x27]+)', prompts)
    name = OVERRIDES.get(pid) or (headings[0] if headings else None)
    assert name, ('Missing actual-subject name', pid)
    sku = 'PEACHES-' + pid
    assert sku not in prior and sku not in skus; skus.add(sku)
    urls = []
    for filename in NAMES:
        saved = 'New/' + filename; sha = hashlib.sha256((folder / saved).read_bytes()).hexdigest()
        assert any(r.get('saved_file') == saved and r.get('sha256') == sha and r.get('checked') is True for r in notes['records']), (pid, saved)
        url = 'https://raw.githubusercontent.com/heshannamal/peachesImg/main/PRODUCT_PHOTOS/' + quote(product['folder'] + '/' + saved, safe='/')
        assert url in verified, ('Unverified live URL', url)
        urls.append(url)
    row = {h: '' for h in HEADERS}
    row.update(name=name, description=DESCRIPTIONS.get(pid, name + '. View the product photos for the complete design or assortment.'), price='1', sku=sku, category=category(name), image_url=urls[0], currency='LKR', seo_title=name + ' | Sri Lanka', seo_description='Shop ' + name + ' in Sri Lanka. View the product photos for the available design or assortment.', gallery_urls='|'.join(urls[1:]))
    rows.append(row)
    evidence.append(dict(product_id=pid, name=name, name_source='actual inspected subject and checked generation notes' if pid in OVERRIDES else 'checked promotional heading', actual_subject=notes.get('actual_subject'), folder=product['folder'], verified_urls=urls))

files = []
for i in range(0, len(rows), 20):
    path = OUT / f'mytradevia-batch-{31+i//20}.csv'
    with path.open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=HEADERS, lineterminator='\r\n'); writer.writeheader(); writer.writerows(rows[i:i+20])
    data = path.read_bytes(); assert data.startswith(b'\xef\xbb\xbf') and b'\r\n' in data
    parsed = list(csv.DictReader(path.open(encoding='utf-8-sig', newline='')))
    assert len(parsed) == len(rows[i:i+20]) and all(r['price'] == '1' and r['currency'] == 'LKR' and len(r) == 15 for r in parsed)
    files.append(dict(file=path.name, products=len(parsed), sha256=hashlib.sha256(data).hexdigest()))

manifest = dict(created_at=datetime.now(timezone.utc).isoformat(), frozen_queue='END100_2416_2517_PLAN.json', total_products=len(rows), price='1', currency='LKR', rows_per_file=[r['products'] for r in files], total_verified_image_urls=len(rows)*5, prior_export_duplicates=0, encoding='UTF-8 BOM', line_endings='CRLF', files=files, products=evidence)
manifest_path = OUT / 'batch-31-34-manifest.json'; manifest_path.write_text(json.dumps(manifest, indent=2)+'\n')
zip_path = OUT / 'mytradevia-batches-31-34-price-1.zip'
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as z:
    for item in files: z.write(OUT/item['file'], item['file'])
    z.write(manifest_path, manifest_path.name)
with zipfile.ZipFile(zip_path) as z: assert z.testzip() is None
print(json.dumps(dict(products=len(rows), files=files, zip=zip_path.name, verified_urls=len(rows)*5)))
