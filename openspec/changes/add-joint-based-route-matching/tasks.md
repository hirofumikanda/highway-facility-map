## 1. 空間一致判定ロジックの共通化（Issue: #91）

- [x] 1.1 `pipeline/preprocess/spatial_match.py`を新設し、`filter_points.py`が持つ座標一致判定ロジック（`CONNECTION_DISTANCE_THRESHOLD_DEGREES`とShapelyによる距離判定）を切り出す
- [x] 1.2 `filter_points.py`を、新設した共通ロジックを利用する形にリファクタリングする（既存の挙動・出力を変えない）

## 2. 路線への始点・終点接合部名の付与（Issue: #92）

- [x] 2.1 `filter_lines.py`で、`geojson/N06-25_Joint.geojson`の現況接合部地物（`N06_014`が`9999`）を読み込む
- [x] 2.2 各路線地物のジオメトリの始点・終点座標について、1.1の共通ロジックで一致する接合部を判定し、`start_point_name`・`end_point_name`（接合部の`N06_018`）を付与する（一致なしの場合はプロパティを付与しない）
- [x] 2.3 同一座標に複数の接合部が一致する場合、接合部種別の重要度順（ジャンクション＞一般IC＞スマートIC＞その他の接合部）で最も重要度の高い接合部を採用するタイブレークを実装する

## 3. 始点・終点接合部による通称名の追加解決（Issue: #93）

- [x] 3.1 `pipeline/preprocess/route_common_names_by_endpoints.py`を新設し、法定路線名→`{始点・終点接合部名の組（順不同）, 通称名}`のリストを保持する`ROUTE_COMMON_NAMES_BY_ENDPOINTS`を定義する
- [x] 3.2 法定路線名が複数の通称名区間に分かれるため`ROUTE_COMMON_NAMES`から除外されている法定路線名（`北海道横断自動車道黒松内釧路線`等）を対象に、Wikipedia等の出典で各区間の境界接合部を確認し、確認できた範囲でエントリを収録する（出典・確認日をコード内コメントに明記する。全件の網羅は本変更のスコープ外）
- [x] 3.3 `filter_lines.py`で、法定路線名による`ROUTE_COMMON_NAMES`照合がヒットせず、`route_category`が`1`であり、`start_point_name`・`end_point_name`が両方付与されている路線地物に対して、`ROUTE_COMMON_NAMES_BY_ENDPOINTS`との追加照合を行い、ヒットした場合に`common_name`を付与する

## 4. 通称名による路線番号の追加解決（Issue: #94）

- [x] 4.1 `pipeline/preprocess/route_numbers_by_common_name.py`を新設し、通称名→路線番号の対応表`ROUTE_NUMBERS_BY_COMMON_NAME`を定義する
- [x] 4.2 法定路線名による`ROUTE_NUMBERS`照合が未解決の法定路線名のうち、（3章までの解決により）`common_name`が付与されるものを対象に、国土交通省「高速道路ナンバリング一覧」を通称名ベースで突き合わせ、確認できた範囲でエントリを収録する（出典・確認日をコード内コメントに明記する。全件の網羅は本変更のスコープ外）
- [x] 4.3 `filter_lines.py`で、法定路線名による`ROUTE_NUMBERS`照合がヒットせず、`route_category`が`1`から`5`のいずれかであり、`common_name`が付与されている路線地物に対して、`ROUTE_NUMBERS_BY_COMMON_NAME`との追加照合を行い、ヒットした場合に`route_number`を付与する

## 5. 前処理パイプラインの検証（Issue: #95）

- [ ] 5.1 `pipeline/preprocess/verify_counts.py`を、`start_point_name`・`end_point_name`の付与件数、および追加解決された`common_name`・`route_number`の件数集計を検証できるよう更新する
- [ ] 5.2 `pipeline/preprocess/run.sh`を実行し、`lines.current.geojson`・`points.current.geojson`を再生成して検証が通ることを確認する

## 6. 路線ポップアップの表示形式変更（Issue: #96）

- [ ] 6.1 `site/main.js`の路線クリックハンドラを、`法定名`・`通称名`（存在時のみ）・`種別`・`車線数`をラベル付きで表示し、続けて既存の`路線番号`（存在時のみ）を表示する形式に変更する

## 7. タイル再生成と動作確認（Issue: #97）

- [ ] 7.1 `pipeline/tilegen/build_lines.sh`等でPMTilesを再生成し、`site/tiles/`へ配置する
- [ ] 7.2 ブラウザでサイトを開き、始点・終点接合部により追加解決された路線、および従来どおり法定路線名のみで解決される路線の双方でポップアップ表示（法定名・通称名・種別・車線数・路線番号）を確認する
