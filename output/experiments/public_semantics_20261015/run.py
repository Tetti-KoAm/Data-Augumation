"""Public-data paired low-label benchmark; run from repository root."""
import os,sys,json,time,hashlib,platform,zipfile,io
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'research-bench/src'))
import numpy as np,pandas as pd,torch,scipy,sklearn
from scipy.io import arff
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler,LabelEncoder,StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score,balanced_accuracy_score,f1_score
from tabular_research.corruption import ColumnShuffleCorruptor,GaussianCopulaCorruptor
from tabular_research.vime_torch import VIMEClassifier,VIMEConfig
from fast_copula import FastGaussianCopula
OUT=Path(__file__).resolve().parent; DATA=OUT/'data'; torch.set_num_threads(1)
SEEDS=[11,23,37,51,67]; LABELS=[30,100]
def load(name):
 if name=='bean': f=next((DATA/'602').rglob('*.arff')); df=pd.DataFrame(arff.loadarff(f)[0])
 elif name=='rice': f=next((DATA/'545').rglob('*.arff')); df=pd.DataFrame(arff.loadarff(f)[0])
 elif name=='raisin':
  f=next((DATA/'850').rglob('*.arff')); df=pd.DataFrame(arff.loadarff(f)[0])
 elif name=='grid': df=pd.read_csv(next((DATA/'471').rglob('*.csv'))); df=df.drop(columns='stab').rename(columns={'stabf':'Class'})
 else:
  df=pd.read_csv(DATA/'357/datatraining.txt').drop(columns='date').rename(columns={'Occupancy':'Class'})
 df.columns=[c.replace('_','') for c in df.columns]
 target='Class'; y=LabelEncoder().fit_transform(df.pop(target)); return df.astype(float),y

def violations(name,x,cols):
 d={c:x[:,i] for i,c in enumerate(cols)}
 if name in ['bean','rice','raisin']:
  a,b,e=d['MajorAxisLength'],d['MinorAxisLength'],d['Eccentricity']
  residual=np.abs(e-np.sqrt(np.maximum(0,1-(b/a)**2)))
  return (residual>0.01)|(b>a)|(d['Area']>d['ConvexArea']+1),residual
 if name=='grid':
  r=np.abs(d['p1']+d['p2']+d['p3']+d['p4']); return r>0.01,r
 # Standard pressure approximation; 5% tolerance accommodates source formula differences.
 t,h=d['Temperature'],d['Humidity']; pv=h/100*610.78*np.exp(17.2694*t/(t+237.3)); expected=.62198*pv/(101325-pv)
 r=np.abs(d['HumidityRatio']-expected)/expected
 return r>.05,r

def scores(y,p):
 return dict(auc=float(roc_auc_score(y,p[:,1]) if p.shape[1]==2 else roc_auc_score(y,p,multi_class='ovr',average='macro')),balanced_accuracy=float(balanced_accuracy_score(y,p.argmax(1))),macro_f1=float(f1_score(y,p.argmax(1),average='macro')))

