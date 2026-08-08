#!/usr/bin/env bash
# 現況路線GeoJSONからtippecanoeで路線レイヤーのMVT（PMTiles）を生成する。
# ズームレベル4〜14。地物単位の間引きは行わず、tippecanoeの標準的な
# ジオメトリ簡略化に任せる（design.md 決定4）。
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

INPUT="$REPO_ROOT/pipeline/output/lines.current.geojson"
OUTPUT="$REPO_ROOT/pipeline/output/lines.pmtiles"

if [[ ! -f "$INPUT" ]]; then
  echo "入力が見つかりません: $INPUT" >&2
  echo "先に pipeline/preprocess/run.sh を実行してください。" >&2
  exit 1
fi

# 出力先の拡張子が .pmtiles の場合、tippecanoeはPMTiles形式を直接出力する
# （mbtiles経由の変換ステップは不要）。
tippecanoe \
  --output="$OUTPUT" \
  --minimum-zoom=4 \
  --maximum-zoom=14 \
  --layer=lines \
  --quiet \
  --force \
  "$INPUT"

echo "路線タイルを生成しました: $OUTPUT"
