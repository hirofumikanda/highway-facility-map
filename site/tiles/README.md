# 生成タイルの配置先（生成物はGit管理対象外）

`pipeline/tilegen/deploy.sh`（または `pipeline/build.sh`）が生成したPMTilesファイル
をこのディレクトリに配置する。`*.pmtiles` はリポジトリの `.gitignore` で除外される。

- `lines.pmtiles` — 路線レイヤー（z4-14）
- `points.pmtiles` — 地点レイヤー（z8-14）

- OpenSpec Change: `highway-facility-map`
- tasks.md タスク番号: 3.4（GitHub Issue #3）
