from pathlib import Path
import sys,json
import numpy as np,pandas as pd
from threadpoolctl import threadpool_limits
# Keep the same evaluate function and settings as the saved benchmark.
E=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('output/experiments/minority_ratios_20261023').resolve()
sys.path.insert(0,str(E));from run import evaluate
R=E/'results';saved=pd.read_csv(R/'metrics.csv');rows=[];audit=[]
threadpool_limits(limits=1)
for d in ['rice','raisin','grid']:
 for rho in [.1,.2,.3]:
  for seed in [11,23,37,51,67]:
   w=R/f'{d}_{int(rho*100)}_{seed}';sp=np.load(w/'split.npz');x,y=sp['x_train'],sp['y_train'];g=np.load(w/'duplicate_generated.npz')['generated'];minor=x[y==1]
   known={tuple(r) for r in minor};assert all(tuple(r) in known for r in g)
   assert len(g)==int(sum(y==0)-sum(y==1))
   xa=np.concatenate([x,g]);ya=np.concatenate([y,np.ones(len(g),dtype=int)]);assert sum(ya==0)==sum(ya==1)
   for out in evaluate(xa,ya,sp['x_test'],sp['y_test'],seed,False):
    expected=saved[(saved.dataset==d)&(saved.minority_fraction==rho)&(saved.seed==seed)&(saved.method=='duplicate')&(saved.variant=='base')&(saved.classifier==out['classifier'])]
    assert len(expected)==1
    for metric in ['macro_f1','balanced_accuracy','recall','precision','roc_auc','average_precision']:
     assert abs(out[metric]-float(expected.iloc[0][metric]))<1e-12,(d,rho,seed,metric)
    rows.append(dict(dataset=d,minority_fraction=rho,seed=seed,method='random_oversampling',source_method_id='duplicate',n_added=len(g),**out))
   audit.append(dict(dataset=d,minority_fraction=rho,seed=seed,generated_copy_fraction=1.0,n_added=len(g),balanced_train_counts=np.bincount(ya).tolist()))
pd.DataFrame(rows).to_csv(R/'ros_recheck.csv',index=False)
b=saved.query('variant=="base"');pair=[]
for (d,r,c),grp in b.groupby(['dataset','minority_fraction','classifier']):
 baseline=grp.query('method=="duplicate"').set_index('seed')
 for method in ['shuffle','copula','smote','copula_smote','ctgan','ctgan_copula']:
  val=grp.query('method==@method').set_index('seed');delta=val.macro_f1-baseline.macro_f1
  pair.append(dict(dataset=d,minority_fraction=r,classifier=c,method=method,mean_f1=float(val.macro_f1.mean()),ros_mean_f1=float(baseline.macro_f1.mean()),mean_delta=float(delta.mean()),sd_delta=float(delta.std()),wins_of_5=int((delta>1e-12).sum())))
pd.DataFrame(pair).to_csv(R/'augmentation_vs_ros.csv',index=False)
(R/'ros_audit.json').write_text(json.dumps(dict(passed=True,conditions=45,classifier_rechecks=90,definition='minority-only random sampling with replacement, no smoothing; equivalent ROS operation',checks=['all added rows exactly match an original minority row','class balance 1:1','same added row count as each generator','90 classifier evaluations replayed; all six reported metrics equal saved duplicate results within 1e-12'],conditions_detail=audit),indent=2))
print('ROS confirmed: 45 conditions, 90 classifier evaluations match saved results')
