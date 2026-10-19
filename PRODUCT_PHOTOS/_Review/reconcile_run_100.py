"""Reconcile reviewed product folders and write a resumable batch checkpoint."""
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REVIEW = ROOT / '_Review'
VARIANTS = ['01_White-Background.png', '02_Styled-Background.png',
            '03_Lifestyle.png', '04_Detail.png', '05_Promotional.png']


def atomic_json(path, value):
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value, indent=2) + '\n')
    os.replace(temp, path)


def main():
    queue = json.loads((REVIEW / 'RUN_100.json').read_text())
    products = json.loads((REVIEW / 'products.json').read_text())
    index = {p['product_id']: p for p in products}
    rows = []
    for item in queue['products']:
        pid = item['product_id']
        matches = list(ROOT.glob(pid + '_*'))
        if len(matches) != 1:
            rows.append({'product_id': pid, 'status': 'folder-conflict'})
            continue
        folder = matches[0]
        files = [folder / 'New' / name for name in VARIANTS]
        present = [str(f.relative_to(ROOT)) for f in files if f.is_file()]
        notes_path = folder / 'GENERATION_NOTES.json'
        try:
            notes = json.loads(notes_path.read_text())
        except (OSError, ValueError):
            notes = {}
        records = notes.get('records', [])
        checked = {r.get('saved_file') for r in records if r.get('checked') is True}
        complete = (folder.name.endswith('-1') and len(present) == 5
                    and all('New/' + name in checked for name in VARIANTS))
        review_needed = not complete and notes.get('status') == 'saved_review_needed'
        if complete:
            index[pid].update(folder=folder.name, new_images=5,
                              generation_complete=True,
                              generation_status='complete',
                              generation_batch='run-100-2026-10-19',
                              style_review='visually-checked')
        else:
            index[pid].update(folder=folder.name, new_images=len(present),
                              generation_complete=False,
                              generation_status=('review_needed' if review_needed else
                                                 ('in_progress' if present else 'pending')))
        rows.append({'product_id': pid, 'folder': folder.name,
                     'status': ('complete' if complete else ('review_needed' if review_needed else
                                                            ('partial' if present else 'pending'))),
                     'saved_images': len(present), 'files': present})
    atomic_json(REVIEW / 'products.json', products)
    snapshot = {'updated_at': datetime.now(timezone.utc).isoformat(),
                'target_products': 100,
                'completed_products': sum(r['status'] == 'complete' for r in rows),
                'review_needed_products': sum(r['status'] == 'review_needed' for r in rows),
                'saved_images': sum(r.get('saved_images', 0) for r in rows),
                'products': rows}
    atomic_json(REVIEW / 'RUN_100_PROGRESS.json', snapshot)
    print(json.dumps({k: v for k, v in snapshot.items() if k != 'products'}))


if __name__ == '__main__':
    main()