def run():
 started=time.time(); rows=[]; diags=[]; meta={}
 for name in ['bean','rice','raisin','occupancy','grid']:
  df,y=load(name); x=df.to_numpy(); cols=list(df.columns)
  meta[name]={'n':len(y),'features':cols,'classes':np.bincount(y).tolist()}
  for seed in SEEDS:
   if name=='occupancy':
    tr=np.arange(len(y)); tests=[pd.read_csv(DATA/'357'/f).drop(columns='date') for f in ['datatest.txt','datatest2.txt']]; te=pd.concat(tests); xt=te[cols].to_numpy(); yt=te.Occupancy.to_numpy()
   else:
    tr,ti=train_test_split(np.arange(len(y)),test_size=.2,stratify=y,random_state=seed); xt=x[ti]; yt=y[ti]
   if len(tr)>2000: tr,_=train_test_split(tr,train_size=2000,stratify=y[tr],random_state=seed+1)
   scaler=MinMaxScaler().fit(x[tr]); train=scaler.transform(x[tr]).astype('float32'); test=scaler.transform(xt).astype('float32')
   corr=pd.DataFrame(x[tr],columns=cols).corr(); pairs=[(cols[i],cols[j],float(corr.iloc[i,j])) for i in range(len(cols)) for j in range(i)]
   low=sorted(pairs,key=lambda z:abs(z[2])); meta[name].setdefault('train_correlation',[]).append({'seed':seed,'mean_abs':float(np.mean([abs(z[2]) for z in pairs])),'fraction_abs_below_point1':float(np.mean([abs(z[2])<.1 for z in pairs])),'lowest_pairs':low[:5]})
   for nl in LABELS:
    li,ui=train_test_split(np.arange(len(tr)),train_size=nl,stratify=y[tr],random_state=seed+100003)
    # Persist exact source positions; no target enters augmentation fitting.
    np.savez(OUT/f'split_{name}_{seed}_{nl}.npz',train_source_indices=tr,labeled_positions=li,unlabeled_positions=ui,**({'test_source_indices':ti} if name!='occupancy' else {}))
    for method in ['supervised_logistic','vime_shuffle','vime_copula']:
     st=time.time()
     if method=='supervised_logistic':
      model=make_pipeline(StandardScaler(),LogisticRegression(max_iter=2000,C=1)); model.fit(x[tr[li]],y[tr[li]]); p=model.predict_proba(xt)
     else:
      config=VIMEConfig(corruption_probability=.4,self_epochs=15,semi_iterations=300,batch_size=64,encoder_hidden_dim=32,encoder_depth=4,predictor_hidden_dim=32,validation_fraction=0,device='cpu',seed=seed)
      model=VIMEClassifier(config,FastGaussianCopula() if method=='vime_copula' else ColumnShuffleCorruptor()); model.fit(train[li],y[tr[li]],train[ui]); p=model.predict_proba(test)
     row=dict(dataset=name,seed=seed,n_labels=nl,n_unlabeled=len(ui),method=method,seconds=time.time()-st,**scores(yt,p)); rows.append(row); pd.DataFrame(rows).to_csv(OUT/'metrics.csv',index=False); print(row,flush=True)
    # Same unlabeled anchors and same mask, independent RNG for values.
    anchor=train[ui[:min(1000,len(ui))]]; mask=np.random.default_rng(seed+17).random(anchor.shape)<.4
    for method,c in [('original',None),('shuffle',ColumnShuffleCorruptor()),('copula',FastGaussianCopula().fit(train[ui]))]:
     aug=anchor if c is None else c(anchor,mask,np.random.default_rng(seed+29)); raw=scaler.inverse_transform(aug); bad,res=violations(name,raw,cols)
     d=dict(dataset=name,seed=seed,n_labels=nl,method=method,violation_rate=float(bad.mean()),mean_residual=float(res.mean()),n=len(raw)); diags.append(d)
     if method=='shuffle' and bad.any() and seed==11 and nl==30:
      j=int(np.flatnonzero(bad)[0]); meta[name]['example']={'original':dict(zip(cols,map(float,scaler.inverse_transform(anchor)[j]))),'augmented':dict(zip(cols,map(float,raw[j]))),'masked':[cols[k] for k in np.flatnonzero(mask[j])],'residual':float(res[j])}
    pd.DataFrame(diags).to_csv(OUT/'semantics.csv',index=False); (OUT/'metadata.json').write_text(json.dumps(meta,indent=2))
 result={'seconds':time.time()-started,'seeds':SEEDS,'labels':LABELS,'python':platform.python_version(),'numpy':np.__version__,'torch':torch.__version__,'scipy':scipy.__version__,'sklearn':sklearn.__version__,'archive_sha256':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in DATA.glob('*.zip')}}
 (OUT/'environment.json').write_text(json.dumps(result,indent=2))
if __name__=='__main__': run()
