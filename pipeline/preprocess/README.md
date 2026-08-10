# 前処理スクリプト

`geojson/N06-25_HighwaySection.geojson` / `geojson/N06-25_Joint.geojson` から
現況（供用期間終了年が`9999`）の地物のみを抽出し、タイル生成用のGeoJSONを
`../output/` に書き出す。地点データには、接合部種別（`N06_019`）に基づく重要度
ティアとtippecanoe用`minzoom`プロパティも付与する。また、地点座標とライン地物の
頂点一致判定により、各地点に空間的に接続する路線の車線数（`lane_counts`）を
付与する。路線データには、`route_common_names.py`の静的対応表を参照して、法定
路線名が単一の通称名に一意対応する路線にのみ通称名・路線番号（`common_name`・
`route_number`）を付与する。

## 依存関係

- Python 3
- [Shapely](https://shapely.readthedocs.io/) — `filter_points.py`が地点と路線の
  空間的な接続判定（頂点一致判定）に使用する。`pip install shapely`（Debian/Ubuntu
  では`apt install python3-shapely`でも可）でインストールする。

## 実行方法

```
$ ./pipeline/preprocess/run.sh
```

`filter_lines.py` → `filter_points.py` → `verify_counts.py` の順に実行し、最後に
出力件数・内訳の検証結果を表示する。個々のスクリプトも単独で実行できる
（`python3 pipeline/preprocess/filter_lines.py` 等）。

## スクリプト

- `route_common_names.py` — Wikipedia「高速自動車国道」ページの一覧表を出典に、
  法定路線名が単一の通称名・路線番号の組に一意対応する路線のみを収録した静的
  対応表（`ROUTE_COMMON_NAMES`辞書）
- `filter_lines.py` — 現況路線を抽出し、`route_name`（路線名）・
  `route_category`（路線種別区分）・`lane_count`（車線数、`N06_010`を整数として
  保持）を保持した `../output/lines.current.geojson` を書き出す。`route_name`が
  `ROUTE_COMMON_NAMES`にヒットする地物には、`common_name`（通称名）・
  `route_number`（路線番号、例：E1）も付与する（ヒットしない場合は両属性を
  付与しない）
- `filter_points.py` — 現況地点を抽出し、`point_name`（地点名）・
  `point_type`（接合部種別コード）・`lane_counts`（地点座標とライン地物の頂点
  一致判定により空間的に接続すると判定した路線の`lane_count`を重複排除・昇順
  ソートした配列）を保持しつつ、種別ごとのtippecanoe`minzoom`（ジャンクション=8
  / 一般IC=10 / スマートIC=12 / その他=14）を付与した
  `../output/points.current.geojson` を書き出す
- `verify_counts.py` — 上記2ファイルの件数・内訳・minzoom付与・`lane_count`/
  `lane_counts`属性の付与が期待通りであることを検証し、`lane_counts`が空になる
  地点数、および`common_name`/`route_number`が付与された路線地物数を報告する

## 出力

- `../output/lines.current.geojson` — 現況路線1,289件
- `../output/points.current.geojson` — 現況地点2,384件
  （ジャンクション245 / 一般IC1,942 / スマートIC164 / その他33）

出力ファイルは`.gitignore`（`*.geojson`）により Git 管理対象外。

- OpenSpec Change: `highway-facility-map`
- 対応するspec: `openspec/changes/highway-facility-map/specs/highway-tile-pipeline/spec.md`
- tasks.md タスク番号: 2.1, 2.2, 2.3, 2.4, 2.5（GitHub Issue #2）
