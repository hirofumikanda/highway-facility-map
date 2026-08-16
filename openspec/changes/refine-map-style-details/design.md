## Context

`site/style/map-style.js`の`mapStyle.sources`（`lines`・`points`・`prefectures`）は、`attribution`にプレーンテキストのみを設定している。MapLibre GL JSのAttributionControlはソースの`attribution`文字列をHTMLとしてそのまま描画する（Mapbox/MapLibreスタイル仕様のTileJSON `attribution`フィールドと同じ扱い）ため、`<a>`タグを含めれば追加のJS実装なしにリンクとして表示できる。

`route-number-badges`・`route-number-badges-shield`レイヤーは共通の`ROUTE_NUMBER_BADGE_LAYOUT_BASE`を使い、`text-font: ["Klokantech Noto Sans CJK Regular"]`を指定している。`route_number`属性（`pipeline/preprocess/route_numbers.py`・`route_numbers_by_common_name.py`）の値はすべて英数字（例：`E1`、`E86`、`1`〜`5`）で、CJK文字は含まれない。

シールド形バッジの背景画像（`registerRouteNumberBadgeShieldImage`）は32×32のSDF画像を実行時に手続き的に生成し、`map.addImage(id, {width, height, data}, {sdf: true})`で登録している。`content`・`stretchX`・`stretchY`は指定していない。`icon-text-fit: "both"`（`ROUTE_NUMBER_BADGE_LAYOUT_BASE`で全バッジ共通）は、これらのメタデータがない場合、画像全体をテキストサイズ＋パディングに合わせて縦横独立に単純拡縮する。画像は上部60%（`ROUTE_NUMBER_BADGE_SHIELD_RECT_RATIO`）が矩形、下部40%が中央へ先細りする形状であるため、1桁（`5`）と2桁（`16`）のように横幅の必要量が変わると、この先細り部分の傾斜角度・矩形部分の縦横比が大きく変化し、シールドらしい見た目が崩れる。参考記事（https://qiita.com/k_hirofumi/items/9f04086860ada14cc382）は、この種の可変長ラベル向けシールドアイコンについて、画像に伸縮可能領域（`content`・`stretchX`・`stretchY`、9-slice/9-patchと同様の仕組み）を定義し、`icon-text-fit: "both"`と組み合わせることで、形状のプロポーションを保ったまま必要な軸だけ伸縮させる手法を紹介している。MapLibre GL JSの`map.addImage`は、この`content`・`stretchX`・`stretchY`を実行時生成画像に対しても第3引数のオプションとして受け付ける（スプライトJSONの同名フィールドと同じセマンティクス）。

矩形バッジ（`registerRouteNumberBadgeImage`）は全ピクセルが同一値の単色画像のため、`icon-text-fit: "both"`による単純な縦横独立拡縮でも見た目上の形状崩れは生じない（本変更の対象外）。

## Goals / Non-Goals

**Goals:**
- attribution文字列に出典元へのリンクを追加する。
- 路線番号バッジのラベル文字を太字にする。
- シールド形バッジが、路線番号の桁数によらず形状のプロポーションを維持するようにする。

**Non-Goals:**
- 矩形バッジ（MLITナンバリング由来）の見た目・生成方式の変更。
- `route_number`以外のラベル（路線名・地点名）のフォント変更。

## Decisions

### 決定1: attributionのリンク先は、国土数値情報ダウンロードサイトの各データセットの個別ページとする
高速道路時系列データ（`lines`・`points`ソース）は`https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N06-2025.html`、行政区域データ（`prefectures`ソース）は`https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2026.html`を、それぞれのattribution文字列のリンク先とする。データセット別ページの方が、トップページよりも実際に利用しているデータの詳細（データセットの説明・ダウンロードリンク）に直接到達でき、出典表示の目的（データの出所を示し、参照可能にすること）をより高い精度で満たす。

代替案として検討したが不採用:
- **国土数値情報ダウンロードサイトのトップページ（`https://nlftp.mlit.go.jp/ksj/`）にリンクする**: URLの安定性は高いが、ユーザーが実際に参照しているデータセットの詳細に到達するには、トップページから改めてナビゲーションする必要があり、出典表示としての利便性に劣るため不採用。

### 決定2: 路線番号バッジの`text-font`は、CJK対応フォントではなくラテン文字用の太字フォント（`Klokantech Noto Sans Bold`）に変更する
`route_number`属性の値はすべて英数字であり、CJK文字を表示する必要がない。`glyphs`エンドポイント（`fonts.openmaptiles.org`）がホストするopenmaptiles/fontsのフォントセットには、CJK結合フォントはRegularウェイトのみが含まれ、Boldウェイトの結合フォント（`Klokantech Noto Sans CJK Bold`）は提供されていない一方、ラテン文字用の`Klokantech Noto Sans Bold`は標準的に提供されている（openmaptiles標準スタイルで広く使われているフォントスタック）。CJK文字を含まない`route_number`に対しては、ラテン文字用の太字フォントを直接指定する方が、存在が確認できないCJK太字フォント名に依存するより確実である。

