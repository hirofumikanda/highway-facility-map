## Why

`add-jct-symbolrank`変更により、ジャンクション（JCT）は接続する路線の車線数合計に基づく`symbolrank`でズーム選別されるようになったが、一般インターチェンジ（IC）・スマートインターチェンジ（SIC）は依然として種別ごとの固定`minzoom`（IC=10、SIC=12）で一律に扱われている。IC・SICは合計2,106件（IC 1,942件・SIC 164件）と規模差が大きいにもかかわらず、周辺人口の多寡が表示タイミングに反映されず、低ズームでは主要都市近郊の重要なICも郊外の小規模ICと同時にしか出現しない。

## What Changes

- 地点地物（`points`）のうち、IC（`point_type`が`1`）・SIC（`point_type`が`2`）に、周辺人口に基づく`symbolrank`属性（`2`〜`5`の整数、値が小さいほど上位）を新設する。人口は、国土数値情報の250mメッシュ別将来推計人口データ（`geojson/250m_mesh_2024_GEOJSON/`）の2025年総数人口（男女計、`PTN_2025`）を用い、各地点を中心とする半径10km以内のメッシュの値を合算する。
- `symbolrank`は全国一律の人口順位ではなく、各地点が接続する路線（`route_name`）ごとにグループ化した上での相対順位（人口降順の四分位）で決定する。複数の`route_name`に接続する地点（路線境界に位置するIC/SIC、約10%）は、接続する`route_name`の組を1つの複合グループとして評価する。JCT・その他の接合部には`symbolrank`を付与しない（対象外）。
- IC・SICのタイル収録ズームを、現行の種別固定`minzoom`（IC=10、SIC=12）から、`symbolrank`に応じた段階（`symbolrank=2`は`minzoom=9`、`3`は`10`、`4`は`11`、`5`は`12`）に変更する。JCT・その他の接合部のズーム選別は変更しない。
- 地点名ラベルの衝突判定（`symbol-sort-key`）に、IC・SICの`symbolrank`を反映する。JCTが最優先である既存の階層（JCT＞IC/SIC＞その他）は維持しつつ、IC・SIC間は種別（IC/SIC）ではなく`symbolrank`（人口）で優先順位を決定する形に変更する（**BREAKING**: 従来は同一symbolrank帯がなく「IC＞SIC」の固定順だったが、本変更後は人口が多いSICが人口の少ないICより優先表示され得る）。

## Capabilities

### New Capabilities

（なし）

### Modified Capabilities

- `highway-tile-pipeline`: 「地点データの重要度に基づくズーム選別」要件に、IC・SICの`symbolrank`に応じた段階的ズーム選別を追加する。IC・SICへの人口ベース`symbolrank`付与を新しい要件として追加する。
- `highway-map-viewer`: 「地点名ラベルの重要度に応じた表示」要件に、IC・SICの`symbolrank`に応じた段階的表示と、重なり時のIC・SIC間の`symbolrank`優先表示を追加する。

## Impact

- `pipeline/preprocess/`: 新設スクリプト（IC/SIC周辺人口の算出）を追加し、`filter_points.py`にIC/SICの`symbolrank`算出・`route_name`グループ化・`minzoom`決定ロジックを追加。
- `geojson/250m_mesh_2024_GEOJSON/`（既存データ、Git管理対象外、合計約7.7GB）を新たに参照する前処理ステップを追加。ビルド時間の増加が見込まれる。
- `pipeline/preprocess/verify_counts.py`: IC/SICの`symbolrank`属性・件数集計の検証を追加。
- `site/style/map-style.js`: `point-labels`レイヤーの`symbol-sort-key`を、IC・SICの`symbolrank`を反映する形に変更。
- `pipeline/preprocess/README.md`: 新設スクリプトの依存関係（人口メッシュデータ、必要に応じて追加ライブラリ）を追記。
- 既存の`lane_counts`・JCTの`symbolrank`（車線数合計ベース）の算出ロジックは変更しない。
