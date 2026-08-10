## 1. 通称名・路線番号の対応表整備（Issue: #42）

- [x] 1.1 Wikipedia「高速自動車国道」ページの一覧表（高速道路ナンバリング・通称名・
      政令による路線名）を書き起こす
- [x] 1.2 書き起こした一覧を法定路線名でグルーピングし、単一の通称名・路線番号に
      一意に対応するエントリのみを抽出する（複数の通称名区間に分かれる法定路線名は
      除外する）
- [x] 1.3 `pipeline/preprocess/route_common_names.py`に、法定路線名をキーとした
      `common_name`・`route_number`の静的対応表（`ROUTE_COMMON_NAMES`辞書）として
      書き出す
- [x] 1.4 対応表の各エントリをWikipediaページの記載と突き合わせ、転記誤りがないか
      目視確認する

## 2. パイプライン前処理: 路線への通称名・路線番号付与（Issue: #43）

- [x] 2.1 `pipeline/preprocess/filter_lines.py`で`route_name`をキーに
      `ROUTE_COMMON_NAMES`を参照し、ヒットした地物にのみ`common_name`・
      `route_number`属性を追加する（ヒットしない場合は両属性を追加しない）
- [x] 2.2 `pipeline/preprocess/verify_counts.py`に、`common_name`・
      `route_number`が付与された路線地物数を出力する検証を追加する
- [x] 2.3 `pipeline/preprocess/README.md`の出力属性説明を更新する

## 3. パイプライン前処理: JCTのlane_counts重複排除の廃止（Issue: #44）

- [x] 3.1 `pipeline/preprocess/filter_points.py`の`connected_lane_counts`が
      `lane_count`を集める際のデータ構造を`set`から`list`に変更し、重複を排除せず
      昇順ソートのみ行うようにする
- [x] 3.2 `pipeline/preprocess/README.md`の`lane_counts`属性の説明
      （重複排除・昇順ソート → 昇順ソートのみ）を更新する

## 4. パイプライン前処理の実行確認（Issue: #45）

- [x] 4.1 `pipeline/preprocess/run.sh`を実行し、`common_name`・`route_number`・
      `lane_counts`（重複を含む）が期待通り付与されることを確認する
- [x] 4.2 車線数が同じ複数路線が接続する既知のJCT（例：主要JCTを1件以上）で、
      `lane_counts`が重複値を含む配列になっていることを個別に確認する

## 5. タイル生成・配置（Issue: #46）

- [ ] 5.1 `./pipeline/build.sh`を実行し、`common_name`・`route_number`・更新済み
      `lane_counts`を含む`lines.pmtiles`・`points.pmtiles`を再生成する
- [ ] 5.2 `pipeline/tilegen/verify_tiles.py`で新属性がタイル内に保持されていることを
      確認する
- [ ] 5.3 再生成した`site/tiles/lines.pmtiles`・`points.pmtiles`を配置する

## 6. サイト: 路線ラベルの通称名優先表示（Issue: #47）

- [ ] 6.1 `site/style/map-style.js`の`route-labels`レイヤーの`text-field`を
      `["coalesce", ["get", "common_name"], ["get", "route_name"]]`に変更する

## 7. サイト: 路線ポップアップの通称名・路線番号表示（Issue: #48）

- [ ] 7.1 `site/main.js`の路線クリックハンドラで、名称表示要素を
      `common_name`優先（存在しない場合は`route_name`）に変更する
- [ ] 7.2 `common_name`が存在する場合に、路線番号（`route_number`）を表示する行を
      ポップアップに追加する（存在しない場合は表示しない）

## 8. 動作確認（Issue: #49）

- [ ] 8.1 `npx serve site`でローカル起動し、通称名が付与された路線（例：東名高速
      道路）でラベル・ポップアップに通称名・路線番号が表示されることを確認する
- [ ] 8.2 通称名が付与されていない路線（指定都市高速道路や、法定路線名が複数の
      通称名区間に分かれる路線）で、従来通り法定路線名が表示されることを確認する
- [ ] 8.3 車線数が同じ複数路線が接続するJCTで、地点ポップアップの車線数表示が
      重複値を含む形（例：「車線数: 4, 4」）になっていることを確認する
- [ ] 8.4 README.mdに変更点（通称名・路線番号表示、lane_countsの重複排除廃止）が
      あれば反映する
