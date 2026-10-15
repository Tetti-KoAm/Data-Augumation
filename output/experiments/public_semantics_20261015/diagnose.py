"""Post-hoc diagnosis of low-AUC VIME runs; no exclusion or retuning."""
import json
import numpy as np,pandas as pd,torch
from run import OUT,load,MinMaxScaler,VIMEClassifier,VIMEConfig,FastGaussianCopula,ColumnShuffleCorruptor,scores
m=pd.read_csv(OUT/'metrics.csv'); results=[]
for row in m[(m.auc<.55)&m.method.str.startswith('vime')].itertuples():
 df,y=load(row.dataset); x=df.to_numpy(); sp=np.load(OUT/f'split_{row.dataset}_{row.seed}_{row.n_labels}.npz'); tr=sp['train_source_indices']; li=sp['labeled_positions']; ui=sp['unlabeled_positions']; scaler=MinMaxScaler().fit(x[tr]); train=scaler.transform(x[tr]).astype('float32')
 if row.dataset=='occupancy':
  tests=[pd.read_csv(OUT/'data/357'/f).drop(columns='date') for f in ['datatest.txt','datatest2.txt']]; te=pd.concat(tests); xt=te[list(df.columns)].to_numpy()
 else: xt=x[sp['test_source_indices']]
 yt=te.Occupancy.to_numpy() if row.dataset=='occupancy' else y[sp['test_source_indices']]
 config=VIMEConfig(corruption_probability=.4,self_epochs=15,semi_iterations=300,batch_size=64,encoder_hidden_dim=32,encoder_depth=4,predictor_hidden_dim=32,validation_fraction=0,device='cpu',seed=row.seed)
 model=VIMEClassifier(config,FastGaussianCopula() if row.method=='vime_copula' else ColumnShuffleCorruptor()); model.fit(train[li],y[tr[li]],train[ui]); test=scaler.transform(xt).astype('float32'); prob=model.predict_proba(test)
 rerun_auc=scores(yt,prob)['auc']; assert abs(rerun_auc-row.auc)<1e-7
 with torch.no_grad(): z=model.pretext.encoder(torch.tensor(test)).numpy()
 d={'dataset':row.dataset,'seed':row.seed,'n_labels':row.n_labels,'method':row.method,'original_auc':row.auc,'rerun_auc':rerun_auc,'probability_std_mean':float(prob.std(axis=0).mean()),'encoder_std_mean':float(z.std(axis=0).mean()),'unique_probability_rows':len(np.unique(prob,axis=0))}
 results.append(d); print(d,flush=True)
(OUT/'low_auc_diagnosis.json').write_text(json.dumps(results,indent=2))
