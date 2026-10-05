"""Controlled dependence benchmark. Run with the seminar experiment_env Python.
No test data is used to fit scalers or copulas. Configs fixed before results.
"""
from pathlib import Path
import sys, json, time, random, platform
import numpy as np
import scipy, sklearn, torch
from scipy.stats import spearmanr, bootstrap
from sklearn.datasets import load_breast_cancer,load_wine
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import roc_auc_score,accuracy_score,balanced_accuracy_score,f1_score
ROOT=Path(__file__).resolve().parent
project=next(p for p in [Path.cwd(),*ROOT.parents] if (p/'research-bench/src').exists())
sys.path.insert(0,str(project/'research-bench/src'))
from tabular_research.corruption import GaussianCopulaCorruptor,ColumnShuffleCorruptor
from tabular_research.vime_torch import VIMEClassifier,VIMEConfig
SEEDS=[11,23,37,51,67]
N=1000;D=12
CONFIGS=[('independent_mean',0.,'mean'),('moderate_mean',.5,'mean'),('strong_mean',.9,'mean'),('strong_contrast',.9,'contrast')]
torch.set_num_threads(1)

def dependence(x,names=None):
 pc=np.corrcoef(x.T);sc=np.asarray(spearmanr(x).statistic)
 ix=np.triu_indices(x.shape[1],1);p=abs(pc[ix]);s=abs(sc[ix]);top=np.argsort(p)[-5:][::-1]
 return {'n_rows':len(x),'n_features':x.shape[1],'mean_abs_pearson':float(p.mean()),'median_abs_pearson':float(np.median(p)),'max_abs_pearson':float(p.max()),'fraction_abs_pearson_gt_0_7':float((p>.7).mean()),'mean_abs_spearman':float(s.mean()),'median_abs_spearman':float(np.median(s)),'max_abs_spearman':float(s.max()),'top_pairs':[{'a':str(names[ix[0][k]]) if names is not None else int(ix[0][k]),'b':str(names[ix[1][k]]) if names is not None else int(ix[1][k]),'pearson':float(pc[ix[0][k],ix[1][k]]),'spearman':float(sc[ix[0][k],ix[1][k]])} for k in top]}

def make_data(seed,rho,task):
 rng=np.random.default_rng(20261004+seed)
 common=rng.normal(size=(N,1));noise=rng.normal(size=(N,D))
 x=np.sqrt(rho)*common+np.sqrt(1-rho)*noise
 score=x.sum(1)/np.sqrt(D*(1+(D-1)*rho)) if task=='mean' else (x[:,0]-x[:,1])/np.sqrt(2*(1-rho))
 # Both tasks have N(0,1) clean scores; noise level is identical across configs.
 y=(score+.35*rng.normal(size=N)>0).astype(int)
 return x.astype('float32'),y

def true_score(x,rho,task):
 return x.sum(1)/np.sqrt(D*(1+(D-1)*rho)) if task=='mean' else (x[:,0]-x[:,1])/np.sqrt(2*(1-rho))

def quality(xfit,xeval,rho,task,seed):
 rng=np.random.default_rng(seed+800000)
 mask=rng.random(xeval.shape)<.4
 cop=GaussianCopulaCorruptor().fit(xfit)
 R=(1-rho)*np.eye(D)+rho*np.ones((D,D))
 # Correctly generated residuals have expected standardized squared value 1.
 def residual_calibration(g):
  squared=[]
  for i in range(len(xeval)):
   m=np.flatnonzero(mask[i]);o=np.flatnonzero(~mask[i])
   if not len(m):continue
   if len(o):
    cross=R[np.ix_(m,o)];sol=np.linalg.solve(R[np.ix_(o,o)],xeval[i,o]);mu=cross@sol
    cov=R[np.ix_(m,m)]-cross@np.linalg.solve(R[np.ix_(o,o)],R[np.ix_(o,m)])
   else:mu=np.zeros(len(m));cov=R[np.ix_(m,m)]
   # Marginal conditional-variance calibration, not a full distribution score.
   squared.extend(((g[i,m]-mu)**2/np.diag(cov)).tolist())
  return float(np.mean(squared))
 base_corr=np.corrcoef(xeval.T);tri=np.triu_indices(D,1)
 records={'original':{'mean_abs_pearson':dependence(xeval)['mean_abs_pearson'],'conditional_residual_ratio':residual_calibration(xeval),'oracle_boundary_flip_rate':0.}}
 for name,c in [('column_shuffle',ColumnShuffleCorruptor()),('gaussian_copula',cop)]:
  g=c(xeval,mask,np.random.default_rng(seed+900000));corr=np.corrcoef(g.T)
  assert np.array_equal(g[~mask],xeval[~mask])
  records[name]={'mean_abs_pearson':float(np.abs(corr[tri]).mean()),'pair_corr_mae_vs_original':float(np.abs(corr[tri]-base_corr[tri]).mean()),'conditional_residual_ratio':residual_calibration(g),'oracle_boundary_flip_rate':float(np.mean((true_score(g,rho,task)>0)!=(true_score(xeval,rho,task)>0))),'mean_squared_change_masked':float(np.mean((g[mask]-xeval[mask])**2)),'observed_unchanged':True}
 return records

