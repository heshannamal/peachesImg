"""Immediately preserve a generated output and its resumable review record."""
import argparse
import hashlib
import json
import shutil
from pathlib import Path

p = argparse.ArgumentParser()
p.add_argument('--product', required=True)
p.add_argument('--variant', required=True)
p.add_argument('--cache', required=True)
p.add_argument('--prompt', required=True)
a = p.parse_args()
b = Path(__file__).resolve().parent.parent
d = next(b.glob(a.product + '_*'))
out = d / 'New' / (a.variant + '.png')
out.parent.mkdir(exist_ok=True)
if out.exists():
    raise SystemExit('Refusing to overwrite existing saved image')
shutil.copy2(a.cache, out)
f = d / 'GENERATION_NOTES.json'
n = json.loads(f.read_text()) if f.exists() else {
    'tool': 'built-in image_gen', 'whole_assortment': True,
    'original_hashes': {str(x.relative_to(d)): hashlib.sha256(x.read_bytes()).hexdigest()
                        for x in (d / 'Originals').rglob('*') if x.is_file()}, 'records': []}
n['status'] = 'in_progress'
n['quality_standard'] = 'website-ready; preserve identity/count/shape/colour; accept minor cosmetic differences'
n.setdefault('records', []).append({'saved_file': str(out.relative_to(d)),
    'source_output': a.cache, 'prompt': a.prompt,
    'sha256': hashlib.sha256(out.read_bytes()).hexdigest(), 'checked': False})
f.write_text(json.dumps(n, indent=2) + '\n')
print(out)
