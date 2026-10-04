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
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'research-bench/src'))
from tabular_research.vime_torch import VIMEClassifier,VIMEConfig
from tabular_research.corruption import GaussianCopulaCorruptor,ColumnShuffleCorruptor
ROOT=Path(__file__).parent
torch.set_num_threads(1)
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
