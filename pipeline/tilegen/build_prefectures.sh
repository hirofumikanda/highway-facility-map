#!/usr/bin/env bash
# 都道府県境界GeoJSONからtippecanoeで都道府県境界レイヤーのMVT（PMTiles）を
# 生成する。ズームレベル4〜8。時系列データではないため`pipeline/preprocess/`
# を経由せず`geojson/`の元データを直接入力とする（design.md 決定4）。
# `--include`で必要な属性（都道府県名・都道府県コード）のみに絞り込み、
# `--coalesce`・`--detect-shared-borders`で細かい境界断片を統合してタイル
# サイズを抑える（design.md 決定4）。
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

INPUT="$REPO_ROOT/geojson/N03-20260101_prefecture.geojson"
OUTPUT="$REPO_ROOT/pipeline/output/prefectures.pmtiles"

if [[ ! -f "$INPUT" ]]; then
  echo "入力が見つかりません: $INPUT" >&2
  exit 1
fi

mkdir -p "$(dirname "$OUTPUT")"

tippecanoe \
  --output="$OUTPUT" \
  --minimum-zoom=4 \
  --maximum-zoom=8 \
  --layer=prefectures \
  --include=N03_001 \
  --include=N03_007 \
  --coalesce \
  --detect-shared-borders \
  --quiet \
  --force \
  "$INPUT"

echo "都道府県境界タイルを生成しました: $OUTPUT"
