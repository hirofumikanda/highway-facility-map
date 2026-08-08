#!/usr/bin/env bash
# 前処理→タイル生成→静的サイトへの配置→検証までを1コマンドで実行する。
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

"$SCRIPT_DIR/preprocess/run.sh"
"$SCRIPT_DIR/tilegen/build_lines.sh"
"$SCRIPT_DIR/tilegen/build_points.sh"
"$SCRIPT_DIR/tilegen/deploy.sh"
python3 "$SCRIPT_DIR/tilegen/verify_tiles.py"

echo "ビルド完了: site/tiles/ にPMTilesを配置しました"
