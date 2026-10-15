import numpy as np,torch
from class_conditioned import AuthorModel,fast_contrastive,sample_class_views,ClassConditionedClassifier
torch.set_num_threads(1); torch.manual_seed(19)
m=AuthorModel(5,256,2); a=torch.randn(8,256,dtype=torch.float64,requires_grad=True); b=torch.randn(8,256,dtype=torch.float64,requires_grad=True)
old=m.contrastive_loss(a,b); go=torch.autograd.grad(old,(a,b)); new=fast_contrastive(a,b); gn=torch.autograd.grad(new,(a,b))
torch.testing.assert_close(old,new,rtol=1e-10,atol=1e-10)
for u,v in zip(go,gn): torch.testing.assert_close(u,v,rtol=1e-9,atol=1e-10)
x=np.arange(400).reshape(80,5).astype('float32'); pseudo=np.repeat([0,1],40); idx=np.arange(80); mask=np.random.default_rng(1).random(x.shape)<.4
out=sample_class_views(x,pseudo,idx,mask,np.random.default_rng(2)); np.testing.assert_array_equal(out[~mask],x[~mask])
for i,j in zip(*np.where(mask)): assert out[i,j] in x[pseudo==pseudo[i],j]
y=np.full(80,-1); known=np.zeros(80,dtype=bool); known[[0,1,40,41]]=True; y[known]=pseudo[known]
fit=ClassConditionedClassifier(3,epochs=10,head_epochs=2,width=256).fit(x/400,y,known); np.testing.assert_array_equal(fit.final_pseudo[known],y[known]); assert np.isfinite(fit.predict_proba(x/400)).all()
print('PASS: original loss/gradients, same-class donors, unchanged unmasked cells, unknown-label exclusion, known-label preservation, end-to-end smoke')
