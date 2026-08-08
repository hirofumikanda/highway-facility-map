#!/usr/bin/env bash
# 生成された路線用・地点用PMTilesを静的サイトの出力ディレクトリに配置する。
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

LINES_SRC="$REPO_ROOT/pipeline/output/lines.pmtiles"
POINTS_SRC="$REPO_ROOT/pipeline/output/points.pmtiles"
DEST_DIR="$REPO_ROOT/site/tiles"

for f in "$LINES_SRC" "$POINTS_SRC"; do
  if [[ ! -f "$f" ]]; then
    echo "入力が見つかりません: $f" >&2
    echo "先に build_lines.sh / build_points.sh を実行してください。" >&2
    exit 1
  fi
done

mkdir -p "$DEST_DIR"
cp "$LINES_SRC" "$DEST_DIR/lines.pmtiles"
cp "$POINTS_SRC" "$DEST_DIR/points.pmtiles"

echo "配置しました: $DEST_DIR/lines.pmtiles, $DEST_DIR/points.pmtiles"
