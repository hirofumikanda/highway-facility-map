# タイル生成スクリプト（未実装）

`../output/` の前処理済みGeoJSONから、tippecanoeでMVTを生成し、PMTiles形式に
変換して `../../site/tiles/` に配置するスクリプトをここに実装する。前処理から
配置までを1コマンドで実行できるビルドスクリプトも、このディレクトリにまとめる。

- OpenSpec Change: `highway-facility-map`
- 対応するspec: `openspec/changes/highway-facility-map/specs/highway-tile-pipeline/spec.md`
- tasks.md タスク番号: 3.1, 3.2, 3.3, 3.4, 3.5（GitHub Issue #3）
- 検証スクリプト（生成タイルのズーム範囲・重要度順収録・全収録の確認）:
  tasks.md タスク番号 4.1〜4.4（GitHub Issue #3）
