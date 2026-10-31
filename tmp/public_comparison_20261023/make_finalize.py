from pathlib import Path
s=Path('tmp/six_methods_main_20261022/finalize.mjs').read_text().replace('26.1020.11127','26.1022.11436').replace('tmp/six_methods_main_20261022','tmp/public_comparison_20261023').replace('output/presentations/テーブルデータ拡張_20261022/テーブルデータにおけるデータ拡張_６手法比較と改善案_発表版.pptx','output/presentations/公開データ比較_20261023/テーブルデータにおけるデータ拡張_公開データ3件_実験比較.pptx').replace('[5,7,8,9,10,14]','[7,8,9,10,11,12,19,20]')
Path('tmp/public_comparison_20261023/finalize.mjs').write_text(s)
