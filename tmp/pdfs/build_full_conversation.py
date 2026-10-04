import json,re,html
from pathlib import Path
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate,Paragraph,Spacer,Table,TableStyle,PageBreak,HRFlowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from pypdf import PdfReader
root=Path('/Users/kouta/Github/data augumation/Data-Augumation')
source=Path('/Users/kouta/.codex/sessions/2026/10/03/rollout-2026-10-03T16-57-38-01a100c4-c738-75a3-97b5-1fbab3f40589.jsonl')
messages=[]
for line in source.open():
 r=json.loads(line);q=r.get('payload',{})
 if r.get('type')!='response_item' or q.get('type')!='message' or q.get('role') not in ['user','assistant'] or q.get('channel')=='analysis':continue
 s=''.join(c.get('text','') for c in q.get('content',[]) if c.get('type') in ['input_text','output_text']).strip()
 if not s or s.startswith('<environment_context>') or s.startswith('<external_codex_apps_open_page>'):continue
 messages.append((q['role'],s))
 if q['role']=='user' and s=='初めから全ての会話を':break
assert len(messages)==18,len(messages)
font='ConversationJP'
pdfmetrics.registerFont(TTFont(font,'/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
styles={
 'title':ParagraphStyle('title',fontName=font,fontSize=20,leading=30,textColor=colors.HexColor('#193C56'),spaceAfter=18,wordWrap='CJK'),
 'body':ParagraphStyle('body',fontName=font,fontSize=10,leading=17,spaceAfter=8,wordWrap='CJK'),
 'role':ParagraphStyle('role',fontName=font,fontSize=11,leading=18,textColor=colors.HexColor('#193C56'),spaceBefore=12,spaceAfter=8,keepWithNext=True,wordWrap='CJK'),
 'head':ParagraphStyle('head',fontName=font,fontSize=11.5,leading=19,textColor=colors.HexColor('#193C56'),spaceBefore=10,spaceAfter=8,keepWithNext=True,wordWrap='CJK'),
 'small':ParagraphStyle('small',fontName=font,fontSize=8,leading=13,spaceAfter=6,wordWrap='CJK'),
 'cell':ParagraphStyle('cell',fontName=font,fontSize=9,leading=14,wordWrap='CJK'),
 'math':ParagraphStyle('math',fontName=font,fontSize=11,leading=20,leftIndent=12,spaceAfter=9,wordWrap='CJK')}
def inline(s):
 links=[]
 def link(m):
  label,url=m.group(1),m.group(2)
  if url.startswith('http'): rep='<link href="'+html.escape(url,quote=True)+'" color="#245A88">'+html.escape(label)+'</link>'
  else: rep=html.escape(label)
  links.append(rep);return f'@@LINK{len(links)-1}@@'
 s=re.sub(r'\[([^\]]+)\]\(([^)]+)\)',link,s)
 s=html.escape(s)
 s=re.sub(r'\*\*(.*?)\*\*',r'<b>\1</b>',s)
 s=re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<i>\1</i>',s)
 s=re.sub(r'`([^`]+)`',r'\1',s)
 for i,x in enumerate(links):s=s.replace(f'@@LINK{i}@@',x)
 return s
story=[]
def add(s,k='body'):story.append(Paragraph(inline(s),styles[k]))
add('コピュラの先行研究と<br/>条件付きサンプリング：会話全記録'.replace('<br/>','\n'),'title')
add('収録範囲：最初の先行研究の質問から「初めから全ての会話を」まで。ユーザー発言・回答・作業中の案内を会話順に収録しています。本文は要約せず、表・数式・参照リンクはPDF向けに組版しています。','small')
add('作成日：2026年10月3日','small')
story.append(HRFlowable(width='100%',thickness=.6,color=colors.HexColor('#C5D2DC')))
mathmap={
 r'v(S)=\mathbb{E}[f(X)\mid X_S=x_S^*]':'v(S) = E[f(X) | X<sub>S</sub> = x<sub>S</sub><super>*</super>]' ,
 r'(\text{特徴量1},\text{特徴量2},\text{特徴量3})\n=(0.2,\ 0.8,\ 0.7)':'（特徴量1, 特徴量2, 特徴量3） = (0.2, 0.8, 0.7)',
 r'\text{最小残高}\leq\text{平均残高}\leq\text{最大残高}':'最小残高 ≤ 平均残高 ≤ 最大残高',
 r'z_j=\Phi^{-1}(F_j(x_j))':'z<sub>j</sub> = Φ<super>-1</super>(F<sub>j</sub>(x<sub>j</sub>))',
 r'Z\sim\mathcal N(0,R)':'Z ~ N(0, R)',
 r'\text{体重}\sim p(\text{体重}\mid\text{身長}=180)':'体重 ~ p(体重 | 身長 = 180)',
 r'x_j=F_j^{-1}(\Phi(z_j))':'x<sub>j</sub> = F<sub>j</sub><super>-1</super>(Φ(z<sub>j</sub>))'}
def math(s):
 key=s.strip(); value=mathmap.get(key)
 if value is None:
  if '特徴量1' in key:value='（特徴量1, 特徴量2, 特徴量3） = (0.2, 0.8, 0.7)'
  else:raise ValueError(key)
 story.append(Paragraph(value,styles['math']))
def render(s):
 # Native UI artifact controls are displayed as their visible text.
 s=re.sub(r':codex-file-citation\{path="([^"]+)" purpose="output"\}',lambda m:'[作成済みPDF：'+Path(m.group(1)).name+']',s)
 s=re.sub(r':codex-followup\[([^\]]+)\]\{prompt="[^"]*"\}',r'\1',s)
 lines=s.splitlines();i=0
 while i<len(lines):
  line=lines[i].strip()
  if not line:i+=1;continue
  if line=='---':
   story.append(Spacer(1,5));story.append(HRFlowable(width='100%',thickness=.4,color=colors.HexColor('#CBD5DF')));i+=1;continue
  if line==r'\[':
   eq=[];i+=1
   while i<len(lines) and lines[i].strip()!=r'\]':eq.append(lines[i]);i+=1
   math('\n'.join(eq));i+=1;continue
  if line.startswith('|'):
   rows=[]
   while i<len(lines) and lines[i].strip().startswith('|'):
    cells=[x.strip() for x in lines[i].strip().strip('|').split('|')]
    if not all(re.fullmatch(r':?-+:?',x) for x in cells):rows.append(cells)
    i+=1
   n=len(rows[0]); widths={2:[165,330],3:[130,125,240],4:[100,100,100,195]}.get(n,[495/n]*n)
   t=Table([[Paragraph(inline(x),styles['cell']) for x in row] for row in rows],colWidths=widths,repeatRows=1,hAlign='LEFT')
   t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EAF0F5')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#CBD5DF')),('VALIGN',(0,0),(-1,-1),'TOP'),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),7),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8)]))
   story.append(t);story.append(Spacer(1,9));continue
  if line.startswith('- '):add('・'+line[2:]);i+=1;continue
  if re.match(r'^\d+\. ',line):
   block=[line];i+=1
   while i<len(lines) and lines[i].strip() and not re.match(r'^\d+\. ',lines[i].strip()):block.append(lines[i].strip());i+=1
   add(' '.join(block));continue
  block=[line];i+=1
  while i<len(lines) and lines[i].strip() and not lines[i].strip().startswith(('|','- ',r'\[')) and lines[i].strip()!='---':
   block.append(lines[i].strip());i+=1
  text=' '.join(block)
  add(text,'head' if re.fullmatch(r'\*\*[^*]+\*\*',text) else 'body')
turn=0
for role,s in messages:
 if role=='user':
  turn+=1
  if turn>1:story.append(PageBreak())
  add(f'会話 {turn}｜ユーザー','role')
 else:add('アシスタント','role')
 render(s)
output=root/'output/pdf/copula_full_conversation_ja.pdf'
def footer(c,d):
 c.setFont(font,8);c.setFillColor(colors.HexColor('#657789'));c.drawString(50,25,'コピュラの先行研究と条件付きサンプリング | 会話全記録');c.drawRightString(545,25,str(d.page))
doc=SimpleDocTemplate(str(output),pagesize=(595.28,841.89),leftMargin=50,rightMargin=50,topMargin=40,bottomMargin=47,title='コピュラの先行研究と条件付きサンプリング：会話全記録')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
r=PdfReader(str(output)); text='\n'.join(p.extract_text() for p in r.pages)
assert '今回使えそうなコピュラ' in text
assert '初めから全ての会話を' in text
assert text.count('｜ユーザー')==7
print(json.dumps({'messages':len(messages),'user_turns':turn,'pages':len(r.pages),'source_characters':sum(len(s) for _,s in messages),'pdf_bytes':output.stat().st_size},ensure_ascii=False))
