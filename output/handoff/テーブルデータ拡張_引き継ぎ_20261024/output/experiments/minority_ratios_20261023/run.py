"""Fully labelled, controlled imbalance benchmark. No held-out information in synthesis."""
import os
os.environ.setdefault('OMP_NUM_THREADS','1')
os.environ.setdefault('OPENBLAS_NUM_THREADS','1')
os.environ.setdefault('MKL_NUM_THREADS','1')
import argparse, hashlib, importlib.metadata, json, platform, time, warnings
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import numpy as np
import pandas as pd
import torch
from scipy.io import arff
from scipy.stats import norm, rankdata, spearmanr, ks_2samp
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors, KNeighborsClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import balanced_accuracy_score, f1_score, recall_score, precision_score, roc_auc_score, average_precision_score, confusion_matrix
from imblearn.over_sampling import SMOTE
from ctgan import CTGAN
from threadpoolctl import threadpool_limits

ROOT=Path(__file__).resolve().parents[3]
BASE=Path(__file__).resolve().parent
DATA=ROOT/'output/experiments/public_semantics_20261015/data'
METHODS=['none','duplicate','class_weight','shuffle','copula','smote','copula_smote','ctgan','ctgan_copula']
SOURCES={'rice':'https://archive.ics.uci.edu/dataset/545/rice+cammeo+and+osmancik','raisin':'https://archive.ics.uci.edu/dataset/850/raisin','grid':'https://archive.ics.uci.edu/dataset/471/electrical+grid+stability+simulated+data'}

def load(name):
    if name in ['rice','raisin']:
        did='545' if name=='rice' else '850'
        f=next((DATA/did).rglob('*.arff'))
        df=pd.DataFrame(arff.loadarff(f)[0]); df.columns=[c.replace('_','') for c in df.columns]
        target=df.pop('Class').str.decode('utf8')
        positive='Cammeo' if name=='rice' else 'Besni'
    else:
        f=next((DATA/'471').rglob('*.csv'))
        df=pd.read_csv(f); target=df.pop('stabf'); df=df.drop(columns='stab'); positive='stable'
    x=df.to_numpy(dtype=float); y=(target==positive).to_numpy(dtype=int)
    assert np.isfinite(x).all() and set(y)=={0,1}
    return x,y,list(df.columns),{'n':len(y),'features':len(df.columns),'positive':positive,'negative':[v for v in sorted(target.unique()) if v!=positive][0],'original_counts':np.bincount(y).tolist(),'source':SOURCES[name],'file':str(f.relative_to(ROOT)),'sha256':hashlib.sha256(f.read_bytes()).hexdigest()}

class Marginals:
    def fit(self,x):
        self.sorted=np.sort(x,axis=0); self.n=len(x); self.q=(np.arange(self.n)+.5)/self.n
        self.unique=[]
        for j in range(x.shape[1]):
            u,inv=np.unique(x[:,j],return_inverse=True)
            ranks=rankdata(x[:,j],method='average'); probs=(ranks-.5)/len(x)
            self.unique.append((u,np.array([probs[inv==i][0] for i in range(len(u))])))
        return self
    def transform(self,x):
        return np.column_stack([norm.ppf(np.clip(np.interp(x[:,j],u,v),.5/self.n,1-.5/self.n)) for j,(u,v) in enumerate(self.unique)])
    def inverse(self,z):
        return np.column_stack([np.interp(norm.cdf(z[:,j]),self.q,self.sorted[:,j]) for j in range(z.shape[1])])

def common_round(name,x,cols):
    x=np.array(x,dtype=float,copy=True)
    if name in ['rice','raisin']:
        for c in ['Area','ConvexArea']: x[:,cols.index(c)]=np.rint(x[:,cols.index(c)])
    return x

def repair(name,x,cols):
    """Predefined algebraic guard. Uses no classifiers or test information."""
    z=x.copy(); d={c:i for i,c in enumerate(cols)}
    if name in ['rice','raisin']:
        for c in ['Area','ConvexArea','MajorAxisLength','MinorAxisLength','Perimeter']:
            z[:,d[c]]=np.maximum(z[:,d[c]],1e-6 if c not in ['Area','ConvexArea'] else 1)
        a=z[:,d['MajorAxisLength']]; b=z[:,d['MinorAxisLength']]
        z[:,d['MinorAxisLength']]=np.minimum(a,b)
        z[:,d['Eccentricity']]=np.sqrt(np.maximum(0,1-(z[:,d['MinorAxisLength']]/a)**2))
        z[:,d['ConvexArea']]=np.maximum(z[:,d['ConvexArea']],z[:,d['Area']])
        z[:,d['Extent']]=np.clip(z[:,d['Extent']],0,1)
    else:
        z[:,d['p1']]=-(z[:,d['p2']]+z[:,d['p3']]+z[:,d['p4']])
    return common_round(name,z,cols)

