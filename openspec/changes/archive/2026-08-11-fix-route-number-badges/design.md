## Context

`route-number-badges`レイヤー（`site/style/map-style.js`）は、`symbol-placement: "line"`
のSDFアイコン（`icon-text-fit: "both"`で`text-field`のバウンディングボックスに
追従）としてIssue #64（`add-mlit-route-numbering`）で実装済み（[[main spec]]
`highway-map-viewer`の「路線番号のライン沿い表示」要件）。SDF画像は全ピクセルを
最大値（255）にした一様矩形（8x8）で、`icon-color`固定色（`#0a5c34`）と組み合わせて
矩形バッジを表現している。

`route_category`が`5`（指定都市高速道路：首都高速・阪神高速・名古屋高速・
福岡高速・北九州高速・広島高速）の`route_number`は、MLITの高速道路ナンバリング
一覧（E/C系統）ではなく、法定路線名に埋め込まれた事業者独自の番号（`pipeline/preprocess/route_numbers.py`の決定1a）から抽出されており、値は`"1"`〜`"9"`
程度の桁数の少ない数字文字列になる（`route_category`が`1`〜`4`の`route_number`は
常に`E`または`C`で始まる）。

MapLibre GL JSのスタイル仕様では、`symbol-placement: "line"`のシンボルは
`icon-rotation-alignment`／`text-rotation-alignment`が`"map"`（`"auto"`時の
既定値）の場合、ライン区間の角度に追従して回転する。この既定値には、ラインの
向きに応じてバッジが傾いたり天地が逆になったりして読みにくくなる問題がある。
一方`"viewport"`を指定すると、ライン追従の回転が無効化され、シンボルは常に
ビューポート（画面）に対して正立する。

`hash: true`（`site/main.js`）により地図の回転（bearing）・傾き（pitch）はURL
ハッシュに同期されるが、ナビゲーションコントロールの「回転リセット」ボタンが
示すとおり既定は北が上（bearing 0）であり、地図自体を回転させるのは付随的な
操作である。

## Goals / Non-Goals

**Goals:**
- `route-number-badges`のバッジ回転をライン角度から切り離し、常にビューポートに
  対して正立させる。
- `route_number`が存在しない路線ではバッジ（アイコン・テキストとも）が一切
  描画されないことを、`filter`により明示的に保証する。
- `route_category`が`5`（MLITナンバリング一覧に由来しない路線番号）のバッジを、
  形状のみシールド形に変更する（配色は変更しない）。

**Non-Goals:**
- ユーザーが地図自体を回転（bearing操作）させた場合に、バッジを常に真北基準で
  正立させ続けること。MapLibreのスタイル仕様には、ライン沿い配置を維持したまま
  地図の回転量を打ち消す向きの表現がなく、実現には`rotate`イベント監視による
  命令的な再描画が必要になり、本変更の範囲を超える。本変更では、既定表示
  （bearing 0＝北が上）でバッジが常に正立すること、およびライン角度に追従して
  傾かないことを「北を上にする」の実装として扱う（想定と異なる場合は要修正）。
- バッジの矩形／シールドの形状比率を、実際の首都高速等の標識デザインに厳密に
  一致させること（緑背景×白字・番号のみを主眼とし、形状は「矩形ではない」こと
  が識別できれば足りる）。
- `route_numbers.py`の対応表内容や`route_category`の判定ロジック自体の変更。

## Decisions

### 決定1: バッジの回転を`icon-rotation-alignment`/`text-rotation-alignment: "viewport"`で無効化する
`route-number-badges`レイヤー（および決定3で分離する派生レイヤー）の
`layout`に`"icon-rotation-alignment": "viewport"`・`"text-rotation-alignment": "viewport"`
を追加する。`symbol-placement: "line"`によるライン沿いの配置（一定間隔での
アンカー位置決定）はそのまま維持しつつ、各アンカー位置でのアイコン・テキストの
回転はビューポート基準の正立に固定される。

代替案として検討したが不採用:
- **`icon-rotate`/`text-rotate`に固定値（0）を指定する**: `symbol-placement: "line"`
  では`rotation-alignment`が`"map"`（既定）の場合、回転はライン角度から自動計算
  され、`icon-rotate`/`text-rotate`はその上に加算される角度でしかないため、
  ライン追従そのものを打ち消せない。
- **`symbol-placement`を`"point"`に変更する**: ライン沿いへの一定間隔配置
  （`symbol-spacing`）ができなくなり、既存要件（路線に沿った複数箇所への表示）
  を満たせない。

### 決定2: `route-number-badges`系レイヤーに`route_number`存在の`filter`を追加する
現行実装は`text-field: ["get", "route_number"]`がnullを返すことでテキストが
非表示になる挙動に暗黙に依存しており、`icon-image`自体は`route_number`の有無に
かかわらず定数で参照され続ける。`layout.filter`ではなく、レイヤーの`filter`
プロパティに`["has", "route_number"]`（決定3の分岐後は`route_category`条件と
`"all"`で結合）を追加し、`route_number`を持たない地物はレイヤーの描画対象
（アイコン・テキストとも）から明示的に除外する。

代替案として検討したが不採用:
- **現状の`text-field`のnull依存のまま維持する**: `text-field`がnullのときに
  アイコンが描画されるかどうかはレンダラー・`icon-text-fit`実装の詳細に依存し、
  仕様として保証されない。実際にIssue #64のバグ（8x8化前は背景が描画されない
  問題）でもSDFのnull/エッジ挙動に起因する不具合が発生しており、暗黙の挙動には
  頼らない。

