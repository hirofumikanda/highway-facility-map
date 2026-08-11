## Context

現行の`route_number`は、`pipeline/preprocess/route_common_names.py`の
`ROUTE_COMMON_NAMES`辞書（法定路線名→`common_name`・`route_number`、
Wikipedia出典、`route_category`が`1`かつ1対1一致のみ、14件）でのみ解決されて
いる。`filter_lines.py`はこの辞書を1回引くだけで、ヒットしなければ両属性とも
付与しない。

国土交通省「高速道路ナンバリング一覧」（`https://www.mlit.go.jp/road/sign/numbering/list/index.html`
ほか関連ページ）は、路線番号（E1、E1A、C2等）ごとに、現地の案内で使われている
路線名を列挙する形式（「路線番号 | 路線名（複数可）」）で公開されている。実地
調査の結果、1つの路線番号に対して複数の案内路線名が対応するケース（例：
`E6`は「常磐自動車道、仙台東部道路、三陸沿岸道路（仙台港北～利府）、仙台北部
道路」）が多数あり、これらの案内路線名は`N06_007`の法定路線名と完全一致する
場合と、法定路線名がさらに細かい区間（`唐桑道路`・`唐桑高田道路`等）に分かれて
いる場合がある。また対象範囲も、高速自動車国道（`route_category`1）だけで
なく、一般国道の自専道（3、地域高規格道路の多く）・指定都市高速道路（5）にも
及ぶ（決定はユーザー確認済み：`route_category`1〜5を対象、`6`＝その他は除外）。

`common_name`（Wikipedia出典・1対1限定）とは出典・粒度・対象範囲が異なるため、
両属性の解決を独立させる（ユーザー確認済み）。

実装調査の結果、国土交通省の2016年「高速道路ナンバリング」（E1〜E98、C系統）は
指定都市高速道路（首都高速・阪神高速・名古屋高速・福岡高速・北九州高速・広島
高速、`route_category`が`5`）を対象外としていることが判明した。都市高速道路は
新ナンバリング制定以前から各事業者独自の路線番号体系を持っており、その番号は
法定路線名自体に「N号」として埋め込まれている（例：`阪神高速3号神戸線`の
「3号」、`首都高速1号羽田線`の「1号」）。そのため`route_category`が`5`の路線
番号は、E/Cナンバリング一覧ではなく、法定路線名に埋め込まれた番号から解決する
（ユーザー確認済み・決定1a）。

## Goals / Non-Goals

**Goals:**
- 国土交通省の高速道路ナンバリング一覧を出典として、`route_category`が`1`〜`5`
  の路線に`route_number`を付与できるようにする。1つの路線番号に複数の法定
  路線名が対応する場合はまとめて同一の`route_number`を付与する。
- `route_number`の付与を`common_name`の有無から独立させる。
- 路線番号をライン沿いに一定間隔で表示する、矩形の緑背景×白字のシンボルレイヤー
  を追加する。背景色は路線本体（ケーシング・塗り）の緑と混同しない配色にする。
- 路線ポップアップの路線番号表示条件を、`route_number`の有無のみを条件とする
  ように変更する。

**Non-Goals:**
- `common_name`（通称名）の対応表・付与条件の見直し（Wikipedia出典・
  `route_category`1・1対1限定のまま変更しない）。
- 法定路線名から地物単位（始点・終点）での区間判定によるナンバリング一覧上の
  区間境界（例：`E6`のうち「仙台港北～利府」）の厳密な再現。区間名の但し書きが
  ある場合も、対応する法定路線名の地物全体に同一の`route_number`を付与する
  （区間内でさらに細かく`route_number`を出し分けない）。
- ナンバリング対応表の自動生成・自動更新の仕組み（今回も静的な対応表を手動で
  整備する）。

## Decisions

### 決定1: 路線番号の対応表を新設し、`common_name`の対応表とは独立させる
`pipeline/preprocess/route_numbers.py`を新設し、法定路線名（`route_name`文字列）
をキー、`route_number`を値とする静的な対応表`ROUTE_NUMBERS`を持つ。
`route_category`が`1`〜`4`のエントリは国土交通省「高速道路ナンバリング一覧」
（E/Cナンバリング）を法定路線名単位まで突き合わせて書き起こす（1つの
`route_number`に複数の法定路線名キーが対応してよい＝多対1を許容）。
`route_category`が`5`（指定都市高速道路）のエントリは決定1aの方法で解決した
値を同じ辞書に含める。両者は出典が異なるが、`filter_lines.py`側の参照方法
（法定路線名でのキー検索）は共通のため、1つの辞書にまとめる（対応表ファイルを
分ける決定2とは異なり、こちらは参照インターフェースの単純さを優先する）。

