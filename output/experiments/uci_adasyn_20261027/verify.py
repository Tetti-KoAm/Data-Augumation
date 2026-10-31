"""Audit saved splits, class ratios, generated counts, and aggregate completeness."""
import argparse
import json
from pathlib import Path
import numpy as np
import pandas as pd
from run import load
from summarize import summarize

def verify(out):
    out=Path(out); config=json.loads((out/'protocol.json').read_text()); checked=0
    for dataset in config['datasets']:
        x,y,cols,_=load(dataset)
        for seed in config['seeds']:
            splits=[]
            for ratio in sorted(config['minority_fractions']):
                work=out/f'{dataset}_{int(ratio*100)}_{seed}'
                if not (work/'result.json').exists(): continue
                result=json.loads((work/'result.json').read_text())
                with np.load(work/'split.npz') as z:
                    tr,te=z['train_indices'],z['test_indices']
                    assert not set(tr)&set(te) and len(set(tr))==len(tr)
                    for key,value in [('x_train',x[tr]),('y_train',y[tr]),('x_test',x[te]),('y_test',y[te])]: np.testing.assert_array_equal(z[key],value)
                    assert abs(y[tr].mean()-ratio)<1e-12
                    splits.append((tr,te))
                failures={r['method'] for r in result['failures']}
                assert failures<= {'adasyn','copula_adasyn'}
                for method in config['methods']:
                    if method in failures: continue
                    if method not in ['none','class_weight']:
                        g=np.load(work/f'{method}_generated.npz')['generated']
                        assert len(g)>0 and g.shape[1]==len(cols) and np.isfinite(g).all()
                        if method not in ['adasyn','copula_adasyn']: assert len(g)==sum(y[tr]==0)-sum(y[tr]==1)
                        for r in result['metrics']:
                            if r['method']==method: assert r['n_added']==len(g)
                    if method in ['ctgan','ctgan_copula']: assert len(pd.read_csv(work/f'{method}_loss.csv'))==config['ctgan_epochs']
                checked+=1
            if splits:
                assert len({len(tr) for tr,te in splits})==1
                for tr,te in splits: np.testing.assert_array_equal(te,splits[0][1])
                for (a,_),(b,_) in zip(splits,splits[1:]):
                    assert set(a[y[a]==1])<=set(b[y[b]==1])
                    assert set(b[y[b]==0])<=set(a[y[a]==0])
    summary=summarize(out)
    report=dict(passed=True,checked_jobs=checked,complete=bool(summary.complete.all()))
    (out/'audit.json').write_text(json.dumps(report,indent=2)); print(report)

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--out',type=Path,default=Path(__file__).resolve().parent/'results'); verify(ap.parse_args().out)
