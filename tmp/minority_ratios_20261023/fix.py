from pathlib import Path
p=Path('tmp/minority_ratios_20261023/build.mjs');s=p.read_text().replace('top:4,bottom:4','top:2,bottom:2');s=s.replace("take(s,'最高平均　'+winners.join(' ／ '));", "text(s,'最高平均　'+winners.join(' ／ '),68,594,1144,59,24,C.teal,true);")
s=s.replace('米のLR：複製は10％・30％とも約0.928','米のLR：複製は10％ 0.928、30％ 0.927').replace('米のロジスティック回帰では、少数割合が増えると拡張なしとの差が小さくなった','米のロジスティック回帰では、少数割合を増やすと拡張なしとの差が縮小')
p.write_text(s)
p=Path('tmp/minority_ratios_20261023/finalize.mjs');s=p.read_text().replace('30％比較.pptx','30％比較_改訂版.pptx').replace('validation-final-v2.json','validation-final-v3.json');p.write_text(s)
