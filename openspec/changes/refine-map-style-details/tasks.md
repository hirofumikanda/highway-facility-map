## 1. attributionへのリンク追加 (#143)

- [x] 1.1 `site/style/map-style.js`の`lines`ソースの`attribution`文字列に、`https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N06-2025.html`へのリンク（`target="_blank"`・`rel="noopener noreferrer"`）を追加する
- [x] 1.2 `points`ソースの`attribution`文字列に同様のリンクを追加する
- [x] 1.3 `prefectures`ソースの`attribution`文字列に、`https://nlftp.mlit.go.jp/ksj/gml/datalist/KsjTmplt-N03-2026.html`へのリンク（`target="_blank"`・`rel="noopener noreferrer"`）を追加する

## 2. 路線番号ラベルの太字化 (#144)

- [x] 2.1 `ROUTE_NUMBER_BADGE_LAYOUT_BASE`の`text-font`を`["Klokantech Noto Sans CJK Regular"]`から`["Klokantech Noto Sans Bold"]`に変更する

## 3. シールド形バッジの9-slice対応 (#145)

- [x] 3.1 `buildRouteNumberBadgeShieldImageData`の画像設計（32×32、上部60%矩形・下部40%先細り）を踏まえ、水平方向の伸縮可能領域（`stretchX`）を中央付近の限られた帯に限定するピクセル範囲を決定する
- [x] 3.2 テキスト配置領域（`content`）を、上部矩形部分の内側に定義する
- [x] 3.3 `registerRouteNumberBadgeShieldImage`の`map.addImage`呼び出しに、算出した`content`・`stretchX`（`stretchY`は指定しない）を`{sdf: true}`とあわせてオプションとして渡すよう変更する

## 4. 動作確認 (#146)

- [ ] 4.1 `npx serve site`でローカル起動し、地図右下のAttributionControlの国土数値情報の出典表示がリンクとして機能し、クリックで国土数値情報ダウンロードサイトが開くことを確認する
- [ ] 4.2 矩形バッジ（MLITナンバリング由来、例：`E1`）・シールド形バッジ（指定都市高速道路、例：首都高速の路線番号）のいずれも、ラベル文字が太字で表示されることを確認する
- [ ] 4.3 1桁（例：`5`）・2桁（例：`16`）の路線番号を持つシールド形バッジを見比べ、上部矩形・下部の先細り形状のプロポーションが大きく崩れていないことを確認する
- [ ] 4.4 矩形バッジの見た目（形状・サイズ感）に変化がないことを確認する

## 5. デプロイ (#147)

- [ ] 5.1 `site/**`の変更を`main`にpushし、既存のGitHub Actionsによる自動デプロイを確認する
