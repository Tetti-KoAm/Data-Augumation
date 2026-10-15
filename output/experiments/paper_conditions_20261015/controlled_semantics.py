"""Common anchors and fixed-count masks for an augmentation-only diagnosis."""
import json
import numpy as np,pandas as pd
from run import P,NAMES,SEEDS,prepare,data_module,FastGaussianCopula,MinMaxScaler,StandardScaler,sample_class_views
rows=[]; examples={}
for name in NAMES:
 for seed in SEEDS:
  if not all((P/'runs'/f'{name}_{seed}'/f'{method}.json').exists() for method in ['vime','class_conditioned','proposed_copula']): continue
  x,xt,labels,known,yt,cols,meta,split=prepare(name,seed); unknown=np.flatnonzero(~known); anchor_idx=np.random.default_rng(seed+990).choice(unknown,size=min(1000,len(unknown)),replace=False); anchor=x[anchor_idx]; rng=np.random.default_rng(seed+991); mask=np.zeros(anchor.shape,dtype=bool)
  np.put_along_axis(mask,np.argsort(rng.random(mask.shape),axis=1)[:,:int(np.ceil(.4*x.shape[1]))],True,axis=1)
  scal=MinMaxScaler().fit(x); xs=scal.transform(x).astype('float32'); cop=FastGaussianCopula().fit(xs[~known]); pseudo=np.load(P/'runs'/f'{name}_{seed}'/'final_pseudo_labels.npy')
  for method in ['original','vime','class_conditioned','proposed_copula']:
   if method=='original': generated=anchor.copy()
   elif method=='vime':
    rng=np.random.default_rng(seed+992); donors=rng.choice(unknown,size=anchor.shape); generated=anchor.copy(); vals=x[donors,np.arange(x.shape[1])]; generated[mask]=vals[mask]
   elif method=='class_conditioned': generated=sample_class_views(x,pseudo,anchor_idx,mask,np.random.default_rng(seed+992))
   else: generated=scal.inverse_transform(cop(xs[anchor_idx],mask,np.random.default_rng(seed+992)))
   np.testing.assert_allclose(generated[~mask],anchor[~mask],atol=0.03,rtol=1e-6)
   bad,res=data_module.violations(name,generated,cols); rows.append(dict(dataset=name,seed=seed,method=method,n=len(anchor),violation_rate=float(bad.mean()),mean_residual=float(res.mean())))
   if seed==SEEDS[0] and method=='class_conditioned' and bad.any():
    k=int(np.flatnonzero(bad)[0]); examples[name]={'original':dict(zip(cols,map(float,anchor[k]))),'class_conditioned':dict(zip(cols,map(float,generated[k]))),'pseudo_class':int(pseudo[anchor_idx[k]]),'masked':[cols[i] for i in np.flatnonzero(mask[k])]}
pd.DataFrame(rows).to_csv(P/'controlled_semantics.csv',index=False); (P/'class_conditioned_examples.json').write_text(json.dumps(examples,indent=2)); print('Common-mask generation diagnosis complete:',len(rows))
