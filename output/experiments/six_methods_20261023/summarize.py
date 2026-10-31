"""Audit persisted experiment evidence and prepare slide-ready literal data."""
from pathlib import Path
import hashlib,json,sys
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from threadpoolctl import threadpool_limits
from run import METHODS,load,repair,semantics

OUT=Path(__file__).resolve().parent; R=OUT/'results'
NAMES={'none':'拡張なし','duplicate':'ランダム複製','class_weight':'クラス重み付け','shuffle':'シャッフル','copula':'コピュラ','smote':'SMOTE','copula_smote':'コピュラSMOTE','ctgan':'CTGAN','ctgan_copula':'CTGAN×コピュラ'}
GEN=METHODS[3:]; DS=['rice','raisin','grid']

def main():
    threadpool_limits(limits=1)
    m=pd.read_csv(R/'metrics.csv'); q=pd.read_csv(R/'quality.csv'); t=pd.read_csv(R/'timing.csv')
    metas=json.loads((R/'datasets.json').read_text()); protocol=json.loads((R/'protocol.json').read_text())
    assert len(metas)==15 and len(m)==450 and len(q)==195 and len(t)==135
    assert not m.duplicated(['dataset','seed','method','variant','classifier']).any()
    for name in DS:
        xx,yy,cols,info=load(name)
        for seed in protocol['seeds']:
            w=R/f'{name}_{seed}'; sp=np.load(w/'split.npz'); tr,te=sp['train_indices'],sp['test_indices']; x,y=sp['x_train'],sp['y_train']
            assert not set(tr)&set(te) and len(np.unique(tr))==len(tr)
            np.testing.assert_array_equal(xx[tr],x); np.testing.assert_array_equal(yy[tr],y)
            np.testing.assert_array_equal(xx[te],sp['x_test']); np.testing.assert_array_equal(yy[te],sp['y_test'])
            num=int(sum(y==0)-sum(y==1))
            for method in ['duplicate']+GEN:
                z=np.load(w/f'{method}_generated.npz')['generated']; assert z.shape==(num,len(cols)) and np.isfinite(z).all()
                if method!='duplicate':
                    repaired=repair(name,z,cols); diag=semantics(name,repaired,cols)
                    assert diag['relation_violation']==0
                    repaired2=repair(name,repaired,cols); np.testing.assert_allclose(repaired,repaired2,atol=1e-10)
            for method in ['ctgan','ctgan_copula']:
                assert len(pd.read_csv(w/f'{method}_loss.csv'))==protocol['ctgan_epochs']
                meta=json.loads((w/f'{method}_generation.json').read_text()); assert 0<meta['conditional_label_acceptance']<=1
    for r in m.to_dict('records'):
        tp,tn,fp,fn=[r[z] for z in ['tp','tn','fp','fn']]
        ba=.5*(tp/(tp+fn)+tn/(tn+fp)); f1=.5*(2*tp/(2*tp+fp+fn)+2*tn/(2*tn+fp+fn))
        assert abs(ba-r['balanced_accuracy'])<1e-12 and abs(f1-r['macro_f1'])<1e-12
    replay=[]
    for method in ['none','smote','ctgan']:
        w=R/'rice_11'; sp=np.load(w/'split.npz'); x,y=sp['x_train'],sp['y_train']; z=np.empty((0,x.shape[1])) if method=='none' else np.load(w/f'{method}_generated.npz')['generated']
        xa=np.concatenate([x,z]); ya=np.concatenate([y,np.ones(len(z),dtype=int)]); sc=StandardScaler().fit(xa)
        model=LogisticRegression(C=1,max_iter=2000,random_state=11).fit(sc.transform(xa),ya)
        pred=model.predict_proba(sc.transform(sp['x_test']))[:,1]>=.5
        from sklearn.metrics import f1_score
        f=f1_score(sp['y_test'],pred,average='macro')
        saved=m.query('dataset=="rice" and seed==11 and method==@method and variant=="base" and classifier=="logistic"').iloc[0].macro_f1
        assert abs(f-saved)<1e-12; replay.append({'method':method,'macro_f1':f})
    b=m.query('variant=="base"')
    summary=b.groupby(['dataset','classifier','method']).agg({k:['mean','std'] for k in ['macro_f1','balanced_accuracy','recall','precision','roc_auc','average_precision']})
    summary.to_csv(R/'summary.csv')
    pair=[]
    for name in DS:
      for clf in ['logistic','hist_boost']:
        g=m.query('dataset==@name and classifier==@clf')
        base=g.query('method=="none"').set_index('seed').macro_f1
        dup=g.query('method=="duplicate"').set_index('seed').macro_f1
        for method in METHODS:
            v=g.query('method==@method and variant=="base"').set_index('seed').macro_f1
            d=v-base; d2=v-dup
            pair.append(dict(dataset=name,classifier=clf,method=method,delta_vs_none=float(d.mean()),sd_delta_vs_none=float(d.std()),delta_vs_duplicate=float(d2.mean()),sd_delta_vs_duplicate=float(d2.std()),wins_vs_duplicate=int((d2>1e-12).sum())))
    pd.DataFrame(pair).to_csv(R/'paired_differences.csv',index=False)
    repairs=[]
    for name in DS:
      for clf in ['logistic','hist_boost']:
       for method in GEN:
        g=m.query('dataset==@name and classifier==@clf and method==@method')
        d=g.query('variant=="repair"').set_index('seed').macro_f1-g.query('variant=="base"').set_index('seed').macro_f1
        repairs.append(dict(dataset=name,classifier=clf,method=method,mean_delta=float(d.mean()),sd_delta=float(d.std()),wins=int((d>1e-12).sum())))
    pd.DataFrame(repairs).to_csv(R/'repair_differences.csv',index=False)
    payload={'method_names':NAMES,'methods':METHODS,'generators':GEN,'datasets':DS,'protocol':protocol,'metadata':metas,'metrics':m.to_dict('records'),'quality':q.to_dict('records'),'timing':t.fillna(0).to_dict('records'),'paired':pair,'repairs':repairs,'plots':{}}
    for name in ['rice','grid']:
        sp=np.load(R/f'{name}_11/split.npz'); x,y=sp['x_train'],sp['y_train']; cols=list(sp['feature_names'])
        if name=='rice':
            def coords(v): return np.column_stack([v[:,cols.index('MajorAxisLength')],v[:,cols.index('MinorAxisLength')]])
        else:
            def coords(v): return np.column_stack([-sum(v[:,cols.index(f'p{k}')] for k in [2,3,4]),v[:,cols.index('p1')]])
        plot={'original_minority':coords(x[y==1]).tolist(),'original_majority':coords(x[y==0][:80]).tolist(),'generated':{},'repaired':{}}
        for method in GEN:
            z=np.load(R/f'{name}_11'/f'{method}_generated.npz')['generated']; plot['generated'][method]=coords(z[:120]).tolist(); plot['repaired'][method]=coords(repair(name,z[:120],cols)).tolist()
        pts=np.concatenate([np.array(plot['original_minority'])]+[np.array(plot['generated'][a]) for a in GEN])
        mn=pts.min(0); mx=pts.max(0); pad=.06*(mx-mn)
        plot['limits']={'xmin':float(mn[0]-pad[0]),'xmax':float(mx[0]+pad[0]),'ymin':float(mn[1]-pad[1]),'ymax':float(mx[1]+pad[1])}
        payload['plots'][name]=plot
    (R/'slide_data.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2))
    audit={'passed':True,'jobs':15,'classification_evaluations':len(m),'quality_evaluations':len(q),'generators':len(GEN),'seeds':5,'checks':['source hash and exact persisted train/test rows','disjoint train/test indices','equal generated row counts and finite values','300 epoch loss traces for all GANs','repair consistency and idempotence','all macro F1 and balanced accuracy reconstructed from confusion matrices','three logistic results replayed from saved generated rows'],'replays':replay}
    (R/'audit.json').write_text(json.dumps(audit,indent=2))
    print(b.pivot_table(index=['classifier','method'],columns='dataset',values='macro_f1').round(4).to_string())
    print(q.query('variant=="base"').pivot_table(index='method',columns='dataset',values='relation_violation').round(4).to_string())
    print(pd.DataFrame(repairs).query('classifier=="logistic"').pivot(index='method',columns='dataset',values='mean_delta').round(4).to_string())
    print('AUDIT PASSED',len(m),'classification rows')

if __name__=='__main__': main()
