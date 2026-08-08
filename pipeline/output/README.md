# 中間生成物の出力先（生成物はGit管理対象外）

前処理済みGeoJSON、tippecanoeの中間出力（PMTiles等）をこのディレクトリに出力する。
`*.geojson` / `*.mbtiles` および、このディレクトリの `*.pmtiles`
（`/pipeline/output/*.pmtiles`）はリポジトリの `.gitignore` で除外される。
`deploy.sh` が配置する `site/tiles/*.pmtiles` は、静的ホスティング先へそのまま
配信できるようGit管理対象としている。

- `lines.current.geojson` — `pipeline/preprocess/filter_lines.py` が出力する現況路線
- `points.current.geojson` — `pipeline/preprocess/filter_points.py` が出力する現況地点
- `lines.pmtiles` — `pipeline/tilegen/build_lines.sh` が出力する路線タイル（z4-14）
- `points.pmtiles` — `pipeline/tilegen/build_points.sh` が出力する地点タイル（z8-14）
