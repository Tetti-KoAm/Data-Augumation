# スライドの編集元

build.mjs は44枚の参照レイアウト反映版の編集元です。実験CSVに由来する slide_data.json を読み、PowerPointとPNGを生成します。元PCへの絶対パスは相対パスへ変更しています。完成PPTXは「資料」で直接編集できます。

再生成にはCodexのpresentationsスキルと付属の @oai/artifact-tool ランタイムが必要です。通常のPython実験環境とは別です。依存ランタイムはこのフォルダに含めていません。移行先のCodexでスキルを確認し、PRESENTATIONS_SKILL_DIR、Nodeの実行パス、node_modulesの解決先を設定してください。公開npmから取得できると仮定してインストールしないでください。

- PRESENTATIONS_SKILL_DIR：移行先のpresentationsスキルのフォルダ。
- SLIDE_FONT_FAMILY：利用可能な日本語フォント。省略時Hiragino Sans（Mac）。Windowsではインストール済みの日本語フォントを確認して変更。
- 生成先：presentation_source/build_out/candidate.pptx と各slide-XX.png。
- 生成後はそのPCのpresentationsスキルの手順で検証し、資料フォルダに別名で保存。

レイアウト参照PDFに合わせる修正では、まずPDFを表示し、title/body/tableの座標・フォント・色と余白を確認してこのソースを更新してください。モデルの再学習は不要です。

finalize.mjsは検証・完成ファイル出力用。移行先スキルの実装説明に従い、RUNTIME_PYTHON、RUNTIME_NODE_MODULES、RUNTIME_BIN_DIRなどの実行環境も設定してください。Node本体やライブラリを手作業でコピーする必要はありません。

2026-10-24追記：６手法の文献対応と特徴量・列関係の説明を追加。主結果の再実験なし。参照文献は「文献一覧と実装の対応.md」、特徴量の補足は「特徴量と列関係の補足.md」。
