"""Atomically claim the next highest two product IDs after finishing prior work."""
import argparse,fcntl,json,os
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--worker',required=True);a=p.parse_args();review=Path(__file__).resolve().parent;root=review.parent;path=review/'END100_2416_2517_DISPATCH.json';names=['01_White-Background.png','02_Styled-Background.png','03_Lifestyle.png','04_Detail.png','05_Promotional.png']
with (review/'.end100_2416_2517_dispatch.lock').open('a+') as lock:
 fcntl.flock(lock,fcntl.LOCK_EX);d=json.loads(path.read_text());previous=d.get('assigned',{}).get(a.worker,[])
 for pid in previous:
  f=next(root.glob(pid+'_*'));n=json.loads((f/'GENERATION_NOTES.json').read_text()) if (f/'GENERATION_NOTES.json').exists() else {};terminal=str(n.get('status','')).lower() in {'partial_corrective_spent','partial_corrective_spent_result_lost'} or f.name.endswith('-1') or (str(n.get('status','')).lower().startswith('blocked') or str(n.get('status','')).lower() in {'moderation_blocked','output_moderation_blocked'}) or all((f/'New'/v).exists() for v in names)
  if not terminal:raise SystemExit('Prior product still partial/missing: '+pid+'; retain assignment and finish or report blocker.')
 if previous:d.setdefault('assignment_history',[]).append({'worker':a.worker,'product_ids':previous})
 queue=d['next_unassigned'];pair=queue[:2];d['next_unassigned']=queue[2:];d.setdefault('assigned',{})[a.worker]=pair;tmp=path.with_suffix('.claim.tmp');tmp.write_text(json.dumps(d,indent=2)+'\n');os.replace(tmp,path);print(json.dumps({'worker':a.worker,'product_ids':pair,'remaining_unassigned':len(d['next_unassigned'])}))
