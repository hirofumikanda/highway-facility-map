## Why

パイプラインは、ジャンクション・一般インターチェンジ・スマートインターチェンジの`symbolrank`（表示優先度）や、一般インターチェンジ・スマートインターチェンジの周辺人口（`symbolrank`算出の基礎値）をすでに計算しているが、これらの値は地図上では確認できない。表示優先度・タイル収録ズームの調整結果を目視確認する手段がなく、`symbolrank`の妥当性検証には前処理スクリプトの出力を別途確認する必要がある。

## What Changes

- 結合部ポイントのポップアップ（地点クリック時）に、`symbolrank`属性が付与されている地物（ジャンクション・一般インターチェンジ・スマートインターチェンジ）について、`symbolrank`の値を表示する行を追加する。`symbolrank`が付与されていない地物（その他の接合部）には、この行を表示しない。
- 一般インターチェンジ・スマートインターチェンジの周辺人口（`symbolrank`算出に用いた半径10km以内人口合計、`pipeline/preprocess/point_population.py`の`surrounding_population`ですでに算出済みの値）を、地点地物の新規属性として出力に含め、ポップアップに表示する行を追加する。周辺人口が算出されていない地物（ジャンクション・その他の接合部）には、この行を表示しない。
- 周辺人口・`symbolrank`いずれの算出ロジックも変更しない（既存の計算結果を出力・表示するのみ）。

## Capabilities

### New Capabilities

（なし）

### Modified Capabilities

- `highway-tile-pipeline`: 「一般インターチェンジ・スマートインターチェンジへのsymbolrank付与」要件に、算出済みの周辺人口を地点地物の属性として出力する要件を追加する。
- `highway-map-viewer`: 「地点クリック時のポップアップ表示」要件に、`symbolrank`・周辺人口（属性が付与されている地物のみ）の表示を追加する。

## Impact

- `pipeline/preprocess/filter_points.py`: 一般インターチェンジ・スマートインターチェンジの出力属性に、算出済みの周辺人口を追加。
- `pipeline/preprocess/verify_counts.py`: 周辺人口属性の付与検証を追加。
- `site/main.js`: 地点クリックのポップアップ生成処理に、`symbolrank`・周辺人口の表示行を追加。
- 既存のJCTのsymbolrank算出（車線数合計ベース）・IC/SICのsymbolrank算出（周辺人口の路線内相対順位ベース）・周辺人口算出ロジック自体は変更しない。
