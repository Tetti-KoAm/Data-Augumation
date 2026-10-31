# 検証記録（2026-10-27）

既存 `six_methods_20261023/.venv`（Python 3.12、Torch 2.9.0）で確認。

- GAN以外の9条件：UCI 3データ×3割合×10 seed＝90ジョブを実行し、全完了。ADASYN生成失敗0件。`validation_non_gan/completion.json` と `audit.json` に保存。
- 全11条件：レーズン10%、seed 11/23、GAN 1 epochで2ジョブ実行し監査合格。`validation_all_methods` に保存。最終コードでも `/private/tmp/uci-adasyn-final-smoke` へ同条件を実行し監査合格。
- 監査項目：訓練とテストの非重複、元データとの配列一致、10/20/30%の正確な割合、割合間の訓練総数固定・共通テスト・クラス別部分集合の包含、生成行の有限値・件数、GAN epoch数、混同行列からのMacro-F1再計算。
- `test_summary.py`：標本SD（ddof=1）の数値確認、未完了seedの表示、全失敗手法の欠測値・完了判定を確認し合格。

**300 epochの全90ジョブによる本実験は完了**。全180回のGAN学習で損失ログ300行を確認。全342評価条件（base/repair込み）に10回ずつ、合計3420評価行。生成失敗0件。`results/audit.json` の90条件監査に合格。

短縮したGAN結果は本実験に混在させず、本実験は `results/` に保存。`comparison.md` が全手法の主比較。終了時にワーカー2件が待機し続けたため、全結果保存・監査後に当該ワーカーのみ停止して正常終了。保存済み結果の再監査も合格。

検証コマンド：

```bash
output/experiments/six_methods_20261023/.venv/bin/python -m unittest discover -s output/experiments/uci_adasyn_20261027 -p 'test_*.py'
output/experiments/six_methods_20261023/.venv/bin/python output/experiments/uci_adasyn_20261027/verify.py --out output/experiments/uci_adasyn_20261027/validation_non_gan
```
