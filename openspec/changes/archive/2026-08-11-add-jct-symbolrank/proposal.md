## Why

現行のジャンクション（JCT）は、地点種別（`point_type`）に基づく重要度ティア（ジャンクション ＞ 一般インターチェンジ ＞ スマートインターチェンジ ＞ その他の接合部）でのみズーム選別されており、245件のJCTすべてが一様にズームレベル8から表示される。JCT間の規模差（接続する路線の車線数の合計、1〜24の幅がある）が反映されないため、低ズームでは規模の小さいJCTも大規模なJCTと同時に表示され、地図が煩雑になりやすい。

## What Changes

- 地点地物（`points`）に、JCT（`point_type`が`3`）に限り`symbolrank`属性（`1`〜`3`の整数、値が小さいほど上位）を新設する。値は、その地点に接続する路線の車線数の合計（`lane_counts`の合計値）に基づき、実データ（245件のJCT）でおおむね均等な3分割となる閾値で算出する：合計値が`12`以上なら`symbolrank=1`、`8`〜`11`なら`symbolrank=2`、`7`以下なら`symbolrank=3`。JCT以外の地点には`symbolrank`を付与しない。
- JCTのタイル収録ズームを、現行の一律`minzoom=8`から、`symbolrank`に応じた段階（`symbolrank=1`は`minzoom=8`、`symbolrank=2`は`minzoom=9`、`symbolrank=3`は`minzoom=10`）に変更する。JCT以外の地点種別のズーム選別（一般IC・スマートIC・その他）は変更しない。
- 地点名ラベルの衝突判定に、`symbolrank`に基づく優先順位（値が小さいほど優先表示）を追加する。同一画面上でJCTラベル同士の表示位置が重なる場合、`symbolrank`が小さいJCTのみを表示する。地点種別間の既存の優先順位（ジャンクション ＞ 一般IC ＞ スマートIC ＞ その他）は変更しない。

## Capabilities

### New Capabilities

（なし）

### Modified Capabilities

- `highway-tile-pipeline`: 「地点データの重要度に基づくズーム選別」要件に、JCT内での`symbolrank`に応じた段階的ズーム選別を追加する。JCTへの`symbolrank`付与を新しい要件として追加する。
- `highway-map-viewer`: 「地点名ラベルの重要度に応じた表示」要件に、JCT内での`symbolrank`に応じた段階的表示と、重なり時の`symbolrank`優先表示を追加する。

## Impact

- `pipeline/preprocess/filter_points.py`: JCTの`symbolrank`算出（`lane_counts`合計値からの3分割判定）と、`symbolrank`に応じた`tippecanoe.minzoom`の算出ロジックを追加。
- `pipeline/preprocess/verify_counts.py`・`pipeline/tilegen/verify_tiles.py`: `symbolrank`属性・段階的ズーム収録の検証を追加（既存の`lane_counts`検証は変更しない）。
- `site/style/map-style.js`: `point-labels`レイヤーに`symbol-sort-key`を追加し、`symbolrank`（JCT）と地点種別に基づく優先順位を反映。
- 既存の`lane_counts`属性（重複排除なしの接続路線車線数リスト）自体の算出ロジックは変更しない。
