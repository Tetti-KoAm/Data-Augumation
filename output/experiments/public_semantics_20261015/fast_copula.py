"""Vectorize marginal transforms; preserve the existing copula sampling model."""
import numpy as np
from tabular_research.corruption import GaussianCopulaCorruptor
class FastGaussianCopula(GaussianCopulaCorruptor):
 def sample_conditional(self,x,mask,rng):
  if self._corr is None: raise RuntimeError('Call fit first')
  x=np.asarray(x,dtype=float); mask=np.asarray(mask,dtype=bool)
  if x.ndim!=2 or x.shape!=mask.shape or x.shape[1]!=len(self._corr) or not np.isfinite(x).all(): raise ValueError('Invalid input')
  out=x.copy(); latent=np.column_stack([self._to_latent(x[:,j],j) for j in range(x.shape[1])]); znew=np.zeros_like(x)
  for i in range(len(x)):
   missing=np.flatnonzero(mask[i]); observed=np.flatnonzero(~mask[i])
   if not len(missing): continue
   if not len(observed): mean=np.zeros(len(missing)); cov=self._corr[np.ix_(missing,missing)]
   else:
    oo=self._corr[np.ix_(observed,observed)]; mo=self._corr[np.ix_(missing,observed)]; om=self._corr[np.ix_(observed,missing)]; mm=self._corr[np.ix_(missing,missing)]
    mean=mo@np.linalg.solve(oo+self.jitter*np.eye(len(observed)),latent[i,observed]); cov=mm-mo@np.linalg.solve(oo+self.jitter*np.eye(len(observed)),om)
   cov=(cov+cov.T)/2; cov+=self.jitter*np.eye(len(missing))
   try: chol=np.linalg.cholesky(cov)
   except np.linalg.LinAlgError: chol=np.linalg.cholesky(cov+max(self.jitter,1e-8)*np.eye(len(missing)))
   znew[i,missing]=mean+chol@rng.standard_normal(len(missing))
  for j in range(x.shape[1]):
   selected=mask[:,j]
   if selected.any(): out[selected,j]=self._from_latent(znew[selected,j],j)
  return out.astype(np.float32)
