# highway-facility-map

国土数値情報の高速道路時系列データ（N06）を用いた、現況の高速道路網（路線＋IC/JCT等
の地点）を表示する静的地図サイト。MVT（PMTiles）を[tippecanoe](https://github.com/felt/tippecanoe)
で生成し、[MapLibre GL JS](https://maplibre.org/)で描画する。

## ディレクトリ構成

- `geojson/` — 国土数値情報の元データ（Git管理対象外）
- `pipeline/` — GeoJSON→MVT（PMTiles）ビルドパイプライン。詳細は `pipeline/README.md`
- `site/` — MapLibre GL JSによる静的地図サイト
- `openspec/` — 本プロジェクトの計画資料（proposal / specs / design / tasks）

## 開発計画

実装計画・仕様の詳細は `openspec/changes/highway-facility-map/` を参照。
実装タスクはGitHub Issueで管理している（#1〜#8）。ビルド・デプロイ手順は、
パイプラインとサイトの実装が揃った段階でこのREADMEに追記する。
