## ADDED Requirements

### Requirement: 都道府県境界データのPMTiles出力
パイプラインは、`N03-20260101_prefecture.geojson`（行政区域（都道府県）GeoJSONデータ）から、都道府県境界のPMTilesアーカイブを生成しなければならない（SHALL）。生成物は、路線用・地点用PMTilesと同様に、タイルサーバープロセスなしで静的ファイルのHTTP配信のみによってMVTとして参照可能でなければならない（SHALL）。

#### Scenario: 都道府県境界PMTilesの生成
- **WHEN** パイプラインが`N03-20260101_prefecture.geojson`を処理する
- **THEN** 都道府県境界のPMTilesアーカイブファイルが生成され、静的ファイルのHTTP配信のみでMVTタイルとして参照できる

### Requirement: 都道府県境界レイヤーのズーム範囲
都道府県境界レイヤーのMVTは、ズームレベル4から8までの範囲で生成しなければならない（SHALL）。

#### Scenario: 都道府県境界タイルのズーム範囲
- **WHEN** 都道府県境界レイヤーのMVTを生成する
- **THEN** 出力タイルはズームレベル4から8の範囲で生成される
