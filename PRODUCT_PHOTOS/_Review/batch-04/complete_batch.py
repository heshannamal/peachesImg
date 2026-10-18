from pathlib import Path
from PIL import Image
import csv,json,hashlib,html
from urllib.parse import quote

base=Path(r'E:\CEAESSON WHOLESALE ITEMS\PRODUCT_PHOTOS')
review=base/'_Review';batch=review/'batch-04'
plan=json.loads((batch/'plan.json').read_text(encoding='utf-8'))
products=json.loads((review/'products.json').read_text(encoding='utf-8'))
byid={p['product_id']:p for p in products}
with (review/'inventory.csv').open(encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f);invfields=reader.fieldnames;inventory=list(reader)
with (base/'product-catalog.csv').open(encoding='utf-8-sig',newline='') as f:
    reader=csv.DictReader(f);catfields=reader.fieldnames;catalog=list(reader)
variants=['01_White-Background.png','02_Styled-Background.png','03_Lifestyle.png','04_Detail.png','05_Promotional.png']
for s in plan['specs']:
    product=byid[s['id']]
    source=base/product['folder']
    target=base/f'{s["id"]}_{s["newName"]}-1'
    assert source.exists() and not target.exists(), f'Unexpected folder state: {s["id"]}'
    for k,name in enumerate(variants,1):
        assert (source/'New'/name).exists(), f'Missing image: {s["id"]} {name}'
        record=json.loads((batch/f'{s["id"]}_{k:02}.json').read_text(encoding='utf-8'))
        assert record['checked'] is True, f'Image still awaiting review: {s["id"]} {name}'
changes={};completed=[]
for s in plan['specs']:
    p=byid[s['id']];old=base/p['folder'];new=base/f'{s["id"]}_{s["newName"]}-1'
    assert old.resolve().parent==base.resolve() and new.resolve().parent==base.resolve()
    assert old.exists() and not new.exists(),f'Unexpected folder state: {s["id"]}'
    records=[]
    for k,name in enumerate(variants,1):
        file=old/'New'/name
        with Image.open(file) as im:
            assert im.width==im.height and im.width>=1024
            im.verify()
        record=json.loads((batch/f'{s["id"]}_{k:02}.json').read_text(encoding='utf-8'))
        assert record['checked'] is True
        record.update(saved_file=f'New/{name}',sha256=hashlib.sha256(file.read_bytes()).hexdigest())
        records.append(record)
    for row in inventory:
        if row['product_folder']==old.name:
            assert hashlib.sha256((old/'Originals'/row['filename']).read_bytes()).hexdigest()==row['sha256']
    notes={'tool':'built-in image_gen','generation_date':'2026-10-18','status':'five images generated and visually checked','whole_assortment':True,'records':records}
    (old/'GENERATION_NOTES.json').write_text(json.dumps(notes,indent=2),encoding='utf-8')
    old.rename(new)
    changes[old.name]=new.name
    p.update(folder=new.name,new_images=5,generation_complete=True,generation_status='complete',style_review='approved-style-applied',generation_batch='batch-04')
    completed.append({'product_id':s['id'],'folder':new.name,'new_images':5})
for row in inventory:
    if row['product_folder'] in changes:row['product_folder']=changes[row['product_folder']]
for row in catalog:
    if row['folder'] in changes:row['folder']=changes[row['folder']]
    if row['product_id'] in {s['id'] for s in plan['specs']}:row.update(new_images=5,status='complete')
for path,fields,rows in [(review/'inventory.csv',invfields,inventory),(base/'product-catalog.csv',catfields,catalog)]:
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
(review/'products.json').write_text(json.dumps(products,indent=2),encoding='utf-8')
summary=json.loads((review/'FINALIZED.json').read_text(encoding='utf-8'))
summary.update(new_images_generated=sum(p['new_images'] for p in products),completed_product_groups=sum(p['generation_complete'] for p in products))
(review/'FINALIZED.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
report={'completed_products':completed,'new_images_this_batch':50,'skipped_for_grouping_review':plan['skipped'],'total_complete_products':summary['completed_product_groups'],'total_new_images':summary['new_images_generated']}
(batch/'COMPLETED.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
sections=[]
for item in completed:
    cards=[]
    for label,name in zip(['White background','Styled background','Lifestyle','Detail','Promotional'],variants):
        url=quote(item['folder']+'/New/'+name)
        cards.append(f'<a href="{url}"><img loading="lazy" src="{url}" alt="{html.escape(label)}"><span>{html.escape(label)}</span></a>')
    sections.append(f'<section><h2>{html.escape(item["folder"])}</h2><div class="grid">'+''.join(cards)+'</div></section>')
page='<!doctype html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Product photos - Batch 04</title><style>body{font:16px system-ui;margin:32px;background:#f4f0f8;color:#33243c}h1{margin-bottom:4px}h2{font-size:18px;overflow-wrap:anywhere}.grid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:12px}a{display:block;background:white;border-radius:12px;overflow:hidden;color:inherit;text-decoration:none}img{display:block;width:100%;aspect-ratio:1;object-fit:contain}span{display:block;padding:12px}section{margin:36px 0}@media(max-width:800px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}</style></head><body><h1>Batch 04 - 10 products, 50 new images</h1><p>Each complete folder ends in -1. Click an image to view it at full size. Original photos remain in each product folder.</p>'+''.join(sections)+'</body></html>'
(base/'batch-04-preview.html').write_text(page,encoding='utf-8')
print(json.dumps(report,indent=2))


