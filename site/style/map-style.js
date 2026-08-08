// MapLibre GL JSのスタイル定義（背景地図なし、高速道路レイヤーのみ）。
//
// pipeline/tilegen が生成したPMTiles（路線・地点）をベクトルタイルソース
// として登録する。路線・地点の詳細なスタイル（国土地理院の最適化ベクトル
// タイルやGoogleマップを参考にした表現、路線名・地点名のラベル表示）は
// Issue #5 / #6 で拡張する。ここでは、地物が表示されることを確認できる
// 最小限のレイヤーのみを定義する。

const TILES_BASE_URL = new URL("../tiles/", import.meta.url).href;

export const mapStyle = {
  version: 8,
  sources: {
    lines: {
      type: "vector",
      url: `pmtiles://${TILES_BASE_URL}lines.pmtiles`,
    },
    points: {
      type: "vector",
      url: `pmtiles://${TILES_BASE_URL}points.pmtiles`,
    },
  },
  layers: [
    {
      id: "lines",
      type: "line",
      source: "lines",
      "source-layer": "lines",
      paint: {
        "line-color": "#e8770d",
        "line-width": 1.5,
      },
    },
    {
      id: "points",
      type: "circle",
      source: "points",
      "source-layer": "points",
      paint: {
        "circle-radius": 3,
        "circle-color": "#1a73e8",
      },
    },
  ],
};
