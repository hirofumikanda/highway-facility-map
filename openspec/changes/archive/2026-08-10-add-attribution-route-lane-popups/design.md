## Context

`geojson/N06-25_HighwaySection.geojson` の属性のうち、`N06_010`が車線数
（上下線の合計、整数値。実データでの分布は2車線737件・4車線664件・6車線86件が
大半で、奇数値は分岐部等のごく少数）である（国土数値情報 製品仕様書 N06 に基づく。
既存コードが参照する`N06_009`は供用状況区分であり車線数ではない）。

現行の前処理（`pipeline/preprocess/filter_lines.py`）は`route_name`
（`N06_007`）・`route_category`（`N06_008`）のみを残し、`filter_points.py`は
`point_name`（`N06_018`）・`point_type`（`N06_019`）のみを残す。両者の間に
空間的な関連付け処理は存在しない。地点データ（`N06-25_Joint.geojson`）の
接合部ポイントは、対応する路線ラインのジオメトリ上の頂点として記録されている
（国土数値情報の同一整備事業に由来するデータのため、座標は一致する）。

サイト側（`site/main.js`・`site/style/map-style.js`）は、地点クリック時の
ポップアップのみを実装済みで、路線クリックのハンドラは存在せず、地図ソースにも
attributionは設定されていない。

## Goals / Non-Goals

**Goals:**
- 路線・地点・都道府県境界の3ソースにデータ出典を表示する。
- 路線クリックで路線名・路線種別（人が読める名称）・車線数をポップアップ表示する。
- 地点に接続する路線の車線数（複数路線が異なる車線数を持つ場合は全て）を
  地点属性として保持し、地点ポップアップに表示する。

**Non-Goals:**
- 出典表示のスタイル・レイアウトのカスタマイズ（MapLibre標準の
  AttributionControl表示に委ねる）。
- 路線・地点以外の新規属性（管理者・供用年等）のポップアップ表示。
- 车線数以外の属性を用いた地点⇔路線の関連付け（例: 道路管理者の突合）。

## Decisions

### 決定1: attributionはスタイルJSONの各vectorソースに設定する
MapLibreはスタイルJSONの各ソースの`attribution`プロパティを収集し、デフォルトの
AttributionControlに連結表示する。サイトは`Map`生成時に`attributionControl`を
無効化していないため、既定のAttributionControlが有効。ソースごとに文言を設定する
だけで表示され、`main.js`側の変更は不要。

- `lines`・`points`ソース: `出典：国土数値情報（高速道路時系列データ）(国土交通省)`
- `prefectures`ソース: `出典：国土数値情報（行政区域データ）(国土交通省)`

（ユーザー確認済み：国土数値情報の標準的な出典表記でよい）

### 決定2: 路線ポップアップは地点ポップアップと同じ`click`ハンドラパターンで実装
`map-style.js`の`lines-fill`レイヤー（塗り部分、判定領域として最も広い）に対して
`map.on("click", "lines-fill", ...)`を追加する。`lines-casing`には登録しない
（同一地物で二重発火するため）。地点用ハンドラと同様、DOM要素を組み立てて
`Popup#setDOMContent`に渡す（innerHTML直書きはしない）。

路線種別区分（`route_category`）は、既存の`design.md`（archive済み
`2026-08-09-highway-facility-map`）で確定済みのコード表を人が読める名称に変換する
マップとして`main.js`に追加する:
`1:高速自動車国道 / 2:高速自動車国道に並行する自専道 / 3:一般国道の自専道 /
4:本州四国連絡高速道路 / 5:指定都市高速道路 / 6:その他`

### 決定3: 車線数は路線側で`N06_010`をそのまま`lane_count`として保持
`filter_lines.py`の出力属性に`lane_count`（整数）を追加する。地点側で使う
（決定4）ため、`lines.current.geojson`は地点前処理からも参照される。

### 決定4: 地点⇔路線の車線数の紐付けは、ポイント座標とライン頂点の一致判定で行う
`filter_points.py`が`lines.current.geojson`（`filter_lines.py`の出力）を読み込み、
Shapely（新規依存追加）でライン地物ごとにジオメトリを構築、各地点座標について
「ラインとの距離が閾値（1e-6度、約0.1m相当）以下」であるライン地物を接続路線と
判定する。国土数値情報の同一整備由来データで座標が実質一致するため、頂点一致判定
で十分と考える（設計上の前提。ビルド後の`verify_counts.py`検証で0件マッチの
地点が出ないか確認する）。

判定で得られた接続路線群の`lane_count`を集合として重複排除し、昇順ソートした
リストを地点属性`lane_counts`（配列）として付与する。マッチする路線が1件もない
地点（データ不整合等）が発生した場合は空リスト`[]`とし、`verify_counts.py`で
件数を報告する（無視できない件数であればビルドを止めずに警告のみ）。

代替案として検討したが不採用:
- **バッファによる近傍判定（数十m〜）**: 密集地帯で誤って隣接路線を拾う
  リスクがあり、頂点一致より不正確。
- **属性突合（道路管理者コード等）**: 地点データに路線を一意に特定できる
  外部キー属性がなく、突合キーとして使えない。

### 決定5: `lane_counts`のポップアップ表示形式
地点ポップアップに「車線数: 2, 4」のようにカンマ区切りで表示する（`lane_counts`
が空の場合は当該行を表示しない）。

### 決定6: MVT内での`lane_counts`のエンコーディング
MVT（Mapbox Vector Tile）仕様は配列型のfeature属性をサポートしないため、
tippecanoeは`lane_counts`配列をJSON文字列（例: `"[2, 4]"`、空配列は`"[]"`）
としてタイルにエンコードする（`lane_count`は整数値なのでそのまま数値として
保持される）。`site/main.js`側で地点クリック時に`JSON.parse(feature.properties
.lane_counts)`でパースしてから表示に使う必要がある（タスク6.1で対応）。

## Risks / Trade-offs

- [Risk] 頂点一致判定の閾値が実データの座標誤差と合わず、一部地点で接続路線が
  0件または想定外の複数件になる可能性 → `verify_counts.py`に`lane_counts`が
  空の地点数を出力する検証を追加し、ビルド時に目視確認できるようにする。
- [Risk] Shapelyという新規Python依存が前処理に追加される → `pipeline/README.md`・
  `check-tools.sh`もしくは前処理READMEに依存追加を明記する。
- [Trade-off] 空間結合は全路線×全地点の総当たりだと計算量が大きい
  （路線1,289件×地点2,384件）が、件数規模的にShapelyの単純な距離判定で十分
  実用的な時間で完了すると想定（事前の性能最適化＝空間インデックス導入は
  Non-Goalとし、実測して問題があれば後続対応とする）。

## Migration Plan

1. `pipeline/preprocess/filter_lines.py`・`filter_points.py`を変更。
2. `pipeline/preprocess/verify_counts.py`に新属性の検証を追加。
3. `./pipeline/build.sh`を再実行し、`site/tiles/lines.pmtiles`・
   `points.pmtiles`を再生成・配置。
4. `site/style/map-style.js`（attribution追加）・`site/main.js`
   （路線クリックハンドラ、地点ポップアップ拡張）を変更。
5. ローカルで`npx serve site`を用いて動作確認（出典表示・路線ポップアップ・
   複数路線接続地点でのポップアップ）。
6. `main`への`site/**`変更pushで既存のGitHub Actionsが自動デプロイ
   （ロールバックは直前コミットへのrevertで対応、追加の移行作業は不要）。
