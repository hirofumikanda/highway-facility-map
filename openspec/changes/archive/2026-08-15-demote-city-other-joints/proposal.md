## Why

JCT・IC・SICのsymbolrank／minzoomは、接続する路線の重要度（車線数・周辺人口）のみに基づいて決定されており、接続先の路線種別区分（`route_category`）は考慮されていない。指定都市高速道路（`5`：首都高速・阪神高速等）や、その他（`6`）の路線にのみ連結する結合部は、高速自動車国道等の広域幹線（`route_category`が`1`〜`4`）に連結する結合部と比べて、全国規模の地図では相対的に重要度が低いと考えられるが、現状は同列に扱われ、低ズームから同じタイミングで表示されてしまう。

## What Changes

- JCT・IC・SICの結合部ポイントのうち、頂点一致判定で接続する路線地物の`route_category`が指定都市高速道路（`5`）またはその他（`6`）のみで構成される（`1`〜`4`のいずれにも接続しない）ものについて、既存ロジックで算出済みの`symbolrank`を1段階下位側（値を+1）に補正し、対応する`minzoom`を1段階引き上げる（優先度を一段下げる）。接続する路線が1件もない結合部（対象外、既存データで1件）は補正しない。
- JCT・その他の接合部（接合部種別`4`）のズーム選別・symbolrank付与ロジック自体は変更しない。その他の接合部（接合部種別`4`）は本変更の対象外のまま（`route_category`に関わらず補正しない）。
- 地点名ラベルの衝突判定（`symbol-sort-key`）は、上記の補正後`symbolrank`をそのまま用いる（既存の「JCT＞IC/SIC＞その他の接合部」という種別間の優先階層は維持する）。IC・SICの補正後symbolrankの最大値が既存の「その他の接合部」固定値と重複しないよう、`symbol-sort-key`の値域を再配置する（**BREAKING**: その他の接合部の`symbol-sort-key`固定値が変わる。振る舞いへの影響はない）。

## Capabilities

### New Capabilities

（なし）

### Modified Capabilities

- `highway-tile-pipeline`: 「地点データの重要度に基づくズーム選別」要件に、指定都市高速道路・その他にのみ連結するJCT・IC・SICのsymbolrank／minzoom補正を追加する。
- `highway-map-viewer`: 「地点名ラベルの重要度に応じた表示」要件に、上記補正後symbolrankを反映した表示・衝突優先順位の扱いを追加し、`symbol-sort-key`の値域再配置を反映する。

## Impact

- `pipeline/preprocess/filter_points.py`: JCT・IC・SICの接続路線の`route_category`判定ロジックと、それに基づくsymbolrank／minzoom補正ロジックを追加。
- `pipeline/preprocess/verify_counts.py`: 補正後のsymbolrank別件数期待値・minzoom整合性検証を更新。
- `pipeline/tilegen/verify_tiles.py`: ズーム別収録件数の期待値を更新。
- `site/style/map-style.js`: `point-labels`レイヤーの`symbol-sort-key`の値域（その他の接合部の固定値）を調整。
- 既存のJCTのsymbolrank算出（車線数合計ベース）・IC/SICのsymbolrank算出（周辺人口の路線内相対順位ベース）のロジック自体は変更しない。
