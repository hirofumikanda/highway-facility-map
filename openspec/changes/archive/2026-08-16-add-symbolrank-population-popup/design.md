## Context

`pipeline/preprocess/filter_points.py`は、一般インターチェンジ・スマートインターチェンジ（`point_type`が`1`・`2`）の`symbolrank`算出時に`point_population.surrounding_population`で周辺人口を計算し、地物ごとの一時変数`entry["population"]`として保持しているが、出力GeoJSON（`pipeline/output/points.current.geojson`）の`properties`には書き込んでいない（[[main spec]] `highway-tile-pipeline`の「一般インターチェンジ・スマートインターチェンジへのsymbolrank付与」要件）。

`site/main.js`の`points`レイヤークリックハンドラは、タイル（MVT）の`feature.properties`から`point_name`・`point_type`・`lane_counts`を読み取ってポップアップを組み立てる。`lane_counts`はMVTの配列非対応制約からJSON文字列として保持されており、表示前に`JSON.parse`している。`symbolrank`は数値としてすでにタイルに含まれているが、ポップアップでは未使用。

## Goals / Non-Goals

**Goals:**
- 既存の`symbolrank`計算結果（JCT・IC・SIC）をポップアップに表示する。
- 既存の周辺人口計算結果（IC・SICのみ）を、出力属性として追加した上でポップアップに表示する。

**Non-Goals:**
- 周辺人口計算のJCT・その他の接合部への拡張（対象外のまま。`demote-city-other-joints`変更（symbolrank・minzoomの優先度補正）とは独立した変更）。
- `symbolrank`・周辺人口の算出ロジック自体の変更。
- ポップアップ全体のデザイン刷新（既存のプレーンなDOM組み立て方式を踏襲する）。

## Decisions

### 決定1: `population`属性は、`symbolrank`算出に用いた値を四捨五入した整数として出力する
`surrounding_population`が返す値はNumPyのfloat64（250mメッシュの`PTN_2025`合計、小数を含む推計値）である。人口という性質上小数点以下の精度は意味を持たないため、`filter_points.py`で`round()`により整数化してから`properties["population"]`に書き込む。`symbolrank`の算出（四分位の順位付け）は、丸め処理前の元の値（`entry["population"]`）を使い続け、丸めは出力属性への書き込み時にのみ適用する（順位付けの結果に影響しない）。

代替案として検討したが不採用:
- **小数のまま出力する**: 250mメッシュ人口推計値の性質上、小数点以下は意味のある精度ではなく、ポップアップ表示時に読みにくいため不採用。

### 決定2: ポップアップの`symbolrank`・周辺人口の表示行は、既存の`lane_counts`と同じ「属性が存在する場合のみ行を追加する」パターンに従う
`site/main.js`の`points`クリックハンドラで、`feature.properties.symbolrank`が`undefined`でない場合に`symbolrank`行を、`feature.properties.population`が`undefined`でない場合に周辺人口行を、それぞれ`container.append`する。地点種別ごとに条件分岐するのではなく、属性の有無で判定することで、将来`symbolrank`・`population`の付与対象地点種別が変わっても表示ロジックの変更が不要になる（既存の`lane_counts`と同じ設計判断）。

表示順序は、既存の「地点名 → 地点種別 → 車線数」に続けて「symbolrank → 周辺人口」を追加する。

表示文言は、`symbolrank`は`symbolrank: <値>`（属性名をそのまま用いる。ユーザーがデータ検証目的で`symbolrank`という用語自体を指定しているため）、周辺人口は`周辺人口: <値>人（半径10km以内）`（値は3桁区切り、`toLocaleString("ja-JP")`）とする。

代替案として検討したが不採用:
- **`symbolrank`を「表示優先度」等の意訳ラベルに置き換える**: ユーザーが明示的に「symbolrank」という属性名を指定しており、データ検証用途では元の属性名の方が前処理スクリプトの出力と対応付けやすいため不採用。

## Risks / Trade-offs

- [Trade-off] `population`属性はIC・SICのみに付与され、JCT・その他の接合部には付与されない。ポップアップの周辺人口行はIC・SICのみに表示され、地点種別間で表示項目が非対称になるが、既存の`symbolrank`（JCT・IC・SICのみ）や`lane_counts`（接続路線がない場合は非表示）と同様の既存パターンであり、新たなリスクではない。
- [Risk] `population`属性追加により`points.pmtiles`のタイルサイズがわずかに増加する（IC・SIC 2,106件分の整数属性1件） → 既存の`symbolrank`属性と同程度の増分であり無視できる規模。

## Migration Plan

1. `pipeline/preprocess/filter_points.py`で、IC・SICの`symbolrank`付与ループ内に、丸めた周辺人口を`properties["population"]`へ書き込む処理を追加する（決定1）。
2. `pipeline/preprocess/run.sh`を実行し、`points.current.geojson`に`population`属性が期待通り付与されることを確認する。
3. `pipeline/preprocess/verify_counts.py`に、IC・SICの`population`属性の欠落件数検証（`symbolrank`の欠落検証と同様の形式）を追加する。
4. `./pipeline/build.sh`を実行し、`site/tiles/points.pmtiles`を再生成・配置する。
5. `site/main.js`の`points`クリックハンドラに、`symbolrank`・`population`属性が存在する場合の表示行を追加する（決定2）。
6. `npx serve site`でローカル動作確認（JCT・IC・SICで`symbolrank`が表示されること、IC・SICでのみ周辺人口が表示されること、その他の接合部でいずれも表示されないこと、既存の地点名・種別・車線数表示に変化がないことを含む）を行う。
7. `main`への`site/**`・`pipeline/**`変更pushで、`site/**`分は既存のGitHub Actionsが自動デプロイする。タイル（`site/tiles/points.pmtiles`）の再生成・配置はビルドスクリプト実行が必要なため、手動での配置確認も行う。
