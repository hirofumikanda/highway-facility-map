## Context

`pipeline/preprocess/filter_points.py`は現在、`connected_route_names`（頂点一致判定、`spatial_match.matching_values`）でIC・SICの接続路線の`route_name`のみを取得しており、`route_category`は取得していない。JCTは接続路線の`lane_count`のみを取得している（`connected_lane_counts`）。`route_category`自体は`pipeline/output/lines.current.geojson`の各路線地物にすでに`N06_008`由来の属性として存在する（`filter_lines.py`）。

`site/style/map-style.js`の`point-labels`レイヤーの`symbol-sort-key`は、`match`式で`point_type`ごとに以下を返す（[[main spec]] `highway-map-viewer`の「地点名ラベルの重要度に応じた表示」要件）：
- JCT（`point_type`が`"3"`）: `symbolrank`（`1`〜`3`）をそのまま使用
- IC・SIC（`point_type`が`"1"`・`"2"`）: `symbolrank`（`2`〜`5`）に`3`を加えた値（`5`〜`8`）
- その他の接合部（`point_type`が上記以外）: 固定値`9`

本変更でIC・SICの`symbolrank`の最大値が`5`から`6`に広がると、`symbolrank+3`は最大`9`となり、その他の接合部の固定値`9`と重複する（[[proposal]] 参照）。

## Goals / Non-Goals

**Goals:**
- JCT・IC・SICのうち、頂点一致判定で接続する路線地物の`route_category`が`5`（指定都市高速道路）・`6`（その他）のみで構成される地物の`symbolrank`を1段階下位側に補正し、対応する`minzoom`を1段階引き上げる。
- `symbol-sort-key`の値域を、補正後の`symbolrank`の拡張範囲（JCT: 最大`4`、IC/SIC: 最大`6`）に対して、既存の種別間優先階層（JCT ＞ IC/SIC ＞ その他の接合部）を壊さずに再配置する。

**Non-Goals:**
- JCTの`symbolrank`算出ロジック自体（車線数合計ベース）、IC・SICの`symbolrank`算出ロジック自体（周辺人口の路線内相対順位ベース）の変更。本変更はそれらの算出結果に対する事後補正のみを追加する。
- その他の接合部（`point_type`が`"4"`）への本補正の適用。`route_category`に関わらず対象外のまま。
- `route_category`が判定できない（接続路線が1件もない）地点への補正適用。

## Decisions

### 決定1: 補正は既存のsymbolrank算出後の事後加算として実装し、既存のsymbolrank算出ロジック・グループ化ロジックには手を加えない
JCTの`jct_symbolrank(lane_counts)`、IC・SICの`assign_ic_sic_symbolranks(entries)`（路線内相対順位に基づく四分位算出）はそのまま実行し、その結果に対して「接続する路線の`route_category`がすべて`5`・`6`のみ」の場合に`symbolrank += 1`する後処理ステップを追加する。IC・SICのグループ化・四分位算出は接続路線の`route_name`のみに基づいており`route_category`を考慮しないため、同一グループ内に補正対象・非対象の地点が混在し得るが、これは意図した挙動である（人口による路線内相対評価と、路線種別区分による全国的な重要度補正は独立した軸として扱う）。

代替案として検討したが不採用:
- **`route_category`をグループ化キーに含め、指定都市高速道路・その他にのみ接続する地点を別グループとして四分位評価する**: 対象グループのサイズが小さい路線では四分位の意味が薄れ、既存の「路線ごとに表示密度を均一にする」設計意図（add-ic-sic-symbolrank design.md 決定3）から外れるため不採用。ユーザー指示は「symbolrankを一つずつ下げる」という単純な段階シフトであり、再評価ではない。

### 決定2: 補正対象の判定は、JCT・IC・SIC共通の`connected_route_categories`ヘルパーで、頂点一致判定による接続路線の`route_category`集合を求め、それが空でなく`{"5", "6"}`の部分集合であるかで行う
`filter_points.py`に、`connected_lane_counts`・`connected_route_names`と同様のパターンで`connected_route_categories(point_geom, route_category_candidates)`を追加する。`route_category_candidates`は`load_line_geometries`が返す路線ジオメトリリストに`route_category`を含めるよう拡張して構築する。判定関数`is_city_or_other_only(route_categories)`は、`route_categories`が空集合でなく、かつ`set(route_categories) <= {"5", "6"}`であることを確認する。

接続路線が1件もない地点（実データでIC・SIC 1件）は`route_categories`が空集合となり、判定は`False`（補正なし）となる。「指定都市高速道路・その他にのみ連結する」という条件は接続路線の存在を前提とするため、この扱いが自然である。

代替案として検討したが不採用:
- **接続路線が1件もない地点も補正対象に含める**: 「指定都市高速道路(5)又はその他(6)にのみ連結する」という条件文言上、連結先が存在しない地点は文字通りには該当しないため不採用。実データでの該当件数は極小（IC・SIC 1件、常にsymbolrank=2固定グループ）であり、扱いによる表示への影響も軽微。

