#!/usr/bin/env bash
# タイル生成パイプラインの前提ツール（tippecanoe / pmtiles CLI）が
# インストールされ、実行可能であることを確認する。
set -euo pipefail

echo "== tippecanoe =="
tippecanoe --version

echo "== pmtiles =="
pmtiles version
