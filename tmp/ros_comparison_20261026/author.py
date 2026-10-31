from pathlib import Path
R=Path.cwd();T=R/'tmp/ros_comparison_20261026';s=(R/'tmp/literature_features_20261024/build.mjs').read_text().replace('tmp/literature_features_20261024','tmp/ros_comparison_20261026').replace('26.1022.11436','26.1025.11240')
s=s.replace("duplicate:'ランダム複製'", "duplicate:'ROS（単純複製）'")
s=s.replace('６生成法に加え、拡張なし・ランダム複製・重み付けを比較','６生成法とROSを比較し、拡張なし・重み付けも対照にする')
pos=s.index("prose('評価指標'")
s=s[:pos]+r'''
s=add('追加する対照：ランダムオーバーサンプリング','単純複製との比較','ROSは少数訓練行を復元抽出し、特徴とラベルをそのまま複製。平滑化やノイズは付けない。６生成法と同じ追加件数でクラス1:1へ。既存コードのduplicateがこの操作であり、全45条件の追加行が元少数行と完全一致すること、90件の分類再評価が既存保存結果と一致することを再確認済み。新しく別の10番目のアルゴリズムを実行したという意味ではない。ROSも広い意味ではデータ拡張に含まれる。','同じ件数の単純複製に対し、生成法が上乗せできるかを評価します。',['https://imbalanced-learn.org/stable/references/generated/imblearn.over_sampling.RandomOverSampler.html']);
note(s,'ROS：Random Over-Sampling。特徴量を変えず、少数の行を復元抽出。');
tbl(s,[['比較対象','増やし方','確認したい効果'],['拡張なし','元の不均衡な訓練行を使う','元の性能を確認'],['ROS（単純複製）','少数行をそのままコピー','少数行の学習頻度を増やす効果'],['６つの生成法','組替え・補間・モデルで行を作る','ROSを超える追加の効果']],[325,405,414],{y:188,h:300,size:26});
text(s,'例：米・少数10％は、元の少数110件から880件を複製\n６生成法も880件を追加し、多数990件・少数990件にそろえる',76,513,1125,74,26);
take(s,'同じ訓練行・追加件数・テスト集合で、生成と単純複製を比較する');
''' +s[pos:]
key="for(const d of datasets)for(const c of ['logistic','hist_boost'])resultTable(d,c);"
pos=s.index(key)+len(key)
s=s[:pos]+r'''
for(const d of datasets){
 s=add(dn[d]+'：６生成法はROSを上回ったか','ROSとの差による比較','各セルはロジスティック回帰／HistGradientBoostingの順。Macro-F1の同seedにおける生成法base−duplicateの差を５回平均。プラスがROSより高い。標本SDと５回中の改善回数はaugmentation_vs_ros.csv。探索的で小差の有意性は主張しない。','絶対値の性能表と、ROSからの差を合わせて解釈します。');
 note(s,'ΔMacro-F1（各生成法 − ROS）の５回平均');
 text(s,'各セル：LR（ロジスティック回帰）／Boost（勾配ブースティング）',76,167,1125,28,21,C.muted);
 const diff=(r,m,c)=>{let v=mean(d,r,m,c)-mean(d,r,'duplicate',c);return Math.abs(v)<.0005?'0.000':(v>0?'+':'')+v.toFixed(3)};
 tbl(s,[['手法','少数10％','少数20％','少数30％'],...gens.map(m=>[names[m],...ratios.map(r=>diff(r,m,'logistic')+' ／ '+diff(r,m,'hist_boost'))])],[365,260,260,259],{y:210,h:350,size:24});
 take(s,'プラス：ROSより高い ／ マイナス：ROSより低い（今回の固定条件）');
}
''' +s[pos:]
# Show the ROS baseline in the main plot and quality table as well.
s=s.replace("'#8B63A9','#C59B28'];ch=", "'#8B63A9','#C59B28','#777777'];ch=")
s=s.replace("series:gens.map((m,i)=>", "series:[...gens,'duplicate'].map((m,i)=>")
s=s.replace("name:names[m],values:ratios.map(r=>mean('grid'", "name:m==='duplicate'?'ROS':names[m],values:ratios.map(r=>mean('grid'")
s=s.replace("...gens.map(m=>[names[m],...ratios.map(r=>{let a=D.quality", "...['duplicate',...gens].map(m=>[names[m],...ratios.map(r=>{let a=D.quality")
s=s.replace('米のLR：複製は10％ 0.928、30％ 0.927','米のLR：ROSは10％ 0.928、30％ 0.927')
s=s.replace('単純な複製や重み付けと比べても、生成する利点があるか','ROS（単純複製）や重み付けと比べても、生成する利点があるか')
# Include a visible reference for the added control.
s=s.replace("// Add a short, visible source attribution", "text(s,'[8] imbalanced-learn. RandomOverSampler（公式文書、2026-10-26確認）',76,650,1125,26,18,C.muted);\ns.speakerNotes.text+='\\n[8] ROSの操作定義：https://imbalanced-learn.org/stable/references/generated/imblearn.over_sampling.RandomOverSampler.html';\n// Add a short, visible source attribution")
(T/'build.mjs').write_text(s)
O=R/'output/handoff/テーブルデータ拡張_ROS比較_20261026';(O/'資料').mkdir(parents=True,exist_ok=True)
f=(R/'tmp/literature_features_20261024/finalize.mjs').read_text().replace('tmp/literature_features_20261024','tmp/ros_comparison_20261026').replace('26.1022.11436','26.1025.11240').replace('output/handoff/テーブルデータ拡張_文献特徴量追加_20261024/資料/テーブルデータにおけるデータ拡張_文献と特徴量_完成版.pptx','output/handoff/テーブルデータ拡張_ROS比較_20261026/資料/テーブルデータにおけるデータ拡張_ROS比較版.pptx').replace('validation-literature-complete.json','validation-ros.json').replace('requiredNativeChartOwnerSlides:[31]','requiredNativeChartOwnerSlides:[35]')
(T/'finalize.mjs').write_text(f)
