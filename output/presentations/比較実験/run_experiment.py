"""Seminar rerun: existing VIME implementation, only its two corruptors compared.
Run: PYTHONPATH=research-bench/src experiment_env/bin/python run_experiment.py
"""
from pathlib import Path
import sys, json, random, time, platform
import numpy as np
import scipy, sklearn, torch
from scipy.stats import bootstrap
from sklearn.datasets import load_breast_cancer, load_wine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import accuracy_score,balanced_accuracy_score,f1_score,roc_auc_score
project_root = next(p for p in [Path.cwd(), *Path(__file__).resolve().parents] if (p/'research-bench/src').is_dir())
sys.path.insert(0,str(project_root/'research-bench/src'))
from tabular_research.vime_torch import VIMEClassifier,VIMEConfig
from tabular_research.corruption import GaussianCopulaCorruptor,ColumnShuffleCorruptor
ROOT=Path(__file__).parent
torch.set_num_threads(1)
seeds=[11,23,37,51,67]; runs=[]; begin=time.time()
for name,loader in [('breast_cancer',load_breast_cancer),('wine',load_wine)]:
 d=loader();x=np.asarray(d.data,dtype=np.float32);y=np.asarray(d.target,dtype=int)
 for seed in seeds:
  tr,te=train_test_split(np.arange(len(y)),test_size=.2,stratify=y,random_state=seed)
  il,iu=train_test_split(tr,train_size=.3,stratify=y[tr],random_state=seed+100003)
  scaler=MinMaxScaler().fit(x[tr]);xl=scaler.transform(x[il]).astype('float32');xu=scaler.transform(x[iu]).astype('float32');xt=scaler.transform(x[te]).astype('float32')
  cfg=VIMEConfig(corruption_probability=.4,reconstruction_weight=2.,n_augmented_views=3,consistency_weight=1.,self_epochs=15,semi_iterations=300,batch_size=64,predictor_hidden_dim=32,encoder_hidden_dim=32,encoder_depth=4,encoder_dropout=0.,validation_fraction=0.,device='cpu',seed=seed)
  result={}
  for method,corruptor in [('column_shuffle',None),('gaussian_copula',GaussianCopulaCorruptor())]:
   random.seed(seed);np.random.seed(seed);torch.manual_seed(seed)
   est=VIMEClassifier(config=cfg,corruptor=corruptor);est.fit(xl,y[il],xu);probs=est.predict_proba(xt);pred=probs.argmax(1)
   result[method]={'auc':float(roc_auc_score(y[te],probs[:,1]) if len(np.unique(y))==2 else roc_auc_score(y[te],probs,multi_class='ovr',average='macro')),'accuracy':float(accuracy_score(y[te],pred)),'balanced_accuracy':float(balanced_accuracy_score(y[te],pred)),'macro_f1':float(f1_score(y[te],pred,average='macro'))}
   print(name,seed,method,result[method],flush=True)
  runs.append({'dataset':name,'seed':seed,'metrics':result,'n_labeled':len(il),'n_unlabeled':len(iu),'n_test':len(te)})
summary={}
for name in ['breast_cancer','wine']:
 rr=[r for r in runs if r['dataset']==name];ss={}
 for method in ['column_shuffle','gaussian_copula']:
  a=np.array([r['metrics'][method]['auc'] for r in rr]);ss[method]={'mean':float(a.mean()),'std':float(a.std(ddof=1)),'values':a.tolist()}
 diff=np.array([r['metrics']['gaussian_copula']['auc']-r['metrics']['column_shuffle']['auc'] for r in rr]);ci=bootstrap((diff,),np.mean,n_resamples=10000,method='percentile',random_state=2026).confidence_interval
 ss['paired_difference']={'mean':float(diff.mean()),'ci95':[float(ci.low),float(ci.high)]};summary[name]=ss
versions={'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'sklearn':sklearn.__version__,'torch':torch.__version__,'platform':platform.platform(),'threads':1}
out={'executed':'2026-10-04','versions':versions,'protocol':{'seeds':seeds,'train_test':'80/20 stratified','labeled_fraction':.3,'mask':.4,'epochs':15,'semi_iterations':300,'batch':64,'encoder':'4x32','n_views':3,'device':'CPU'},'runs':runs,'summary':summary,'elapsed_sec':time.time()-begin}
(ROOT/'rerun_results.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(summary,indent=2),flush=True)
# Independent vs conditional generation on known continuous synthetic data.
rng=np.random.default_rng(20261004);z1=rng.normal(size=2500);z2=.8*z1+.6*rng.normal(size=2500);data=np.column_stack([z1,z2]).astype('float32');mask=np.zeros_like(data,dtype=bool);mask[:,1]=True
records={}
for method,c in [('original',None),('column_shuffle',ColumnShuffleCorruptor()),('gaussian_copula',GaussianCopulaCorruptor())]:
 if c is None: generated=data.copy()
 else:
  if hasattr(c,"fit"): c.fit(data)
  generated=c(data,mask,np.random.default_rng(314159))
 error=float(np.mean((generated[:,1]-.8*data[:,0])**2));records[method]={'correlation':float(np.corrcoef(generated.T)[0,1]),'conditional_mean_residual_mse':error,'observed_unchanged':bool(np.array_equal(generated[:,0],data[:,0])),'x':generated[:180,0].tolist(),'y':generated[:180,1].tolist()}
(ROOT/'toy_results.json').write_text(json.dumps({'label':'synthetic example; not downstream classification proof','n':2500,'rho':.8,'seed':20261004,'results':records},indent=2));print('toy',[(k,v['correlation'],v['conditional_mean_residual_mse']) for k,v in records.items()])
