from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    HRFlowable,
    KeepTogether,
    PageBreak,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "docs" / "artifacts" / "研究内容の理解と確認事項_中間発表1.pdf"
OUTPUT.parent.mkdir(parents=True, exist_ok=True)

FONT_CANDIDATES = [
    Path("/System/Library/Fonts/Supplemental/Arial Unicode.ttf"),
    Path("/System/Library/Fonts/ヒラギノ角ゴシック W3.ttc"),
    Path("/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"),
]
FONT_PATH = next((path for path in FONT_CANDIDATES if path.exists()), None)
if FONT_PATH is None:
    raise FileNotFoundError(
        "Japanese font not found. Install Noto Sans CJK or update FONT_CANDIDATES."
    )
pdfmetrics.registerFont(TTFont("JP", FONT_PATH))
pdfmetrics.registerFontFamily("JP", normal="JP", bold="JP", italic="JP", boldItalic="JP")

PAGE_W, PAGE_H = A4
NAVY = colors.HexColor("#18324A")
BLUE = colors.HexColor("#2B6F8E")
PALE_BLUE = colors.HexColor("#EAF3F7")
PALE_RED = colors.HexColor("#FBECEC")
PALE_GOLD = colors.HexColor("#FFF6DD")
INK = colors.HexColor("#202A33")
MUTED = colors.HexColor("#5F6B76")
LINE = colors.HexColor("#CAD5DC")


class ReportDocTemplate(BaseDocTemplate):
    def __init__(self, filename):
        super().__init__(
            filename,
            pagesize=A4,
            leftMargin=19 * mm,
            rightMargin=19 * mm,
            topMargin=21 * mm,
            bottomMargin=18 * mm,
            title="研究内容の理解と確認事項",
            author="Codex",
            subject="2026.09.12 中間発表1の内容整理と技術的確認",
        )
        frame = Frame(
            self.leftMargin,
            self.bottomMargin,
            self.width,
            self.height,
            id="main",
            leftPadding=0,
            rightPadding=0,
            topPadding=0,
            bottomPadding=0,
        )
        self.addPageTemplates([PageTemplate(id="report", frames=[frame], onPage=draw_page)])


def draw_page(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(LINE)
    canvas.setLineWidth(0.5)
    canvas.line(19 * mm, PAGE_H - 13 * mm, PAGE_W - 19 * mm, PAGE_H - 13 * mm)
    canvas.setFont("JP", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(19 * mm, PAGE_H - 10 * mm, "中間発表資料の理解と研究設計上の確認")
    canvas.drawRightString(PAGE_W - 19 * mm, 10 * mm, f"{doc.page}")
    canvas.restoreState()


styles = getSampleStyleSheet()


def pstyle(name, **kwargs):
    defaults = dict(fontName="JP", textColor=INK, wordWrap="CJK")
    defaults.update(kwargs)
    return ParagraphStyle(name, **defaults)


TITLE = pstyle(
    "TitleJP",
    fontSize=24,
    leading=33,
    textColor=NAVY,
    alignment=TA_LEFT,
    spaceAfter=8 * mm,
)
SUBTITLE = pstyle(
    "SubtitleJP",
    fontSize=10.5,
    leading=17,
    textColor=MUTED,
    spaceAfter=4 * mm,
)
H1 = pstyle(
    "H1JP",
    fontSize=16,
    leading=22,
    textColor=NAVY,
    spaceBefore=7 * mm,
    spaceAfter=3 * mm,
    keepWithNext=True,
)
H2 = pstyle(
    "H2JP",
    fontSize=12.5,
    leading=18,
    textColor=BLUE,
    spaceBefore=4 * mm,
    spaceAfter=1.5 * mm,
    keepWithNext=True,
)
BODY = pstyle(
    "BodyJP",
    fontSize=9.6,
    leading=16.2,
    alignment=TA_JUSTIFY,
    spaceAfter=2.2 * mm,
)
SMALL = pstyle(
    "SmallJP",
    fontSize=8.2,
    leading=13.5,
    textColor=MUTED,
    spaceAfter=1.5 * mm,
)
BULLET = pstyle(
    "BulletJP",
    parent=BODY,
    leftIndent=5 * mm,
    firstLineIndent=-3.5 * mm,
    bulletIndent=0,
    spaceAfter=1.2 * mm,
)
NUMBER = pstyle(
    "NumberJP",
    parent=BODY,
    leftIndent=7 * mm,
    firstLineIndent=-6 * mm,
    spaceAfter=1.5 * mm,
)
QUOTE = pstyle(
    "QuoteJP",
    fontSize=11.5,
    leading=19,
    textColor=NAVY,
    alignment=TA_CENTER,
    leftIndent=7 * mm,
    rightIndent=7 * mm,
)
CALLOUT = pstyle(
    "CalloutJP",
    fontSize=10,
    leading=16.5,
    textColor=INK,
)
SOURCE = pstyle(
    "SourceJP",
    fontSize=7.7,
    leading=12.5,
    textColor=MUTED,
)


def para(text, style=BODY):
    return Paragraph(text, style)


def bullet(text):
    return Paragraph(f"・{text}", BULLET)


def number(n, text):
    return Paragraph(f"{n}. {text}", NUMBER)


def callout(text, background=PALE_BLUE, border=BLUE, style=CALLOUT):
    table = Table([[Paragraph(text, style)]], colWidths=[166 * mm])
    table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), background),
                ("BOX", (0, 0), (-1, -1), 0.8, border),
                ("LEFTPADDING", (0, 0), (-1, -1), 7 * mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 7 * mm),
                ("TOPPADDING", (0, 0), (-1, -1), 4.5 * mm),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5 * mm),
            ]
        )
    )
    return table


