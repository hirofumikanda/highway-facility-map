# highway-facility-map

国土数値情報の高速道路時系列データ（N06）を用いた、現況の高速道路網（路線＋IC/JCT等
の地点）を表示する静的地図サイト。MVT（PMTiles）を[tippecanoe](https://github.com/felt/tippecanoe)
で生成し、[MapLibre GL JS](https://maplibre.org/)で描画する。

## ディレクトリ構成

- `geojson/` — 国土数値情報の元データ（Git管理対象外）
- `pipeline/` — GeoJSON→MVT（PMTiles）ビルドパイプライン。詳細は `pipeline/README.md`
- `site/` — MapLibre GL JSによる静的地図サイト
- `openspec/` — 本プロジェクトの計画資料（proposal / specs / design / tasks）

## ビルド手順

1. 前提ツール（[tippecanoe](https://github.com/felt/tippecanoe) v2.80.0以降 /
   [pmtiles CLI](https://github.com/protomaps/go-pmtiles)）が導入済みか確認する
   ```
   $ ./pipeline/check-tools.sh
   ```
2. 国土数値情報の元データ（`N06-25_HighwaySection.geojson` /
   `N06-25_Joint.geojson`）を `geojson/` に配置する（Git管理対象外）。
3. 前処理→タイル生成→`site/tiles/`への配置→検証までを1コマンドで実行する
   ```
   $ ./pipeline/build.sh
   ```
   個々のステップは `pipeline/README.md`・`pipeline/preprocess/README.md`・
   `pipeline/tilegen/README.md` を参照。

## ローカルでの動作確認

`site/` はビルド済みの静的ファイル一式（HTML/JS/CSS＋PMTiles）のみで完結して
おり、追加のビルドステップなしでそのまま任意の静的ホスティングに配置できる。
ローカル確認時は、PMTilesの読み込みに**HTTP Range Request対応の静的サーバー**
が必須な点に注意する（`python3 -m http.server` はRangeリクエストに対応して
いないため使用不可）。例:

```
$ npx serve site
```

## デプロイ

`main`ブランチへの`site/**`の変更のpushをトリガーに、GitHub Actions
（`.github/workflows/deploy-pages.yml`）がGitHub Pagesへ自動デプロイする。
`site/`をアップロードするだけで、ビルドステップは行わない。

## 開発計画

実装計画・仕様の詳細は `openspec/changes/highway-facility-map/` を参照。
実装タスクはGitHub Issueで管理している（#1〜#8）。
