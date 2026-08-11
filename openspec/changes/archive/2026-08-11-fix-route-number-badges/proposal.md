## Why

現行の路線番号バッジ（`route-number-badges`レイヤー）には3点の不具合・改善要望がある。(1) `symbol-placement: "line"`のデフォルト挙動により、バッジがラインの向き（傾き・上下逆）に追従して回転し、番号が読みにくくなる。(2) `route_number`が存在しない路線でもバッジ（矩形背景画像）が意図せず描画されうる、`text-field`のnull時挙動に依存した脆い実装になっている。(3) 首都高速・阪神高速等の指定都市高速道路（`route_category`が`5`）の路線番号は、国土交通省の高速道路ナンバリング一覧（E/C系統）ではなく法定路線名に埋め込まれた事業者独自の番号から抽出したものであり、E/C系統の路線番号と同じ矩形バッジで表示すると出典の異なる番号体系が視覚的に区別できない。

## What Changes

- 路線番号バッジの向きを、ラインの傾きによらず常に北を上（画面に対して常に正立）にする。`icon-rotation-alignment`／`text-rotation-alignment`を`"viewport"`にし、ライン角度への追従回転を無効化する。
- `route-number-badges`レイヤーに`route_number`の存在を明示的に要求する`filter`（`["has", "route_number"]`）を追加し、`route_number`が存在しない路線ではバッジ画像・テキストとも一切描画されないことを、暗黙のnull挙動ではなく明示的な条件として保証する。
- `route_category`が`5`（指定都市高速道路、MLITナンバリング一覧に由来しない路線番号）のバッジは、形状を矩形からシールド形に変更する。背景色（`ROUTE_NUMBER_BADGE_COLOR`）は変更しない。`route_category`が`1`〜`4`（MLITナンバリング一覧由来）のバッジは矩形のまま変更しない。

## Capabilities

### New Capabilities

（なし）

### Modified Capabilities

- `highway-map-viewer`: 路線番号のライン沿い表示要件を、(a) バッジの向き（常に北が上）、(b) `route_number`非存在時の非表示保証、(c) `route_category`に応じたバッジ形状（矩形／シールド）の描き分け、を含む形に変更する。

## Impact

- `site/style/map-style.js`: `route-number-badges`レイヤーの`layout`（`icon-rotation-alignment`／`text-rotation-alignment`／`filter`）、シールド形SDF画像の追加登録、`route_category`に応じてレイヤーを分岐させる変更。
- `openspec/specs/highway-map-viewer/spec.md`: 「路線番号のライン沿い表示」要件のシナリオ追加・変更。
- 影響を受けるのは`site/`配下の表示ロジックのみで、`pipeline/`（`route_number`属性の解決・タイル生成）には変更なし。
