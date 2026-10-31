"""Write the full 10-repeat comparison after the 300-epoch run and audit."""
import json
from pathlib import Path
import pandas as pd

BASE=Path(__file__).resolve().parent
LABELS={'none':'拡張なし','duplicate':'ランダム複製','class_weight':'クラス重み付け','shuffle':'列シャッフル','copula':'Gaussian copula','smote':'SMOTE','copula_smote':'コピュラSMOTE','adasyn':'ADASYN','copula_adasyn':'コピュラADASYN','ctgan':'CTGAN','ctgan_copula':'CTGAN×コピュラ'}

def main():
    out=BASE/'results'
    completion=json.loads((out/'completion.json').read_text())
    protocol=json.loads((out/'protocol.json').read_text())
    audit=json.loads((out/'audit.json').read_text())
    assert completion['complete'] and audit['passed'] and protocol['ctgan_epochs']==300 and len(protocol['seeds'])==10
    s=pd.read_csv(out/'summary.csv').query('variant=="base"')
    m=pd.read_csv(out/'metrics.csv').query('variant=="base"')
    lines=['# UCI二値分類：全手法300 epoch本実験','', '3データ×少数割合10%・20%・30%×各10回。CTGANとCTGAN×コピュラは各300 epoch。全条件完了、保存データの監査合格。', '', '主指標はMacro-F1。表は平均 ± 標本標準偏差（ddof=1）、各セル10回。制約修正なしのbaseを主比較とする。拡張前の訓練件数は米・電力網1100、レーズン350。テストは元データの割合。', '']
    best=[]
    for dataset in protocol['datasets']:
        for classifier in ['logistic','hist_boost']:
            group=s[(s.dataset==dataset)&(s.classifier==classifier)]
            lines.extend([f'## {dataset} / {classifier}','','|手法|少数10%|少数20%|少数30%|','|---|---|---|---|'])
            for method in protocol['methods']:
                cells=[]
                for ratio in [.1,.2,.3]:
                    row=group[(group.method==method)&(group.minority_fraction==ratio)].iloc[0]
                    value=f'{row.macro_f1_mean:.4f} ± {row.macro_f1_std:.4f}'
                    if row.macro_f1_mean==group[group.minority_fraction==ratio].macro_f1_mean.max(): value='**'+value+'**'
                    cells.append(value)
                lines.append('|'+LABELS[method]+'|'+'|'.join(cells)+'|')
            lines.append('')
            for ratio,g in group.groupby('minority_fraction'):
                row=g.loc[g.macro_f1_mean.idxmax()]
                best.append(dict(dataset=dataset,classifier=classifier,minority_fraction=ratio,method=row.method,mean=row.macro_f1_mean,std=row.macro_f1_std))
    pd.DataFrame(best).to_csv(out/'best_by_condition.csv',index=False)
    deltas=[]
    for left,right in [('adasyn','smote'),('copula_adasyn','copula_smote'),('ctgan','smote'),('ctgan_copula','copula'),('ctgan_copula','ctgan')]:
        for (d,c,r),g in m.groupby(['dataset','classifier','minority_fraction']):
            a=g[g.method==left].set_index('seed').macro_f1
            b=g[g.method==right].set_index('seed').macro_f1
            diff=a-b
            deltas.append(dict(dataset=d,classifier=c,minority_fraction=r,left=left,right=right,n=len(diff),mean_difference=diff.mean(),std_difference=diff.std(ddof=1),positive_seeds=int((diff>0).sum())))
    delta=pd.DataFrame(deltas); delta.to_csv(out/'paired_comparisons.csv',index=False)
    lines.extend(['## 比較の読み取り',''])
    for (left,right),g in delta.groupby(['left','right'],sort=False):
        lines.append(f'- {LABELS[left]}が{LABELS[right]}を平均Macro-F1で上回った条件は18条件中{int((g.mean_difference>0).sum())}条件。')
    lines.extend(['','平均差とその標本SDは `paired_comparisons.csv` に保存。これは同じseedを対応づけた差であり、元の性能のSDとは異なる。', '', '## 解釈上の制約','', '反復holdoutのテスト集合は重なり得る。平均値の順位は統計的有意差や一般的な優位性を意味しない。ハイパーパラメータ探索なし。人工的な不均衡と小標本を対象にしており、大規模データでのCTGANの性能は検証していない。ADASYNは局所配分の丸めにより追加件数が他法と少し異なる。米とレーズンは形状特徴、電力網はシミュレーションであり、対象領域にも制約がある。','', 'Macro-F1以外のbalanced accuracy、Recall、Precision、ROC-AUC、average precisionの平均・SDと、repairの補助比較は `summary.csv` を参照。'])
    (out/'comparison.md').write_text('\n'.join(lines)+'\n')
    print(pd.DataFrame(best).to_string(index=False))
    print(delta.groupby(['left','right']).mean_difference.agg(['min','max']))

if __name__=='__main__': main()