既存の`route_common_names.py`（`ROUTE_COMMON_NAMES`、Wikipedia出典・
`common_name`＋`route_number`のペア）はそのまま残すが、`route_number`の
実際の付与判定には使わなくなる（`common_name`の付与判定にのみ引き続き使う）。

代替案として検討したが不採用:
- **`ROUTE_COMMON_NAMES`に`route_number`を上書き統合する**: 出典・対象
  `route_category`・多対1可否が異なる2つの対応表を1つの辞書に混在させると、
  どちらの出典に基づく値か読み手が判別しづらくなるため、ファイルを分離する。

### 決定1a: 指定都市高速道路（`route_category`が`5`）の路線番号は法定路線名から抽出する
国土交通省の高速道路ナンバリング一覧（E/C系統）は指定都市高速道路を対象と
していない（都市高速道路は新ナンバリング制定以前から独自の路線番号体系を
持つため、対象外とされている）。指定都市高速道路の法定路線名には、多くの
場合その事業者自身の路線番号が「N号」として埋め込まれている（例：
`阪神高速3号神戸線` → `3`、`首都高速1号羽田線` → `1`、
`名古屋高速1号楠線` → `1`）。`route_numbers.py`の対応表作成時に、
`route_category`が`5`の法定路線名から`N号`パターンの数字を抽出し、
`route_number`の値（例：`"3"`）として`ROUTE_NUMBERS`に加える。

「N号」パターンが法定路線名に含まれない路線（例：`首都高速中央環状線`、
`首都高速都心環状線`、`首都高速湾岸線`、`名古屋高速都心環状線`、
`大阪府道高速大和川線`等の環状線・特定区間名称）は、対応表に含めない
（`route_number`は付与しない）。これらの路線は独自の記号（`C1`等）を持つ
場合があるが、法定路線名から機械的に抽出できる情報ではなく、誤った番号を
機械的に補うリスクの方が大きいため、本対応表では対象外とする。

代替案として検討したが不採用:
- **`route_category`が`5`を対象外のままにする（Non-Goal）**: ユーザーが
  「全カテゴリへの付与」を要望しており、都市高速道路の路線番号は実際に現地の
  標識・案内図で使われているため、対象外にすると要望を満たせない。
- **各都市高速道路事業者の公式サイトのナンバリング表記をそのまま出典とする**:
  法定路線名に番号が一意に埋め込まれており、追加の出典突き合わせをしなくても
  機械的に抽出可能なため、シンプルさを優先し法定路線名からの抽出を採用する。

### 決定2: `filter_lines.py`は`route_number`を`ROUTE_NUMBERS`から独立して解決する
各地物について、`route_category`が`1`〜`5`の場合のみ`ROUTE_NUMBERS`を
`route_name`で引き、ヒットすれば`common_name`の有無にかかわらず`route_number`
をpropertiesに追加する（`common_name`は従来どおり`ROUTE_COMMON_NAMES`を別途
引いて判定する）。`route_category`が`6`、または対応表に存在しない場合は
`route_number`を付与しない。

### 決定3: 路線番号バッジは、SDFアイコン＋`icon-text-fit`によるライン沿いシンボルとして実装する
MapLibre GL JSには背景色付きテキストを直接指定するプロパティがないため、
`route-labels`と同じ`lines`ソースに対する新規`symbol`レイヤー
（`route-number-badges`）を追加し、次の組み合わせで矩形バッジを表現する。

- `layout.symbol-placement: "line"`・`symbol-spacing`で、`route-labels`同様
  ライン沿いに一定間隔でシンボルを配置する。
- 1x1のSDF（signed distance field）画像を`map.addImage`でスタイルに登録し、
  `icon-image`として参照する。`icon-text-fit: "both"`・`icon-text-fit-padding`
  により、アイコン（矩形）が`text-field`（`route_number`）の描画サイズに
  自動追従する。
