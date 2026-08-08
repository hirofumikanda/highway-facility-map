# 中間生成物の出力先（生成物はGit管理対象外）

前処理済みGeoJSON、tippecanoeの中間出力（mbtiles等）をこのディレクトリに出力する。
`*.geojson` / `*.mbtiles` はリポジトリの `.gitignore` で除外される。

- `lines.current.geojson` — `pipeline/preprocess/filter_lines.py` が出力する現況路線
- `points.current.geojson` — `pipeline/preprocess/filter_points.py` が出力する現況地点
