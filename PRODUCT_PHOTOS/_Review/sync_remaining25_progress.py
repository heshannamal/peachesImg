"""Stage saved, hash-matched outputs and scope metadata for GitHub recovery."""
from pathlib import Path
import hashlib,json,subprocess
repo=Path(__file__).resolve().parents[2];root=repo/'PRODUCT_PHOTOS';review=root/'_Review'
scope=json.loads((review/'REMAINING25.json').read_text());paths=[]
for pid in scope['product_ids']:
 folder=next(root.glob(pid+'_*'));notes_path=folder/'GENERATION_NOTES.json'
 paths += [str(f.relative_to(repo)) for f in (folder/'Originals').glob('*') if f.is_file()]
 if not notes_path.exists():continue
 notes=json.loads(notes_path.read_text());paths.append(str(notes_path.relative_to(repo)))
 for record in notes.get('records',[]):
  if not record.get('saved_file'):continue
  f=folder/record['saved_file']
  if f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==record.get('sha256'):paths.append(str(f.relative_to(repo)))
 paths += [str(f.relative_to(repo)) for f in (folder/'Rejected').glob('*') if f.is_file()]
for tracked in subprocess.check_output(['git','ls-files'],cwd=repo,text=True).splitlines():
 parts=tracked.split('/')
 if len(parts)>2 and parts[0]=='PRODUCT_PHOTOS' and parts[1][:4] in scope['product_ids'] and not (repo/tracked).exists():paths.append(tracked)
for pattern in ['REMAINING25*.json','verify_remaining25.py','checkpoint_remaining25.py','sync_remaining25_progress.py','products.json','RUN_100_PROGRESS.json','CONTINUE_PRODUCT_PHOTOS.md']:
 paths += [str(f.relative_to(repo)) for f in review.glob(pattern) if f.is_file()]
subprocess.run(['git','add','--pathspec-from-file=-','--pathspec-file-nul'],cwd=repo,input=b'\0'.join(p.encode() for p in sorted(set(paths)))+b'\0',check=True)
print('Staged recovery checkpoint.')