### 決定3: 補正後のsymbolrankからminzoomを導出するマッピング表を、既存の段階的minzoom表の1段階分だけ拡張する
`JCT_SYMBOLRANK_MINZOOM`に`4: 11`を追加し、`IC_SIC_SYMBOLRANK_MINZOOM`に`6: 13`を追加する。既存のminzoom決定コード（`entry["minzoom"] = JCT_SYMBOLRANK_MINZOOM[symbolrank]`等）は、補正後の`symbolrank`をキーとしてそのまま利用できる。両表の値はいずれも既存の最大値に`+1`した値であり、ユーザー指示の「minzoomを一つずつ上げる」と数値的に一致する。最大ズーム（`--maximum-zoom=14`、`pipeline/tilegen/build_points.sh`）を超えないため、収録自体が失われることはない。

### 決定4: `symbol-sort-key`は、IC・SICのオフセット（`symbolrank + 3`）はそのまま維持し、その他の接合部の固定値を`9`から`10`に引き上げる
IC・SICの補正後`symbolrank`の最大値が`6`になるため、`symbolrank + 3`の最大値は`9`となる。この値がその他の接合部の既存固定値`9`と重複するため、その他の接合部の固定値を、IC・SICの拡張後の値域（`5`〜`9`）よりも大きい`10`に変更する。JCTの補正後`symbolrank`の最大値は`4`であり、IC・SICの最小値`5`未満のままなので、JCT側のsort-key式（`symbolrank`をそのまま使用）は変更不要。この結果、`symbol-sort-key`の値域は「JCT: 1〜4」＜「IC・SIC: 5〜9」＜「その他の接合部: 10」に再配置され、既存の種別間優先階層（JCT＞IC/SIC＞その他の接合部）は保たれる。

代替案として検討したが不採用:
- **IC・SICのオフセットを`4`に引き上げ、その他の接合部の固定値は`9`のまま維持する**: JCTの最大値`4`とIC・SICの最小値（`2+4=6`）の間に十分な余白があり一見成立するが、オフセット定数の変更はJCT側の値域とのマージンが縮む変更であり、その他の接合部の固定値を1つ引き上げるだけの決定4の方が変更範囲が小さく理解しやすいため不採用。

## Risks / Trade-offs

- [Risk] `connected_route_categories`の空間頂点一致判定は既存の`matching_values`をJCTにも新規適用するため、JCTの前処理時間がわずかに増加する（IC・SICはすでに`connected_route_names`で同等の空間探索を行っており、増分は無視できる） → 実行頻度・データ規模（JCT 245件）を踏まえ許容範囲とする。
- [Risk] `pipeline/preprocess/verify_counts.py`・`pipeline/tilegen/verify_tiles.py`のsymbolrank別件数・ズーム別収録件数のハードコードされた期待値は、本補正により変化する（一部の地点がより高い`symbolrank`区分に移動する） → 実装時（tasks.md）に、`pipeline/preprocess/run.sh`実行後の実データで期待値を再計算し更新する。
- [Trade-off] その他の接合部の`symbol-sort-key`固定値を`9`から`10`に変更するため、その他の接合部同士のラベル衝突優先順位の相対関係自体は変わらないが、数値そのものが変わる（振る舞いへの影響はない、add-ic-sic-symbolrank design.md 決定6と同種のtrade-off）。

## Migration Plan

1. `pipeline/preprocess/filter_points.py`の`load_line_geometries`が返すタプルに`route_category`を追加し、`route_category_candidates`（`[(geom, route_category), ...]`）を構築する。
2. `connected_route_categories(point_geom, route_category_candidates)`と、判定関数（`{"5", "6"}`の空でない部分集合か）を追加する。
3. JCT・IC・SICそれぞれのsymbolrank算出後に、上記判定に基づく`symbolrank += 1`の補正を適用する（決定1）。IC・SICは`assign_ic_sic_symbolranks`によるグループ内四分位算出が完了した後に適用する。
4. `JCT_SYMBOLRANK_MINZOOM`・`IC_SIC_SYMBOLRANK_MINZOOM`に、それぞれ`4: 11`・`6: 13`を追加する（決定3）。
5. `pipeline/preprocess/run.sh`を実行し、`points.current.geojson`が期待通り生成されることを確認する。
6. `pipeline/preprocess/verify_counts.py`のsymbolrank別件数期待値・minzoom整合性検証を、実データに基づき更新する。
7. `./pipeline/build.sh`を実行し、`site/tiles/points.pmtiles`を再生成・配置する。
8. `pipeline/tilegen/verify_tiles.py`のズーム別収録件数期待値・symbolrank範囲を、実データに基づき更新する。
9. `site/style/map-style.js`の`point-labels`レイヤーの`symbol-sort-key`のその他の接合部固定値を`9`から`10`に変更する（決定4）。
10. `npx serve site`でローカル動作確認（指定都市高速道路・その他にのみ連結するJCT・IC・SICが1段階高いズームから表示されること、広域路線に接続する結合部の表示に変化がないこと、JCTが常に最優先のままであることを含む）を行う。
11. `main`への`site/**`・`pipeline/**`変更pushで、`site/**`分は既存のGitHub Actionsが自動デプロイする。タイル（`site/tiles/points.pmtiles`）の再生成・配置はビルドスクリプト実行が必要なため、手動での配置確認も行う。
