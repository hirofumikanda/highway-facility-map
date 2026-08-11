## Why

現在、路線番号（`route_number`）は法定路線名がWikipedia「高速自動車国道」ページの一覧表と1対1で一致する場合のみ付与されており、高速自動車国道（`route_category`が`1`）の一部路線（14件）に限られている。地域高規格道路や指定都市高速道路など、実際には国土交通省の公式な高速道路ナンバリングで路線番号が付与されている多くの路線に、地図上で路線番号が表示されていない。国土交通省の公式ナンバリング一覧を出典とすることで、より多くの路線に路線番号を付与し、地図の視認性・案内性を高める。

## What Changes

- 路線番号の対応表の出典を、Wikipedia「高速自動車国道」ページから国土交通省「高速道路ナンバリング一覧」（`https://www.mlit.go.jp/road/sign/numbering/list/index.html` 等の公式資料）に変更・拡充する。
- 対応表は、1つの路線番号に複数の法定路線名（区間）が対応する場合（例：`唐桑道路`・`唐桑高田道路`が共に`E45`）、それらをまとめて同じ`route_number`を付与できるようにする（多対1のマッピングを許容）。
- 付与対象を、国土交通省の公式ナンバリングが実際に付与している路線種別区分（`route_category`が`1`〜`5`：高速自動車国道、並行する自専道、一般国道の自専道、本州四国連絡高速道路、指定都市高速道路）まで拡大する（`6`＝その他は対象外のまま）。
- `route_number`の付与は`common_name`の有無から独立させる（`common_name`がない路線にも`route_number`のみを付与できるようにする）。
- 地図上の路線ラベルとは別に、路線番号をラインに沿って一定間隔で表示するシンボルレイヤーを追加する。スタイルは矩形の緑背景に白字とし、路線本体の配色（緑系統のケーシング＋塗り）と混同しないよう差別化する。
- 路線クリック時のポップアップの路線番号表示条件を、「`common_name`が存在する場合のみ」から「`route_number`が存在する場合は常に表示」に変更する。

## Capabilities

### Modified Capabilities
- `highway-tile-pipeline`: 路線番号の対応表の出典・対象範囲（`route_category`1〜5、多対1マッピング）を国土交通省ナンバリング一覧に変更する。
- `highway-map-viewer`: 路線番号をラインに沿って一定間隔で表示するスタイルを追加し、路線クリック時ポップアップの路線番号表示条件を変更する。

## Impact

- `pipeline/preprocess/route_common_names.py`: 対応表データを国土交通省ナンバリング一覧に基づき再構築（大幅に拡充）。
- `pipeline/preprocess/filter_lines.py`: `route_number`付与ロジックを`common_name`の有無から独立させ、対象`route_category`を拡大。
- `pipeline/preprocess/verify_counts.py`: 新しい対応表・付与件数に応じた検証項目の更新。
- `pipeline/output/lines.current.geojson`、`site/tiles/lines.pmtiles`: 再生成が必要。
- `site/style/map-style.js`: 路線番号バッジ用のシンボルレイヤーを追加。
- `site/main.js`: 路線ポップアップの路線番号表示条件を変更。
