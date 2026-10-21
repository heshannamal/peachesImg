"""Reconcile, preserve and verify only the scheduled0153–0252 photo queue."""
import argparse,concurrent.futures,hashlib,json,os,subprocess,time,urllib.request,zipfile
from datetime import datetime,timezone
from pathlib import Path
from urllib.parse import quote
ROOT=Path(__file__).resolve().parent.parent; REVIEW=ROOT/'_Review'; REPO=ROOT.parent
PLAN=json.loads((REVIEW/'SCHEDULED_NEXT_100_0153_0252.json').read_text())
NAMES=['01_White-Background.png','02_Styled-Background.png','03_Lifestyle.png','04_Detail.png','05_Promotional.png']
def read(p,default=None):
 try:return json.loads(p.read_text())
 except (FileNotFoundError,json.JSONDecodeError):return {} if default is None else default

def write(p,data):
 tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(data,indent=2)+'\n');os.replace(tmp,p)

def reconcile():
 inventory=read(REVIEW/'products.json',[]); index={p['product_id']:p for p in inventory};rows=[]
 for pid in PLAN['product_ids']:
  folders=list(ROOT.glob(pid+'_*'));assert len(folders)==1,(pid,'folder conflict')
  folder=folders[0];notes=read(folder/'GENERATION_NOTES.json');records=notes.get('records',[])
  originals={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in (folder/'Originals').iterdir() if p.is_file()}
  assert originals==PLAN['original_sha256'][pid],(pid,'ORIGINAL HASH MISMATCH')
  present=[];checked=[];errors=[];hashes=[]
  for name in NAMES:
   f=folder/'New'/name
   if not f.exists():continue
   sha=hashlib.sha256(f.read_bytes()).hexdigest();hashes.append(sha);present.append(name)
   matches=[r for r in records if r.get('saved_file')=='New/'+name and r.get('sha256')==sha]
   if any(r.get('checked') is True for r in matches):checked.append(name)
   else:errors.append('unreviewed or unrecorded: '+name)
  if len(set(hashes))!=len(hashes):errors.append('duplicate generated files')
  complete=folder.name.endswith('-1') and len(checked)==5 and not errors
  blocked=str(notes.get('status','')).startswith('blocked')
  status='complete' if complete else ('blocked' if blocked else ('partial' if present else 'pending'))
  if folder.name.endswith('-1') and not complete:errors.append('incorrect complete suffix')
  index[pid].update(folder=folder.name,new_images=len(present),generation_complete=complete,generation_status=('complete' if complete else (notes.get('status') if blocked else ('in_progress' if present else 'pending'))))
  if complete:index[pid].update(generation_batch='scheduled-0153-0252',style_review='visually-checked')
  rows.append({'product_id':pid,'folder':folder.name,'status':status,'saved_images':len(present),'checked_images':len(checked),'files':['New/'+n for n in present],'missing_images':['New/'+n for n in NAMES if n not in present],'review_needed_images':['New/'+n for n in present if n not in checked],'notes_status':notes.get('status'),'errors':errors,'originals_unchanged':True})
 result={'updated_at':datetime.now(timezone.utc).isoformat(),'target_products':100,'target_images':500,'completed_products':sum(r['status']=='complete' for r in rows),'partial_products':sum(r['status']=='partial' for r in rows),'pending_products':sum(r['status']=='pending' for r in rows),'blocked_products':sum(r['status']=='blocked' for r in rows),'saved_images':sum(r['saved_images'] for r in rows),'checked_images':sum(r['checked_images'] for r in rows),'products':rows}
 write(REVIEW/'products.json',inventory);write(REVIEW/'NEXT100_PROGRESS.json',result)
 state=read(REVIEW/'NEXT100_STATE.json');state.update({k:v for k,v in result.items() if k!='products'});write(REVIEW/'NEXT100_STATE.json',state)
 print(json.dumps({k:v for k,v in result.items() if k!='products'}));return result

