"""Regression checks for sample SD and incomplete repeated experiments."""
import json
import tempfile
import unittest
from pathlib import Path
from summarize import summarize, METRICS

class SummaryTests(unittest.TestCase):
    def test_sample_sd_and_missing_seed(self):
        with tempfile.TemporaryDirectory() as directory:
            out=Path(directory)
            protocol=dict(datasets=['rice'],minority_fractions=[.1],seeds=[11,23,37],methods=['none','adasyn'])
            (out/'protocol.json').write_text(json.dumps(protocol))
            for seed,value in [(11,1.),(23,0.)]:
                work=out/f'rice_10_{seed}'; work.mkdir()
                counts=dict(tp=1,tn=1,fp=0,fn=0) if value else dict(tp=0,tn=0,fp=1,fn=1)
                rows=[dict(dataset='rice',minority_fraction=.1,classifier=c,method='none',variant='base',seed=seed,**counts,**{k:value for k in METRICS}) for c in ['logistic','hist_boost']]
                (work/'result.json').write_text(json.dumps(dict(metrics=rows,failures=[])))
            summary=summarize(out)
            row=summary.query('method=="none" and classifier=="logistic"').iloc[0]
            self.assertAlmostEqual(row.macro_f1_mean,.5)
            self.assertAlmostEqual(row.macro_f1_std,2**-.5)
            self.assertEqual(row.n_success,2)
            self.assertFalse(row.complete)
            self.assertTrue(summary.query('method=="adasyn"').macro_f1_mean.isna().all())
            self.assertFalse(json.loads((out/'completion.json').read_text())['complete'])

if __name__=='__main__': unittest.main()
