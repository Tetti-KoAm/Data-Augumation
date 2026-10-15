"""Five public datasets, paper-scale architecture/budget and 8 paired seeds."""
import sys,os,time,json,math,random,hashlib,platform,gc
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor,as_completed
P=Path(__file__).resolve().parent; ROOT=P.parents[2]; PREV=P.parent/'public_semantics_20261015'
sys.path.insert(0,str(PREV)); sys.path.insert(0,str(ROOT/'research-bench/src'))
import numpy as np,pandas as pd,torch,sklearn,scipy
# Import previous loader without shadowing this run.py.
import importlib.util
spec=importlib.util.spec_from_file_location('previous_data',PREV/'run.py'); data_module=importlib.util.module_from_spec(spec); spec.loader.exec_module(data_module)
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler,StandardScaler
from sklearn.metrics import accuracy_score,roc_auc_score,balanced_accuracy_score,f1_score
from tabular_research.vime_torch import VIMEClassifier,VIMEConfig
from tabular_research.corruption import ColumnShuffleCorruptor
from fast_copula import FastGaussianCopula
from class_conditioned import ClassConditionedClassifier,sample_class_views
SEEDS=[614579,336466,974761,450967,743562,843198,502837,328984]
NAMES=['bean','rice','raisin','occupancy','grid']; METHODS=['vime','class_conditioned','proposed_copula']

def prepare(name,seed):
 df,y=data_module.load(name); rows=np.arange(len(y)); before=len(y)
 if name=='bean':
  keep=~df.duplicated(); rows=rows[keep]; df=df.loc[keep].reset_index(drop=True); y=y[keep]
 x=df.to_numpy()
 if name=='occupancy':
  tr=np.arange(len(y)); xt=pd.concat([pd.read_csv(PREV/'data/357'/f).drop(columns='date') for f in ['datatest.txt','datatest2.txt']]); yt=xt.Occupancy.to_numpy(); xt=xt[list(df.columns)].to_numpy(); ti=np.arange(len(yt))
 else:
  tr,ti=train_test_split(np.arange(len(y)),test_size=.2,stratify=y,random_state=seed); xt=x[ti]; yt=y[ti]
 # Authors select 30% by uniform permutation, not stratification.
 li=np.random.RandomState(seed).permutation(len(tr))[:int(.3*len(tr))]; known=np.zeros(len(tr),dtype=bool); known[li]=True
 assert len(np.unique(y[tr[li]]))==len(np.unique(y))
 labels=np.full(len(tr),-1,dtype=int); labels[known]=y[tr[known]]
 return x[tr],xt,labels,known,yt,list(df.columns),dict(n_source=before,n_after_dedup=len(y),n_train=len(tr),n_test=len(yt),n_labeled=int(known.sum()),n_unlabeled=int((~known).sum()),n_features=len(df.columns),n_classes=len(np.unique(y))),dict(train_original_rows=rows[tr],test_original_rows=rows[ti] if name!='occupancy' else ti,labeled_positions=li)

def score(y,probs):
 return {'accuracy':float(accuracy_score(y,probs.argmax(1))),'auc':float(roc_auc_score(y,probs[:,1]) if probs.shape[1]==2 else roc_auc_score(y,probs,multi_class='ovr',average='macro')),'balanced_accuracy':float(balanced_accuracy_score(y,probs.argmax(1))),'macro_f1':float(f1_score(y,probs.argmax(1),average='macro')),'unique_probability_rows':len(np.unique(probs,axis=0))}

