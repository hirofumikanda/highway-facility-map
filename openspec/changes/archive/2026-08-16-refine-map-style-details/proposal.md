## Why

現在のスタイルには3つの改善余地がある。(1) データ出典（国土数値情報）のattribution表示が文字列のみで、出典元へのリンクがない。(2) 路線番号ラベル（`route_number`）の文字が細く、地図上で視認しづらい。(3) 指定都市高速道路の路線番号シールドアイコンは、`icon-text-fit: "both"`でテキストの長さに合わせて縦横それぞれ独立に伸縮するため、路線番号の桁数（1〜2桁）によってシールド形状の縦横比が大きく崩れる。

## What Changes

- `lines`・`points`・`prefectures`の各PMTilesソースの`attribution`文字列に、出典元（国土数値情報）へのハイパーリンクを追加する。リンク先は、高速道路時系列データ（`lines`・`points`ソース）は当該データセットの個別ページ（`https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N06-2025.html`）、行政区域データ（`prefectures`ソース）は当該データセットの個別ページ（`https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2026.html`）とする。
- 路線番号バッジ（矩形・シールド形の両方、`route-number-badges`・`route-number-badges-shield`レイヤー）のラベル文字を、現在の`text-font`（`Klokantech Noto Sans CJK Regular`）から、太字のラテン文字用フォント（`Klokantech Noto Sans Bold`）に変更する。`route_number`属性の値はラテン文字・数字のみ（例：`E1`、`5`）でCJK文字を含まないため、CJK対応フォントは不要（**BREAKING**: 対象レイヤーの`text-font`をCJK対応フォントから非対応フォントに変更するため、`route_number`に将来CJK文字が含まれるようになった場合は文字化けする）。
- シールド形バッジ（`route-number-badges-shield`レイヤー、指定都市高速道路の路線番号用）のSDF画像生成を、単純な画像全体の伸縮ではなく、伸縮可能な領域と固定領域を区別する仕組み（9-slice、`content`・`stretchX`・`stretchY`のメタデータ）を用いる方式に変更し、路線番号の桁数によらずシールドの上部矩形・下部の先細り形状のプロポーションが大きく崩れないようにする。

## Capabilities

### New Capabilities

（なし）

### Modified Capabilities

- `highway-map-viewer`: 「路線番号のライン沿い表示」要件に、ラベル文字の太さ・シールド形バッジの縦横比維持を追加する。「ソースデータ出典（attribution）の表示」要件（現行のメインspecには未反映だが実装済み、`add-attribution-route-lane-popups`変更で導入）に、出典元へのリンクを追加する。

## Impact

- `site/style/map-style.js`: `attribution`文字列へのリンク追加、`ROUTE_NUMBER_BADGE_LAYOUT_BASE`の`text-font`変更、`registerRouteNumberBadgeShieldImage`のSDF画像生成・`map.addImage`呼び出しの変更（9-slice メタデータ追加）。
- 矩形バッジ（`route-number-badges`、MLITナンバリング由来の路線番号用）のSDF画像生成自体は変更しない（単色矩形のため伸縮による形状崩れがなく、対象外）。
