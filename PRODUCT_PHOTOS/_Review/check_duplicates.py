from pathlib import Path
from PIL import Image, ImageOps
import numpy as np, csv
r=Path(r'E:\CEAESSON WHOLESALE ITEMS\PRODUCT_PHOTOS\_Review')
hashes=[]; thumbs=[]
for p in sorted(r.glob('contact-*.jpg')):
    sheet=Image.open(p)
    for k in range(80):
        i=(int(p.stem.split('-')[1])-1)*80+k+1
        if i>3156: break
        x=k%8*200;y=k//8*200
        im=sheet.crop((x,y,x+200,y+174))
        g=np.asarray(im.convert('L').resize((9,8)),dtype=np.int16)
        h=0
        for bit in (g[:,1:]>g[:,:-1]).flatten(): h=(h<<1)|int(bit)
        hashes.append(h);thumbs.append(np.asarray(im.resize((32,32)),dtype=np.int16))
found=[]
for i,h in enumerate(hashes):
    for j in range(i):
        if (h^hashes[j]).bit_count()>3: continue
        difference=float(np.abs(thumbs[i]-thumbs[j]).mean())
        if difference<2.3: found.append((j+1,i+1,round(difference,3)))
with (r/'near-duplicate-candidates.csv').open('w',newline='',encoding='utf-8-sig') as f:
    w=csv.writer(f);w.writerow(['image_id_a','image_id_b','mean_pixel_difference']);w.writerows(found)
print('Strict near-identical image candidates:',len(found))
print(found[:100])
