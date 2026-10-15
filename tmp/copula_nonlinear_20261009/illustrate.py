import sys,json,os,importlib.util
os.environ["MPLCONFIGDIR"]="/private/tmp/copula-nonlinear-mpl-20261009"
from pathlib import Path
import numpy as np
from scipy.stats import norm
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path('/Users/kouta/Github/data augumation/Data-Augumation')
sys.path.insert(0,str(ROOT/'research-bench/src'))
spec=importlib.util.spec_from_file_location("copula_illustration_corruption",ROOT/"research-bench/src/tabular_research/corruption.py")
module=importlib.util.module_from_spec(spec);sys.modules[spec.name]=module;spec.loader.exec_module(module)
GaussianCopulaCorruptor=module.GaussianCopulaCorruptor;ColumnShuffleCorruptor=module.ColumnShuffleCorruptor
rng=np.random.default_rng(20261009); n=2000
z1=rng.normal(size=n);z2=.9*z1+np.sqrt(1-.9**2)*rng.normal(size=n)
mono=np.column_stack([10*norm.cdf(z1),(10*norm.cdf(z2))**2]).astype(np.float32)
x=rng.uniform(-1,1,n); u_shape=np.column_stack([x,x*x]).astype(np.float32)
fig,ax=plt.subplots(2,3,figsize=(12.8,7.4),layout='constrained')
report={}
for row,(name,data) in enumerate([('Monotone nonlinear',mono),('U-shaped',u_shape)]):
 m=np.zeros_like(data,dtype=bool);m[:,1]=True
 model=GaussianCopulaCorruptor().fit(data)
 generated=model(data,m,np.random.default_rng(314159))
 shuffle=ColumnShuffleCorruptor()(data,m,np.random.default_rng(314159))
 for col,(title,points,color) in enumerate([('Original data',data,'#2B6777'),('Independent column shuffle',shuffle,'#C86B32'),('Gaussian copula replacement',generated,'#2E7D5B')]):
  a=ax[row,col]; a.scatter(points[:650,0],points[:650,1],s=8,alpha=.45,color=color,rasterized=True)
  a.set_title(title,fontsize=12,pad=11);a.set_xlabel('Observed feature X');a.set_ylabel('Replaced feature Y');a.grid(alpha=.15);a.spines[['top','right']].set_visible(False)
  if row==0:a.set_xlim(0,10);a.set_ylim(-2,102)
  else:
   t=np.linspace(-1,1,200);a.plot(t,t*t,c='#303030',lw=1.5,label='Y = X squared');a.set_xlim(-1.03,1.03);a.set_ylim(-.03,1.03)
 report[name]={'n':n,'estimated_regularized_latent_correlation':float(model._corr[0,1]),'observed_X_unchanged':bool(np.array_equal(data[:,0],generated[:,0]))}
 if row==1:report[name]['squared_curve_mse']={'shuffle':float(np.mean((shuffle[:,1]-data[:,0]**2)**2)),'gaussian':float(np.mean((generated[:,1]-data[:,0]**2)**2))}
fig.suptitle('Nonlinear dependence: what the current Gaussian copula can and cannot preserve',fontsize=15)
fig.savefig(ROOT/'output/figures/非線形依存_Gaussianコピュラの保持と限界.png',dpi=170)
fig.savefig(ROOT/'output/figures/非線形依存_Gaussianコピュラの保持と限界.pdf')
(ROOT/'tmp/copula_nonlinear_20261009/results.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
