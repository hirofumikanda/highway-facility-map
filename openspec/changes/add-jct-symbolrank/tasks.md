## 1. パイプライン: symbolrank算出とminzoom導出（Issue: #81）

- [x] 1.1 `pipeline/preprocess/filter_points.py`に、ジャンクション（`point_type`が`3`）向けの`symbolrank`算出ロジックを追加する。`connected_lane_counts()`が返す`lane_counts`の合計値に基づき、`12`以上なら`1`、`8`〜`11`なら`2`、`7`以下なら`3`を付与する。ジャンクション以外には`symbolrank`を付与しない。
- [x] 1.2 同ファイルの`POINT_TYPE_MINZOOM`の扱いを変更し、ジャンクションについては`symbolrank`から導出した`minzoom`（`symbolrank=1`→`8`、`2`→`9`、`3`→`10`）を地物ごとの`tippecanoe.minzoom`として使用する。ジャンクション以外の地点種別（一般IC=10、スマートIC=12、その他=14）の`minzoom`は変更しない。

## 2. パイプライン: 検証追加と実行確認（Issue: #82）

- [x] 2.1 `pipeline/preprocess/verify_counts.py`に、ジャンクションの`symbolrank`ランク別件数（`1`・`2`・`3`それぞれの件数）を出力する検証を追加する。
- [x] 2.2 `pipeline/preprocess/run.sh`を実行し、`pipeline/output/points.current.geojson`のジャンクション地物に`symbolrank`が期待通り付与されること（ジャンクション以外には付与されないこと、車線数合計と閾値の対応が正しいこと）を確認する。

## 3. タイル生成・配置（Issue: #83）

- [x] 3.1 `pipeline/tilegen/verify_tiles.py`に、ジャンクションの`symbolrank`別ズーム収録の検証を追加する：ズームレベル8には`symbolrank=1`のジャンクションのみ、ズームレベル9には`symbolrank`が`1`・`2`のジャンクション、ズームレベル10以降はすべてのジャンクションが収録されることを確認する。
- [x] 3.2 `./pipeline/build.sh`を実行し、`site/tiles/points.pmtiles`を再生成・配置する。

## 4. サイト: ラベル衝突優先順位への反映（Issue: #84）

- [x] 4.1 `site/style/map-style.js`の`point-labels`レイヤーに`symbol-sort-key`を追加する。ジャンクションは`symbolrank`（`1`〜`3`）をそのまま使用し、一般IC・スマートIC・その他には既存の種別間優先順位（ジャンクション＞一般IC＞スマートIC＞その他）を保つ固定値（例：`4`・`5`・`6`）を割り当てる式にする。

## 5. 動作確認（Issue: #85）

- [ ] 5.1 `npx serve site`でローカルサーバーを起動し、ブラウザで以下を確認する: (a) ズームレベル8では`symbolrank=1`のジャンクションのみ表示される、(b) ズームレベル9で`symbolrank=2`のジャンクションが追加表示される、(c) ズームレベル10で`symbolrank=3`のジャンクションが追加表示され全ジャンクションが揃う、(d) 複数のジャンクションラベルが近接する箇所で`symbolrank`が小さい（優先度の高い）ジャンクションのラベルが優先的に表示される、(e) 一般IC・スマートIC・その他の接合部の表示順・重なり回避の既存挙動が変わっていない。
- [ ] 5.2 design.mdの該当決定（決定1〜4）に、実機確認結果に基づく更新が必要であれば反映する。
