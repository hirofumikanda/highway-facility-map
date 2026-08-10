## Context

現行の`pipeline/preprocess/filter_lines.py`は、`N06-25_HighwaySection.geojson`の
`N06_007`（法定路線名）をそのまま`route_name`属性として保持している。法定路線名は
国土数値情報の元データにおいて路線の物理的な区間（整備時期・事業単位）ごとに
1,289件の地物へ分割されているが、値としては314種類の文字列（うち`route_category`
が`1`＝高速自動車国道の地物に限ると47種類）に集約される。

Wikipedia「高速自動車国道」ページの一覧表は、高速道路ナンバリング（例：E1）・
通称名（例：東名高速道路）・政令による路線名（法定路線名）の対応を示すが、法定
路線名47種類に対し通称名は64種類あり、両者は1対1ではない（例：法定路線名
「北海道横断自動車道黒松内釧路線」は、通称名「札樽自動車道」「後志自動車道」
「道東自動車道」の3区間に分かれる）。地物（ライン）側には区間を識別できる属性が
なく、どの地物がどの通称区間に属するかを法定路線名だけから判別することはできない
（ユーザー確認済み：区間分割の判別は行わず、1対1対応の路線のみを対象とする）。

`pipeline/preprocess/filter_points.py`の`connected_lane_counts`は、地点座標に
頂点一致判定で接続する路線の`lane_count`を`set`（集合）に集めてから昇順ソートして
おり、同じ車線数を持つ路線が複数接続していても1件に集約される。

## Goals / Non-Goals

**Goals:**
- 法定路線名が単一の通称名に一意に対応する路線（`route_category`が`1`の一部）に、
  通称名・路線番号を属性として付与する。
- 地図上のラベル・ポップアップで、通称名が存在する路線は通称名を優先表示する。
- JCT等の`lane_counts`について、重複排除をやめ、接続する路線地物の数だけ値を
  保持するようにする。

**Non-Goals:**
- 法定路線名が複数の通称名区間に分かれる路線（東北自動車道・北海道横断自動車道系統
  など）の区間ごとの通称名付与。地物の始点・終点座標や隣接IC名からの区間判定は、
  誤判定リスクと実装コストに対して本変更の目的（主要路線の視認性向上）に見合わない
  ため対象外とする。
- 指定都市高速道路・本州四国連絡高速道路等（`route_category`が`1`以外）への通称名
  付与（Wikipediaの当該ページの対象外のため）。
- 通称名・路線番号対応表の自動生成・自動更新の仕組み（今回は静的な対応表を手動で
  整備する）。

## Decisions

### 決定1: 通称名・路線番号は静的な対応表（Pythonの辞書リテラル）として前処理に持つ
`pipeline/preprocess/`配下に、法定路線名（`route_name`文字列）をキーとし、
`common_name`・`route_number`を値とする静的な対応表（例：
`route_common_names.py`の`ROUTE_COMMON_NAMES`辞書）を新設する。対応表は
Wikipedia「高速自動車国道」ページの一覧表を出典として手動で整備し、**法定路線名が
単一の通称名・路線番号の組に一意に対応するエントリのみ**を含める。1つの法定路線名
が複数の通称名区間に分かれる場合（対応表作成時にWikipediaの一覧表を法定路線名で
グルーピングし、複数行がヒットするケース）は、対応表に含めない。

対応表作成時は、Wikipediaの一覧表を法定路線名でグルーピングし、1行のみヒットする
エントリのみを採用する（実装タスクでWikipediaページから該当行を書き起こし、
グルーピング結果を目視確認する）。

代替案として検討したが不採用:
- **地理的区間判定による全路線マッピング**（Goals/Non-Goals参照）: 誤判定リスクと
  実装コストが大きく、Non-Goalとした。
- **`lines.current.geojson`生成後に別スクリプトで後付けする**: 対応表の参照ロジックが
  分散し、`verify_counts.py`との整合確認が煩雑になるため、`filter_lines.py`内で
  完結させる。

