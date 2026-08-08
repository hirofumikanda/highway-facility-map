# タイル生成パイプライン

`geojson/` の国土数値情報 高速道路時系列データ（N06）から、現況の高速道路網のみを
対象としたMVT（PMTiles）を生成するビルドパイプライン。詳細な設計は
`openspec/changes/highway-facility-map/design.md` を参照。

## ディレクトリ構成

- `preprocess/` — 現況データ（供用期間終了年が`9999`）への絞り込み・属性整形スクリプト
- `tilegen/` — tippecanoeによるMVT生成・PMTiles変換・`site/tiles/`への配置スクリプト
- `output/` — 前処理済みGeoJSONやtippecanoeの中間生成物の出力先。生成物はGit管理対象外
  （`.gitignore`の`*.geojson`/`*.mbtiles`パターンで除外）

## 前提ツール

| ツール | 用途 | このリポジトリで確認済みのバージョン |
|---|---|---|
| [tippecanoe](https://github.com/felt/tippecanoe) | GeoJSON→MVT変換 | v2.80.0 |
| [pmtiles CLI](https://github.com/protomaps/go-pmtiles) | mbtiles→PMTiles変換 | 1.28.0 |

`./check-tools.sh` を実行すると、インストール済みバージョンを確認できる。

```
$ ./pipeline/check-tools.sh
```

Ubuntu の `apt` パッケージのtippecanoeは古いバージョン（2.49.0系）のため、
GitHub Releasesのビルド済みバイナリ、またはソースからのビルドを推奨する。
pmtiles CLIも同様にGitHub Releasesのビルド済みバイナリを利用する。

## 実装状況

前処理（`preprocess/`）とタイル生成（`tilegen/`）のスクリプト本体は後続のIssueで
実装する。

- OpenSpec Change: `highway-facility-map`
- 前処理: tasks.md タスク番号 2.1〜2.5（GitHub Issue #2）
- タイル生成: tasks.md タスク番号 3.1〜3.5（GitHub Issue #3）
