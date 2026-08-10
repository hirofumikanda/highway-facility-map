# 生成タイルの配置先（生成物はGit管理対象）

`pipeline/tilegen/deploy.sh`（または `pipeline/build.sh`）が生成したPMTilesファイル
をこのディレクトリに配置する。静的ホスティング先へビルドステップなしにそのまま
配信できるよう、このディレクトリの `*.pmtiles` はGit管理対象としている
（中間生成物である `pipeline/output/*.pmtiles` は `.gitignore` で除外される）。

- `lines.pmtiles` — 路線レイヤー（z4-14）
- `points.pmtiles` — 地点レイヤー（z8-14）
- `prefectures.pmtiles` — 都道府県境界レイヤー（z4-8、背景レイヤー用）

- OpenSpec Change: `highway-facility-map`, `map-interactivity-and-basemap`
- tasks.md タスク番号: 3.4（GitHub Issue #3）、1.2（GitHub Issue #16）
