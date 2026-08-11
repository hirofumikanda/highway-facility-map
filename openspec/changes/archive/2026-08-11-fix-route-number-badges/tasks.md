## 1. バッジの向きを常に正立にする（Issue: #73）

- [x] 1.1 `site/style/map-style.js`の`route-number-badges`レイヤーの`layout`に`icon-rotation-alignment: "viewport"`・`text-rotation-alignment: "viewport"`を追加する。

## 2. `route_number`非存在時の非表示を明示化する（Issue: #74）

- [x] 2.1 `site/style/map-style.js`の`route-number-badges`レイヤーに`filter: ["has", "route_number"]`を追加する（決定3で`route_category`条件と統合する場合は`"all"`でまとめる）。

## 3. `route_category`に応じた矩形／シールド形の描き分け（Issue: #75）

- [x] 3.1 シールド形SDF画像（2値マスク、矩形＋下部先細り）を生成する関数（例：`registerRouteNumberBadgeShieldImage`）と、その画像ID定数を`site/style/map-style.js`に追加する。
- [x] 3.2 既存`route-number-badges`レイヤーの`filter`を`["all", ["has", "route_number"], ["!=", ["get", "route_category"], "5"]]`に変更する（矩形のまま、`route_category`1〜4のみ対象）。
- [x] 3.3 新規レイヤー`route-number-badges-shield`を`route-number-badges`の直後に追加する。`filter`は`["all", ["has", "route_number"], ["==", ["get", "route_category"], "5"]]`とし、`layout`（`symbol-placement`・`symbol-spacing`・`text-field`・フォント・`text-size`・回転整列）と`paint`（`icon-color`・`text-color`）は既存レイヤーと同じ値、`icon-image`のみシールド画像を参照する。
- [x] 3.4 `site/main.js`の`map.on("load", ...)`内で、新規シールド画像登録関数を`registerRouteNumberBadgeImage`と併せて呼び出す。

## 4. 動作確認（Issue: #76）

- [x] 4.1 `npx serve site`でローカルサーバーを起動し、ブラウザで以下を確認する: (a) 向きの異なる複数のライン区間で路線番号バッジが常に正立して表示される、(b) `route_number`が付与されていない路線（例：唐桑道路）でバッジが一切表示されない、(c) `route_category`1〜4の路線（例：東名高速道路）で矩形バッジが表示される、(d) `route_category`5の路線（例：首都高速1号羽田線）でシールド形バッジが表示され背景色は矩形バッジと同じである、(e) 路線名ラベルとバッジの重なりが引き続き回避される。

  実施結果: これまでIssue #73〜#75では、本セッションのサンドボックス制約（Chromium起動に必要なシステム依存ライブラリ`libasound2t64`が不足しsudoでのインストールもできない）によりブラウザでの目視確認ができなかった。本タスクで、`apt-get download`でdebパッケージを取得し`dpkg-deb -x`でroot権限なしに展開、`LD_LIBRARY_PATH`で参照させることでライブラリ不足を解消し、初めてブラウザでの実描画確認に成功した。あわせて、ヘッドレスChromiumでWebGLを有効化する`--use-gl=angle --use-angle=swiftshader-webgl`、および地図データが読み込まれない別の問題（MapLibre GL JSのモジュールワーカーがblob URLから読み込めずnet::ERR_FILE_NOT_FOUNDになる）を解消する`--disable-site-isolation-trials --disable-features=IsolateOrigins,site-per-process`が必要だった。

  `npx serve site`でローカル起動し、Playwright（ヘッドレスChromium）でスクリーンショットを取得して以下を確認した：
  - (a) 山陽自動車道（E2、カーブしたライン）・首都高速（シールド、斜めのライン）のいずれも、ライン区間の角度によらずバッジが常に画面に対して正立して表示される
  - (b) `route_number`が付与されていない唐桑道路で、バッジが一切表示されない（路線名ラベルのみ表示）
  - (c) `route_category`が1の山陽自動車道で、矩形の緑背景×白字のバッジ（E2）が表示される
  - (d) `route_category`が5の広島高速・首都高速で、シールド形（上部矩形・下部先細り）のバッジ（例：1、6）が表示され、背景色は矩形バッジ（E2）と同じ濃い緑である
  - (e) 路線名ラベルと路線番号バッジが近接する箇所（例：山陽自動車道）でも重なりは見られなかった

- [x] 4.2 design.mdの該当決定（決定1〜3）に、実機確認結果に基づく更新が必要であれば反映する。

  実施結果: 決定1（"viewport"回転整列）・決定2（`filter`による明示的な非表示）・決定3（`route_category`によるレイヤー分岐とシールド形SDF画像）はいずれも実機確認で意図通り動作することを確認し、設計変更は不要だった。Risks/Trade-offsの該当2件（シールド形の視覚的歪み、既定表示以外でのviewport整列の限界）に実機確認結果を追記した。