def run_job(name,seed):
 torch.set_num_threads(1); out=P/'runs'/f'{name}_{seed}'; out.mkdir(parents=True,exist_ok=True); logfile=out/'progress.jsonl'
 def progress(info):
  with logfile.open('a') as f: f.write(json.dumps({'time':time.time(),**info})+'\n')
 x,xt,labels,known,yt,cols,meta,split=prepare(name,seed); np.savez(out/'split.npz',**split); (out/'metadata.json').write_text(json.dumps(meta,indent=2))
 # The two VIME methods retain sigmoid reconstruction and train-only MinMax.
 minmax=MinMaxScaler().fit(x); xv=minmax.transform(x).astype('float32'); tv=minmax.transform(xt).astype('float32')
 zscore=StandardScaler().fit(x); xc=zscore.transform(x).astype('float32'); tc=zscore.transform(xt).astype('float32')
 for method in METHODS:
  dest=out/f'{method}.json'
  if dest.exists() and (out/f'{method}_semantics.json').exists(): continue
  start=time.time(); progress({'method':method,'stage':'start'})
  random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
  if method=='class_conditioned':
   estimator=ClassConditionedClassifier(seed,progress=lambda d:progress({'method':method,'stage':'train',**d})); estimator.fit(xc,labels,known); probabilities=estimator.predict_proba(tc)
   history={'contrastive_loss':estimator.history,'pseudo_updates':estimator.pseudo_history}
   # Diagnostic only; hidden training labels never enter fit().
   pred=estimator.final_pseudo.copy()
   # Store predictions; no hidden-label score needed for model selection.
   np.save(out/'final_pseudo_labels.npy',pred)
  else:
   iterations=100*math.ceil(int(known.sum())/256)
   config=VIMEConfig(corruption_probability=.4,self_epochs=500,semi_iterations=iterations,batch_size=256,encoder_hidden_dim=256,encoder_depth=4,predictor_hidden_dim=256,validation_fraction=0,device='cpu',seed=seed)
   estimator=VIMEClassifier(config,FastGaussianCopula() if method=='proposed_copula' else ColumnShuffleCorruptor()); estimator.fit(xv[known],labels[known],xv[~known]); probabilities=estimator.predict_proba(tv); history=estimator.history_
  np.savez_compressed(out/f'{method}_predictions.npz',probabilities=probabilities,y_test=yt)
  result={'dataset':name,'seed':seed,'method':method,'seconds':time.time()-start,**meta,**score(yt,probabilities)}
  (out/f'{method}_history.json').write_text(json.dumps(history)); dest.write_text(json.dumps(result,indent=2)); progress({'method':method,'stage':'complete',**result})
  # Shared anchors/masks for all three generation diagnostics, outside training.
  if method!='class_conditioned':
   a=xv[~known][:1000]; mask=np.random.default_rng(seed+91).random(a.shape)<.4; c=FastGaussianCopula().fit(xv[~known]) if method=='proposed_copula' else ColumnShuffleCorruptor(); generated=minmax.inverse_transform(c(a,mask,np.random.default_rng(seed+92))); original=minmax.inverse_transform(a)
  else:
   a=xc[:1000]; nmask=int(np.ceil(.4*xc.shape[1])); rng=np.random.default_rng(seed+91); mask=np.zeros(a.shape,dtype=bool); np.put_along_axis(mask,np.argsort(rng.random(a.shape),axis=1)[:,:nmask],True,axis=1)
   generated=zscore.inverse_transform(sample_class_views(xc,estimator.final_pseudo,np.arange(len(a)),mask,np.random.default_rng(seed+92))); original=zscore.inverse_transform(a)
  bad,res=data_module.violations(name,generated,cols); origbad,_=data_module.violations(name,original,cols)
  (out/f'{method}_semantics.json').write_text(json.dumps({'dataset':name,'seed':seed,'method':method,'n':len(a),'violation_rate':float(bad.mean()),'original_violation_rate':float(origbad.mean()),'mean_residual':float(res.mean()),'note':'masks follow each method: Bernoulli for VIME; fixed ceil(.4*p) for class-conditioned'}))
  del estimator; gc.collect()
 return {'dataset':name,'seed':seed,'status':'done'}

def collect():
 rows=[json.loads(f.read_text()) for f in (P/'runs').glob('*/*.json') if f.stem in METHODS]
 if rows: pd.DataFrame(rows).sort_values(['dataset','seed','method']).to_csv(P/'metrics.csv',index=False)
 diag=[json.loads(f.read_text()) for f in (P/'runs').glob('*/*_semantics.json')]
 if diag: pd.DataFrame(diag).to_csv(P/'semantics.csv',index=False)
 return len(rows)
if __name__=='__main__':
 import argparse
 args=argparse.ArgumentParser(); args.add_argument('--workers',type=int,default=4); args.add_argument('--collect-only',action='store_true'); a=args.parse_args()
 if a.collect_only: print(collect()); sys.exit()
 started=time.time(); (P/'runs').mkdir(exist_ok=True)
 (P/'environment.json').write_text(json.dumps({'python':platform.python_version(),'torch':torch.__version__,'numpy':np.__version__,'pandas':pd.__version__,'sklearn':sklearn.__version__,'scipy':scipy.__version__,'seeds':SEEDS,'methods':METHODS,'workers':a.workers,'source_pdf_sha256':hashlib.sha256(Path('/Users/kouta/Downloads/tabular_class_conditioned_augmentation_ja_summary.pdf').read_bytes()).hexdigest()},indent=2))
 with ProcessPoolExecutor(max_workers=a.workers) as pool:
  futures=[pool.submit(run_job,name,seed) for seed in SEEDS for name in NAMES]
  for future in as_completed(futures):
   print(future.result(),flush=True); print('completed model fits',collect(),flush=True)
 (P/'timing.json').write_text(json.dumps({'wall_seconds':time.time()-started})); print('DONE',collect(),flush=True)
