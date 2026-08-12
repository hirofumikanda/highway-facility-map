## Context

`filter_lines.py`は現在、法定路線名（`N06_007`）を`ROUTE_COMMON_NAMES`（Wikipedia出典・14件・`route_category`が`1`かつ1対1一致のみ）、`ROUTE_NUMBERS`（国土交通省ナンバリング一覧＋指定都市高速道路の路線名埋め込み番号、`route_category`が`1`〜`5`）の2つの独立した静的対応表と照合するだけで、`common_name`・`route_number`を解決している。ヒットしない場合、両属性とも一切付与しない。

現況路線1,289地物のうち、`route_category`が`1`で`common_name`が未解決の地物は496件（33法定路線名）、`route_category`が`1`〜`5`で`route_number`が未解決の地物は787件（216法定路線名）ある（2026-08-12時点集計）。

`filter_points.py`は既に、地点座標と路線ジオメトリの頂点一致判定（`CONNECTION_DISTANCE_THRESHOLD_DEGREES = 1e-6`度）により、地点に接続する路線の車線数を求めるロジックを持つ。本変更は同じ頂点一致判定の考え方を逆方向（路線→地点）に適用する。

## Goals / Non-Goals

**Goals:**
- 各路線地物に、始点・終点座標に空間的に一致する接合部の地点名を`start_point_name`・`end_point_name`属性として付与する。
- 法定路線名による既存の`common_name`解決でヒットしなかった路線について、法定路線名＋始点・終点接合部名を鍵とする新しい静的対応表で追加解決する。
- 法定路線名による既存の`route_number`解決でヒットしなかった路線について、（既存表または上記で）解決済みの`common_name`を鍵とする新しい静的対応表で追加解決する。
- 路線ポップアップを、法定名・通称名を区別して常時ラベル付き表示する形式に変更する。

**Non-Goals:**
- 未解決496件／787件の全件について、今回の変更で対応表を完全に整備しきること。新しい対応表は既存の対応表と同様に手動で出典を確認しながら整備する静的表とし、今回確認できた範囲のみを収録する。残りは将来の変更で拡充する（`route_numbers.py`の既存方針を踏襲）。
- 対応表の自動生成・自動更新の仕組み。
- 接合部の名寄せ（表記ゆれの吸収）や、接合部データ自体の品質改善。

## Decisions

### 決定1: 空間一致判定ロジックの共通化
`filter_points.py`が持つ頂点一致判定（`CONNECTION_DISTANCE_THRESHOLD_DEGREES`と、Shapelyジオメトリによる距離判定）を`pipeline/preprocess/spatial_match.py`に切り出し、`filter_lines.py`（路線の始点・終点→接合部名の解決）と`filter_points.py`（地点→接続路線の車線数の解決）の両方から利用する。同一の距離閾値・判定方法を2箇所に重複実装しない。

**代替案**: `filter_lines.py`内に別途同等ロジックを実装する。→ 閾値や判定方法が将来ズレるリスクがあるため採用しない。

### 決定2: 始点・終点接合部プロパティの解決方法
路線地物のジオメトリ（LineString）の最初と最後の座標それぞれについて、決定1の判定ロジックで座標が一致する接合部地物を検索し、その`N06_018`（地点名）を`start_point_name`・`end_point_name`として付与する。

- 一致する接合部が存在しない場合、当該プロパティは付与しない（`common_name`・`route_number`と同様、存在しないことを示すのに`null`ではなくキー省略を用いる既存の規約に合わせる）。
- 同一座標に複数の接合部が一致する場合（データ上まれ）、既存の重要度順（ジャンクション＞一般IC＞スマートIC＞その他の接合部、`filter_points.py`の`POINT_TYPE_MINZOOM`と同じ順序）で最も重要度の高い接合部を採用する。

**代替案**: 複数一致時に地点名を配列で保持する。→ 後続の対応表照合の鍵が複雑になり、かつ実データ上の発生頻度が低いため採用しない。

### 決定3: 始点・終点接合部を用いた通称名の追加解決
新しい静的対応表`ROUTE_COMMON_NAMES_BY_ENDPOINTS`（法定路線名 → `{始点・終点接合部名の組, 通称名}`のリスト）を新設する。始点・終点接合部名の組は、地物の走査方向に依存しないよう順序を問わない組として保持・照合する。

