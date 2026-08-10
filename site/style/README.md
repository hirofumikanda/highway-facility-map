# MapLibre GL JS スタイル定義

`map-style.js` は、`site/tiles/` のPMTiles（路線・地点）をベクトルタイル
ソースとして登録するMapLibreスタイル定義（`site/main.js` から読み込まれる）。

## 路線スタイル（実装済み: Issue #5）

国土地理院の最適化ベクトルタイル（標準地図）の道路表現を参考に、路線は
ケーシング用（`lines-casing`）・塗り用（`lines-fill`）の2つの`line`レイヤーで
描画する。`line-width`はズームレベル（`interpolate`）と路線種別区分
`route_category`＝`N06_008`（`match`）の両方に応じて変化し、高速自動車国道系統
（1・2・3・4）を太く濃い配色、指定都市高速道路（5）・その他（6）を控えめな
太さ・配色にする（design.md 決定7）。

路線名は`symbol-placement: "line"`の`route-labels`レイヤーでライン沿いに
表示し、`text-allow-overlap: false`とMapLibre標準の衝突検出でラベルの重なりを
回避する（design.md 決定8）。`text-field`は`coalesce`式で、通称名
（`common_name`）が付与された路線はその通称名を、付与されていない路線は
法定路線名（`route_name`＝`N06_007`）を表示する（Issue #47、詳細は後述の
「路線の通称名・路線番号表示」参照）。文字（表意文字）を
確実に描画するため、`main.js`側で`localIdeographFontFamily: false`を指定し、
`glyphs`（`https://fonts.openmaptiles.org/{fontstack}/{range}.pbf` /
`Klokantech Noto Sans CJK Regular`）からCJK対応フォントを取得させている
（MapLibreは既定では表意文字をクライアントのシステムフォントでローカル描画
するため、CJKフォント未インストール環境では文字化けする）。

## 地点スタイル（実装済み: Issue #6）

Googleマップのピン/POIマーカー表現を参考に、地点は`circle`レイヤー
（`points`）で描画する。`circle-radius`はズームレベル（`interpolate`）と
接合部種別`point_type`＝`N06_019`（`match`）の両方に応じて変化し、
ジャンクション（3）はやや大きめの目立つ赤、一般インターチェンジ（1）は
標準サイズの青、スマートインターチェンジ（2）はIC系だが区別できるティール、
その他（4）は控えめなグレーにする（design.md 決定9）。マーカーのminzoom
制御はタイル生成時点で種別ごとに設定済みのため、レイヤー側に追加のズーム式は
不要で、そのまま重要度順の段階的表示が実現される。

地点名（`point_name`＝`N06_018`）は`point-labels`という`symbol`レイヤーで
表示する。`text-anchor: "top"`と`text-offset: [0, 0.6]`でマーカーの下に
配置し、マーカーとラベルが重ならないようにしている。

## データ出典表示（実装済み: Issue #31）

`lines`・`points`・`prefectures`の各ソースに`attribution`（国土数値情報
（高速道路時系列データ／行政区域データ）(国土交通省)）を設定している。
`main.js`側でAttributionControlを無効化していないため、MapLibre標準の
AttributionControl（右下）に自動的に連結表示される（design.md 決定1）。

## 路線の通称名・路線番号表示（実装済み: Issue #47, #48）

Wikipedia「高速自動車国道」ページの一覧表を出典とする静的対応表
（`pipeline/preprocess/route_common_names.py`）に基づき、法定路線名が単一の
通称名に一意対応する路線（現在14路線）には、前処理段階で通称名
（`common_name`）・路線番号（`route_number`、例：E1）が属性として付与される
（1つの法定路線名が複数の通称名区間に分かれる路線は対象外、design.md 決定1）。

`route-labels`レイヤーは`common_name`優先でラベルを表示し（前述）、路線
ポップアップ（`main.js`）も名称表示を`common_name`優先とし、`common_name`が
存在する路線には路線番号もあわせて表示する（design.md 決定3）。

- OpenSpec Change: `highway-facility-map`, `add-attribution-route-lane-popups`, `add-route-common-name-jct-lanes`
- 対応するspec: `openspec/changes/highway-facility-map/specs/highway-map-viewer/spec.md`
