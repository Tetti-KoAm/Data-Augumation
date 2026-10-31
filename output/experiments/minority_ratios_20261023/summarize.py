from pathlib import Path
import json
import numpy as np
import pandas as pd
from run import load,repair,semantics,METHODS
E=Path(__file__).resolve().parent; R=E/'results'; seeds=[11,23,37,51,67]; ratios=[.1,.2,.3]
def main():
 m=pd.read_csv(R/'metrics.csv');q=pd.read_csv(R/'quality.csv');t=pd.read_csv(R/'timing.csv');metas=json.loads((R/'datasets.json').read_text());protocol=json.loads((R/'protocol.json').read_text())
 assert len(metas)==45 and len(m)==1350 and len(q)==585 and len(t)==405
 assert not m.duplicated(['dataset','minority_fraction','seed','method','variant','classifier']).any()
 for d in ['rice','raisin','grid']:
  xx,yy,cols,info=load(d)
  for seed in seeds:
   splits=[]
   for r in ratios:
    w=R/f'{d}_{int(r*100)}_{seed}';sp=np.load(w/'split.npz');tr,te=sp['train_indices'],sp['test_indices'];x,y=sp['x_train'],sp['y_train'];splits.append(sp)
    assert not set(tr)&set(te) and len(set(tr))==len(tr)
    assert y.mean()==r
    np.testing.assert_array_equal(xx[tr],x);np.testing.assert_array_equal(yy[tr],y);np.testing.assert_array_equal(xx[te],sp['x_test']);np.testing.assert_array_equal(yy[te],sp['y_test'])
    for method in METHODS[1:]:
     if method=='class_weight':continue
     g=np.load(w/f'{method}_generated.npz')['generated'];assert g.shape==(sum(y==0)-sum(y==1),len(cols)) and np.isfinite(g).all()
     if method!='duplicate':assert semantics(d,repair(d,g,cols),cols)['relation_violation']==0
    for method in ['ctgan','ctgan_copula']:assert len(pd.read_csv(w/f'{method}_loss.csv'))==300
   assert len(set(len(z['y_train']) for z in splits))==1
   for z in splits[1:]:np.testing.assert_array_equal(z['test_indices'],splits[0]['test_indices'])
   for a,b in zip(splits,splits[1:]):
    assert set(a['train_indices'][a['y_train']==1])<=set(b['train_indices'][b['y_train']==1])
    assert set(b['train_indices'][b['y_train']==0])<=set(a['train_indices'][a['y_train']==0])
 for row in m.itertuples():
  assert abs(row.macro_f1-.5*(2*row.tp/(2*row.tp+row.fp+row.fn)+2*row.tn/(2*row.tn+row.fp+row.fn)))<1e-12
 b=m.query('variant=="base"'); b.groupby(['dataset','minority_fraction','classifier','method']).agg({k:['mean','std'] for k in ['macro_f1','balanced_accuracy','recall','precision','roc_auc','average_precision']}).to_csv(R/'summary.csv')
 pair=[]
 for (d,r,c),g in b.groupby(['dataset','minority_fraction','classifier']):
  dup=g.query('method=="duplicate"').set_index('seed').macro_f1
  for method in METHODS:
   delta=g.query('method==@method').set_index('seed').macro_f1-dup
   pair.append(dict(dataset=d,minority_fraction=r,classifier=c,method=method,delta_vs_duplicate=delta.mean(),sd=delta.std(),wins=int((delta>1e-12).sum())))
 pd.DataFrame(pair).to_csv(R/'paired_differences.csv',index=False)
 (R/'slide_data.json').write_text(json.dumps(dict(metrics=m.to_dict('records'),quality=q.to_dict('records'),timing=t.fillna(0).to_dict('records'),metadata=metas,protocol=protocol),ensure_ascii=False))
 (R/'audit.json').write_text(json.dumps(dict(passed=True,jobs=45,classification_rows=1350,checks=['exact original and persisted train/test arrays','disjoint indices','fixed training totals and exact minority ratios','common test set and nested class subsets across ratios','equal generated counts and finite values','300 GAN epochs','all Macro-F1 values from confusion counts','predefined repair relation checks']),indent=2))
 print(b.pivot_table(index=['dataset','classifier','method'],columns='minority_fraction',values='macro_f1').round(4).to_string())
 print('AUDIT PASSED')
if __name__=='__main__':main()
