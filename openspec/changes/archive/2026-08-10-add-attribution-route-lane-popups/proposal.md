## Why

現状の地図サイトは、国土数値情報（国土交通省）を加工した路線・地点・都道府県境界の
データを表示しているが、データ出典（attribution）をどこにも表示していない。また
路線をクリックしても属性ポップアップが出ず、地点のポップアップも地点名・地点種別
のみで、その地点に接続する路線の車線数がわからない。データ利用規約に沿った出典
表示と、路線・地点それぞれの主要属性をポップアップで確認できるようにする。

## What Changes

- 路線用・地点用・都道府県境界用の各PMTilesソースに、国土数値情報の出典
  （データ出典元）を示すattributionを設定し、地図のAttributionControlに表示する。
- 地図上で路線をクリックすると、その路線の属性（路線名・路線種別・車線数）を表示
  するポップアップを表示する。路線種別区分コード（`N06_008`）は人が読める種別名
  （高速自動車国道／指定都市高速道路等）に変換して表示する。
- タイル生成パイプラインの前処理で、路線データの車線数（`N06_010`）を
  `lines.current.geojson` の属性として保持し、路線用PMTilesに含める。
- タイル生成パイプラインの前処理で、各接合部ポイント（IC・JCT等）の位置に空間的に
  接続する路線を判定し、それらの車線数を重複排除・昇順ソートしたリストとして
  `points.current.geojson` の属性（`lane_counts`）に付与する。1つのポイントに
  車線数の異なる複数路線が接続する場合（主にJCT）は、すべての値をリストとして
  保持する（ユーザー確認済み）。
- 地点クリック時のポップアップに、既存の地点名・地点種別に加えて、上記の接続路線
  車線数（複数ある場合はカンマ区切り等で列挙）を表示する。

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `highway-map-viewer`: ソースのattribution表示、路線クリック時のポップアップ表示、
  地点ポップアップへの接続路線車線数の追加を requirement として追加・変更する。
- `highway-tile-pipeline`: 路線属性への車線数追加、地点属性への接続路線車線数
  （`lane_counts`）の空間的な紐付け・付与を requirement として追加する。

## Impact

- `site/style/map-style.js`: 各vectorソースへの`attribution`設定を追加。
- `site/main.js`: `lines`レイヤーのクリックハンドラ追加（路線ポップアップ）、
  地点ポップアップの表示内容拡張（`lane_counts`）、路線種別区分のラベル変換表を追加。
- `pipeline/preprocess/filter_lines.py`: 出力属性に`lane_count`（`N06_010`）を追加。
- `pipeline/preprocess/filter_points.py`: 路線データ（`lines.current.geojson`相当の
  ジオメトリ・属性）を読み込み、地点ごとに空間的に接続する路線を判定して
  `lane_counts`属性を付与するロジックを追加（新規に空間結合処理が必要、Shapely等の
  依存追加を想定）。
- `pipeline/preprocess/verify_counts.py`: 新属性（`lane_count`・`lane_counts`）の
  存在・妥当性検証を追加。
- 既存PMTiles（`site/tiles/lines.pmtiles`・`points.pmtiles`）の再生成が必要
  （`pipeline/build.sh`の再実行）。
