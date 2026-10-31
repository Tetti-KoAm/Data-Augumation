from PIL import Image,ImageOps,ImageDraw
from pathlib import Path
D=Path('tmp/public_comparison_20261023')
for start in range(1,30,6):
 im=Image.new('RGB',(1280,3*380),'#ddd');draw=ImageDraw.Draw(im)
 for k,i in enumerate(range(start,min(30,start+6))):
  s=Image.open(D/f'slide-{i:02}.png').resize((640,360));im.paste(s,((k%2)*640,(k//2)*380));draw.text(((k%2)*640+10,(k//2)*380+360),str(i),fill='black')
 im.save(D/f'contact-{start}.png')
