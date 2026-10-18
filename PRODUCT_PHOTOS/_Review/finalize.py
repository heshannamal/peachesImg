from pathlib import Path
import csv, json, hashlib, shutil

root=Path(r'E:\CEAESSON WHOLESALE ITEMS')
base=root/'PRODUCT_PHOTOS'; review=base/'_Review'
assert not (review/'FINALIZED.json').exists(), 'Already finalized'
rows=list(csv.DictReader((review/'inventory.csv').open(encoding='utf-8-sig')))
products=json.loads((review/'products.json').read_text(encoding='utf-8'))
by_image={i:k for k,p in enumerate(products) for i in p['source_image_ids']}
parents=list(range(len(products)))
def find(i):
    while parents[i]!=i:
        parents[i]=parents[parents[i]];i=parents[i]
    return i
def union(a,b):
    a,b=find(a),find(b)
    if a!=b:parents[max(a,b)]=min(a,b)
for pair in csv.DictReader((review/'near-duplicate-candidates.csv').open(encoding='utf-8-sig')):
    a,b=int(pair['image_id_a']),int(pair['image_id_b'])
    if a in by_image and b in by_image:union(by_image[a],by_image[b])
refs=('Mixed-Product-Catalog-Reference','Phone-Compatibility-Reference','Necklace-Catalog-Reference')
archive=review/'_Merged-Folders';archive.mkdir(exist_ok=True)
def safe_move(source,dest):
    assert source.resolve().is_relative_to(base.resolve())
    assert dest.resolve().is_relative_to(review.resolve())
    assert not dest.exists()
    dest.parent.mkdir(parents=True,exist_ok=True)
    shutil.move(str(source),str(dest))
final=[];merged=0
for k,p in enumerate(products):
    if find(k)!=k:continue
    members=[q for j,q in enumerate(products) if find(j)==k]
    ids=sorted(i for q in members for i in q['source_image_ids'])
    target=base/p['folder']
    for i in ids:
        row=rows[i-1];dest=target/'Originals'/row['filename']
        if not dest.exists():shutil.copy2(root/row['filename'],dest)
        row['product_folder']=p['folder']
    for q in members[1:]:
        obsolete=base/q['folder']
        assert not any((obsolete/'New').iterdir()), 'Generated output exists; keep it'
        for f in (obsolete/'Originals').iterdir():
            source=root/f.name
            assert source.exists() and hashlib.sha256(f.read_bytes()).digest()==hashlib.sha256(source.read_bytes()).digest()
        safe_move(obsolete,archive/q['folder']);merged+=1
    p['source_image_ids']=ids
    if any(label in p['folder'] for label in refs):
        safe_move(target,review/'References'/p['folder'])
        for i in ids:
            rows[i-1]['review_status']='non-product-reference'
            rows[i-1]['product_folder']=''
        continue
    expected={rows[i-1]['filename'] for i in ids}
    for f in (target/'Originals').iterdir():
        if f.name not in expected:
            assert hashlib.sha256(f.read_bytes()).digest()==hashlib.sha256((root/f.name).read_bytes()).digest()
            safe_move(f,review/'_Reassigned-Originals'/p['folder']/f.name)
    p['generation_status']='pending'
    p['grouping_status']='initial-visual-grouping'
    p['required_new_images']=5
    final.append(p)
for row in rows:
    if row['review_status']=='non-product-store-reference':
        dest=review/'References'/row['filename'];dest.parent.mkdir(exist_ok=True)
        if not dest.exists():shutil.copy2(root/row['filename'],dest)
        row['review_status']='non-product-reference'
for row in rows:
    assert row['review_status']!='pending'
    assert hashlib.sha256((root/row['filename']).read_bytes()).hexdigest()==row['sha256'], 'Source changed'
    if row['product_folder']:
        assert hashlib.sha256((base/row['product_folder']/'Originals'/row['filename']).read_bytes()).hexdigest()==row['sha256'], 'Copy differs'
with (review/'inventory.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
(review/'products.json').write_text(json.dumps(final,indent=2),encoding='utf-8')
with (base/'product-catalog.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f);w.writerow(['product_id','folder','original_photos','new_images','required_new_images','status'])
    for p in final:w.writerow([p['product_id'],p['folder'],len(p['source_image_ids']),0,5,'pending'])
summary={'source_photos':len(rows),'initial_product_groups':len(final),'product_source_photos':sum(bool(r['product_folder']) for r in rows),'reference_photos':sum(not r['product_folder'] for r in rows),'merged_folders':merged,'new_images_generated':0,'videos_not_reviewed':[p.name for p in root.glob('*.mp4')],'source_and_copy_hashes_verified':True,'assortment_policy':'A - whole pack is one product','grouping_note':'Initial visual groups; similar packs may still require SKU confirmation before generation.'}
(review/'FINALIZED.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
print(json.dumps(summary,indent=2))