- `paint.icon-color`に、路線本体のケーシング／塗り（`CASING_COLOR`／
  `FILL_COLOR`、`#1b7a3d`〜`#8fae91`系統）のいずれとも異なる、固定の濃い緑
  （例：`#0a5c34`。ズーム・`route_category`によらず単色）を指定し、
  `paint.text-color: "#ffffff"`を指定する。単色固定にすること自体が、
  ズーム・種別に応じて変化する路線本体の配色との差別化になる。
- `text-field: ["get", "route_number"]`とし、`route_number`が存在しない地物
  には（MapLibreの式が`null`を返すため）シンボルは描画されない。
- `icon-allow-overlap: false`・`text-allow-overlap: false`を維持し、既存の
  `route-labels`（路線名ラベル）とレイヤー間で共有される衝突判定により、
  名称ラベルと路線番号バッジが重ならないようにする。レイヤー順は
  `route-labels`の後（上）に配置し、優先度は名称ラベルを優先する
  （`route-labels`が既に配置された位置を路線番号バッジが避ける）。

代替案として検討したが不採用:
- **`text-field`に路線番号を含めて`route-labels`と一体化する（例：
  「E1 東名高速道路」）**: 矩形の緑背景という独立した視覚表現が実現できず、
  ユーザー要件（矩形背景・路線色との差別化）を満たせない。
- **ラスター画像を静的アセットとして用意する**: 路線番号は`E1`〜`E98`・
  `C2`等の可変長文字列であり、固定サイズのラスター画像では文字数に対応
  できない。`icon-text-fit`による動的サイズ調整が必要。

### 決定4: ポップアップの路線番号表示条件を`route_number`の有無のみにする
`site/main.js`の路線ポップアップで、`route_number`を表示する条件を
`if (common_name)`から`if (route_number)`に変更する。名称欄の表示ロジック
（`common_name ?? route_name`）自体は変更しない。

## Risks / Trade-offs

- [Risk] 国土交通省ナンバリング一覧の案内路線名と、`N06_007`の法定路線名の
  粒度が一致しない箇所（例：ナンバリング一覧側の区間但し書き「（仙台港北～
  利府）」）があり、対応表作成時に法定路線名への割り当てを誤る可能性がある
  → 実装タスクで、対応表の各エントリをナンバリング一覧の記載と突き合わせて
  目視確認し、`verify_counts.py`に対応表エントリ数・`route_number`が付与された
  路線地物数の集計を追加して期待値と比較できるようにする。
- [Trade-off] 法定路線名の区間がナンバリング一覧の区間表記より粗い場合、
  同一法定路線名の地物すべてに同じ`route_number`が付与され、実際の区間境界
  より広い範囲に番号が表示されうる → Non-Goalとして許容する。
- [Risk] 固定色バッジ（`#0a5c34`）が、将来`CASING_COLOR`／`FILL_COLOR`の配色
  変更で偶然近い色になり差別化が薄れる可能性がある → 配色変更時は
  `route-number-badges`の`icon-color`との対比を目視確認する運用でカバーする。

## Migration Plan

1. `pipeline/preprocess/route_numbers.py`（新規対応表）を、国土交通省
   「高速道路ナンバリング一覧」を出典として整備する。
2. `pipeline/preprocess/filter_lines.py`を変更し、`route_number`の解決を
   `ROUTE_NUMBERS`から独立して行うようにする。
3. `pipeline/preprocess/verify_counts.py`に、新対応表エントリ数・
   `route_number`付与件数の検証を追加する。
4. `pipeline/preprocess/run.sh`を実行し、新属性が期待通り付与されることを
   確認する。
5. `./pipeline/build.sh`を実行し、`site/tiles/lines.pmtiles`を再生成・配置
   する。
6. `site/style/map-style.js`に`route-number-badges`レイヤー（SDFアイコン登録
   ・`icon-text-fit`設定を含む）を追加する。
7. `site/main.js`の路線ポップアップの路線番号表示条件を変更する。
8. `npx serve site`でローカル動作確認（路線番号バッジのライン沿い表示・
   路線本体色との差別化・既存ラベルとの重なり回避・`common_name`なし路線
   でのポップアップ路線番号表示）を行う。
9. `main`への`site/**`変更pushで既存のGitHub Actionsが自動デプロイ
   （ロールバックは直前コミットへのrevertで対応）。
