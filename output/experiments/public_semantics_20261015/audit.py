import json
import numpy as np,pandas as pd
from run import OUT,load
m=pd.read_csv(OUT/'metrics.csv'); s=pd.read_csv(OUT/'semantics.csv')
assert len(m)==150 and len(s)==150
assert not m.duplicated(['dataset','seed','n_labels','method']).any()
assert (m.groupby(['dataset','n_labels','method']).size()==5).all()
assert np.isfinite(m[['auc','balanced_accuracy','macro_f1']].to_numpy()).all()
assert ((m[['auc','balanced_accuracy','macro_f1']]>=0)&(m[['auc','balanced_accuracy','macro_f1']]<=1)).all().all()
audit=[]
for name in m.dataset.unique():
 df,y=load(name); x=df.to_numpy()
 for seed in [11,23,37,51,67]:
  for n in [30,100]:
   sp=np.load(OUT/f'split_{name}_{seed}_{n}.npz'); tr=sp['train_source_indices']; li=sp['labeled_positions']; ui=sp['unlabeled_positions']
   assert len(li)==n and not set(li)&set(ui) and len(li)+len(ui)==len(tr)
   assert len(np.unique(y[tr[li]]))==len(np.unique(y))
   if name!='occupancy':
    ti=sp['test_source_indices']; assert not set(tr)&set(ti)
    trainrows=set(map(tuple,x[tr])); dup=sum(tuple(r) in trainrows for r in x[ti]); audit.append({'dataset':name,'seed':seed,'n_labels':n,'test_rows_exactly_matching_training_features':dup})
(OUT/'audit.json').write_text(json.dumps({'checks':'PASS: 150 scores, 150 generation diagnoses, paired conditions, valid metrics, disjoint row indices, class coverage','duplicate_feature_rows':audit},indent=2))
print('PASS: benchmark output and saved splits audited')
