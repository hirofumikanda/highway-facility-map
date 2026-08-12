## Why

現状、`common_name`（通称名）・`route_number`（路線番号）は法定路線名（`N06_007`）の文字列を静的対応表と照合してのみ解決している。このため、法定路線名が複数の通称名区間に分かれる路線（例：`北海道横断自動車道黒松内釧路線`）や、対応表に法定路線名が存在しない路線は、通称名・路線番号のいずれも一切付与されない。路線地物が接続する始点・終点の接合部（IC・JCT等の地点名）を手がかりにすれば、これらの未マッチ路線の一部を追加で解決できる。あわせて、路線ポップアップの表示形式を整理し、法定名・通称名を常に区別して表示できるようにする。

## What Changes

- `filter_lines.py`に、各路線地物の始点・終点座標を接合部（`N06-25_Joint.geojson`の現況地物）と空間照合し、`start_point_name`・`end_point_name`属性として付与する処理を追加する。
- 法定路線名による既存の`ROUTE_COMMON_NAMES`照合で`common_name`が付与されなかった路線について、法定路線名＋始点・終点接合部名をキーとした新しい静的対応表で追加照合し、ヒットした場合に`common_name`を付与する（`route_category`が`1`の路線のみを対象とする既存の制約は維持する）。
- 法定路線名による既存の`ROUTE_NUMBERS`照合で`route_number`が付与されなかった路線について、（既存表または上記の接合部照合で）解決済みの`common_name`をキーとした新しい静的対応表で追加照合し、ヒットした場合に`route_number`を付与する（`route_category`が`1`〜`5`の路線のみを対象とする既存の制約は維持する）。
- 路線クリック時のポップアップを、`法定名`・`通称名`・`種別`・`車線数`をラベル付きで表示する形式に変更する。`通称名`は`common_name`が存在する場合のみ表示する。既存の`路線番号`表示（`route_number`が存在する場合のみ表示）は維持する。

## Capabilities

### New Capabilities

(なし)

### Modified Capabilities

- `highway-tile-pipeline`: 路線地物への始点・終点接合部名の付与、および通称名・路線番号の解決に、接合部名・通称名を手がかりとした追加の照合経路を導入する。
- `highway-map-viewer`: 路線クリック時のポップアップ表示形式を、法定名・通称名を分けてラベル付きで表示する形式に変更する。

## Impact

- `pipeline/preprocess/filter_lines.py`: 接合部との空間照合処理、および追加の通称名・路線番号解決ロジックを追加。
- `pipeline/preprocess/filter_points.py`: 接合部データの読み込み・空間照合ロジックを`filter_lines.py`と共有する場合は共通化を検討（設計判断はdesign.mdで扱う）。
- `pipeline/preprocess/`配下に、接合部名を手がかりとした通称名対応表、および通称名を手がかりとした路線番号対応表を新設。
- `site/main.js`: 路線ポップアップのDOM構築ロジックを変更。
- `pipeline/output/lines.current.geojson`・タイル生成物・`openspec/specs/highway-tile-pipeline/spec.md`・`openspec/specs/highway-map-viewer/spec.md`。
