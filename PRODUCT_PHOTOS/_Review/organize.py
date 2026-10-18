from pathlib import Path
import csv, shutil, json

root=Path(r'E:\CEAESSON WHOLESALE ITEMS')
review=root/'PRODUCT_PHOTOS'/'_Review'
assert not (review/'FINALIZED.json').exists(), 'Initial organization has been finalized; use the saved inventory for further updates.'
rows=list(csv.DictReader((review/'inventory.csv').open(encoding='utf-8-sig')))
# Visually reviewed product groups. Numbers refer to the contact-sheet image IDs.
groups=[
('Rose-Hair-Clips',[1]),('Mixed-Accessories-Assortment',[2]),
('Silver-Tone-Ring-Assortment',[3,10]),('Gold-Tone-Ring-Assortment',[4,9]),
('Gold-Tone-Black-Stone-Bracelet',[5]),('Gold-Tone-Earring-Assortment',[6]),
('Pendant-Necklace-Assortment',[7]),('Stud-Earring-Assortment',[8]),
('Butterfly-Pendant-Necklace',[11,14]),('Hair-Clip-Assortment',[12]),
('Mini-Colourful-Hair-Claws',[13]),('Metal-Hair-Barrettes',[15]),
('Colourful-Beaded-Bracelet-Assortment',[16]),('Shell-Accessory-Assortment',[17]),
('Shell-Keyring-Assortment',[18]),('Vehicle-Design-Hair-Clips',[19]),
('Pink-Cord-Bracelet-Assortment',[20,21]),('Sunglasses-Assortment-Display',[22]),
('Plush-Bunny-Ear-Headbands',[23]),('Doves-Perfume',[24]),
('Gold-Tone-Deer-Pendant-Necklace',[25]),('Flower-Stud-Earrings',[26]),
('Star-Pendant-Necklace',[27]),('Gold-Tone-Bracelets',[28]),
('Flower-Hair-Claws',[29]),('Colourful-Mini-Hair-Claws',[30]),
('Daisy-Stud-Earrings',[31]),('Colourful-Mini-Container-Set',[32]),
('Coloured-Contact-Lenses',[33]),('Dark-Craft-Beads',[34]),
('Pale-Green-Craft-Beads',[35]),('Pink-Strap-Water-Bottle',[36]),
('Small-Round-Hair-Clips',[37]),('Large-Round-Hair-Clips',[38]),
('LED-Light-Up-Accessories',[39]),('Colourful-Character-Water-Bottles',[40]),
('Brown-Beaded-Necklace-Assortment',[41]),('Colourful-Cosmetic-Pot-Assortment',[42]),
('Colourful-Pencil-Assortment',[43]),('Floral-Decorative-Pins',[44]),
('Faceted-Beaded-Bracelets',[45]),('Plush-Character-Hair-Claws',[46]),
('Pastel-Character-Hair-Claws',[47,48]),('Colourful-Flower-Ring-Assortment',[49]),
('Mini-Bottle-Accessory-Assortment',[50]),('White-Beaded-Necklace',[51]),
('White-Beaded-Bracelet',[52]),('Pink-Bunny-Ear-Headbands',[53]),
('Plush-Animal-Ear-Headbands',[54]),('Black-And-Neutral-Hair-Claw-Assortment',[55]),
('Red-And-Gold-Tone-Earrings',[56]),('Colourful-Rectangular-Hair-Clip-Assortment',[57]),
('Neutral-Hair-Claw-Assortment',[58]),('Brown-And-Black-Hair-Claws',[59]),
('Mixed-Shape-Neutral-Hair-Claws',[60]),('Large-Rectangular-Hair-Claws',[61]),
('Mini-Neutral-Hair-Claw-Sets',[62]),('Sequin-Animal-Ear-Headbands',[63]),
('Character-Hair-Accessory-Cards',[64]),('Pastel-Hair-Accessory-Cards',[65]),
('Small-Packaged-Accessory-Assortment',[66]),('Pink-Decorative-Hair-Clips',[67]),
('Pastel-Decorative-Hair-Clips',[68]),('Printed-Fabric-Headbands',[69]),
('Watermelon-Design-Hot-Water-Bottle',[70]),('Pom-Pom-Wallets',[71]),
('Small-Flap-Wallets',[72]),('Butterfly-Wand-And-Tiara-Set',[73]),
('Small-Pendant-Necklace-Assortment',[74]),('Colourful-Bunny-Ear-Headbands',[75]),
('Sri-Lanka-Shell-Souvenir',[76]),('Statement-Necklace-Assortment',[77]),
('Butterfly-Hair-Accessory-Cards',[78]),('Floral-Bunny-Ear-Headbands',[79]),
('Colourful-Zip-Wallets',[80]),
]
for line in (review/'groups-extra.txt').read_text(encoding='utf-8').splitlines():
    if not line.strip(): continue
    ids,name=line.split('|',1)
    groups.append((name,[int(i) for i in ids.split(',')]))
all_ids=[i for _,ids in groups for i in ids]
assert len(all_ids)==len(set(all_ids)), 'A source image was assigned twice'
manifest=[]
number=0
for row in rows:
    row['product_folder']=''
    row['review_status']='pending'
for name,ids in groups:
    if name=='Store-Contact-Reference':
        for i in ids:
            rows[i-1]['review_status']='non-product-store-reference'
        continue
    number+=1
    folder=root/'PRODUCT_PHOTOS'/f'{number:04}_{name}-0'
    (folder/'Originals').mkdir(parents=True,exist_ok=True)
    (folder/'New').mkdir(exist_ok=True)
    for image_id in ids:
        row=rows[image_id-1]
        dest=folder/'Originals'/row['filename']
        if not dest.exists(): shutil.copy2(root/row['filename'],dest)
        row['product_folder']=folder.name
        row['review_status']='visually-grouped-provisional-name'
    manifest.append({'product_id':f'{number:04}','folder':folder.name,'source_image_ids':ids,'new_images':0,'generation_complete':False})
with (review/'inventory.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.DictWriter(f,fieldnames=rows[0].keys());w.writeheader();w.writerows(rows)
(review/'products.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
(root/'PRODUCT_PHOTOS'/'README.txt').write_text('Folder suffix -0 = five new images pending or incomplete.\nFolder suffix -1 = all five new images generated and checked.\nOriginals are copies; source files in the parent folder are preserved.\nProduct names are provisional visual descriptions, not verified brands or specifications.\nUser selected option A: a complete pack or assortment is one product. Do not split its individual items.\nInitial visual grouping merges clear repeated views; similar packs may still need SKU confirmation.\nSee _Review/inventory.csv for reviewed and pending source files.\nNo new product images have been generated yet.\n',encoding='utf-8')
print(f'Created {len(groups)} pending product folders from {sum(len(ids) for _,ids in groups)} reviewed source photos. Remaining photos: {sum(r["review_status"]=="pending" for r in rows)}')