### 決定3: `route_category`に応じてレイヤーを矩形用・シールド用に分岐する
単一の`route-number-badges`レイヤーを、`filter`で`route_category`によって
描き分ける2レイヤーに分割する。`layout`（`symbol-placement`・`symbol-spacing`・
`text-field`・フォント・`text-size`等）と`paint`（`icon-color`・`text-color`）は
共通のまま、`icon-image`と`filter`のみを差し替える。

- `route-number-badges`（矩形、既存レイヤーIDを維持）: `filter`に
  `["all", ["has", "route_number"], ["!=", ["get", "route_category"], "5"]]`
  を設定し、既存の矩形SDF画像（`ROUTE_NUMBER_BADGE_IMAGE_ID`）を使用する。
- `route-number-badges-shield`（新規）: `filter`に
  `["all", ["has", "route_number"], ["==", ["get", "route_category"], "5"]]`
  を設定し、新規のシールド形SDF画像（`ROUTE_NUMBER_BADGE_SHIELD_IMAGE_ID`）を
  使用する。`route-number-badges`の直後（上）に配置する。

シールド形SDF画像は、既存の「全ピクセル255の一様画像」方式を拡張し、画像内に
シールド形状のマスク（上部は矩形、下部は中央に向けて先細りする五角形／盾形）を
描く。マスク内側のピクセルは255（完全に内側）、外側は0（完全に外側）とする
2値マスクとし、Issue #64での実機確認で判明したSDFサンプリングの制約
（極小解像度では縁が正しく評価されない）を踏まえ、既存の8x8より大きい解像度
（例：32x32）を用いる。`icon-text-fit: "both"`により、矩形と同様にテキスト
サイズへ自動追従してシールドが伸縮する。

代替案として検討したが不採用:
- **`route_category`を式（`match`/`case`）で`icon-image`に渡し、1レイヤーのまま
  形状を出し分ける**: `icon-image`をdata-drivenにすること自体は可能だが、
  `filter`による除外（決定2）と組み合わせる場合、結局`route_category`条件を
  `icon-image`式と`filter`式の両方に書くことになり、レイヤー分割より複雑になる。
  レイヤー分割の方が、矩形／シールドそれぞれの意図が`filter`から一目で読み取れる。
- **シールド画像を外部の静的画像アセット（PNG）として用意する**: 既存の矩形
  バッジも実行時生成のSDF画像であり、ビルド不要・アセット管理不要という既存の
  方針（決定3のSDFアプローチ）と一貫させる。

## Risks / Trade-offs

- [Risk] `"viewport"`回転整列は、地図自体が回転（bearing≠0）した状態では、
  バッジは画面に対して正立し続けるが、地図上の真北方向とは一致しなくなる
  （Non-Goals参照）→ 既定表示（bearing 0）でのみ「北が上」を意味することを
  design.md・実装コメントに明記し、想定外なら別変更で対応する。
  実機確認（Issue #76、既定のbearing 0）では、カーブしたライン（山陽自動車道
  E2）・斜めのライン（首都高速）のいずれでもバッジが画面に対して正立して
  表示されることを確認した。
- [Risk] シールド形SDF画像（2値マスク）が、`icon-text-fit`によるテキスト
  バウンディングボックスへの非一様な伸縮で、意図した盾形から視覚的に歪む
  可能性がある（`route_category`5の番号は1〜2桁と桁数が少なく、比較的正方形に
  近いテキストボックスになる想定）→ 実装時にブラウザでの目視確認
  （タスクに含める）で許容範囲か確認する。
  実機確認（Issue #76）で、広島高速・首都高速（例：番号1、6）のシールド形
  バッジが、上部矩形・下部先細りの意図した形状で視覚的な歪みなく表示される
  ことを確認した。背景色は矩形バッジ（E2）と同じ濃い緑であることも確認した。
- [Trade-off] レイヤーを2分割することで、`route-labels`との重なり回避の衝突
  判定グループが増える（矩形レイヤー・シールドレイヤーそれぞれが独立した
  シンボルレイヤーになる）→ 両レイヤーとも`icon-allow-overlap`/
  `text-allow-overlap`を既存同様`false`のまま維持し、`route-labels`の後（上）に
  連続して配置することで、実質的な衝突回避の優先順位は変えない。

## Migration Plan

1. `site/style/map-style.js`の`route-number-badges`レイヤーに
   `icon-rotation-alignment`/`text-rotation-alignment: "viewport"`を追加する。
2. 同レイヤーに`filter: ["has", "route_number"]`を追加する。
3. シールド形SDF画像生成関数（`registerRouteNumberBadgeShieldImage`等）を追加し、
   `route-number-badges`レイヤーの`filter`を`route_category`5を除外する条件に
   変更、`route-number-badges-shield`レイヤーを新設する。
4. `site/main.js`で新規のシールド画像登録関数を`map.on("load", ...)`内で呼び出す。
5. `npx serve site`でローカル動作確認（バッジがライン角度によらず正立すること、
   `route_number`のない路線でバッジが表示されないこと、`route_category`5の路線
   でシールド形バッジが表示され矩形レイヤーとは重複表示されないこと、矩形の
   路線（`route_category`1〜4）は従来通り矩形で表示されることを含む）を行う。
6. `main`への`site/**`変更pushで既存のGitHub Actionsが自動デプロイ
   （ロールバックは直前コミットへのrevertで対応）。
