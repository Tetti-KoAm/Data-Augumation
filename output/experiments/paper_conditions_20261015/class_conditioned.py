"""Numeric-only adapter for pinned Cui et al. model and training algorithm.

Uses the authors' unmodified MLP definition/initialization, vectorized equivalent
cosine loss, and fixed-encoder feature caching during classifier updates.
"""
import sys,types,importlib.util,time
from pathlib import Path
import numpy as np
import torch
from torch import nn
from torch.nn import functional as F
ROOT=Path(__file__).resolve().parents[3]
def author_model_class():
 shim=types.ModuleType('utils'); shim.DEVICE=torch.device('cpu')
 old=sys.modules.get('utils'); sys.modules['utils']=shim
 try:
  spec=importlib.util.spec_from_file_location('pinned_cc_model',ROOT/'research-bench/upstream/Tabular-Class-Conditioned-SSL/model.py'); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
 finally:
  if old is None: del sys.modules['utils']
  else: sys.modules['utils']=old
 return m.Neural_Net
AuthorModel=author_model_class()
def fast_contrastive(zi,zj,temp=1.):
 z=F.normalize(torch.cat([zi,zj]),dim=1,eps=1e-8); sim=z@z.T; n=len(zi)
 positive=torch.cat([sim.diag(n),sim.diag(-n)]); denominator=torch.exp(sim/temp).masked_fill(torch.eye(2*n,dtype=torch.bool),0).sum(1)
 return -(torch.exp(positive/temp)/denominator).log().mean()

def train_head(model,x,y,positions,epochs,batch,rng):
 model.freeze_encoder(); model.initialize_classification_head()
 with torch.no_grad(): z=model.encoder(x[positions])
 yy=y[positions]; opt=torch.optim.Adam(model.classification_head.parameters(),lr=.001)
 # Original sampler visits current order and shuffles at epoch end. Caching is
 # exact because encoder is fixed and author architecture has zero dropout.
 order=np.arange(len(positions)); loss=0.
 for _ in range(epochs):
  for start in range(0,len(order),batch):
   idx=order[start:start+batch]; pred=model.classification_head(z[idx]); l=F.cross_entropy(pred,yy[idx]); opt.zero_grad(); l.backward(); opt.step(); loss=float(l.detach())
  order=rng.permutation(order)
 return loss

def sample_class_views(x,pseudo,idx,mask,rng):
 donors=np.empty_like(mask,dtype=int)
 for c in np.unique(pseudo[idx]):
  selected=np.flatnonzero(pseudo[idx]==c); candidates=np.flatnonzero(pseudo==c)
  donors[selected]=rng.choice(candidates,size=(len(selected),x.shape[1]))
 out=x[idx].copy(); vals=x[donors,np.arange(x.shape[1])]; out[mask]=vals[mask]; return out

class ClassConditionedClassifier:
 def __init__(self,seed,epochs=500,head_epochs=100,batch=256,width=256,progress=None):
  self.seed=seed; self.epochs=epochs; self.head_epochs=head_epochs; self.batch=batch; self.width=width; self.progress=progress; self.history=[]; self.pseudo_history=[]
 def fit(self,x,known_labels,known_mask):
  assert np.isfinite(x).all() and known_mask.dtype==bool
  # Unknown labels must be explicitly masked at the API boundary.
  assert np.all(known_labels[~known_mask]==-1)
  np.random.seed(self.seed); torch.manual_seed(self.seed); rng=np.random.default_rng(self.seed)
  xt=torch.from_numpy(x.astype('float32')); known=np.flatnonzero(known_mask); yy=torch.tensor(known_labels,dtype=torch.long); nc=len(np.unique(known_labels[known]))
  bootstrap=AuthorModel(x.shape[1],self.width,nc)
  train_head(bootstrap,xt,yy,known,self.head_epochs,self.batch,rng)
  with torch.no_grad(): pseudo=bootstrap.get_classification_prediction_logits(xt).argmax(1).numpy()
  pseudo[known]=known_labels[known]
  self.model=AuthorModel(x.shape[1],self.width,nc)
  opt=torch.optim.Adam(self.model.parameters(),lr=.001); order=np.arange(len(x)); nmask=int(np.ceil(.4*x.shape[1])); starttime=time.time()
  for epoch in range(1,self.epochs+1):
   if epoch%10==0:
    train_head(self.model,xt,yy,known,self.head_epochs,self.batch,rng)
    with torch.no_grad(): pseudo=self.model.get_classification_prediction_logits(xt).argmax(1).numpy()
    pseudo[known]=known_labels[known]; self.model.unfreeze_encoder()
    self.pseudo_history.append({'epoch':epoch,'class_counts':np.bincount(pseudo,minlength=nc).tolist()})
   loss_sum=0.; nb=0
   for offset in range(0,len(order),self.batch):
    idx=order[offset:offset+self.batch]
    mask=np.zeros((len(idx),x.shape[1]),dtype=bool)
    # Uniform fixed ceil(.4*p) feature subset, as in authors' random mask.
    selected=np.argsort(rng.random(mask.shape),axis=1)[:,:nmask]; np.put_along_axis(mask,selected,True,axis=1)
    views=sample_class_views(x,pseudo,idx,mask,rng)
    za=self.model.get_final_embedding(xt[idx]); zv=self.model.get_final_embedding(torch.from_numpy(views.astype('float32')))
    loss=fast_contrastive(za,zv); opt.zero_grad(); loss.backward(); opt.step(); loss_sum+=float(loss.detach()); nb+=1
   order=rng.permutation(order); self.history.append(loss_sum/nb)
   if self.progress and epoch%50==0: self.progress({'epoch':epoch,'loss':self.history[-1],'seconds':time.time()-starttime})
  train_head(self.model,xt,yy,known,self.head_epochs,self.batch,rng)
  with torch.no_grad(): self.final_pseudo=self.model.get_classification_prediction_logits(xt).argmax(1).numpy()
  self.final_pseudo[known]=known_labels[known]; return self
 def predict_proba(self,x):
  self.model.eval()
  with torch.no_grad(): return self.model.get_classification_prediction_logits(torch.from_numpy(x.astype('float32'))).softmax(1).numpy()