def semantics(name,x,cols):
    d={c:x[:,i] for i,c in enumerate(cols)}
    if name in ['rice','raisin']:
        a,b=d['MajorAxisLength'],d['MinorAxisLength']
        residual=np.abs(d['Eccentricity']-np.sqrt(np.maximum(0,1-(b/np.maximum(a,1e-12))**2)))
        relation=(residual>.01)|(b>a)|(d['Area']>d['ConvexArea']+1)
        bounds=(np.column_stack([d[c]<=0 for c in ['Area','ConvexArea','MajorAxisLength','MinorAxisLength','Perimeter']]).any(1))|(d['Extent']<0)|(d['Extent']>1)|(d['Eccentricity']<0)|(d['Eccentricity']>1)
    else:
        residual=np.abs(d['p1']+d['p2']+d['p3']+d['p4']); relation=residual>.01
        bounds=np.column_stack([(d['tau'+str(k)]<.5)|(d['tau'+str(k)]>10)|(d['g'+str(k)]<.05)|(d['g'+str(k)]>1) for k in range(1,5)]).any(1)
        bounds=bounds|np.column_stack([(d['p'+str(k)]< -2)|(d['p'+str(k)]>-.5) for k in range(2,5)]).any(1)
    return dict(relation_violation=float(np.mean(relation)),bound_violation=float(np.mean(bounds)),relation_residual=float(np.mean(residual)))

def synth(method,x,y,cols,n,seed,epochs,work):
    rng=np.random.default_rng(seed+6001); xm=x[y==1]; extra={}
    if method=='duplicate': return xm[rng.integers(len(xm),size=n)],extra
    if method=='shuffle': return np.column_stack([rng.choice(xm[:,j],n) for j in range(x.shape[1])]),extra
    if method=='copula':
        marginal=Marginals().fit(xm); z=marginal.transform(xm); r=np.corrcoef(z,rowvar=False)
        r=np.nan_to_num(r); np.fill_diagonal(r,1); r=.95*r+.05*np.eye(len(cols))
        val,vec=np.linalg.eigh(r); cov=(vec*np.maximum(val,1e-8))@vec.T
        return marginal.inverse(rng.multivariate_normal(np.zeros(len(cols)),cov,size=n)),extra
    if method=='smote':
        sc=StandardScaler().fit(x); v=sc.transform(x)
        xa,ya=SMOTE(random_state=seed,k_neighbors=5).fit_resample(v,y)
        return sc.inverse_transform(xa[len(x):]),extra
    if method=='copula_smote':
        marginal=Marginals().fit(xm); z=marginal.transform(xm)
        nn=NearestNeighbors(n_neighbors=6).fit(z).kneighbors(z,return_distance=False)[:,1:]
        i=rng.integers(len(z),size=n); j=nn[i,rng.integers(5,size=n)]
        return marginal.inverse(z[i]+rng.random((n,1))*(z[j]-z[i])),extra
    assert method in ['ctgan','ctgan_copula']
    train=x.copy(); margins={}
    if method=='ctgan_copula':
        for c in [0,1]:
            margins[c]=Marginals().fit(x[y==c]); train[y==c]=margins[c].transform(x[y==c])
    df=pd.DataFrame(train,columns=cols); df['label']=np.where(y==1,'minority','majority')
    model=CTGAN(epochs=epochs,embedding_dim=128,generator_dim=(128,128),discriminator_dim=(128,128),batch_size=200,pac=10,verbose=False,cuda=False)
    model.set_random_state(seed); model.fit(df,discrete_columns=['label'])
    model.loss_values.to_csv(work/f'{method}_loss.csv',index=False)
    model.save(work/f'{method}_model.pkl')
    got=[]; candidates=0; returned_minor=0
    for _ in range(100):
        size=max(n-sum(len(t) for t in got),200)
        out=model.sample(size,condition_column='label',condition_value='minority')
        candidates+=len(out); out=out[out.label=='minority']; returned_minor+=len(out)
        if len(out): got.append(out[cols].to_numpy(dtype=float))
        if sum(len(t) for t in got)>=n: break
    if not got or sum(len(t) for t in got)<n: raise RuntimeError('Insufficient conditional minority samples')
    g=np.concatenate(got)[:n]
    if method=='ctgan_copula': g=margins[1].inverse(g)
    extra={'conditional_label_acceptance':returned_minor/candidates,'conditional_candidates':candidates,'conditional_returned_minority':returned_minor}
    return g,extra

