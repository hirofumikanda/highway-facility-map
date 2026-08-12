# 前処理スクリプト

`geojson/N06-25_HighwaySection.geojson` / `geojson/N06-25_Joint.geojson` から
現況（供用期間終了年が`9999`）の地物のみを抽出し、タイル生成用のGeoJSONを
`../output/` に書き出す。地点データには、接合部種別（`N06_019`）に基づく重要度
ティアとtippecanoe用`minzoom`プロパティも付与する。また、地点座標とライン地物の
頂点一致判定により、各地点に空間的に接続する路線の車線数（`lane_counts`）を
付与する。路線データには、通称名（`common_name`）・路線番号（`route_number`）を
それぞれ独立した静的対応表から付与する。`common_name`は`route_common_names.py`
（Wikipedia出典）を参照し、法定路線名が単一の通称名に一意対応する路線にのみ
付与する。`route_number`は`route_numbers.py`（国土交通省ナンバリング一覧・
指定都市高速道路は法定路線名からの抽出が出典）を参照し、路線種別区分が`1`〜`5`
かつ対応表にヒットする路線に、`common_name`の有無にかかわらず付与する。

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

- `spatial_match.py` — 地点・路線間の座標一致判定（距離閾値
  `CONNECTION_DISTANCE_THRESHOLD_DEGREES`とShapelyによる距離判定）を行う
  共通ロジック。`filter_points.py`（地点→接続路線の車線数の解決）から利用する
- `route_common_names.py` — Wikipedia「高速自動車国道」ページの一覧表を出典に、
  法定路線名が単一の通称名に一意対応する路線のみを収録した静的対応表
  （`ROUTE_COMMON_NAMES`辞書、`common_name`の解決にのみ用いる）
- `route_numbers.py` — 路線種別区分が`1`〜`4`の路線は国土交通省「高速道路
  ナンバリング一覧」、`5`（指定都市高速道路）の路線は法定路線名に埋め込まれた
  「N号」表記の抽出を出典とする静的対応表（`ROUTE_NUMBERS`辞書、`route_number`
  の解決にのみ用いる）
- `filter_lines.py` — 現況路線を抽出し、`route_name`（路線名）・
  `route_category`（路線種別区分）・`lane_count`（車線数、`N06_010`を整数として
  保持）を保持した `../output/lines.current.geojson` を書き出す。`route_name`が
  `ROUTE_COMMON_NAMES`にヒットする地物には`common_name`（通称名）を付与する。
  `route_category`が`1`〜`5`かつ`route_name`が`ROUTE_NUMBERS`にヒットする地物
  には、`common_name`の有無にかかわらず`route_number`（路線番号、例：E1・3）を
  付与する（いずれもヒットしない場合は各属性を付与しない）
- `filter_points.py` — 現況地点を抽出し、`point_name`（地点名）・
  `point_type`（接合部種別コード）・`lane_counts`（地点座標とライン地物の
  `spatial_match.py`による座標一致判定で空間的に接続すると判定した路線の
  `lane_count`を昇順ソートした配列。重複は排除せず、接続する路線の数だけ値を
  保持する。例えば車線数4の路線が2本接続するJCTでは`[4, 4]`になる）を保持
  しつつ、種別ごとの
  tippecanoe`minzoom`（ジャンクション=8 / 一般IC=10 / スマートIC=12 /
  その他=14）を付与した `../output/points.current.geojson` を書き出す
- `verify_counts.py` — 上記2ファイルの件数・内訳・minzoom付与・`lane_count`/
  `lane_counts`属性の付与が期待通りであることを検証し、`lane_counts`が空になる
  地点数、`ROUTE_NUMBERS`対応表のエントリ数、および`common_name`/
  `route_number`がそれぞれ付与された路線地物数を報告する

## 出力

- `../output/lines.current.geojson` — 現況路線1,289件
- `../output/points.current.geojson` — 現況地点2,384件
  （ジャンクション245 / 一般IC1,942 / スマートIC164 / その他33）

出力ファイルは`.gitignore`（`*.geojson`）により Git 管理対象外。

- OpenSpec Change: `highway-facility-map`, `add-mlit-route-numbering`, `add-joint-based-route-matching`
- 対応するspec: `openspec/changes/highway-facility-map/specs/highway-tile-pipeline/spec.md`
- tasks.md タスク番号: 2.1, 2.2, 2.3, 2.4, 2.5（GitHub Issue #2） / 2.1, 2.2（GitHub Issue #59） / 1.1, 1.2（GitHub Issue #91）
