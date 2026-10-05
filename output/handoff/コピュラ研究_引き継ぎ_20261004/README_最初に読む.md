# 別のPCで研究を続けるための手順

## まず行うこと

1. ZIPを展開する。展開後の「コピュラ研究_引き継ぎ_20261004」フォルダ全体を保存する。
2. そのPCのCodexで、このフォルダをプロジェクトとして開く。
3. 下の文章を、新しいチャットの最初のメッセージに貼る。

```text
このフォルダの「研究引き継ぎ.md」を読み、研究の目的、私が理解できていること、スライドの制約、実装と実験結果、未解決の課題を引き継いでください。
次に「output/presentations/流れ改善版_発表ガイド.md」と「output/experiments/dependence_comparison/実験レポート.md」を読み、現在の状態を短く確認してください。
最初の4枚のスライドは変更しないでください。本編は20枚程度、補足は必要なだけという構成を維持してください。
実験の追加実行や資料の変更は、これから私が依頼する内容に沿って進めてください。
ファイルの場所は以前のPCの /Users/kouta/... ではなく、今開いているプロジェクトフォルダを基準に探してください。
```

会話の引き継ぎと、ファイルの受け渡しをこのフォルダにまとめた。Python環境を作らなくても、PowerPointと実験レポート・図は開ける。

## 入っているもの

- `研究引き継ぎ.md`：研究の目的、説明で大事にした流れ、実装、最新結果、次の課題。
- `output/presentations/`：本編20枚＋補足29枚の最新版と発表ガイド。
- `参考資料/`：最初の4枚を保持するための元のPowerPoint。
- `output/presentations/比較実験/`：Breast Cancer・Wineの比較、2変量の動作確認。
- `output/experiments/dependence_comparison/`：相関を制御した追加実験、結果、図、レポート、診断コード。
- `research-bench/src/`：VIME再実装と列置換・Gaussian copulaの実装。
- `research-bench/upstream/`：先行研究の参照コード。Git管理情報は除外し、元リビジョンの記録はUPSTREAM_VERSIONS.mdに保持。
- `ファイル一覧とSHA256.json`：受け渡したファイルの一覧とチェックサム。

追加の強相関実験は、PowerPointへまだ反映していない。最新の研究結果は「研究引き継ぎ.md」と追加実験レポートを優先する。

## 実験を再実行する場合

Python 3.12を用意し、展開したフォルダをターミナルの作業フォルダにする。仮想環境そのものはOS・PCに依存するため同梱していない。

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python output/presentations/比較実験/run_experiment.py
python output/experiments/dependence_comparison/run_dependence_comparison.py
python output/experiments/dependence_comparison/check_baseline.py
python output/experiments/dependence_comparison/diagnose_seed37.py
python output/experiments/dependence_comparison/plot_results.py
python output/experiments/dependence_comparison/write_report.py
```

Windows PowerShell:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe output/presentations/比較実験/run_experiment.py
.\.venv\Scripts\python.exe output/experiments/dependence_comparison/run_dependence_comparison.py
.\.venv\Scripts\python.exe output/experiments/dependence_comparison/check_baseline.py
.\.venv\Scripts\python.exe output/experiments/dependence_comparison/diagnose_seed37.py
.\.venv\Scripts\python.exe output/experiments/dependence_comparison/plot_results.py
.\.venv\Scripts\python.exe output/experiments/dependence_comparison/write_report.py
```

保存済みの結果を残すには、再実行用にフォルダのコピーを作ってから実行する。スクリプトは同じフォルダの結果ファイルを更新する。主実験は元のMacで既存データ比較が約8分半、追加実験が約10分だった。別のPCでの実行時間や数値の完全一致は保証しない。

固定バージョンがそのPCへインストールできない場合は、`requirements-compatible.txt`で互換範囲の環境を作り、実際のバージョンを記録する。この場合、元の実験環境と同一ではない。追加実験フォルダには元の環境の全pip freezeも保存してある。

上の手順は今回使った2手法の再実行用。`research-bench/scripts/quick_compare.py`の3手法比較や上流の原実装には、別途research-benchの依存関係が必要になる。
