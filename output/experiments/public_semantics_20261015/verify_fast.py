import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[3]/'research-bench/src'))
import numpy as np
from tabular_research.corruption import GaussianCopulaCorruptor
from fast_copula import FastGaussianCopula
rng=np.random.default_rng(42); x=rng.random((100,16)).astype('float32'); mask=rng.random(x.shape)<.4; mask[0]=True; mask[1]=False
original=GaussianCopulaCorruptor().fit(x); fast=FastGaussianCopula().fit(x)
a=original(x,mask,np.random.default_rng(29)); b=fast(x,mask,np.random.default_rng(29))
np.testing.assert_array_equal(a,b); np.testing.assert_array_equal(b[~mask],x[~mask]); print('PASS: output bitwise identical on 100x16, including fully masked/unmasked rows')