story = []

# Cover / purpose
story.append(Spacer(1, 15 * mm))
story.append(Paragraph("研究内容の理解と確認事項", TITLE))
story.append(
    Paragraph(
        "対象資料：2026.09.12_中間発表1_齊藤光汰.pptx<br/>"
        "テーマ：テーブルデータにおけるデータの拡張",
        SUBTITLE,
    )
)
story.append(HRFlowable(width="100%", thickness=1.2, color=BLUE, spaceBefore=2 * mm, spaceAfter=8 * mm))
story.append(
    callout(
        "本資料は、発表スライド全28枚と発表者ノートを読み取り、研究背景から問題設定、提案モデルまでの論理を整理したものである。併せて、今後の研究設計に影響する確認事項、技術的懸念、資料上の修正候補をまとめる。",
        PALE_BLUE,
        BLUE,
    )
)
story.append(Spacer(1, 8 * mm))
story.append(Paragraph("結論の要約", H1))
story.append(
    para(
        "研究の中心は、テーブルデータのマスク部分を補う際に、無作為な列内置換や推定クラスへの依存を避け、コピュラで推定した変数間の依存構造に基づいて条件付きサンプリングを行うことである。これにより、少数ラベル環境における自己教師あり学習・半教師あり学習のための、より整合的なデータ拡張を目指している。"
    )
)
story.append(
    callout(
        "中心的な考え方<br/><br/>「値をどこから持ってくるか」を、無作為な列内置換や推定クラスではなく、観測されている他の特徴量を条件とした確率分布から決定する。",
        PALE_GOLD,
        colors.HexColor("#C89B2C"),
        QUOTE,
    )
)
story.append(Spacer(1, 8 * mm))
story.append(Paragraph("作成日：2026年9月24日", SMALL))
story.append(PageBreak())

# Understanding
story.append(Paragraph("1. 研究内容の理解", H1))
for i, text in enumerate(
    [
        "深層学習では大量のラベル付きデータが必要になるが、ラベル付与には時間、費用、専門知識が必要である。",
        "少数データを補う手段としてデータ拡張がある。画像では意味を保った変形が容易だが、テーブルデータでは特徴量を無作為に変えると変数間の関係が壊れうる。",
        "VIMEは、マスク位置と元の値を推定する自己教師あり学習と、一貫性正則化による半教師あり学習を組み合わせる。",
        "VIMEの置換値は各特徴量の経験的周辺分布から取得されるため、個々の値は実在していても、行全体として不自然な組み合わせが生じる可能性がある。",
        "先行研究2は、疑似クラスと特徴量間の関係を利用して、意味を維持しやすい拡張を試みている。",
        "一方、疑似ラベルを拡張の基準にすると、初期の誤分類が拡張と表現学習へ影響する可能性がある。",
        "本研究では、疑似ラベルではなくコピュラで推定した依存構造を用い、観測済み特徴量を条件としてマスク部分を補完する。",
        "生成した拡張データを自己教師あり学習・半教師あり学習へ組み込み、少数ラベル環境での予測性能向上を目指す。",
    ],
    1,
):
    story.append(number(i, text))

