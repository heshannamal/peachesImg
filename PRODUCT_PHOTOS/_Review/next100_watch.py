"""Keep scheduled generation backed up while worker agents produce images."""
from pathlib import Path
import datetime,json,subprocess,time
REPO=Path(__file__).resolve().parents[2];REVIEW=REPO/'PRODUCT_PHOTOS/_Review';HELPER=REVIEW/'next100_checkpoint.py';STOP=Path('/tmp/stop-next100-watch')
def command(args):
 result=subprocess.run(args,cwd=REPO,text=True,capture_output=True)
 if result.returncode:raise RuntimeError((result.stderr or result.stdout)[-1800:])
 return result.stdout.strip()
def checkpoint():
 while True:
  before=json.loads((REVIEW/'NEXT100_BACKUPS.json').read_text()) if (REVIEW/'NEXT100_BACKUPS.json').exists() else []
  command(['python',str(HELPER),'backup'])
  after=json.loads((REVIEW/'NEXT100_BACKUPS.json').read_text()) if (REVIEW/'NEXT100_BACKUPS.json').exists() else []
  if len(after)==len(before):break
 command(['python',str(HELPER),'sync'])
 dirty=command(['git','diff','--cached','--name-only'])
 if dirty:
  command(['git','-c','user.name=heshannamal','-c','user.email=heshannamal@users.noreply.github.com','commit','-m','Preserve scheduled product-photo generation checkpoint'])
 command(['git','-c','pack.threads=2','-c','pack.window=0','push','origin','HEAD:main'])
try:old=json.loads(command(['git','show','HEAD:PRODUCT_PHOTOS/_Review/NEXT100_PROGRESS.json']))
except Exception:old={'saved_images':0,'completed_products':0}
while not STOP.exists():
 try:
  command(['python',str(HELPER),'reconcile']);data=json.loads((REVIEW/'NEXT100_PROGRESS.json').read_text())
  print(json.dumps({k:v for k,v in data.items() if k!='products'}),flush=True)
  if data['saved_images']-old['saved_images']>=15 or data['completed_products']-old['completed_products']>=5:
   checkpoint();old=data
   print('GITHUB_CHECKPOINT_UPLOADED',flush=True)
 except Exception as e:print('CHECKPOINT_RETRY_NEEDED: '+str(e),flush=True)
 for _ in range(30):
  if STOP.exists():break
  time.sleep(2)
print('Checkpoint watcher stopped.',flush=True)
