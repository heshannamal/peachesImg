"""Back up and stage newly completed remaining products in groups of five."""
import json,subprocess,zipfile
from pathlib import Path
from datetime import datetime,timezone
root=Path(__file__).resolve().parent.parent
review=root/'_Review';repo=root.parent
verification=json.loads((review/'REMAINING25_VERIFICATION.json').read_text())
manifest=review/'REMAINING25_CHECKPOINTS.json'
checkpoints=json.loads(manifest.read_text()) if manifest.exists() else []
covered={pid for item in checkpoints for pid in item['product_ids']}
new=[p for p in verification['products'] if p['complete'] and p['product_id'] not in covered]
if len(new)<5 and verification['completed_products']<25:
 print(json.dumps({'new_completed_waiting':len(new),'checkpoint_written':False}));raise SystemExit
if not new:
 print(json.dumps({'new_completed_waiting':0,'checkpoint_written':False}));raise SystemExit
out=Path('/workspace/product-photo-backups');out.mkdir(exist_ok=True)
selected=new[:5] if len(new)>=5 else new
ids={p['product_id'] for p in selected};start=len(covered)+1;end=len(covered)+len(selected)
archive=out/f'remaining25-completed-{start:02d}-to-{end:02d}.zip'
paths=[]
with zipfile.ZipFile(archive,'w',zipfile.ZIP_STORED) as z:
 for item in selected:
  for f in (root/item['folder']).rglob('*'):
   if f.is_file():z.write(f,f.relative_to(repo));paths.append(str(f.relative_to(repo)))
 z.writestr('CHECKPOINT.json',json.dumps({'completed_products':selected},indent=2))
for line in subprocess.check_output(['git','ls-files'],cwd=repo,text=True).splitlines():
 parts=line.split('/')
 if len(parts)>1 and parts[0]=='PRODUCT_PHOTOS' and parts[1][:4] in ids and not (repo/line).exists():paths.append(line)
checkpoints.append({'product_ids':sorted(ids),'archive':archive.name,'created_at':datetime.now(timezone.utc).isoformat()})
manifest.write_text(json.dumps(checkpoints,indent=2)+'\n')
for name in ['REMAINING25_CHECKPOINTS.json','REMAINING25_VERIFICATION.json','RUN_100_PROGRESS.json','products.json','checkpoint_remaining25.py']:
 paths.append(str((review/name).relative_to(repo)))
subprocess.run(['git','add','--pathspec-from-file=-','--pathspec-file-nul'],cwd=repo,input=b'\0'.join(p.encode() for p in sorted(set(paths)))+b'\0',check=True)
print(json.dumps({'checkpoint_written':True,'product_ids':sorted(ids),'archive':str(archive)}))