story.append(Paragraph("研究の位置付け", H2))
positioning = [
    [para("既存アプローチ", SMALL), para("拡張値の決め方", SMALL), para("想定される課題", SMALL)],
    [para("VIME", SMALL), para("特徴量ごとの周辺分布から無作為に置換", SMALL), para("変数間依存を壊した組み合わせが生じうる", SMALL)],
    [para("先行研究2", SMALL), para("疑似クラス内の行から置換値を取得", SMALL), para("誤った疑似ラベルの影響を受けうる", SMALL)],
    [para("本研究", SMALL), para("依存構造に基づく条件付きサンプリング", SMALL), para("ラベル不変性と高次元・混合型データへの対応が要検証", SMALL)],
]
tbl = Table(positioning, colWidths=[33 * mm, 62 * mm, 71 * mm], repeatRows=1)
tbl.setStyle(
    TableStyle(
        [
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("BACKGROUND", (0, 1), (-1, -1), colors.white),
            ("GRID", (0, 0), (-1, -1), 0.5, LINE),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 3 * mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3 * mm),
            ("TOPPADDING", (0, 0), (-1, -1), 2.5 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5 * mm),
        ]
    )
)
story.append(tbl)

# Questions
story.append(Paragraph("2. 研究設計について確認したいこと", H1))
questions = [
    (
        "最終的な研究仮説",
        "想定される仮説は、「コピュラに基づく条件付き補完は、無作為な特徴量置換よりも依存構造を維持した拡張データを生成し、その結果、少数ラベル環境での分類性能と一貫性学習の安定性を改善する」である。「自然なデータの生成」と「下流分類性能の改善」のどちらを最終目的とするかを明確にしたい。",
    ),
    (
        "対象とする予測問題",
        "資料は二値分類を中心に構成されている。研究範囲を二値分類、多クラス分類、回帰のどこまでとするかによって、評価指標とコピュラの設計が変わる。",
    ),
    (
        "使用するデータセット",
        "連続変数のみか、カテゴリ変数を含むか、高次元か、欠損値やクラス不均衡があるか、ラベル付きデータの比率をどう設定するかを決める必要がある。",
    ),
    (
        "採用するコピュラモデル",
        "Gaussian copula、t-copula、Archimedean copula、Vine copula、ニューラルなcopula flowなどで、表現力、条件付きサンプリングの容易さ、計算量が異なる。データ型と次元数に合わせた選定が必要である。",
    ),
]
for idx, (title, body) in enumerate(questions, 1):
    story.append(KeepTogether([Paragraph(f"2.{idx} {title}", H2), para(body)]))

# Technical concerns
story.append(Paragraph("3. 技術的に重要な懸念", H1))
story.append(Paragraph("3.1 依存構造の維持とラベル不変性は別の条件", H2))
story.append(
    para(
        "コピュラから P(X_masked | X_observed) を推定すれば、入力特徴量として妥当な値を生成できる可能性が高まる。しかし半教師あり学習では、拡張前後で真のクラス Y が変わらないことも必要になる。全体分布 P(X) に整合したサンプルでも、クラス条件付き分布 P(X | Y) を維持するとは限らない。"
    )
)
story.append(
    callout(
        "重要な論点：コピュラによって「現実的な行」を作れることと、「元の行と同じラベルを持つ行」を作れることは別問題である。ラベル不変性をどのように保証または評価するかが、本研究の中心的な検証課題になる。",
        PALE_RED,
        colors.HexColor("#C95B5B"),
    )
)

story.append(Paragraph("3.2 先行研究2の手順に関する整理", H2))
story.append(
    para(
        "資料では先行研究2を「事前学習、VIME型の半教師あり一貫性正則化、MLP」という流れで説明している。一方、原著の中心は、クラス条件付き破損を用いた対照学習による事前学習と、その後の分類ヘッド学習である。疑似ラベルは対照学習中に反復更新されるが、複数の破損データの予測分散を最小化するVIME型の手順が中心手法というわけではない。スライド15から17では、VIMEと先行研究2の手順が混ざっていないか確認が必要である。"
    )
)
story.append(
    para(
        '原著：<link href="https://arxiv.org/abs/2404.17489" color="#2B6F8E">Tabular Data Contrastive Learning via Class-Conditioned and Feature-Correlation Based Augmentation</link>',
        SOURCE,
    )
)

