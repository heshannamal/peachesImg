from pathlib import Path
import csv,json
base=Path(r'E:\CEAESSON WHOLESALE ITEMS\PRODUCT_PHOTOS')
old='0026_Colourful-Mini-Hair-Claws-0';new='0026_Colourful-Mini-Hair-Claws-1'
review=base/'_Review'
assert len(list((base/new/'New').glob('*.png')))==5
products=json.loads((review/'products.json').read_text(encoding='utf-8'))
for p in products:
    if p['product_id']=='0026':
        assert p['folder'] in (old,new)
        p.update(folder=new,new_images=5,generation_complete=True,generation_status='complete',style_review='awaiting-user-review')
(review/'products.json').write_text(json.dumps(products,indent=2),encoding='utf-8')
for path in [review/'inventory.csv',base/'product-catalog.csv']:
    with path.open(encoding='utf-8-sig',newline='') as f:
        reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
    for row in rows:
        key='product_folder' if 'product_folder' in row else 'folder'
        if row[key] in (old,new):
            row[key]=new
            if 'new_images' in row:row.update(new_images=5,status='complete')
    with path.open('w',encoding='utf-8-sig',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
summary=json.loads((review/'FINALIZED.json').read_text(encoding='utf-8'))
summary.update(new_images_generated=sum(p['new_images'] for p in products),completed_product_groups=sum(p['generation_complete'] for p in products))
(review/'FINALIZED.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
readme=base/'README.txt'
readme.write_text(readme.read_text(encoding='utf-8').replace('No new product images have been generated yet.','Generation progress is recorded in product-catalog.csv. Sample product 0026 has five generated images; its folder ends in -1.'),encoding='utf-8')
print('Sample 0026 complete: five images saved; folder, inventory, catalogue and progress updated.')
