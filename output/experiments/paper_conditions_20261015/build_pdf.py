"""Typeset the complete verified Markdown report as a Japanese PDF."""
from pathlib import Path
import re,html
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,KeepTogether,PageBreak
P=Path(__file__).resolve().parent; ROOT=P.parents[2]
OUT=ROOT/'output/pdf/公開5データ_論文条件による3手法比較.pdf'
pdfmetrics.registerFont(TTFont('JP','/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
pdfmetrics.registerFontFamily('JP',normal='JP',bold='JP',italic='JP',boldItalic='JP')
W,H=A4; WIDTH=W-88; ink=colors.HexColor('#172E48'); accent=colors.HexColor('#146D83')
styles={
 'body':ParagraphStyle('body',fontName='JP',fontSize=9.4,leading=15,wordWrap='CJK',spaceAfter=7,textColor=ink),
 'h1':ParagraphStyle('h1',fontName='JP',fontSize=18,leading=26,wordWrap='CJK',spaceAfter=14,textColor=ink),
 'h2':ParagraphStyle('h2',fontName='JP',fontSize=12.2,leading=19,wordWrap='CJK',spaceBefore=13,spaceAfter=8,keepWithNext=True,textColor=accent),
 'h3':ParagraphStyle('h3',fontName='JP',fontSize=10.4,leading=16,wordWrap='CJK',spaceBefore=9,spaceAfter=6,keepWithNext=True,textColor=ink),
 'cell':ParagraphStyle('cell',fontName='JP',fontSize=8.1,leading=12,wordWrap='CJK',textColor=ink),
 'th':ParagraphStyle('th',fontName='JP',fontSize=8.1,leading=12,wordWrap='CJK',textColor=colors.white),
 'bullet':ParagraphStyle('bullet',fontName='JP',fontSize=9.2,leading=14.6,wordWrap='CJK',spaceAfter=6,leftIndent=11,firstLineIndent=-9,textColor=ink),
}
def inline(s):
 s=s.replace('−','-').replace('–','-').replace('—','-').replace('\u2011','-')
 s=html.escape(s)
 s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',r'<link href="\2" color="#146D83">\1</link>',s)
 s=re.sub(r'\*\*(.+?)\*\*',r'<b>\1</b>',s)
 s=re.sub(r'`([^`]+)`',r'<font color="#315B73">\1</font>',s)
 return s

def make_table(block):
 rows=[]
 for line in block:
  cells=[c.strip() for c in line.strip().strip('|').split('|')]
  if all(re.fullmatch(r':?-+:?',c) for c in cells): continue
  if rows:
   for full,short in [('豆（Dry Bean）','豆'),('米（Rice）','米'),('レーズン（Raisin）','レーズン'),('室内在室（Occupancy）','室内在室'),('電力網（Grid）','電力網')]:
    if cells[0]==full: cells[0]=short
  rows.append(cells)
 n=len(rows[0]); assert all(len(r)==n for r in rows)
 if n==2: widths=[103,WIDTH-103]
 elif n==4: widths=[125]+[(WIDTH-125)/3]*3
 elif n==5: widths=[75,126,115,115,WIDTH-431]
 elif n==7: widths=[119]+[(WIDTH-119)/6]*6
 else: widths=[WIDTH/n]*n
 data=[[Paragraph(inline(c),styles['th' if i==0 else 'cell']) for c in row] for i,row in enumerate(rows)]
 t=Table(data,colWidths=widths,repeatRows=1,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),ink),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),7),('RIGHTPADDING',(0,0),(-1,-1),7),('TOPPADDING',(0,0),(-1,-1),5),('BOTTOMPADDING',(0,0),(-1,-1),5),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.HexColor('#F0F5F8'),colors.white]),('LINEBELOW',(0,0),(-1,0),.6,ink),('LINEBELOW',(0,1),(-1,-1),.3,colors.HexColor('#D5E0E7'))]))
 return KeepTogether([t]) if len(rows)<=8 else t
story=[]; lines=(P/'比較レポート.md').read_text().splitlines(); i=0
while i<len(lines):
 line=lines[i].strip()
 if not line: i+=1; continue
 if line.startswith('|'):
  block=[]
  while i<len(lines) and lines[i].strip().startswith('|'): block.append(lines[i]); i+=1
  table=make_table(block)
  if story and isinstance(story[-1],Paragraph) and getattr(story[-1].style,'keepWithNext',False):
   heading=story.pop(); content=table._content if isinstance(table,KeepTogether) else [table]; story.append(KeepTogether([heading]+content+[Spacer(1,9)]))
  else: story.extend([table,Spacer(1,9)])
  continue
 if line.startswith('# '):
  story.append(Paragraph('PUBLIC TABULAR DATA  /  2026.10.15',ParagraphStyle('eyebrow',fontName='JP',fontSize=8.2,leading=13,textColor=accent,spaceAfter=9)))
  story.append(Paragraph(inline(line[2:]),styles['h1']))
 elif line.startswith('## '):
  if line[3:] in ['分類結果','同じseed間の対応差','実装の検証・限界']: story.append(PageBreak())
  story.append(Paragraph(inline(line[3:]),styles['h2']))
 elif line.startswith('### '):
  if line[4:] in ['公開データの出典と全使用列','論文方式で実際に生じた破綻例']: story.append(PageBreak())
  story.append(Paragraph(inline(line[4:]),styles['h3']))
 elif line.startswith('- '): story.append(Paragraph('・'+inline(line[2:]),styles['bullet']))
 elif line.startswith('**') and line.endswith('**'):
  block=[Paragraph(inline(line),styles['h3'])]
  while i+1<len(lines):
   nxt=lines[i+1].strip()
   if nxt.startswith(('**','##')): break
   i+=1
   if not nxt: continue
   kind='bullet' if nxt.startswith('- ') else 'body'
   block.append(Paragraph(('・'+inline(nxt[2:])) if kind=='bullet' else inline(nxt),styles[kind]))
  story.append(KeepTogether(block))
 else:
  buf=[line]
  while i+1<len(lines) and lines[i+1].strip() and not lines[i+1].lstrip().startswith(('#','|','- ','**')): i+=1; buf.append(lines[i].strip())
  story.append(Paragraph(inline(' '.join(buf)),styles['body']))
 i+=1

def page(canvas,doc):
 canvas.saveState(); canvas.setFont('JP',8); canvas.setFillColor(colors.HexColor('#6A7D8C'))
 canvas.drawString(44,H-31,'公開5データ / VIME・クラス条件付き対照学習・Gaussian copula')
 canvas.setStrokeColor(colors.HexColor('#D4E0E6')); canvas.line(44,H-40,W-44,H-40); canvas.line(44,37,W-44,37)
 canvas.drawString(44,23,'論文の主要条件での比較  |  5 datasets × 3 methods × 8 seeds')
 canvas.drawRightString(W-44,23,str(doc.page)); canvas.restoreState()
SimpleDocTemplate(str(OUT),pagesize=A4,rightMargin=44,leftMargin=44,topMargin=57,bottomMargin=49,title='公開5データ：論文条件によるVIME・論文手法・提案copulaの比較',author='Data-Augumation research benchmark').build(story,onFirstPage=page,onLaterPages=page)
print(OUT)
