from pathlib import Path
import pandas as pd
E=Path('output/experiments/minority_ratios_20261023');q=pd.read_csv(E/'results/augmentation_vs_ros.csv');m=pd.read_csv(E/'results/ros_recheck.csv')
print(q.query('classifier=="hist_boost"').pivot_table(index=['dataset','method'],columns='minority_fraction',values='mean_delta').round(3).to_string())
s='''# 単純複製によるランダムオーバーサンプリング（ROS）との比較

2026-10-26追記。従来の `method=duplicate` は、少数クラスの訓練行をランダムに復元抽出する単純なROSです。別の方式を重ねて２つの対照と数えていません。資料上の名前をROS（単純複製）に統一し、６生成法との差を明示しました。ROSも広義にはデータ拡張・オーバーサンプリングの一種です。

## 条件と確認

３データ×少数割合10%/20%/30%×５seedの45条件。少数を多数と同じ件数まで増やすため、６生成法とROSの追加件数は同じ。訓練集合・テスト集合・分類器設定・閾値も共通です。

保存済みROSの追加行が全て元の少数訓練行と完全一致し、拡張後が1:1になることを確認。90件の分類器学習・評価を再実行し、Macro-F1、balanced accuracy、少数再現率、適合率、ROC-AUC、average precisionが既存duplicate結果と1e-12以内で一致しました。分類器時間は再実行時の値なので一致対象ではありません。GANなど６生成法の再学習はしていません。

- ros_recheck.csv：90件の再評価。
- ros_audit.json：45条件のコピー確認と再現確認。
- augmentation_vs_ros.csv：６生成法−ROSの対応するseedでの差。平均、標本SD、５回中の改善回数。
- 内部IDのduplicateは互換性のため維持。表示だけをROSに変更。

## 解釈

ROSは新しい特徴ベクトルを作らず、元の少数例が学習に現れる回数を増やします。６生成法と比べることで、少数例の学習頻度・クラス比を変える効果に対し、新しい行を生成する追加の効果があるかを検討できます。固定設定での探索的比較であり、わずかな平均差を統計的に有意と解釈しません。

以下はMacro-F1差の５回平均で、プラスはROSより高いことを示します。

'''
names={'shuffle':'列シャッフル','copula':'コピュラ','smote':'SMOTE','copula_smote':'コピュラSMOTE','ctgan':'CTGAN','ctgan_copula':'CTGAN×コピュラ'}
for d in ['rice','raisin','grid']:
 for c in ['logistic','hist_boost']:
  s+=f'### {d} / {c}\n\n|手法|10%|20%|30%|\n|---|---|---|---|\n'
  for key,label in names.items():
   vals=[]
   for ratio in [.1,.2,.3]:
    a=q[(q.dataset==d)&(q.classifier==c)&(q.method==key)&(q.minority_fraction==ratio)].iloc[0];vals.append(f'{a.mean_delta:+.4f} ± {a.sd_delta:.4f}')
   s+='|'+label+'|'+'|'.join(vals)+'|\n'
s+='\n## ROSの操作の参照\n\nim​​balanced-learn公式 RandomOverSampler 文書（2026-10-26確認）：https://imbalanced-learn.org/stable/references/generated/imblearn.over_sampling.RandomOverSampler.html\n\n今回は平滑化・ノイズ付与のない復元抽出です。コードは既存のNumPyサンプラーで、RandomOverSamplerクラスを直接使った結果と同じ乱数列を主張するものではありません。\n'
(E/'ROS比較の説明.md').write_text(s)
