from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
import csv, hashlib

root = Path(r'E:\CEAESSON WHOLESALE ITEMS')
out = root / 'PRODUCT_PHOTOS' / '_Review'
files = sorted(root.glob('*.jpg'))
rows = []
for i, p in enumerate(files, 1):
    rows.append({'image_id':i,'filename':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'product_folder':'','review_status':'pending'})
with (out/'inventory.csv').open('w', newline='', encoding='utf-8-sig') as f:
    w=csv.DictWriter(f, fieldnames=rows[0].keys()); w.writeheader(); w.writerows(rows)
for start in range(0,len(files),80):
    sheet=Image.new('RGB',(1600,2000),'#eeeeee'); draw=ImageDraw.Draw(sheet)
    for k,p in enumerate(files[start:start+80]):
        x=(k%8)*200; y=(k//8)*200
        try:
            with Image.open(p) as im:
                thumb=ImageOps.contain(ImageOps.exif_transpose(im).convert('RGB'),(194,174))
                sheet.paste(thumb,(x+(200-thumb.width)//2,y))
            draw.text((x+5,y+177),str(start+k+1),fill='black')
        except Exception as e: draw.text((x+5,y+20),'Unreadable',fill='red')
    sheet.save(out/f'contact-{start//80+1:02}.jpg',quality=90)
print(f'Inventoried {len(files)} photos; created {(len(files)+79)//80} review sheets.')
