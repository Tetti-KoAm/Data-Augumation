"""Post hoc diagnosis of the pre-registered strong-mean seed37 failure.
Does not change the comparison or discard any runs.
"""
from pathlib import Path
import json,numpy as np,torch,random
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler,StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
p=Path(__file__).parent
ns={'__file__':str(p/'run_dependence_comparison.py')};exec(compile((p/'run_dependence_comparison.py').read_text().split('begin=time.time();runs=[]')[0],'definitions','exec'),ns)
seed=37;rho=.9;x,y=ns['make_data'](seed,rho,'mean')
tr,te=train_test_split(np.arange(len(y)),test_size=.2,stratify=y,random_state=seed)
il,iu=train_test_split(tr,train_size=.3,stratify=y[tr],random_state=seed+100003)
sc=MinMaxScaler().fit(x[tr]);xl=sc.transform(x[il]).astype('float32');xu=sc.transform(x[iu]).astype('float32');xt=sc.transform(x[te]).astype('float32')
out={}
for method,c in [('column_shuffle',None),('gaussian_copula',ns['GaussianCopulaCorruptor']())]:
 random.seed(seed);np.random.seed(seed);torch.manual_seed(seed)
 cfg=ns['VIMEConfig'](corruption_probability=.4,reconstruction_weight=2.,n_augmented_views=3,consistency_weight=1.,self_epochs=15,semi_iterations=300,batch_size=64,predictor_hidden_dim=32,encoder_hidden_dim=32,encoder_depth=4,encoder_dropout=0.,validation_fraction=0.,device='cpu',seed=seed)
 est=ns['VIMEClassifier'](config=cfg,corruptor=c).fit(xl,y[il],xu)
 probs=est.predict_proba(xt)[:,1]
 with torch.no_grad():
  zl=est.pretext.encoder(torch.from_numpy(xl)).numpy();zt=est.pretext.encoder(torch.from_numpy(xt)).numpy()
 diagnostic=make_pipeline(StandardScaler(),LogisticRegression(C=10,max_iter=1000)).fit(zl,y[il])
 out[method]={'vime_auc':float(roc_auc_score(y[te],probs)),'std_predicted_probability':float(probs.std()),'unique_predicted_probabilities':int(np.unique(probs).size),'mean_encoder_coordinate_std':float(zt.std(0).mean()),'logistic_on_frozen_encoder_auc':float(roc_auc_score(y[te],diagnostic.predict_proba(zt)[:,1])),'first_self_loss':est.history_['self_loss'][0],'last_self_loss':est.history_['self_loss'][-1],'first_train_loss':est.history_['train_loss'][0],'last_train_loss':est.history_['train_loss'][-1]}
 print(method,json.dumps(out[method]),flush=True)
(p/'seed37_diagnosis.json').write_text(json.dumps({'post_hoc':True,'case':'rho .9 mean task seed37, identical original settings, outcomes retained','diagnosis':'logistic on same frozen encoding uses another classifier; diagnostic not a fair corruption benchmark','results':out},indent=2))
