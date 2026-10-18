from pathlib import Path
import json
b=Path(r'E:\CEAESSON WHOLESALE ITEMS\PRODUCT_PHOTOS\_Review')
p=json.loads((b/'products.json').read_text(encoding='utf-8'))
notes={'0013':'Broad keyring stock display','0015':'Multiple keyring stock displays','0018':'Broad sunglasses stock display','0029':'Composite reference needs source product photo','0035':'Blurred product needs clearer source','0037':'Cropped stock strands need grouping review','0049':'Bottom headbands cut off','0052':'Dense pack cut by frame'}
for item in p:
    if item['product_id'] in notes and not item['generation_complete']:
        item.update(grouping_status='needs-pack-grouping-review',review_note=notes[item['product_id']])
(b/'products.json').write_text(json.dumps(p,indent=2),encoding='utf-8')
print('Saved review flags for incomplete source photos.')
