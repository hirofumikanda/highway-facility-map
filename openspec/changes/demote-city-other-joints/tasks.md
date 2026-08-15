## 1. 接続路線種別区分（route_category）の取得 (#117)

- [x] 1.1 `pipeline/preprocess/filter_points.py`の`load_line_geometries`を、`route_category`（`N06_008`由来、`lines.current.geojson`の`properties.route_category`）も含めて返すように拡張する
- [x] 1.2 `route_category_candidates`（`[(geom, route_category), ...]`）を構築し、`connected_route_categories(point_geom, route_category_candidates)`ヘルパーを追加する（JCT・IC・SIC共通）
- [x] 1.3 接続路線の`route_category`集合が空でなく`{"5", "6"}`の部分集合であるかを判定するヘルパー（例: `is_city_or_other_only`）を追加する

## 2. symbolrank・minzoomの補正 (#118)

- [x] 2.1 JCTの`symbolrank`算出（`jct_symbolrank`）後に、接続路線の判定結果に基づき`symbolrank += 1`する補正を適用する
- [x] 2.2 IC・SICの`assign_ic_sic_symbolranks`によるグループ内四分位算出完了後に、接続路線の判定結果に基づき`symbolrank += 1`する補正を適用する
- [x] 2.3 `JCT_SYMBOLRANK_MINZOOM`に`4: 11`を追加する
- [x] 2.4 `IC_SIC_SYMBOLRANK_MINZOOM`に`6: 13`を追加する
- [x] 2.5 補正後の`symbolrank`を用いて`tippecanoe.minzoom`が決定されることを確認する（既存の辞書引きロジックがそのまま機能することの確認）

## 3. パイプライン実行と前処理検証の更新 (#119)

- [ ] 3.1 `pipeline/preprocess/run.sh`を実行し、`pipeline/output/points.current.geojson`を再生成する
- [ ] 3.2 実データでのJCT・IC・SICのsymbolrank別件数（補正対象・非対象それぞれ）を集計する
- [ ] 3.3 `pipeline/preprocess/verify_counts.py`のJCT・IC・SICのsymbolrank別件数期待値を、3.2の実データに基づき更新する
- [ ] 3.4 `pipeline/preprocess/verify_counts.py`の`expected_point_minzoom`が、拡張後の`JCT_SYMBOLRANK_MINZOOM`・`IC_SIC_SYMBOLRANK_MINZOOM`を正しく参照することを確認する
- [ ] 3.5 `pipeline/preprocess/verify_counts.py`を実行し、全チェックが成功することを確認する

## 4. タイル生成と収録検証の更新 (#120)

- [ ] 4.1 `./pipeline/build.sh`を実行し、`site/tiles/points.pmtiles`を再生成する
- [ ] 4.2 `pipeline/tilegen/verify_tiles.py`のジャンクションのズーム別収録期待値（z8〜z11）・件数期待値を更新する
- [ ] 4.3 `pipeline/tilegen/verify_tiles.py`のIC・SICのズーム別収録期待値（z9〜z13）・件数期待値を更新する
- [ ] 4.4 `pipeline/tilegen/verify_tiles.py`を実行し、全チェックが成功することを確認する

## 5. ラベル表示スタイルの更新 (#121)

- [ ] 5.1 `site/style/map-style.js`の`point-labels`レイヤーの`symbol-sort-key`の、その他の接合部（`match`のデフォルト値）を`9`から`10`に変更する
- [ ] 5.2 変更箇所のコメントを、値域再配置（JCT: 1〜4、IC/SIC: 5〜9、その他: 10）に合わせて更新する

## 6. 動作確認 (#122)

- [ ] 6.1 `npx serve site`でローカル起動し、指定都市高速道路・その他にのみ連結するJCT・IC・SICが、補正前と比べて1段階高いズームレベルから表示されることを確認する
- [ ] 6.2 広域路線（`route_category`が`1`〜`4`のいずれか）に接続する結合部の表示ズーム・ラベル衝突優先順位に変化がないことを確認する
- [ ] 6.3 補正後もジャンクションが一般インターチェンジ・スマートインターチェンジより常に優先表示されることを確認する
- [ ] 6.4 その他の接合部（point_type=4）の表示に変化がないことを確認する

## 7. デプロイ (#123)

- [ ] 7.1 `pipeline/**`・`site/**`の変更を`main`にpushし、`site/**`分の既存GitHub Actionsによる自動デプロイを確認する
- [ ] 7.2 再生成した`site/tiles/points.pmtiles`が配置されていることを手動で確認する
