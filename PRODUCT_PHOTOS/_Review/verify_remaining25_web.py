"""Check completed-product image URLs after their GitHub upload."""
import concurrent.futures,json,time,urllib.request
from urllib.parse import quote
from pathlib import Path
root=Path(__file__).resolve().parent.parent;review=root/'_Review'
verification=json.loads((review/'REMAINING25_VERIFICATION.json').read_text())
urls=[]
for product in verification['products']:
 if product['complete']:
  urls += ['https://raw.githubusercontent.com/heshannamal/peachesImg/main/PRODUCT_PHOTOS/'+quote(str(p.relative_to(root)),safe='/') for p in sorted((root/product['folder']/'New').glob('*.png'))]
def check(url):
 for attempt in range(3):
  try:
   with urllib.request.urlopen(urllib.request.Request(url,method='HEAD'),timeout=30) as r:result={'url':url,'status':r.status,'content_type':r.headers.get('Content-Type','')}
   if result['status']==200 and result['content_type'].startswith('image/'):return result
  except Exception as e:result={'url':url,'error':str(e)}
  if attempt<2:time.sleep(2)
 return result
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:results=list(pool.map(check,urls))
report={'total':len(results),'verified':sum(r.get('status')==200 and r.get('content_type','').startswith('image/') for r in results),'results':results}
(review/'REMAINING25_WEB_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n');print({k:v for k,v in report.items() if k!='results'});assert report['verified']==report['total']
