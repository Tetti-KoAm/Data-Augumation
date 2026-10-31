"""Aggregate repeated holdouts; expose missing/failed seeds instead of hiding them."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd

METRICS=['macro_f1','balanced_accuracy','recall','precision','roc_auc','average_precision']
KEYS=['dataset','minority_fraction','classifier','method','variant']

def summarize(out):
    out=Path(out)
    protocol=json.loads((out/'protocol.json').read_text())
    results=[]
    for dataset in protocol['datasets']:
        for ratio in protocol['minority_fractions']:
            for seed in protocol['seeds']:
                path=out/f'{dataset}_{int(ratio*100)}_{seed}'/'result.json'
                if path.exists(): results.append(json.loads(path.read_text()))
    rows=[r for result in results for r in result['metrics']]
    m=pd.DataFrame(rows)
    failures=pd.DataFrame([r for result in results for r in result['failures']],columns=['dataset','seed','minority_fraction','method','error'])
    failures.to_csv(out/'failures.csv',index=False)
    expected=len(protocol['seeds'])
    summaries=[]
    if not m.empty:
        assert not m.duplicated(KEYS+['seed']).any(), 'Duplicate evaluations'
        for row in m.itertuples():
            f1=.5*(2*row.tp/(2*row.tp+row.fp+row.fn)+2*row.tn/(2*row.tn+row.fp+row.fn))
            assert abs(row.macro_f1-f1)<1e-12
    for dataset in protocol['datasets']:
        for ratio in protocol['minority_fractions']:
            for classifier in ['logistic','hist_boost']:
                for method in protocol['methods']:
                    variants=['base'] if method in ['none','class_weight','duplicate'] else ['base','repair']
                    for variant in variants:
                        key=dict(zip(KEYS,[dataset,ratio,classifier,method,variant]))
                        group=m
                        if not m.empty:
                            for k,v in key.items(): group=group[group[k]==v]
                        count=len(group)
                        record={**key,'n_success':count,'n_expected':expected,'complete':count==expected}
                        for metric in METRICS:
                            record[metric+'_mean']=group[metric].mean() if count else np.nan
                            record[metric+'_std']=group[metric].std(ddof=1) if count>1 else np.nan
                        summaries.append(record)
    summary=pd.DataFrame(summaries)
    summary.to_csv(out/'summary.csv',index=False)
    lines=['# UCI二値分類：反復実験の集計','',f'予定反復数: {expected}。標準偏差は標本SD（ddof=1）。未完了条件は明記。','', '|データ|少数割合|分類器|手法|成功/予定|Macro-F1 平均 ± SD|状態|','|---|---|---|---|---|---|---|']
    for r in summary.query('variant == "base"').itertuples():
        value=f'{r.macro_f1_mean:.4f} ± {r.macro_f1_std:.4f}' if r.n_success>1 else '未集計（成功2回未満）'
        lines.append(f'|{r.dataset}|{r.minority_fraction:.0%}|{r.classifier}|{r.method}|{r.n_success}/{r.n_expected}|{value}|{"完了" if r.complete else "未完了"}|')
    (out/'summary.md').write_text('\n'.join(lines)+'\n')
    expected_jobs=len(protocol['datasets'])*len(protocol['minority_fractions'])*expected
    (out/'completion.json').write_text(json.dumps(dict(completed_jobs=len(results),expected_jobs=expected_jobs,failed_generations=len(failures),complete=bool(summary.complete.all() and len(results)==expected_jobs)),indent=2))
    return summary

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--out',type=Path,default=Path(__file__).resolve().parent/'results')
    summarize(parser.parse_args().out)
