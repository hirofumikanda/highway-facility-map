#!/usr/bin/env bash
# 現況データの前処理（フィルタリング・属性整形・minzoom付与）を実行し、
# 出力件数を検証する。
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

python3 "$SCRIPT_DIR/filter_lines.py"
python3 "$SCRIPT_DIR/filter_points.py"
python3 "$SCRIPT_DIR/verify_counts.py"