代替案として検討したが不採用:
- **`Klokantech Noto Sans CJK Bold`を指定する**: 提供されているか未確認であり、存在しない場合はグリフ取得に失敗し文字が表示されなくなるリスクがあるため不採用。
- **`text-halo-width`を増やして視覚的に太く見せる**: フォントウェイト自体を変えないため、文字のストローク自体は細いままであり、「文字の太さを太くする」というユーザー指示の意図（フォントウェイトの変更）に直接対応しないため不採用。

### 決定3: シールド形バッジの画像に9-slice（`content`・`stretchX`・`stretchY`）メタデータを追加し、水平方向のみ中央付近の限られた帯を伸縮可能にする
`buildRouteNumberBadgeShieldImageData`が生成する32×32画像に対し、水平方向の伸縮可能領域（`stretchX`）を画像中央付近の限られたピクセル範囲（例：中央から左右対称に数ピクセル幅の帯）に限定し、それ以外の領域（上部矩形の左右端、下部の先細り形状全体を含む輪郭）は伸縮させない。垂直方向（`stretchY`）は指定せず、高さは`icon-size`相当の自然な拡縮のみとする（路線番号バッジの高さはテキスト行数に依存せずほぼ一定のため、高さ方向の9-slice制御は不要）。`content`は、`icon-text-fit-padding`で余白を確保した上でテキストが配置される領域を、既存の矩形部分の内側に定義する。これにより、1桁・2桁いずれの路線番号でも、シールド上部の矩形比率・下部の先細り角度が大きく変わらないまま、必要な幅だけが中央帯で伸縮する。

代替案として検討したが不採用:
- **`icon-text-fit`を`"both"`から`"width"`に変更する**: 高さの拡縮は止まるが、画像全体（先細り部分を含む）が幅方向にのみ単純拡縮されることに変わりはなく、下部の先細り形状の傾斜角度が桁数によって崩れる問題は解決しない。
- **シールド画像を固定サイズ（伸縮なし）にし、`icon-text-fit: "none"`にする**: 2桁の路線番号でテキストがバッジ幅からはみ出す、または1桁でバッジが不必要に大きく見えるなど、可変長テキストへの対応ができないため不採用（ユーザーの参考記事が示す解決方針とも異なる）。

## Risks / Trade-offs

- [Risk] `content`・`stretchX`・`stretchY`の具体的なピクセル範囲は、実装時に実機（ブラウザ）でシールド形状の見た目を確認しながら調整が必要になる（設計段階では方式のみを決定する） → tasks.mdで、複数の桁数の路線番号を含む実データでの目視確認を明示的なタスクとする。
- [Trade-off] `route_number`バッジの`text-font`をCJK非対応フォントに変更するため、将来`route_number`にCJK文字が含まれるデータが追加された場合は文字化けする（**BREAKING**、proposal.md参照）。現状のデータ（MLITナンバリング・指定都市高速道路の独自番号）はいずれも英数字のみであり、この制約は許容範囲とする。
- [Trade-off] attributionのリンク先をデータセット別ページ（`KsjTmplt-N06-2025`・`KsjTmplt-N03-2026`）としたため、国土数値情報側でデータセットのバージョンが更新されURLが変わった場合はリンク切れが生じうる。現時点の最新バージョンへのリンクとし、将来のバージョン更新時は本Changeとは別に更新する。

## Migration Plan

1. `site/style/map-style.js`の`lines`・`points`ソースの`attribution`文字列に`https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N06-2025.html`へ、`prefectures`ソースの`attribution`文字列に`https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2026.html`へのリンク（`target="_blank"`・`rel="noopener noreferrer"`）をそれぞれ含める（決定1）。
2. `ROUTE_NUMBER_BADGE_LAYOUT_BASE`の`text-font`を`["Klokantech Noto Sans Bold"]`に変更する（決定2）。
3. `buildRouteNumberBadgeShieldImageData`または`registerRouteNumberBadgeShieldImage`を、`content`・`stretchX`・`stretchY`を算出・付与するように変更する（決定3）。
4. `npx serve site`でローカル動作確認（attributionのリンクが機能すること、路線番号ラベルが太字で表示されること、1桁・2桁の路線番号を持つ指定都市高速道路のシールドバッジの形状が大きく崩れていないことを含む）を行う。
5. `main`への`site/**`変更pushで、既存のGitHub Actionsが自動デプロイする。
