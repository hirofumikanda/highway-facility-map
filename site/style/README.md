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

路線名（`route_name`＝`N06_007`）は`symbol-placement: "line"`の`route-labels`
レイヤーでライン沿いに表示し、`text-allow-overlap: false`とMapLibre標準の
衝突検出でラベルの重なりを回避する（design.md 決定8）。文字（表意文字）を
確実に描画するため、`main.js`側で`localIdeographFontFamily: false`を指定し、
`glyphs`（`https://fonts.openmaptiles.org/{fontstack}/{range}.pbf` /
`Klokantech Noto Sans CJK Regular`）からCJK対応フォントを取得させている
（MapLibreは既定では表意文字をクライアントのシステムフォントでローカル描画
するため、CJKフォント未インストール環境では文字化けする）。

## 地点スタイル（未実装: Issue #6）

現状は地物が表示されることを確認できる最小限の配色（`circle`レイヤー）のみ。
Googleマップのピン/POIマーカー表現を参考にした種別ごとの配色・形状は
tasks.md タスク番号 7.1〜7.3（GitHub Issue #6）で実装する。

- OpenSpec Change: `highway-facility-map`
- 対応するspec: `openspec/changes/highway-facility-map/specs/highway-map-viewer/spec.md`
