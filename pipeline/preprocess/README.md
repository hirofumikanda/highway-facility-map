# 前処理スクリプト（未実装）

`geojson/N06-25_HighwaySection.geojson` / `geojson/N06-25_Joint.geojson` から
現況（供用期間終了年が`9999`）の地物のみを抽出し、タイル生成用のGeoJSONを
`../output/` に書き出すスクリプトをここに実装する。地点データには、接合部種別
（`N06_019`）に基づく重要度ティアとtippecanoe用`minzoom`プロパティも付与する。

- OpenSpec Change: `highway-facility-map`
- 対応するspec: `openspec/changes/highway-facility-map/specs/highway-tile-pipeline/spec.md`
- tasks.md タスク番号: 2.1, 2.2, 2.3, 2.4, 2.5（GitHub Issue #2）
