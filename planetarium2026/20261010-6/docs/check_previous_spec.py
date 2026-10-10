from pathlib import Path
from PIL import Image, ImageOps
root=Path(__file__).resolve().parents[1]
files=list((root/'tmp/pdfs').glob('revised-*.png'))
files.sort(key=lambda p:int(p.stem.split('-')[-1]))
sheet=Image.new('RGB',(1260,1800),'#cccccc')
for i,p in enumerate(files):
 im=Image.open(p).convert('RGB')
 im.thumbnail((420,600))
 sheet.paste(im,((i%3)*420,(i//3)*600))
sheet.save(root/'tmp/pdfs/revised-all.png')
print(len(files))
