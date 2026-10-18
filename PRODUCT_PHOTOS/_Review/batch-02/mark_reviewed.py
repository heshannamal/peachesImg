from pathlib import Path
import json,sys
root=Path(r'E:\CEAESSON WHOLESALE ITEMS\PRODUCT_PHOTOS\_Review\batch-02')
for key in sys.argv[1:]:
    assert len(key)==7 and key[:4].isdigit() and key[4]=='_' and key[5:].isdigit()
    p=root/(key+'.json')
    data=json.loads(p.read_text(encoding='utf-8'))
    data['checked']=True
    p.write_text(json.dumps(data,indent=2),encoding='utf-8')
print('Reviewed:',', '.join(sys.argv[1:]))