### 決定2: `filter_lines.py`は`route_name`をキーに対応表を引き、ヒットした場合のみ属性を追加する
`filter_lines.py`の各地物の`route_name`で`ROUTE_COMMON_NAMES`を引き、ヒットすれば
`common_name`・`route_number`をpropertiesに追加する。ヒットしない場合（対応表に
存在しない・対象外の`route_category`）は、両属性を追加しない（`None`を入れて
`null`にするのではなく、キー自体を省略する。MVTのタイルサイズ削減と、
site側での`["get", "common_name"]`が未設定時`null`を返す挙動に合わせるため）。

### 決定3: 地図上のラベル・ポップアップは`common_name`優先、フォールバックは`route_name`
`site/style/map-style.js`の`route-labels`レイヤーの`text-field`を
`["get", "route_name"]`から`["coalesce", ["get", "common_name"], ["get", "route_name"]]`
に変更する。MapLibreの`coalesce`式は、最初のオペランドが`null`/`undefined`の場合に
次のオペランドを評価するため、`common_name`が未設定の路線では従来通り
`route_name`が表示される。

`site/main.js`の路線ポップアップも同様に、名称表示要素の`textContent`を
`common_name ?? route_name`とする。`common_name`が存在する場合は、路線番号
（`route_number`）を表示する行を追加する（`common_name`が存在しない場合は
路線番号の行を表示しない）。

### 決定4: `lane_counts`は重複排除をやめ、接続する路線地物の数だけ値を保持する
`filter_points.py`の`connected_lane_counts`が`lane_count`を集める際のデータ構造を
`set`（集合）から`list`（リスト、重複を許容）に変更し、昇順ソートのみ行う。
車線数4の路線が2本接続するJCTでは`lane_counts`が`[4, 4]`になる（ユーザー確認済み）。
site側（`main.js`）は既に`lane_counts.join(", ")`で表示しており、重複値を含む配列を
渡してもそのまま「車線数: 4, 4」のように表示されるため、site側の変更は不要。

## Risks / Trade-offs

- [Risk] Wikipediaの一覧表からの対応表の書き起こしを誤ると、誤った通称名・路線番号を
  表示してしまう → 実装タスクで、対応表の各エントリをWikipediaページの記載と
  突き合わせて目視確認する。また`verify_counts.py`に、対応表エントリ数・
  `common_name`が付与された路線地物数を出力する検証を追加し、期待値と目視で
  比較できるようにする。
- [Trade-off] 法定路線名が複数の通称名区間に分かれる主要路線（東北自動車道等）には
  通称名が付かず、法定路線名のまま表示される → Non-Goalとして許容する。将来的に
  区間判定ロジックを追加する場合は別変更として扱う。
- [Risk] Wikipediaの一覧表は今後更新される可能性があり、対応表が静的なままだと
  実際の道路事情（新規開通・通称名変更等）と乖離しうる → 本変更のスコープ外とし、
  対応表の定期更新は将来の運用課題とする。

## Migration Plan

1. `pipeline/preprocess/route_common_names.py`（対応表）を新設する。
2. `pipeline/preprocess/filter_lines.py`を変更し、`common_name`・`route_number`を
   条件付きで付与する。
3. `pipeline/preprocess/filter_points.py`の`connected_lane_counts`を変更し、
   重複排除をやめる。
4. `pipeline/preprocess/verify_counts.py`に新属性の検証を追加する。
5. `pipeline/preprocess/run.sh`を実行し、新属性が期待通り付与されることを確認する。
6. `./pipeline/build.sh`を実行し、`site/tiles/lines.pmtiles`・`points.pmtiles`を
   再生成・配置する。
7. `site/style/map-style.js`（`route-labels`の`text-field`）・`site/main.js`
   （路線ポップアップの名称・路線番号表示）を変更する。
8. `npx serve site`でローカル動作確認（通称名表示、通称名なし路線のフォールバック、
   車線数が同じ複数路線が接続するJCTでの`lane_counts`重複表示）を行う。
9. `main`への`site/**`変更pushで既存のGitHub Actionsが自動デプロイ
   （ロールバックは直前コミットへのrevertで対応、追加の移行作業は不要）。
