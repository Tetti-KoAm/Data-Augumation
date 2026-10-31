from pathlib import Path
p=Path('tmp/literature_features_20261024/build.mjs');s=p.read_text().replace('同名研究はvine生成。本実験は変換＋補間','先行研究：vine生成\\n本実験：変換＋補間').replace('[5] CTGAN／[6] CopulaGAN公式文書','[5] CTGAN＋[6] CopulaGAN文書')
s=s.replace("lead+refs.map(r=>'['+r.id+'] '+r.short).join(' ／ ')","(prefix==='CTGAN×コピュラ：'?'参考：[5] Xu et al. (2019) ／ [6] SDV CopulaGAN公式文書':lead+refs.map(r=>'['+r.id+'] '+r.short).join(' ／ '))")
p.write_text(s)
p=Path('tmp/literature_features_20261024/finalize.mjs');s=p.read_text().replace('文献と特徴量_追加版.pptx','文献と特徴量_発表版.pptx').replace('validation-literature.json','validation-literature-final.json');p.write_text(s)
