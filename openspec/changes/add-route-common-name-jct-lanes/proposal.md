## Why

現状、地図上の路線名・ポップアップの路線名は国土数値情報の法定路線名（例：「第一東海
自動車道」「北海道縦貫自動車道函館名寄線」）をそのまま表示しており、利用者が日常的に
使う通称名（例：「東名高速道路」「道央自動車道」）や、高速道路ナンバリング（例：E1）が
わからない。Wikipedia「高速自動車国道」ページを参考に、路線に通称名・路線番号を付与し、
地図上は通称名を主表示とすることで視認性・実用性を高める。

また、JCT（複数路線が交差する地点）の接続路線車線数（`lane_counts`）は現在、値を
重複排除してから昇順ソートしているため、車線数4の路線が2本交差するJCTでも
`lane_counts`は`[4]`となり、実際に何本の路線が接続しているかがわからない。重複を
排除せず、接続する路線の数だけ値を保持する（`[4, 4]`）よう修正する。

## What Changes

- 国土数値情報の法定路線名（`route_name`）から、Wikipedia「高速自動車国道」ページの
  一覧表（高速道路ナンバリング・通称名・政令による路線名）を参照して、通称名
  （`common_name`）・路線番号（`route_number`、例：E1）を引く静的な対応表を新設し、
  路線用GeoJSON（`lines.current.geojson`）の属性として付与する。
  - 対応表は、法定路線名が単一の通称名に一意に対応する路線のみを対象とする
    （ユーザー確認済み）。1つの法定路線名が複数の通称名区間に分かれる路線
    （例：「北海道横断自動車道黒松内釧路線」→札樽/後志/道東自動車道等）は、
    区間ごとの地物判別が困難なため対象外とし、`common_name`・`route_number`は
    付与しない（従来通り法定路線名のみを保持）。
  - Wikipediaのページは「高速自動車国道」（`route_category`が`1`の路線）のみを
    対象としており、指定都市高速道路・本州四国連絡高速道路等（`route_category`が
    `2`〜`6`）の路線は対応表の対象外（`common_name`・`route_number`は付与しない）。
- 地図上の路線ラベル（ライン沿いのテキスト）は、`common_name`が存在する路線では
  通称名を表示し、存在しない路線では従来通り法定路線名（`route_name`）を表示する。
- 路線クリック時のポップアップも、名称表示は同様に`common_name`優先とし、
  `common_name`が存在する場合は路線番号もあわせて表示する。
- タイル生成パイプラインの前処理で、JCT等の地点に接続する路線の車線数
  （`lane_counts`）について、重複排除をやめ、接続する路線地物の数だけ値を保持する
  よう変更する（昇順ソートは維持）。車線数4の路線が2本交差するJCTでは
  `lane_counts`が`[4, 4]`になる（ユーザー確認済み）。

## Capabilities

### New Capabilities

(none)

### Modified Capabilities

- `highway-tile-pipeline`: 路線属性への通称名（`common_name`）・路線番号
  （`route_number`）の付与、地点属性`lane_counts`の重複排除の廃止（接続路線数分の
  値を保持）を requirement として追加・変更する。
- `highway-map-viewer`: 路線名ラベル・路線ポップアップでの通称名優先表示を
  requirement として追加・変更する。

## Impact

- `pipeline/preprocess/`: 法定路線名→通称名・路線番号の静的対応表を新設し、
  `filter_lines.py`で参照して`common_name`・`route_number`属性を付与する。
- `pipeline/preprocess/verify_counts.py`: 新属性（`common_name`・`route_number`）の
  付与件数、および`lane_counts`の重複排除廃止に伴う検証内容の更新。
- `site/style/map-style.js`: `route-labels`レイヤーの`text-field`を
  `common_name`優先（存在しない場合は`route_name`）に変更。
- `site/main.js`: 路線ポップアップの名称表示を`common_name`優先に変更し、存在する
  場合は路線番号を追加表示。
- 既存PMTiles（`site/tiles/lines.pmtiles`・`points.pmtiles`）の再生成が必要
  （`pipeline/build.sh`の再実行）。