story.append(Paragraph("3.3 VIMEと疑似ラベルの関係", H2))
story.append(
    para(
        "VIMEの半教師あり部分は、ラベル付きデータに対する教師あり損失と、ラベルなしデータの破損版に対する一貫性損失を組み合わせる。スライド10の「疑似ラベル付与」は半教師あり学習一般の説明としては成立するが、VIME固有の構成要素として見える配置には注意が必要である。"
    )
)
story.append(
    para(
        '原著：<link href="https://proceedings.neurips.cc/paper/2020/file/7d97667a3e056acab9aaf653807b4a03-Paper.pdf" color="#2B6F8E">VIME: Extending the Success of Self- and Semi-supervised Learning to Tabular Domain</link>',
        SOURCE,
    )
)

story.append(Paragraph("3.4 「Pearson相関対コピュラ」という位置付け", H2))
story.append(
    para(
        "先行研究2は、各特徴量を他の特徴量から予測するXGBoostを学習し、その特徴量重要度を関係性の指標として利用している。そのため、先行手法がPearson相関だけを使い、非線形関係を検出できないという対比は正確ではない。"
    )
)
story.append(
    callout(
        "より明確な差分：先行研究2は特徴量間の関係を主に「どこを壊すか」の選択に使う。本研究は結合分布を明示的にモデル化し、観測済み特徴量を条件として「どの値で補うか」を決める。",
        PALE_BLUE,
        BLUE,
    )
)

story.append(
    KeepTogether(
        [
            Paragraph("3.5 主張の強さ", H2),
            para(
                "コピュラは周辺分布と依存構造を分離できるが、選択したコピュラ族の表現能力を超える関係は捉えられず、有限標本からの推定誤差もある。「依存構造をすべて捉える」「文脈を完全に保つ」ではなく、「対象とする依存構造を表現できるコピュラ族を用いる」「無作為な列内置換より整合的な生成を目指す」と表現する方が適切である。"
            ),
            para(
                "同様に、疑似ラベルの誤りについても「決定境界が不可逆的に歪む」と断定するより、「誤った疑似ラベルが反復学習で増幅される可能性がある」と仮説として述べ、実験で検証することが望ましい。"
            ),
        ]
    )
)

# Concrete edits
story.append(Paragraph("4. 発表資料の修正候補", H1))
fixes = [
    "スライド6の「あああああ」を削除する。",
    "先行研究2のarXiv番号を 2402.04414 から 2404.17489 に修正する。",
    "スライド7は「2つの段階」と説明した後に第3段階があるため、段階数と呼称を統一する。",
    "スライド21では「事前学習」と「自己教師あり学習」の関係を明確にする。コピュラ推定を独立した前処理にするのか、自己教師あり事前学習の内部処理にするのかを示す。",
    "スライド21の第3段階のPredictorと、第4段階のMLPの役割の違いを説明する。",
    "スライド22の発表者ノートに残っている、スライド11付近の説明文を削除する。",
    "「一環性正則化」を「一貫性正則化」に修正する。",
    "「意味的に現実的じゃない」は、「意味的に不整合な」または「現実の制約と整合しない」に変更する。",
]
for item in fixes:
    story.append(bullet(item))

story.append(Paragraph("5. 優先的に決めるべき3点", H1))
priorities = [
    "最初に実験するデータセットと予測タスクを決める。",
    "コピュラで生成した行が元の行と同じクラスを維持するか、検証方法を定義する。",
    "VIMEの一貫性正則化にコピュラ拡張を組み込むのか、先行研究2の対照学習に組み込むのか、基本フレームワークを確定する。",
]
for i, text in enumerate(priorities, 1):
    story.append(number(i, text))

story.append(Spacer(1, 4 * mm))
story.append(
    callout(
        "次の作業としては、上記3点を確定したうえで、「研究目的、検証可能な仮説、提案手法、比較手法、評価指標」を一つの実験計画に落とし込むことが適切である。",
        PALE_GOLD,
        colors.HexColor("#C89B2C"),
    )
)

doc = ReportDocTemplate(str(OUTPUT))
doc.build(story)
print(OUTPUT)
