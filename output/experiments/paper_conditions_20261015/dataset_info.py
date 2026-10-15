import json
import numpy as np,pandas as pd
from run import prepare,NAMES,SEEDS,P
out={}
for name in NAMES:
 infos=[]
 for seed in SEEDS:
  x,xt,labels,known,y,cols,meta,split=prepare(name,seed); corr=np.corrcoef(x,rowvar=False); values=corr[np.triu_indices(len(cols),1)]
  pairs=sorted([(cols[i],cols[j],float(corr[i,j])) for i in range(len(cols)) for j in range(i)],key=lambda z:abs(z[2])); infos.append({'seed':seed,'mean_abs_pearson':float(np.mean(np.abs(values))),'low_correlation_fraction':float(np.mean(np.abs(values)<.1)),'lowest_pairs':pairs[:5]})
 out[name]={'features':cols,'per_seed_correlation':infos,**meta}
(P/'dataset_info.json').write_text(json.dumps(out,indent=2)); print('Training-only correlation summaries saved')
