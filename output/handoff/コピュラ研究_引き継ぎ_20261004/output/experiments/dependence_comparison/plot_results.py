from pathlib import Path
import json,csv
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).parent
ns={'__file__':str(ROOT/'run_dependence_comparison.py')}
exec(compile((ROOT/'run_dependence_comparison.py').read_text().split('begin=time.time();runs=[]')[0],'definitions','exec'),ns)
plt.rcParams.update({'font.size':11,'axes.spines.top':False,'axes.spines.right':False})
fig,axes=plt.subplots(1,3,figsize=(12,3.6),layout='constrained')
for ax,rho in zip(axes,[0,.5,.9]):
 x,y=ns['make_data'](11,rho,'mean');im=ax.imshow(np.corrcoef(x.T),vmin=-1,vmax=1,cmap='RdBu_r');ax.set_title(f'Target pairwise correlation = {rho}');ax.set_xlabel('Feature');ax.set_ylabel('Feature')
fig.colorbar(im,ax=axes,label='Pearson correlation',shrink=.85)
fig.savefig(ROOT/'controlled_dependence.png',dpi=180);fig.savefig(ROOT/'controlled_dependence.pdf');plt.close(fig)
if not (ROOT/'results.json').exists():raise SystemExit()
r=json.loads((ROOT/'results.json').read_text());s=r['summary']
labels={'independent_mean':'Independent / mean','moderate_mean':'Moderate / mean','strong_mean':'Strong / mean','strong_contrast':'Strong / contrast'}
names=list(s);pos=np.arange(len(names));colors=['#2b6777','#2e7d5b']
fig,axes=plt.subplots(1,3,figsize=(16,4.5),layout='constrained')
for mi,method in enumerate(['column_shuffle','gaussian_copula']):
 auc=[s[n][method]['auc']['mean'] for n in names];sd=[s[n][method]['auc']['std'] or 0 for n in names]
 axes[0].errorbar(pos+(mi-.5)*.1,auc,yerr=sd,fmt='o',label=method.replace('_',' '),color=colors[mi],capsize=4)
 for ni,name in enumerate(names):
  vals=s[name][method]['auc']['values'];axes[0].scatter(ni+(mi-.5)*.1+np.linspace(-.025,.025,len(vals)),vals,s=13,alpha=.5,color=colors[mi])
 axes[1].plot(pos,[s[n]['quality_mean'][method]['mean_abs_pearson'] for n in names],'o-',label=method.replace('_',' '),color=colors[mi])
 axes[2].plot(pos,[s[n]['quality_mean'][method]['oracle_boundary_flip_rate'] for n in names],'o-',label=method.replace('_',' '),color=colors[mi])
axes[1].plot(pos,[s[n]['quality_mean']['original']['mean_abs_pearson'] for n in names],'k--',label='Original')
axes[0].set(title='VIME test ROC-AUC (mean +/- SD)',ylabel='ROC-AUC',ylim=(0,1.12));axes[0].axhline(.5,color='gray',ls=':',lw=1)
axes[1].set(title='Dependence after corruption',ylabel='Mean absolute pairwise correlation',ylim=(0,1.02))
axes[2].set(title='Clean label-boundary changes',ylabel='Fraction of rows crossing the boundary',ylim=(0,.55))
for ax in axes:ax.set_xticks(pos,[labels[n] for n in names],rotation=25,ha='right');ax.grid(alpha=.2);ax.legend(fontsize=9)
fig.savefig(ROOT/'comparison_results.png',dpi=180);fig.savefig(ROOT/'comparison_results.pdf');plt.close(fig)
with (ROOT/'per_seed_metrics.csv').open('w') as f:
 fields=['dataset','rho','task','seed','method','auc','accuracy','balanced_accuracy','macro_f1'];w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
 for run in r['runs']:
  for method,metrics in run['metrics'].items():w.writerow({**{k:run[k] for k in ['dataset','rho','task','seed']},'method':method,**metrics})
print('Plots and CSV saved.')
