## 1. 路線番号対応表の整備（Issue: #58）

- [ ] 1.1 国土交通省「高速道路ナンバリング一覧」（`https://www.mlit.go.jp/road/sign/numbering/list/index.html`、関連ページ・リーフレットPDF等）を出典として、路線番号（E1〜E98、C系統等）ごとの案内路線名を書き起こす。
- [ ] 1.2 書き起こした案内路線名を、`geojson/N06-25_HighwaySection.geojson`の法定路線名（`N06_007`、`route_category`が`1`〜`5`の314件中の該当分）と突き合わせ、法定路線名→`route_number`の対応を確定する。ナンバリング一覧側の区間但し書き（例：「（仙台港北～利府）」）がある場合は、対応する法定路線名の地物全体に同一の`route_number`を割り当てる（design.md Non-Goals）。
- [ ] 1.3 `pipeline/preprocess/route_numbers.py`を新設し、確定した対応（`ROUTE_NUMBERS`辞書、法定路線名→`route_number`、複数キーが同一値を持つことを許容）を実装する。出典・書き起こし方針をモジュールdocstringに記載する。
- [ ] 1.4 対応表の各エントリを、国土交通省ナンバリング一覧の記載と突き合わせて目視確認する。

## 2. パイプライン前処理: 路線番号付与ロジックの変更（Issue: #59）

- [ ] 2.1 `pipeline/preprocess/filter_lines.py`を変更し、`route_category`が`1`〜`5`の地物について`ROUTE_NUMBERS`を`route_name`で引き、ヒットすれば`common_name`の有無にかかわらず`route_number`を付与する。`common_name`の解決（`ROUTE_COMMON_NAMES`）は既存ロジックのまま独立して行う。
- [ ] 2.2 `pipeline/preprocess/verify_counts.py`に、`ROUTE_NUMBERS`のエントリ数・`route_number`が付与された路線地物数を出力する検証を追加する。

## 3. パイプライン前処理の実行確認（Issue: #60）

- [ ] 3.1 `pipeline/preprocess/run.sh`を実行し、`pipeline/output/lines.current.geojson`に`route_number`が期待通り付与されること（`common_name`がない路線にも付与されること、`route_category`が`6`の路線に付与されないこと）を確認する。

## 4. タイル生成・配置（Issue: #61）

- [ ] 4.1 `./pipeline/build.sh`を実行し、`pipeline/output/lines.pmtiles`を再生成する。
- [ ] 4.2 `pipeline/tilegen/verify_tiles.py`で`route_number`属性がタイル内に保持されていることを確認する。
- [ ] 4.3 再生成した`site/tiles/lines.pmtiles`を配置する。

## 5. サイト: 路線番号のライン沿い表示（Issue: #62）

- [ ] 5.1 `site/style/map-style.js`に、矩形バッジ用のSDF画像を生成し`map.addImage`で登録する処理を追加する。
- [ ] 5.2 `route-number-badges`シンボルレイヤーを追加する（`symbol-placement: "line"`・`symbol-spacing`によるライン沿い一定間隔配置、`icon-image`＋`icon-text-fit: "both"`による矩形背景、`text-field: ["get", "route_number"]`、`text-color: "#ffffff"`、路線本体の`CASING_COLOR`／`FILL_COLOR`とは異なる固定の緑を`icon-color`に設定）。レイヤー順は`route-labels`の直後（上）に配置する。
- [ ] 5.3 `icon-allow-overlap: false`・`text-allow-overlap: false`を設定し、既存の`route-labels`との重なりが衝突検出で回避されることを確認する。

## 6. サイト: 路線ポップアップの路線番号表示条件変更（Issue: #63）

- [ ] 6.1 `site/main.js`の路線ポップアップで、路線番号の表示条件を`if (common_name)`から`if (route_number)`に変更する。

## 7. 動作確認（Issue: #64）

- [ ] 7.1 `npx serve site`でローカル起動し、`common_name`を持つ路線（従来通り路線番号バッジ・ポップアップ路線番号が表示される）を確認する。
- [ ] 7.2 `common_name`を持たないが今回`route_number`が付与された路線（路線番号バッジ・ポップアップ路線番号が新たに表示される）を確認する。
- [ ] 7.3 路線番号バッジの背景色が、路線本体のケーシング・塗り色と目視で区別できることを確認する。
- [ ] 7.4 路線名ラベルと路線番号バッジが近接する箇所で、重なりが回避されていることを確認する。
- [ ] 7.5 `route_number`が付与されていない路線（`route_category`が`6`等）で、バッジ・ポップアップ路線番号のいずれも表示されないことを確認する。
