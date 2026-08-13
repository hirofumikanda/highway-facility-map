#!/usr/bin/env python3
"""地点座標群の周辺人口（半径10km以内メッシュの人口合計）を算出する。

国土数値情報「250mメッシュ別将来推計人口」（`geojson/250m_mesh_2024_GEOJSON/`、
94ファイル・合計約7.7GB、Git管理対象外）を1ファイルずつ読み込みながら、与え
られた地点座標群それぞれの半径10km以内メッシュの2025年総数人口（`PTN_2025`）
合計をNumPy配列演算で算出する（design.md 決定1）。

メッシュ中心点はジオメトリ（Polygon）の外環座標のバウンディングボックス中心
から求め、地点との距離は地点の緯度で経度方向のスケールを補正した平面近似式
（正距円筒図法近似）で算出する（design.md 決定2）。

1ファイルあたりのメッシュ数は最大でも数万件程度だが、地点数（2,106件）との
全組み合わせを一度に密行列化するとメモリを圧迫し得るため、メッシュを
`MESH_CHUNK_SIZE`件ずつに分けてNumPy演算を行う（ファイルの読み込み自体は
1回で完結し、決定1の「ファイル単位で1回だけ読み込む」方針は保たれる）。

OpenSpec Change: add-ic-sic-symbolrank
tasks.md: 1.1, 1.2（GitHub Issue #105）
"""
import json
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
MESH_DIR = REPO_ROOT / "geojson" / "250m_mesh_2024_GEOJSON"

RADIUS_KM = 10.0
LON_KM_PER_DEGREE = 111.32
LAT_KM_PER_DEGREE = 110.57
MESH_CHUNK_SIZE = 20000


def _mesh_centers_and_population(mesh_path):
    """1メッシュファイルから、(中心経度配列, 中心緯度配列, PTN_2025配列) を構築する。

    メッシュ中心点はPolygonの外環座標のバウンディングボックス中心から求める
    （Shapelyの`centroid`計算を全メッシュに適用するより高速、design.md 決定2）。
    `PTN_2025`が`null`のメッシュは0として扱う。
    """
    with open(mesh_path, encoding="utf-8") as f:
        data = json.load(f)

    lons = []
    lats = []
    populations = []
    for feature in data["features"]:
        ring = feature["geometry"]["coordinates"][0]
        xs = [c[0] for c in ring]
        ys = [c[1] for c in ring]
        lons.append((min(xs) + max(xs)) / 2)
        lats.append((min(ys) + max(ys)) / 2)
        populations.append(feature["properties"].get("PTN_2025") or 0.0)

    return np.array(lons), np.array(lats), np.array(populations)


def surrounding_population(points, mesh_dir=MESH_DIR, radius_km=RADIUS_KM):
    """各地点(lon, lat)を中心とする半径radius_km以内メッシュの人口合計を算出する。

    `mesh_dir`配下の全メッシュファイルを1回ずつ読み込みながら、地点群との
    距離判定・人口加算をNumPy配列演算で行う（design.md 決定1）。距離は、
    地点の緯度で経度方向のスケールを補正した平面近似式
    （`dx_km = Δlon * 111.32 * cos(lat)`、`dy_km = Δlat * 110.57`）で算出する
    （design.md 決定2）。

    Args:
        points: `(経度, 緯度)`のタプルのシーケンス。
        mesh_dir: メッシュGeoJSONファイル群を含むディレクトリ。
        radius_km: 合算対象とするメッシュ中心点までの距離の閾値（km）。

    Returns:
        `points`と同じ順序・長さのNumPy配列（各地点の周辺人口合計）。
    """
    point_lons = np.array([p[0] for p in points])
    point_lats = np.array([p[1] for p in points])
    lat_scale = np.cos(np.radians(point_lats)) * LON_KM_PER_DEGREE

    totals = np.zeros(len(points))

    mesh_paths = sorted(Path(mesh_dir).glob("*.geojson"))
    for mesh_path in mesh_paths:
        mesh_lons, mesh_lats, mesh_populations = _mesh_centers_and_population(mesh_path)

        for start in range(0, len(mesh_lons), MESH_CHUNK_SIZE):
            chunk_lons = mesh_lons[start : start + MESH_CHUNK_SIZE]
            chunk_lats = mesh_lats[start : start + MESH_CHUNK_SIZE]
            chunk_populations = mesh_populations[start : start + MESH_CHUNK_SIZE]

            dx_km = (point_lons[:, None] - chunk_lons[None, :]) * lat_scale[:, None]
            dy_km = (point_lats[:, None] - chunk_lats[None, :]) * LAT_KM_PER_DEGREE
            distances = np.sqrt(dx_km**2 + dy_km**2)

            within_radius = distances <= radius_km
            totals += within_radius @ chunk_populations

    return totals