適用条件（`ROUTE_COMMON_NAMES`による既存の解決方法とは独立に評価し、以下すべてを満たす場合のみ）:
- `route_category`が`1`（既存の`common_name`付与条件を維持）
- 法定路線名による`ROUTE_COMMON_NAMES`照合でヒットしなかった
- `start_point_name`・`end_point_name`の両方が付与されている
- `(法定路線名, {start_point_name, end_point_name})`が`ROUTE_COMMON_NAMES_BY_ENDPOINTS`に存在する

この対応表は、法定路線名が複数の通称名区間に分かれるため`ROUTE_COMMON_NAMES`から除外されている路線（例：`北海道横断自動車道黒松内釧路線`）について、各区間の境界接合部（Wikipedia等の出典で確認できるもの）を鍵として個別に解決する用途を主眼とする。

### 決定4: 通称名を用いた路線番号の追加解決
新しい静的対応表`ROUTE_NUMBERS_BY_COMMON_NAME`（通称名 → 路線番号）を新設する。

適用条件（`ROUTE_NUMBERS`による既存の解決方法とは独立に評価し、以下すべてを満たす場合のみ）:
- `route_category`が`1`〜`5`のいずれか（既存の`route_number`付与条件を維持）
- 法定路線名による`ROUTE_NUMBERS`照合でヒットしなかった
- `common_name`が（`ROUTE_COMMON_NAMES`または決定3の追加解決のいずれかにより）解決済みである
- 解決済みの`common_name`が`ROUTE_NUMBERS_BY_COMMON_NAME`に存在する

国土交通省の高速道路ナンバリング一覧は通称名（案内で使われている名称）ベースの表記が多いため、法定路線名では一致しなかったエントリの一部をこの経路で追加解決できる。

### 決定5: 始点・終点接合部プロパティのタイル出力への保持
`start_point_name`・`end_point_name`は対応表照合のための中間値ではなく、要求どおり路線地物の属性としてタイル出力にも保持する（既存の`route_name`・`route_category`・`lane_count`等と同様、`filter_lines.py`の出力プロパティに含め、tippecanoeの入力にそのまま渡す）。ポップアップでの表示は本変更のスコープに含めない（ユーザー確認済みのポップアップ項目は法定名・通称名・種別・車線数・路線番号のみ）。

### 決定6: ポップアップの表示形式
`site/main.js`の路線クリックハンドラを、以下の順でラベル付きテキストノードを生成するよう変更する。
1. `法定名: <route_name>`（常に表示）
2. `通称名: <common_name>`（`common_name`が存在する場合のみ表示）
3. `種別: <ROUTE_CATEGORY_LABELSによる人が読める種別名>`（常に表示）
4. `車線数: <lane_count>`（常に表示）
5. `路線番号: <route_number>`（`route_number`が存在する場合のみ表示。既存仕様を維持）

**代替案**: 名称欄を`common_name ?? route_name`の1行に集約する現行方式を維持しつつラベルだけ付与する。→ ユーザー確認により、法定名・通称名を常に区別して表示する方式を採用。

## Risks / Trade-offs

- [新設対応表のカバレッジが限定的（未解決496件／787件のうち一部のみ解決）] → Non-Goalsに明記し、将来の変更で拡充する前提とする。
- [同一座標に複数接合部が重なる場合の解決先が実態と異なる可能性] → 重要度順の決定的なタイブレークを採用し、挙動を予測可能にする（決定2）。
- [`lines.current.geojson`の属性増加によるタイルサイズの微増] → 属性2つ（文字列）の追加は無視できる規模と判断。
- [新設対応表のデータ誤り（境界接合部の誤認等）] → 既存表と同様、出典（Wikipedia個別路線記事等）をコード内コメントに明記し、後から検証可能にする。

## Migration Plan

- `pipeline/preprocess/run.sh`を再実行し、`lines.current.geojson`・`points.current.geojson`を再生成する。
- `pipeline/tilegen/build_lines.sh`等でPMTilesを再生成し、`site/tiles/`へ配置する。
- `site/main.js`の変更は静的ファイルの差し替えのみで反映される。ロールバックは変更前のPMTiles・`main.js`に戻すだけで可能。
