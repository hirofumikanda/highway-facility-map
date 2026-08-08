# 前処理スクリプト

`geojson/N06-25_HighwaySection.geojson` / `geojson/N06-25_Joint.geojson` から
現況（供用期間終了年が`9999`）の地物のみを抽出し、タイル生成用のGeoJSONを
`../output/` に書き出す。地点データには、接合部種別（`N06_019`）に基づく重要度
ティアとtippecanoe用`minzoom`プロパティも付与する。

## 実行方法

```
$ ./pipeline/preprocess/run.sh
```

`filter_lines.py` → `filter_points.py` → `verify_counts.py` の順に実行し、最後に
出力件数・内訳の検証結果を表示する。個々のスクリプトも単独で実行できる
（`python3 pipeline/preprocess/filter_lines.py` 等）。

## スクリプト

- `filter_lines.py` — 現況路線を抽出し、`route_name`（路線名）・
  `route_category`（路線種別区分）のみを保持した
  `../output/lines.current.geojson` を書き出す
- `filter_points.py` — 現況地点を抽出し、`point_name`（地点名）・
  `point_type`（接合部種別コード）を保持しつつ、種別ごとのtippecanoe
  `minzoom`（ジャンクション=8 / 一般IC=10 / スマートIC=12 / その他=14）を
  付与した `../output/points.current.geojson` を書き出す
- `verify_counts.py` — 上記2ファイルの件数・内訳・minzoom付与が期待通りで
  あることを検証する

## 出力

- `../output/lines.current.geojson` — 現況路線1,289件
- `../output/points.current.geojson` — 現況地点2,384件
  （ジャンクション245 / 一般IC1,942 / スマートIC164 / その他33）

出力ファイルは`.gitignore`（`*.geojson`）により Git 管理対象外。

- OpenSpec Change: `highway-facility-map`
- 対応するspec: `openspec/changes/highway-facility-map/specs/highway-tile-pipeline/spec.md`
- tasks.md タスク番号: 2.1, 2.2, 2.3, 2.4, 2.5（GitHub Issue #2）
