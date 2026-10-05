from pathlib import Path
import importlib.util,json,numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.metrics import roc_auc_score
# Import definitions without executing the main benchmark.
p=Path(__file__).parent
code=(p/'run_dependence_comparison.py').read_text().split('begin=time.time();runs=[]')[0]
ns={'__file__':str(p/'run_dependence_comparison.py')};exec(compile(code,'definitions','exec'),ns)
rows=[]
for name,rho,task in ns['CONFIGS']:
 for seed in ns['SEEDS']:
  x,y=ns['make_data'](seed,rho,task)
  tr,te=train_test_split(np.arange(len(y)),test_size=.2,stratify=y,random_state=seed)
  il,iu=train_test_split(tr,train_size=.3,stratify=y[tr],random_state=seed+100003)
  est=make_pipeline(StandardScaler(),LogisticRegression(C=10,max_iter=1000)).fit(x[il],y[il])
  prob=est.predict_proba(x[te])[:,1]
  rows.append({'dataset':name,'seed':seed,'logistic_auc':float(roc_auc_score(y[te],prob)),'clean_score_auc':float(roc_auc_score(y[te],ns['true_score'](x[te],rho,task)))})
summary={name:{k:{'mean':float(np.mean([r[k] for r in rows if r['dataset']==name])),'std':float(np.std([r[k] for r in rows if r['dataset']==name],ddof=1))} for k in ['logistic_auc','clean_score_auc']} for name,_,_ in ns['CONFIGS']}
(p/'baseline.json').write_text(json.dumps({'purpose':'diagnostic supervised linear baseline; different model/objective, not a corruption comparison','config':'StandardScaler fit on 240 labeled rows; LogisticRegression C=10 max_iter=1000, fixed before checking','runs':rows,'summary':summary},indent=2))
print(json.dumps(summary,indent=2))