def quality(name,g,x,y,cols):
    xm=x[y==1]; sc=StandardScaler().fit(x); gm=sc.transform(g); mm=sc.transform(xm)
    nn=NearestNeighbors(n_neighbors=1).fit(mm).kneighbors(gm)[0][:,0]
    kn=KNeighborsClassifier(n_neighbors=1).fit(sc.transform(x),y)
    c1=pd.DataFrame(xm).corr(method='spearman').to_numpy(); c2=pd.DataFrame(g).corr(method='spearman').to_numpy(); upper=np.triu_indices(len(cols),1)
    return dict(**semantics(name,g,cols),minority_1nn_agreement=float(np.mean(kn.predict(gm)==1)),nn_distance_median=float(np.median(nn)),copy_rate=float(np.mean(nn<1e-8)),unique_fraction=float(len(np.unique(g,axis=0))/len(g)),spearman_error=float(np.mean(np.abs(np.nan_to_num(c1-c2)[upper]))),marginal_ks=float(np.mean([ks_2samp(xm[:,j],g[:,j]).statistic for j in range(len(cols))])))

def evaluate(x,y,xt,yt,seed,weighted):
    results=[]
    sc=StandardScaler().fit(x); a=sc.transform(x); b=sc.transform(xt)
    models={'logistic':LogisticRegression(C=1,max_iter=2000,class_weight='balanced' if weighted else None,random_state=seed),'hist_boost':HistGradientBoostingClassifier(max_iter=100,max_leaf_nodes=15,l2_regularization=1,early_stopping=False,class_weight='balanced' if weighted else None,random_state=seed)}
    for name,model in models.items():
        t=time.perf_counter(); model.fit(a,y); prob=model.predict_proba(b)[:,1]; pred=(prob>=.5).astype(int)
        results.append(dict(classifier=name,macro_f1=float(f1_score(yt,pred,average='macro')),balanced_accuracy=float(balanced_accuracy_score(yt,pred)),recall=float(recall_score(yt,pred)),precision=float(precision_score(yt,pred,zero_division=0)),roc_auc=float(roc_auc_score(yt,prob)),average_precision=float(average_precision_score(yt,prob)),classifier_seconds=time.perf_counter()-t,tn=int(confusion_matrix(yt,pred)[0,0]),fp=int(confusion_matrix(yt,pred)[0,1]),fn=int(confusion_matrix(yt,pred)[1,0]),tp=int(confusion_matrix(yt,pred)[1,1])))
    return results

