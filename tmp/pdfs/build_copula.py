from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
pdfmetrics.registerFont(TTFont('HeiseiKakuGo-W5','/System/Library/Fonts/Supplemental/Arial Unicode.ttf'))
font='HeiseiKakuGo-W5'
styles={
 'title':ParagraphStyle('title',fontName=font,fontSize=19,leading=29,textColor=colors.HexColor('#18344A'),spaceAfter=16,wordWrap='CJK'),
 'head':ParagraphStyle('head',fontName=font,fontSize=13,leading=20,textColor=colors.HexColor('#18344A'),spaceBefore=14,spaceAfter=7,wordWrap='CJK'),
 'body':ParagraphStyle('body',fontName=font,fontSize=10,leading=17,spaceAfter=9,wordWrap='CJK'),
 'small':ParagraphStyle('small',fontName=font,fontSize=8,leading=13,wordWrap='CJK'),
 'formula':ParagraphStyle('formula',fontName=font,fontSize=12,leading=20,leftIndent=15,spaceAfter=10)
}
story=[]
def p(s,k='body'): story.append(Paragraph(s,styles[k]))
def table(rows,widths):
 t=Table([[Paragraph(x,styles['body']) for x in row] for row in rows],colWidths=widths,hAlign='LEFT')
 t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#EAF0F5')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#CBD5DE')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),9),('RIGHTPADDING',(0,0),(-1,-1),9),('TOPPADDING',(0,0),(-1,-1),7),('BOTTOMPADDING',(0,0),(-1,-1),3)]))
 story.append(t)
p('潜在空間の条件付きサンプリングと<br/>コピュラの違い','title')
p('コピュラは「特徴量間の依存関係を表すモデル」、潜在空間の条件付きサンプリングは「そのモデルを使って値を生成する操作」です。別々の生成手法として対立するものではありません。今回のGaussian copulaでは、潜在空間での条件付きサンプリングを利用します。')
p('1. 潜在空間とは','head')
p('元の特徴量を、計算しやすい別の尺度に変換した空間です。今回の場合は、各列の値を正規分布の尺度へ変換したものです。例えば、身長と体重を考えます。')
table([['元の空間','潜在空間'],['身長170 cm','身長の分布の中での位置を表す数値'],['体重65 kg','体重の分布の中での位置を表す数値']],[155,340])
story.append(Spacer(1,10))
p('単に平均を引いて標準偏差で割る標準化とは異なり、各列の累積分布を使って変換することがポイントです。連続変数なら、次のように変換します。')
p('z<sub>j</sub> = &Phi;<super>-1</super>(F<sub>j</sub>(x<sub>j</sub>))','formula')
p('F_jはその列の累積分布、Φ⁻¹は標準正規分布の逆累積分布です。例えば、その列の中央値ならF_j(x_j) = 0.5なので、潜在値はz_j = 0になります。')
p('2. コピュラは何を表すのか','head')
p('身長と体重には、それぞれ固有の分布があります。それとは別に、「身長が高い人は体重も重い傾向がある」という関係があります。コピュラは、この各列の分布とは分けた、列同士の依存関係を表します。')
p('Gaussian copulaでは、変換後の潜在変数が、相関行列Rを持つ多変量正規分布に従うと仮定します。')
p('Z ~ N(0, R)','formula')
p('各列を正規分布へ変換できても、列同士の関係までGaussian型になるとは限りません。そこはモデルとして置いている仮定です。')
story.append(PageBreak())
p('3. 条件付きサンプリングは何をするのか','head')
p('例えば「身長が180 cmであることは分かっているが、体重はマスクされている」とします。条件付きサンプリングは、p(体重 | 身長 = 180)から値をランダムに生成する操作です。')
p('体重の列全体から無作為に取る場合と違い、身長180 cmという情報を使います。ただし、身長だけで体重は決まらないので、毎回同じ値ではなく、条件に応じたばらつきの中から生成します。')
p('4. Gaussian copulaを使った生成の流れ','head')
for s in [
 '① 元データでモデルを推定する。各列の分布F_jと、変換後の潜在変数間の相関Rを推定します。',
 '② 観測済みの値を潜在空間へ変換する。身長180 cmを、その身長分布に対応する潜在値に変換します。',
 '③ 潜在空間で条件付きサンプリングする。その潜在的な身長を条件として、潜在的な体重を生成します。',
 '④ 元の尺度に戻す。生成した潜在値を、次の式によってkgなどの元の値に戻します。']:p(s)
p('x<sub>j</sub> = F<sub>j</sub><super>-1</super>(&Phi;(z<sub>j</sub>))','formula')
p('この流れが、Aasらの論文で使われるGaussian copulaによる条件付き生成です。','body')
p('5. あなたの研究での役割','head')
table([['用語','今回の役割'],['Gaussian copula','特徴量の分布と依存をモデル化する'],['潜在空間','正規分布の尺度に変換して計算する場所'],['条件付きサンプリング','観測済み特徴量を使い、マスク部分を生成する操作']],[155,340])
story.append(Spacer(1,10))
p('あなたの手法は、「Gaussian copulaで依存構造を推定し、その潜在空間で、マスクしていない特徴量に条件づけてマスク部分をサンプリングする」と説明できます。')
p('潜在空間での条件付きサンプリングは、VAEなど別のモデルでも行えます。それだけでコピュラとは呼びません。今回コピュラと呼ぶ理由は、各列の周辺分布と、列同士の依存構造を分けてモデル化していることにあります。')
p('参考文献','head')
p('Aas, K., Jullum, M., &amp; Løland, A. (2021). Explaining individual predictions when features are dependent: More accurate approximations to Shapley values. Artificial Intelligence, 298, 103502. 第3.2節。','small')
p('<link href="https://martinjullum.com/publication/aas-2021-explaining/aas-2021-explaining.pdf" color="#245A88">論文PDF（クリックして開く）</link>','small')
def footer(c,d):
 c.setFont(font,8);c.setFillColor(colors.HexColor('#657789'));c.drawString(50,25,'コピュラと条件付きサンプリング | 解説');c.drawRightString(545,25,str(d.page))
doc=SimpleDocTemplate('output/pdf/copula_conditional_sampling_ja.pdf',pagesize=(595.28,841.89),rightMargin=50,leftMargin=50,topMargin=42,bottomMargin=45,title='潜在空間の条件付きサンプリングとコピュラの違い',author='')
doc.build(story,onFirstPage=footer,onLaterPages=footer)
