# タイル生成スクリプト

`../output/` の前処理済みGeoJSON（路線・地点）、および`geojson/`の元データ
（都道府県境界）から、tippecanoeでMVT（PMTiles）を生成し、
`../../site/tiles/` に配置する。

## 実行方法

前処理から配置・検証までまとめて実行する場合は、リポジトリルートで:

```
$ ./pipeline/build.sh
```

個々のスクリプトも単独で実行できる:

```
$ ./pipeline/tilegen/build_lines.sh       # 路線タイル生成
$ ./pipeline/tilegen/build_points.sh      # 地点タイル生成
$ ./pipeline/tilegen/build_prefectures.sh # 都道府県境界タイル生成
$ ./pipeline/tilegen/deploy.sh            # site/tiles/ への配置
$ python3 ./pipeline/tilegen/verify_tiles.py  # 生成結果の検証
```

## スクリプト

- `build_lines.sh` — `../output/lines.current.geojson` からズーム4〜14の路線
  レイヤーPMTiles（`../output/lines.pmtiles`）を生成する。地物単位の間引きは
  行わず、tippecanoeの標準的なジオメトリ簡略化に任せる
- `build_points.sh` — `../output/points.current.geojson` からズーム8〜14の
  地点レイヤーPMTiles（`../output/points.pmtiles`）を生成する。前処理で
  付与済みの地物単位`minzoom`（重要度ティア）に加えて、
  `--drop-densest-as-needed`で密集エリアの追加間引きを行う。`--generate-ids`
  により、タイル境界のバッファによる重複を検証スクリプト側で除去できる
  ようにする
- `build_prefectures.sh` — `geojson/N03-20260101_prefecture.geojson`
  （国土数値情報 行政区域（都道府県）データ）からズーム4〜8の都道府県境界
  レイヤーPMTiles（`../output/prefectures.pmtiles`）を生成する。時系列データ
  ではないため`pipeline/preprocess/`を経由せず元データを直接入力とし、
  `--include`で都道府県名・都道府県コードのみに絞り込み、`--coalesce`・
  `--detect-shared-borders`で細かい境界断片を統合してタイルサイズを抑える
- `deploy.sh` — 生成された3つのPMTilesを `../../site/tiles/` にコピーする
- `verify_tiles.py` — 生成タイルをズームごとにデコードし、地点の重要度順
  段階的収録・z14での全収録・路線のズーム範囲と属性保持・都道府県境界の
  ズーム範囲と属性保持を検証する

## PMTilesへの出力について

tippecanoe（v2.80.0で確認）は、出力先ファイル名の拡張子が`.pmtiles`の場合、
mbtiles等を経由せずPMTiles形式を直接出力する。本パイプラインではこの機能を
利用しており、別途のmbtiles→PMTiles変換ステップは不要（design.md 決定2）。

- OpenSpec Change: `highway-facility-map`, `map-interactivity-and-basemap`
- 対応するspec: `openspec/changes/highway-facility-map/specs/highway-tile-pipeline/spec.md`
- tasks.md タスク番号: 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 4.4（GitHub Issue #3）、
  1.1, 1.2, 1.3, 1.4（GitHub Issue #16）
