"""Verify remaining twenty-five-product checkpoint without changing photos."""
import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parent.parent
scope=json.loads((root/'_Review/REMAINING25.json').read_text())
variants=['01_White-Background.png','02_Styled-Background.png','03_Lifestyle.png','04_Detail.png','05_Promotional.png']
rows=[]
for pid in scope['product_ids']:
 folders=list(root.glob(pid+'_*'));assert len(folders)==1,pid
 folder=folders[0]; notes=json.loads((folder/'GENERATION_NOTES.json').read_text());errors=[]
 originals={f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in (folder/'Originals').iterdir() if f.is_file()}
 assert originals==scope['original_sha256'][pid],f'{pid}: original changed'
 hashes=[]
 for name in variants:
  f=folder/'New'/name
  if not f.exists():errors.append('missing '+name);continue
  sha=hashlib.sha256(f.read_bytes()).hexdigest();hashes.append(sha)
  records=[r for r in notes.get('records',[]) if r.get('saved_file')=='New/'+name and r.get('checked') is True]
  if not records:errors.append('unchecked '+name)
  elif not any(r.get('sha256')==sha for r in records):errors.append('hash mismatch '+name)
 if len(hashes)!=len(set(hashes)):errors.append('duplicate images')
 if not folder.name.endswith('-1'):errors.append('pending suffix')
 rows.append({'product_id':pid,'folder':folder.name,'saved_images':len(hashes),'originals_unchanged':True,'complete':not errors,'errors':errors})
report={'completed_products':sum(r['complete'] for r in rows),'saved_images':sum(r['saved_images'] for r in rows),'products':rows}
(root/'_Review/REMAINING25_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='products'}))
