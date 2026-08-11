## Context

`pipeline/preprocess/filter_points.py`は現在、地点種別（`point_type`／`N06_019`）ごとに
固定の`POINT_TYPE_MINZOOM`（ジャンクション=8、一般IC=10、スマートIC=12、
その他=14）を地物ごとの`tippecanoe.minzoom`として付与している（[[main spec]]
`highway-tile-pipeline`の「地点データの重要度に基づくズーム選別」要件）。
同ファイルは既に、各地点に空間的に接続する路線地物を頂点一致判定
（`CONNECTION_DISTANCE_THRESHOLD_DEGREES`）で特定し、車線数（`lane_count`）を
重複排除せずに`lane_counts`属性へ格納している（`connected_lane_counts`
関数）。この`lane_counts`の算出ロジック・重複排除しない仕様自体は、既存の
「接合部ポイントへの接続路線車線数の付与」要件で明確に固定されており、本変更
では変更しない。

`site/style/map-style.js`の`point-labels`レイヤーは`symbol-sort-key`を持たず、
衝突時の優先順位はMapLibreの既定動作（`text-allow-overlap: false`のみ）に
委ねられている。`points`（地点マーカー本体）は`circle`タイプのレイヤーであり、
MapLibreの`circle`レイヤーには衝突検出・優先順位付けの仕組みが存在しない
（`symbol`レイヤーのみが対象）。

実データ（`geojson/N06-25_Joint.geojson`・`geojson/N06-25_HighwaySection.geojson`
から`pipeline/preprocess/filter_lines.py`・`filter_points.py`相当のロジックで
算出）で245件のJCTの`lane_counts`合計値を分析した結果、1〜24の範囲に分布し、
合計値`7`以下／`8`〜`11`／`12`以上で区切るとほぼ均等な3群（73／93／79件）に
分かれることを確認済み（ユーザー確認済み）。

## Goals / Non-Goals

**Goals:**
- JCT（`point_type`が`3`）に限り、接続する路線の車線数合計（`lane_counts`の
  合計値）に基づく`symbolrank`（`1`〜`3`、値が小さいほど上位）を新設する。
- JCTのタイル収録ズームを、`symbolrank`に応じて`minzoom` 8／9／10 の3段階に
  分ける（現行は全JCT一律`minzoom=8`）。
- 地点名ラベルの衝突判定に`symbolrank`（JCT）を組み込み、重なる場合は値の
  小さいJCTラベルを優先表示する。既存の地点種別間の優先順位
  （JCT＞一般IC＞スマートIC＞その他）は維持する。

**Non-Goals:**
- `lane_counts`属性自体の算出ロジック・重複排除しない仕様の変更（既存要件を
  変更しない）。
- JCT以外の地点種別への`symbolrank`付与（本変更はJCT限定）。
- `points`（地点マーカー本体、`circle`レイヤー）への衝突検出・優先順位付けの
  導入。MapLibreの`circle`レイヤーは衝突検出の仕組みを持たないため、マーカー
  自体（円）は重なっていても常に描画される。地点をアイコン（`symbol`）表現に
  変更してマーカー自体の重複回避を実現することは、本変更の範囲を超える大きな
  表現変更になるため対象外とする（想定と異なる場合は別変更で対応する）。
- `symbolrank`算出閾値（`7`／`11`）の動的な再計算（分位点の自動算出等）。
  固定値として実装し、データセットが将来大きく変わった場合は別途見直す。

## Decisions

### 決定1: `symbolrank`は接続路線の車線数合計（`lane_counts`の合計値）から算出し、JCT限定で付与する
`filter_points.py`内で、既存の`connected_lane_counts()`が返す`lane_counts`
配列の合計値を求め、閾値判定で`symbolrank`（`1`〜`3`）を算出する。JCT以外の
`point_type`の地物には`symbolrank`属性自体を付与しない（プロパティを省略）。

代替案として検討したが不採用:
- **接続する路線の数（重複排除した路線名の件数）を基準にする**: 実データでは
  自然に1〜3件へ収まり閾値判定が不要になる利点があったが、要件確認の結果
  「車線数の合計値」を基準とすることが正しい意図であることが判明したため
  不採用（当初の提案文言の誤記を修正）。

### 決定2: `symbolrank`の閾値は実データ分析に基づく固定値（合計`12`以上→1、`8`〜`11`→2、`7`以下→3）を使用する
245件のJCTの`lane_counts`合計値の分布を実データで分析し、件数がほぼ均等な
3群（73／93／79件）に分かれる閾値（`7`／`11`）を採用する（ユーザー確認済み）。
`filter_points.py`内の定数として固定値で持たせ、ビルド時に分布から動的に
算出することはしない（Non-Goals参照）。

代替案として検討したが不採用:
- **キリのよい閾値（`8`／`12`）を使う**: 境界値は覚えやすいが、群のサイズが
  不均等になる（133／64／48件）。ユーザーが均等3分割案を選択したため不採用。

### 決定3: JCTの`minzoom`を`symbolrank`から導出する
既存の`POINT_TYPE_MINZOOM["3"] = 8`（全JCT一律）を廃止し、JCTについては
`symbolrank`から`minzoom`を導出するマッピング（`symbolrank`が`1`なら`8`、
`2`なら`9`、`3`なら`10`）を用いて地物ごとの`tippecanoe.minzoom`を決定する。
JCT以外の地点種別（一般IC=10、スマートIC=12、その他=14）の`minzoom`は変更
しない。