def sync():
 paths=[]
 for pid in PLAN['product_ids']:
  folder=next(ROOT.glob(pid+'_*'));notes_path=folder/'GENERATION_NOTES.json';notes=read(notes_path)
  paths.extend(p for p in (folder/'Originals').glob('*') if p.is_file())
  if notes_path.exists():paths.append(notes_path)
  for record in notes.get('records',[]):
   if not record.get('saved_file'):continue
   f=folder/record['saved_file']
   if f.is_file() and hashlib.sha256(f.read_bytes()).hexdigest()==record.get('sha256'):paths.append(f)
  paths.extend(p for p in (folder/'Rejected').rglob('*') if p.is_file())
 selected=[str(p.relative_to(REPO)) for p in paths]
 for tracked in subprocess.check_output(['git','ls-files'],cwd=REPO,text=True).splitlines():
  parts=tracked.split('/')
  if len(parts)>2 and parts[0]=='PRODUCT_PHOTOS' and parts[1][:4] in PLAN['product_ids'] and not (REPO/tracked).exists():selected.append(tracked)
 for pattern in ['NEXT100*.json','next100_checkpoint.py','next100_watch.py','products.json','CONTINUE_PRODUCT_PHOTOS.md']:
  selected.extend(str(p.relative_to(REPO)) for p in REVIEW.glob(pattern))
 subprocess.run(['git','add','--pathspec-from-file=-','--pathspec-file-nul'],cwd=REPO,input=b'\0'.join(p.encode() for p in sorted(set(selected)))+b'\0',check=True)
 print('Scheduled queue recovery files staged.')

def backup(final=False):
 result=read(REVIEW/'NEXT100_PROGRESS.json');manifest=read(REVIEW/'NEXT100_BACKUPS.json',[]);covered={pid for item in manifest for pid in item['product_ids']};new=[r for r in result['products'] if r['status']=='complete' and r['product_id'] not in covered]
 if len(new)<5 and not final:print('Fewer than five new completed products; retaining partials.');return
 if not new and not final:return
 group=new[:5] if not final else new
 out=Path('/workspace/product-photo-backups');out.mkdir(exist_ok=True)
 target=out/(f'next100-completed-{len(covered)+1:03d}-to-{len(covered)+len(group):03d}.zip' if not final else 'next100-latest-recovery-checkpoint.zip')
 rows=group if not final else [r for r in result['products'] if r['saved_images'] or r['status']=='blocked']
 with zipfile.ZipFile(target,'w',zipfile.ZIP_STORED) as z:
  for row in rows:
   for p in (ROOT/row['folder']).rglob('*'):
    if p.is_file():z.write(p,p.relative_to(REPO))
  z.writestr('CHECKPOINT.json',json.dumps({'completed_products':[r for r in rows if r['status']=='complete'],'progress':result},indent=2))
 manifest.append({'product_ids':[r['product_id'] for r in group],'archive':target.name,'created_at':datetime.now(timezone.utc).isoformat()});write(REVIEW/'NEXT100_BACKUPS.json',manifest);print(str(target))

def web():
 result=read(REVIEW/'NEXT100_PROGRESS.json');urls=[]
 for row in result['products']:
  if row['status']=='complete':urls.extend('https://raw.githubusercontent.com/heshannamal/peachesImg/main/PRODUCT_PHOTOS/'+quote(row['folder']+'/'+f,safe='/') for f in row['files'])
 def check(url):
  for attempt in range(3):
   try:
    with urllib.request.urlopen(urllib.request.Request(url,method='HEAD'),timeout=30) as r:entry={'url':url,'status':r.status,'content_type':r.headers.get('Content-Type','')}
    if entry['status']==200 and entry['content_type'].startswith('image/'):return entry
   except Exception as e:entry={'url':url,'error':str(e)}
   if attempt<2:time.sleep(2)
  return entry
 with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:entries=list(pool.map(check,urls))
 report={'total':len(entries),'verified':sum(r.get('status')==200 and r.get('content_type','').startswith('image/') for r in entries),'results':entries};write(REVIEW/'NEXT100_WEB_VERIFICATION.json',report);print({k:v for k,v in report.items() if k!='results'});assert report['verified']==report['total']

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('action',choices=['reconcile','sync','backup','final-backup','web']);a=p.parse_args()
 if a.action=='reconcile':reconcile()
 elif a.action=='sync':sync()
 elif a.action in ['backup','final-backup']:backup(a.action=='final-backup')
 else:web()
