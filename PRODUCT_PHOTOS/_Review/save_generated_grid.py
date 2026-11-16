"""Preserve one native 3x2 grid and crop its five requested product views."""
import argparse,hashlib,json,os,shutil
from pathlib import Path
from PIL import Image
p=argparse.ArgumentParser();p.add_argument('--product',required=True);p.add_argument('--cache',required=True);p.add_argument('--prompt-file',required=True);a=p.parse_args()
root=Path(__file__).resolve().parent.parent;folder=next(root.glob(a.product+'_*'));source=Path(a.cache);prompt=Path(a.prompt_file).read_text();notes_path=folder/'GENERATION_NOTES.json';notes=json.loads(notes_path.read_text()) if notes_path.exists() else {'tool':'built-in image_gen','whole_assortment':True,'original_hashes':{str(f.relative_to(folder)):hashlib.sha256(f.read_bytes()).hexdigest() for f in (folder/'Originals').iterdir() if f.is_file()},'records':[]}
grid_dir=folder/'Generation_Grids';grid_dir.mkdir(exist_ok=True);grid=grid_dir/(source.stem+'.png')
if not grid.exists():shutil.copy2(source,grid)
sha=hashlib.sha256(grid.read_bytes()).hexdigest();im=Image.open(grid);width,height=im.size
if not any(r.get('sha256')==sha and r.get('saved_file')==str(grid.relative_to(folder)) for r in notes['records']):notes['records'].append({'kind':'generation_grid_source','saved_file':str(grid.relative_to(folder)),'source_output':str(source),'sha256':sha,'prompt':prompt,'checked':False,'visual_review':'Source grid preserved; individual crop records carry website-view reviews.'})
names=['01_White-Background','02_Styled-Background','03_Lifestyle','04_Detail','05_Promotional'];(folder/'New').mkdir(exist_ok=True);saved=[];skipped=[]
for i,name in enumerate(names):
 dest=folder/'New'/(name+'.png')
 if dest.exists():skipped.append(name);continue
 col=i%3;row=i//3;box=(round(col*width/3),round(row*height/2),round((col+1)*width/3),round((row+1)*height/2));im.crop(box).save(dest,'PNG');saved.append(str(dest))
 notes['records'].append({'saved_file':str(dest.relative_to(folder)),'source_output':str(source),'prompt':prompt,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'checked':False,'generation_method':'native_five_style_grid_cropped','grid_source_file':str(grid.relative_to(folder)),'grid_sha256':sha,'grid_dimensions':[width,height],'crop_box':list(box)})
notes.update(status='in_progress',quality_standard='website-ready; native grid cropped as explicitly requested; preserve identity/count/shapes/colours',generation_workflow='One native3x2grid; first5cells are views01–05, sixthcellunused; existing outputs preserved')
tmp=notes_path.with_suffix('.tmp');tmp.write_text(json.dumps(notes,indent=2)+'\n');os.replace(tmp,notes_path)
print(json.dumps({'product':a.product,'grid':str(grid),'grid_dimensions':[width,height],'saved':saved,'preserved_existing':skipped}))
