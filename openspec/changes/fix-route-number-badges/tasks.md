## 1. バッジの向きを常に正立にする

- [ ] 1.1 `site/style/map-style.js`の`route-number-badges`レイヤーの`layout`に`icon-rotation-alignment: "viewport"`・`text-rotation-alignment: "viewport"`を追加する。

## 2. `route_number`非存在時の非表示を明示化する

- [ ] 2.1 `site/style/map-style.js`の`route-number-badges`レイヤーに`filter: ["has", "route_number"]`を追加する（決定3で`route_category`条件と統合する場合は`"all"`でまとめる）。

## 3. `route_category`に応じた矩形／シールド形の描き分け

- [ ] 3.1 シールド形SDF画像（2値マスク、矩形＋下部先細り）を生成する関数（例：`registerRouteNumberBadgeShieldImage`）と、その画像ID定数を`site/style/map-style.js`に追加する。
- [ ] 3.2 既存`route-number-badges`レイヤーの`filter`を`["all", ["has", "route_number"], ["!=", ["get", "route_category"], "5"]]`に変更する（矩形のまま、`route_category`1〜4のみ対象）。
- [ ] 3.3 新規レイヤー`route-number-badges-shield`を`route-number-badges`の直後に追加する。`filter`は`["all", ["has", "route_number"], ["==", ["get", "route_category"], "5"]]`とし、`layout`（`symbol-placement`・`symbol-spacing`・`text-field`・フォント・`text-size`・回転整列）と`paint`（`icon-color`・`text-color`）は既存レイヤーと同じ値、`icon-image`のみシールド画像を参照する。
- [ ] 3.4 `site/main.js`の`map.on("load", ...)`内で、新規シールド画像登録関数を`registerRouteNumberBadgeImage`と併せて呼び出す。

## 4. 動作確認

- [ ] 4.1 `npx serve site`でローカルサーバーを起動し、ブラウザで以下を確認する: (a) 向きの異なる複数のライン区間で路線番号バッジが常に正立して表示される、(b) `route_number`が付与されていない路線（例：唐桑道路）でバッジが一切表示されない、(c) `route_category`1〜4の路線（例：東名高速道路）で矩形バッジが表示される、(d) `route_category`5の路線（例：首都高速1号羽田線）でシールド形バッジが表示され背景色は矩形バッジと同じである、(e) 路線名ラベルとバッジの重なりが引き続き回避される。
- [ ] 4.2 design.mdの該当決定（決定1〜3）に、実機確認結果に基づく更新が必要であれば反映する。