def summarize(runs):
 out={}
 for name,rho,task in CONFIGS:
  rr=[r for r in runs if r['dataset']==name]
  if not rr:continue
  s={}
  for method in ['column_shuffle','gaussian_copula']:
   s[method]={}
   for metric in ['auc','accuracy','balanced_accuracy','macro_f1']:
    vals=np.array([r['metrics'][method][metric] for r in rr]);s[method][metric]={'mean':float(vals.mean()),'std':float(vals.std(ddof=1)) if len(vals)>1 else None,'values':vals.tolist()}
  diff=np.array([r['metrics']['gaussian_copula']['auc']-r['metrics']['column_shuffle']['auc'] for r in rr]);ci=bootstrap((diff,),np.mean,method='percentile',n_resamples=10000,random_state=2026).confidence_interval if len(diff)>1 else None
  s['paired_auc_difference']={'mean':float(diff.mean()),'values':diff.tolist(),'ci95':None if ci is None else [float(ci.low),float(ci.high)]}
  s['quality_mean']={m:{metric:float(np.mean([r['quality'][m][metric] for r in rr])) for metric in rr[0]['quality'][m] if isinstance(rr[0]['quality'][m][metric],(float,int)) and not isinstance(rr[0]['quality'][m][metric],bool)} for m in ['original','column_shuffle','gaussian_copula']}
  s['observed_dependence_mean']={k:float(np.mean([r['dependence'][k] for r in rr])) for k in ['mean_abs_pearson','mean_abs_spearman','fraction_abs_pearson_gt_0_7']}
  out[name]=s
 return out

begin=time.time();runs=[]
real={name:dependence(loader().data,loader().feature_names) for name,loader in [('breast_cancer',load_breast_cancer),('wine',load_wine)]}
(ROOT/'existing_data_dependence.json').write_text(json.dumps(real,ensure_ascii=False,indent=2))
print('EXISTING DEPENDENCE',json.dumps(real,ensure_ascii=False),flush=True)
meta={'versions':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__,'sklearn':sklearn.__version__,'torch':torch.__version__,'platform':platform.platform()},'protocol':{'n':N,'d':D,'seeds':SEEDS,'configs':CONFIGS,'data_seed':'20261004 + seed, newly generated per replicate','train_test':'80/20 stratified','labeled_fraction_train':.3,'mask_probability':.4,'self_epochs':15,'semi_iterations':300,'batch':64,'encoder':'4x32','n_views':3,'label_noise_sd':.35,'same_noise_and_hyperparameters_across_rho':True,'fit_copula':'unlabeled train only','quality_evaluation':'held-out test features; diagnostic only, not model selection','threads':1,'seed_ci':'exploratory paired percentile bootstrap, 5 replicates'},'existing_data_dependence':real}
for name,rho,task in CONFIGS:
 for seed in SEEDS:
  x,y=make_data(seed,rho,task)
  tr,te=train_test_split(np.arange(N),test_size=.2,stratify=y,random_state=seed)
  il,iu=train_test_split(tr,train_size=.3,stratify=y[tr],random_state=seed+100003)
  scaler=MinMaxScaler().fit(x[tr]);xl=scaler.transform(x[il]).astype('float32');xu=scaler.transform(x[iu]).astype('float32');xt=scaler.transform(x[te]).astype('float32')
  cfg=VIMEConfig(corruption_probability=.4,reconstruction_weight=2.,n_augmented_views=3,consistency_weight=1.,self_epochs=15,semi_iterations=300,batch_size=64,predictor_hidden_dim=32,encoder_hidden_dim=32,encoder_depth=4,encoder_dropout=0.,validation_fraction=0.,device='cpu',seed=seed)
  q=quality(x[iu],x[te],rho,task,seed);metrics={}
  for method,c in [('column_shuffle',None),('gaussian_copula',GaussianCopulaCorruptor())]:
   random.seed(seed);np.random.seed(seed);torch.manual_seed(seed)
   est=VIMEClassifier(config=cfg,corruptor=c).fit(xl,y[il],xu)
   probs=est.predict_proba(xt);pred=probs.argmax(1)
   metrics[method]={'auc':float(roc_auc_score(y[te],probs[:,1])),'accuracy':float(accuracy_score(y[te],pred)),'balanced_accuracy':float(balanced_accuracy_score(y[te],pred)),'macro_f1':float(f1_score(y[te],pred,average='macro'))}
   print(name,'rho',rho,'seed',seed,method,json.dumps(metrics[method]),flush=True)
  runs.append({'dataset':name,'rho':rho,'task':task,'seed':seed,'n_labeled':len(il),'n_unlabeled':len(iu),'n_test':len(te),'dependence':dependence(x[iu]),'quality':q,'metrics':metrics})
  result={**meta,'runs':runs,'summary':summarize(runs),'elapsed_sec':time.time()-begin}
  (ROOT/'results.json').write_text(json.dumps(result,ensure_ascii=False,indent=2))
print('COMPLETE',json.dumps(summarize(runs)),flush=True)