def job(args):
    name,seed,rho,epochs,out=args; out=Path(out); work=out/f'{name}_{int(rho*100)}_{seed}'; work.mkdir(parents=True,exist_ok=True)
    done=work/'result.json'
    if done.exists(): return json.loads(done.read_text())
    torch.set_num_threads(1)
    warnings.filterwarnings('ignore',category=FutureWarning)
    threadpool_limits(limits=1)
    allx,ally,cols,meta=load(name)
    pool,te=train_test_split(np.arange(len(ally)),test_size=.3,stratify=ally,random_state=seed)
    rng=np.random.default_rng(seed+101); ma=pool[ally[pool]==0]; mi=pool[ally[pool]==1]
    total=(int(min(1100,len(ma)/.9,len(mi)/.3))//10)*10
    ma=rng.permutation(ma)[:int(round(total*(1-rho)))]; mi=rng.permutation(mi)[:int(round(total*rho))]
    tr=np.concatenate([ma,mi]); rng.shuffle(tr); x,y,xt,yt=allx[tr],ally[tr],allx[te],ally[te]
    n=int(sum(y==0)-sum(y==1)); assert len(set(tr)&set(te))==0
    np.savez_compressed(work/'split.npz',train_indices=tr,test_indices=te,x_train=x,y_train=y,x_test=xt,y_test=yt,feature_names=np.array(cols))
    meta.update(seed=seed,minority_fraction=rho,train_total=len(y),train_counts=np.bincount(y).tolist(),test_counts=np.bincount(yt).tolist(),n_added=n,source_train_semantics=semantics(name,x,cols),source_minority_semantics=semantics(name,x[y==1],cols))
    rows=[]; qs=[]; times=[]
    for method in METHODS:
        start=time.perf_counter(); cached=work/f'{method}_generated.npz'
        if method in ['none','class_weight']:
            g=np.empty((0,x.shape[1])); extra={}; seconds=0
        elif cached.exists():
            d=np.load(cached); g=d['generated']; extra=json.loads((work/f'{method}_generation.json').read_text()); seconds=extra['generator_seconds']
        else:
            raw,extra=synth(method,x,y,cols,n,seed,epochs,work); g=common_round(name,raw,cols)
            assert g.shape==(n,x.shape[1]) and np.isfinite(g).all()
            seconds=time.perf_counter()-start; extra.update(generator_seconds=seconds)
            np.savez_compressed(cached,raw_generated=raw,generated=g)
            (work/f'{method}_generation.json').write_text(json.dumps(extra,indent=2))
        times.append(dict(dataset=name,seed=seed,minority_fraction=rho,method=method,generator_seconds=seconds,n_added=len(g),**{k:v for k,v in extra.items() if k!='generator_seconds'}))
        for variant in ['base','repair'] if len(g) and method!='duplicate' else ['base']:
            z=g if variant=='base' else repair(name,g,cols)
            if len(z): qs.append(dict(dataset=name,seed=seed,minority_fraction=rho,method=method,variant=variant,**quality(name,z,x,y,cols)))
            xa=np.concatenate([x,z]); ya=np.concatenate([y,np.ones(len(z),dtype=int)])
            for r in evaluate(xa,ya,xt,yt,seed,method=='class_weight'):
                rows.append(dict(dataset=name,seed=seed,minority_fraction=rho,method=method,variant=variant,n_majority=int(sum(y==0)),n_minority=int(sum(y==1)),n_added=len(z),**r))
        print(json.dumps({'dataset':name,'seed':seed,'minority_fraction':rho,'method':method,'generator_seconds':round(seconds,2),'macro_f1_logistic':round(rows[-2 if len(g)==0 or method=='duplicate' else -4]['macro_f1'],4)},ensure_ascii=False),flush=True)
    result={'metadata':meta,'metrics':rows,'quality':qs,'timing':times}; done.write_text(json.dumps(result,indent=2))
    return result

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--datasets',nargs='+',default=['rice','raisin','grid']); ap.add_argument('--ratios',nargs='+',type=float,default=[.1,.2,.3]); ap.add_argument('--seeds',nargs='+',type=int,default=[11,23,37,51,67]); ap.add_argument('--epochs',type=int,default=300); ap.add_argument('--workers',type=int,default=2); ap.add_argument('--out',type=Path,default=BASE/'results'); a=ap.parse_args(); a.out.mkdir(parents=True,exist_ok=True)
    config={'datasets':a.datasets,'seeds':a.seeds,'ctgan_epochs':a.epochs,'ctgan_hidden':[128,128],'batch_size':200,'test_fraction':.3,'train_total_cap':1100,'minority_fractions':a.ratios,'sampling':'fixed total within dataset; class-specific nested prefixes across ratios','copula_shrinkage':.05,'smote_k':5,'threshold':.5,'hyperparameter_search':False,'repair':'predefined algebraic consistency repair, no test use','platform':platform.platform(),'python':platform.python_version(),'versions':{k:importlib.metadata.version(k) for k in ['numpy','pandas','scipy','scikit-learn','torch','ctgan','rdt','imbalanced-learn']}}
    (a.out/'protocol.json').write_text(json.dumps(config,indent=2))
    tasks=[(d,s,r,a.epochs,str(a.out)) for d in a.datasets for r in a.ratios for s in a.seeds]; results=[]
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for result in ex.map(job,tasks):
            results.append(result)
            for kind in ['metrics','quality','timing']: pd.DataFrame([r for t in results for r in t[kind]]).to_csv(a.out/f'{kind}.csv',index=False)
            (a.out/'datasets.json').write_text(json.dumps([r['metadata'] for r in results],indent=2))
    print(json.dumps({'completed_jobs':len(results),'out':str(a.out)},ensure_ascii=False),flush=True)

if __name__=='__main__': main()
