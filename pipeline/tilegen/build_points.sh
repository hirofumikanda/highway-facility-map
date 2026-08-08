#!/usr/bin/env bash
# 現況地点GeoJSONからtippecanoeで地点レイヤーのMVT（PMTiles）を生成する。
# ズームレベル8〜14。前処理で付与済みの地物単位`minzoom`（重要度ティア）に
# 加えて、`--drop-densest-as-needed`で密集エリアの追加間引きを行う
# （design.md 決定5・決定6）。`--generate-ids`は、タイル境界のバッファに
# よる重複を検証スクリプト側で除去できるようにするための一意なidを付与する。
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

INPUT="$REPO_ROOT/pipeline/output/points.current.geojson"
OUTPUT="$REPO_ROOT/pipeline/output/points.pmtiles"

if [[ ! -f "$INPUT" ]]; then
  echo "入力が見つかりません: $INPUT" >&2
  echo "先に pipeline/preprocess/run.sh を実行してください。" >&2
  exit 1
fi

tippecanoe \
  --output="$OUTPUT" \
  --minimum-zoom=8 \
  --maximum-zoom=14 \
  --layer=points \
  --drop-densest-as-needed \
  --generate-ids \
  --quiet \
  --force \
  "$INPUT"

echo "地点タイルを生成しました: $OUTPUT"
