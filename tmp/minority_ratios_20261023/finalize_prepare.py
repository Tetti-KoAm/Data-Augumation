from pathlib import Path
s=Path('tmp/public_comparison_20261023/finalize.mjs').read_text().replace('tmp/public_comparison_20261023','tmp/minority_ratios_20261023').replace('output/presentations/公開データ比較_20261023/テーブルデータにおけるデータ拡張_公開データ3件_実験比較_発表版.pptx','output/presentations/少数クラス割合比較_20261023/テーブルデータにおけるデータ拡張_課題と６手法_少数10_20_30％比較.pptx').replace('[7,8,9,10,11,12,19,20]','[24]')
Path('tmp/minority_ratios_20261023/finalize.mjs').write_text(s)
