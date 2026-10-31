"""Post-hoc diagnostics of saved generated rows; no new training or synthesis."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
E=Path(__file__).resolve().parent;R=E/'results'
def main():
 out={'condition':{'minority_fraction':.1,'seed':11,'method':'shuffle','variant':'base'},'selection':'largest Area-ConvexArea or largest absolute power residual; extreme illustration, not representative frequency','examples':{}}
 for d in ['rice','raisin','grid']:
  w=R/f'{d}_10_11';sp=np.load(w/'split.npz');cols=list(sp['feature_names']);g=np.load(w/'shuffle_generated.npz')['generated'];df=pd.DataFrame(g,columns=cols)
  if d!='grid':
   residual=df.Area-df.ConvexArea;i=int(np.argmax(residual));assert residual.iloc[i]>1
   out['examples'][d]={'zero_based_generated_row':i,'Area':float(df.iloc[i].Area),'ConvexArea':float(df.iloc[i].ConvexArea),'excess':float(residual.iloc[i]),'required_relation':'Area <= ConvexArea'}
  else:
   residual=df.p1+df.p2+df.p3+df.p4;i=int(np.argmax(abs(residual)))
   out['examples'][d]={'zero_based_generated_row':i,**{p:float(df.iloc[i][p]) for p in ['p1','p2','p3','p4']},'required_p1':float(-df.iloc[i][['p2','p3','p4']].sum()),'signed_power_residual':float(residual.iloc[i]),'required_relation':'p1+p2+p3+p4=0'}
 q=pd.read_csv(R/'quality.csv');q=q.query('method=="shuffle" and variant=="base" and minority_fraction==0.1')
 out['relation_violation_mean_over_5_seeds']=q.groupby('dataset').relation_violation.mean().to_dict()
 (R/'feature_examples.json').write_text(json.dumps(out,ensure_ascii=False,indent=2));print(json.dumps(out,ensure_ascii=False,indent=2))
if __name__=='__main__':main()
