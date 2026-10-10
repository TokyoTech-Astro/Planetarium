from pathlib import Path
import subprocess
import pdfplumber
from PIL import Image
root=Path(__file__).resolve().parents[1]
pdf=next((root/'output/pdf').glob('*.pdf'))
doc=pdfplumber.open(pdf)
out=root/'tmp/pdfs'
out.mkdir(parents=True,exist_ok=True)
sheet=Image.new('RGB',(1260,1190),'#cccccc')
subprocess.run([r'C:\Users\kazu2\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe','-r','72','-png',str(pdf),str(out/'page')],check=True)
for i,page in enumerate(doc.pages):
    im=Image.open(out/f'page-{i+1}.png')
    im.thumbnail((420,595))
    sheet.paste(im,((i%3)*420,(i//3)*595))
    print(i+1,len(page.extract_text()),max(ch['bottom'] for ch in page.chars))
sheet.save(out/'overview.png')