`minzoom`方式（一度設定したズーム以上では常に収録される）により、既存要件
「あるズームレベルで収録される地点種別の集合は、それより低いズームレベルで
収録される集合を包含しなければならない」は、JCT内の`symbolrank`段階間でも
自動的に満たされる（`symbolrank=1`のJCTは`z8`以上、`symbolrank=2`のJCTは
それに加えて`z9`以上で収録され、`z9`の収録集合は`z8`の収録集合を包含する）。

### 決定4: 地点名ラベルの衝突優先順位に`symbol-sort-key`を追加する
`site/style/map-style.js`の`point-labels`レイヤーに`symbol-sort-key`を追加
する。値は地点種別と`symbolrank`を組み合わせた式とし、JCTは`symbolrank`
（`1`〜`3`）をそのまま使用し、一般IC・スマートIC・その他には、既存の種別間
優先順位（JCT＞一般IC＞スマートIC＞その他）を保つ固定値（例：`4`・`5`・`6`）
を割り当てる。MapLibreの`symbol-sort-key`は値が小さいほど配置優先度が高い
仕様であり、「値が小さいほうが上位」という要件と自然に一致する。

代替案として検討したが不採用:
- **`symbolrank`のみをsort-keyにし、非JCTにはsort-keyを設定しない
  （未設定時のデフォルト動作に委ねる）**: `symbol-sort-key`未設定の地物は
  データ順という不定な優先順位になり、既存要件（地点種別間の重要度順）を
  `symbol-sort-key`導入後も保証できなくなるため、全地点種別に明示的な値を
  割り当てる方式を採用する。

## Risks / Trade-offs

- [Risk] 固定閾値（`12`／`8`〜`11`／`7`以下）は現在のデータセット（245件の
  JCT）の分布に基づく静的な値であり、将来データ更新で地物構成が大きく変わる
  と群のバランスが崩れる可能性がある → タイル生成時の検証（`verify_counts.py`
  等）で各ランクの件数を出力し、大きな偏りが生じた場合は閾値の見直しを検討
  する運用でカバーする。
- [Trade-off] `symbol-sort-key`導入に伴い、JCT以外の地点種別にも固定の優先
  順位値を明示的に割り当てる必要がある → 将来、他の地点種別にも`symbolrank`
  相当の細分化を追加する場合は、このマッピングの見直しが必要になる。
  実機確認（Issue #85）で、一般IC・スマートICのラベル表示・重なり回避が
  従来通り動作することを確認した。
- [Risk] `points`（地点マーカー本体）は`circle`レイヤーのままのため、密集
  地域ではマーカー（円）自体が重なって表示され続ける（ラベルの重複回避のみ
  では解決しない）→ Non-Goalsとして許容し、必要であれば別変更でアイコン
  （`symbol`）化を検討する。

実機確認（Issue #85）で、決定1〜4がいずれも意図通り動作することを確認した。
`npx serve site`でブラウザ表示を確認し、以下を確認済み：
- ズームレベル8では`symbolrank=1`のジャンクション（例：更埴JCT、栃木都賀JCT）
  のみラベル表示され、9でsymbolrank=2（例：高崎JCT、川口JCT）、10で
  symbolrank=3を含む全ジャンクションが段階的に追加表示される
- 実際に629m離れた京橋JCT（symbolrank=2）・西銀座JCT（symbolrank=3）の
  ペアで、ズームレベル11〜12（両ラベルが衝突する範囲）では京橋JCTのラベルの
  みが表示され、ズームレベル13以降（衝突しない範囲）では両方のラベルが
  表示されることを確認した
- 一般IC・スマートICのラベル表示・重なり回避の既存挙動に変化がない

## Migration Plan

1. `pipeline/preprocess/filter_points.py`に、JCT向けの`symbolrank`算出ロジック
   （`lane_counts`合計値からの閾値判定）を追加する。
2. 同ファイルの`POINT_TYPE_MINZOOM`の扱いを変更し、JCTは`symbolrank`から
   導出した`minzoom`（8／9／10）を使用するようにする。
3. `pipeline/preprocess/verify_counts.py`に、`symbolrank`のランク別件数の
   検証を追加する。
4. `pipeline/preprocess/run.sh`を実行し、`symbolrank`が期待通り算出される
   ことを確認する。
5. `pipeline/tilegen/verify_tiles.py`に、JCTの`symbolrank`別ズーム収録
   （`z8`は`symbolrank=1`のJCTのみ、`z9`は`symbolrank`が`1`・`2`のJCT、
   `z10`以降は全JCT）の検証を追加する。
6. `./pipeline/build.sh`を実行し、`site/tiles/points.pmtiles`を再生成・配置
   する。
7. `site/style/map-style.js`の`point-labels`レイヤーに`symbol-sort-key`を
   追加する。
8. `npx serve site`でローカル動作確認（`symbolrank`別のJCT表示開始ズーム、
   ラベル重複時に`symbolrank`が小さいJCTが優先表示されること、他の地点種別
   の表示順が変わらないことを含む）を行う。
9. `main`への`site/**`・`pipeline/**`変更pushで、`site/**`分は既存の
   GitHub Actionsが自動デプロイする（ロールバックは直前コミットへのrevertで
   対応）。タイル（`site/tiles/points.pmtiles`）の再生成・配置はビルド
   スクリプト実行が必要なため、手動での配置確認も行う。
