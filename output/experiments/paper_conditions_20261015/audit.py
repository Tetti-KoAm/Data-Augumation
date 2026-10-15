import json,hashlib
from pathlib import Path
import numpy as np,pandas as pd
from run import P,METHODS,SEEDS,NAMES,prepare,score
for source,expected in json.loads((P/'source_hashes.json').read_text()).items(): assert hashlib.sha256(Path(source).read_bytes()).hexdigest()==expected
m=pd.read_csv(P/'metrics.csv'); assert len(m)==120; assert not m.duplicated(['dataset','seed','method']).any(); assert (m.groupby(['dataset','method']).size()==8).all()
assert np.isfinite(m[['accuracy','auc','balanced_accuracy','macro_f1']].to_numpy()).all()
assert ((m[['accuracy','auc','balanced_accuracy','macro_f1']]>=0)&(m[['accuracy','auc','balanced_accuracy','macro_f1']]<=1)).all().all()
c=pd.read_csv(P/'controlled_semantics.csv'); assert len(c)==160 and (c.groupby(['dataset','method']).size()==8).all()
assert (c[c.method=='original'].violation_rate==0).all()
constant=[]
for name in NAMES:
 for seed in SEEDS:
  x,xt,labels,known,y,cols,meta,split=prepare(name,seed); assert np.all(labels[~known]==-1); assert known.sum()==int(.3*len(x)); assert not set(split['labeled_positions'])&set(np.flatnonzero(~known))
  if name!='occupancy': assert not set(split['train_original_rows'])&set(split['test_original_rows'])
  if name=='bean': assert not set(map(tuple,x))&set(map(tuple,xt))
  for method in METHODS:
   f=P/'runs'/f'{name}_{seed}'; v=np.load(f/f'{method}_predictions.npz'); np.testing.assert_array_equal(v['y_test'],y); p=v['probabilities']; assert len(p)==len(y) and np.isfinite(p).all(); np.testing.assert_allclose(p.sum(1),1,atol=1e-6)
   r=m[(m.dataset==name)&(m.seed==seed)&(m.method==method)].iloc[0]
   for key,value in score(y,p).items(): assert abs(r[key]-value)<1e-10
   assert (f/f'{method}_semantics.json').exists()
   if len(np.unique(p,axis=0))==1: constant.append({'dataset':name,'seed':seed,'method':method})
   h=json.loads((f/f'{method}_history.json').read_text())
   if method=='class_conditioned': assert len(h['contrastive_loss'])==500 and len(h['pseudo_updates'])==50
   else: assert len(h['self_loss'])==500
   pseudo=np.load(f/'final_pseudo_labels.npy'); np.testing.assert_array_equal(pseudo[known],labels[known])
a={'status':'PASS','n_model_fits':len(m),'constant_prediction_conditions':constant,'checks':['all 8 seeds for 5 datasets x3 methods','500 self/contrastive epochs','50 pseudo refreshes','valid probabilities and shared test targets','30% known labels and unknown labels masked','disjoint train/test row IDs; no duplicate feature overlap for bean','known labels preserved in final pseudo targets']}
(P/'audit.json').write_text(json.dumps(a,indent=2)); print(a)
