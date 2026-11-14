"""Keep scheduled generation backed up while worker agents produce images."""
from pathlib import Path
import datetime,hashlib,json,subprocess,time
REPO=Path(__file__).resolve().parents[2];REVIEW=REPO/'PRODUCT_PHOTOS/_Review';HELPER=REVIEW/'end100_2316_2415_checkpoint.py';STOP=Path('/tmp/stop-end100-2316-2415-watch')
def command(args):
 result=subprocess.run(args,cwd=REPO,text=True,capture_output=True)
 if result.returncode:raise RuntimeError((result.stderr or result.stdout)[-1800:])
 return result.stdout.strip()
def notes_fingerprint(data):
 digest=hashlib.sha256()
 for row in data['products']:
  p=REPO/'PRODUCT_PHOTOS'/row['folder']/'GENERATION_NOTES.json'
  digest.update(row['folder'].encode())
  if p.exists():digest.update(p.read_bytes())
 return digest.hexdigest()
def checkpoint():
 while True:
  before=json.loads((REVIEW/'END100_2316_2415_BACKUPS.json').read_text()) if (REVIEW/'END100_2316_2415_BACKUPS.json').exists() else []
  command(['python',str(HELPER),'backup'])
  after=json.loads((REVIEW/'END100_2316_2415_BACKUPS.json').read_text()) if (REVIEW/'END100_2316_2415_BACKUPS.json').exists() else []
  if len(after)==len(before):break
 command(['python',str(HELPER),'sync'])
 dirty=command(['git','diff','--cached','--name-only'])
 if dirty:
  command(['git','-c','user.name=heshannamal','-c','user.email=heshannamal@users.noreply.github.com','commit','-m','Preserve scheduled product-photo generation checkpoint'])
 command(['git','-c','pack.threads=2','-c','pack.window=0','push','origin','HEAD:main'])
try:old=json.loads(command(['git','show','HEAD:PRODUCT_PHOTOS/_Review/END100_2316_2415_PROGRESS.json']))
except Exception:old={'saved_images':0,'completed_products':0}
old_notes=None
while not STOP.exists():
 try:
  command(['python',str(HELPER),'reconcile']);data=json.loads((REVIEW/'END100_2316_2415_PROGRESS.json').read_text())
  print(json.dumps({k:v for k,v in data.items() if k!='products'}),flush=True)
  notes=notes_fingerprint(data)
  if notes!=old_notes or data['saved_images']-old['saved_images']>=5 or data['completed_products']-old['completed_products']>=1:
   checkpoint();old=data;old_notes=notes
   print('GITHUB_CHECKPOINT_UPLOADED',flush=True)
 except Exception as e:print('CHECKPOINT_RETRY_NEEDED: '+str(e),flush=True)
 for _ in range(30):
  if STOP.exists():break
  time.sleep(2)
print('Checkpoint watcher stopped.',flush=True)
