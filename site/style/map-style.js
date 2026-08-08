// MapLibre GL JSのスタイル定義（背景地図なし、高速道路レイヤーのみ）。
//
// pipeline/tilegen が生成したPMTiles（路線・地点）をベクトルタイルソース
// として登録する。路線スタイル（国土地理院の最適化ベクトルタイルを参考にした
// ケーシング＋塗り、路線名のライン沿い表示）はIssue #5で実装済み。地点の
// 詳細なスタイル（Googleマップを参考にした表現、地点名ラベル）はIssue #6で
// 拡張する。ここでは、地点は地物が表示されることを確認できる最小限の
// レイヤーのみを定義する。

const TILES_BASE_URL = new URL("../tiles/", import.meta.url).href;

// ズームレベルに応じた基準線幅（国土地理院 最適化ベクトルタイルを参考に、
// 低ズームでは細く、高ズームでは太く表示する）。
const LINE_WIDTH_STOPS_BY_ZOOM = [
  [4, 0.3],
  [6, 0.5],
  [8, 0.9],
  [10, 1.5],
  [12, 2.5],
  [14, 4],
];

// 路線種別区分（N06_008）に応じた線幅の倍率。高速自動車国道系統
// （1:高速自動車国道／2:並行する自専道／3:一般国道の自専道／
// 4:本州四国連絡高速道路）を太く、指定都市高速道路（5）・その他（6）を
// 控えめな太さにする（design.md 決定7）。
const ROUTE_CATEGORY_WIDTH_MULTIPLIER = [
  "match",
  ["get", "route_category"],
  "1",
  1.4,
  "2",
  1.4,
  "3",
  1.15,
  "4",
  1.4,
  "5",
  0.85,
  0.6,
];

// MapLibreの式言語では `["zoom"]` はstep/interpolateの直接の入力としてのみ
// 使用できるため、`["*", <interpolate式>, <match式>]` のような入れ子はできない。
// そのためinterpolateの各ストップの出力値側でカテゴリ倍率を乗算する。
function widthByZoomAndCategory(stops, casingMultiplier = 1) {
  const expression = ["interpolate", ["linear"], ["zoom"]];
  for (const [zoom, baseWidth] of stops) {
    expression.push(zoom, [
      "*",
      baseWidth * casingMultiplier,
      ROUTE_CATEGORY_WIDTH_MULTIPLIER,
    ]);
  }
  return expression;
}

const FILL_WIDTH = widthByZoomAndCategory(LINE_WIDTH_STOPS_BY_ZOOM);
const CASING_WIDTH = widthByZoomAndCategory(LINE_WIDTH_STOPS_BY_ZOOM, 1.7);

// 路線種別区分に応じたケーシング色・塗り色。高速自動車国道系統は濃いオレンジ、
// 指定都市高速道路・その他は控えめな配色にする（design.md 決定7）。
const CASING_COLOR = [
  "match",
  ["get", "route_category"],
  "1",
  "#b35c00",
  "2",
  "#b35c00",
  "3",
  "#c97a1f",
  "4",
  "#b35c00",
  "5",
  "#8a5a2b",
  "#8c8c8c",
];

const FILL_COLOR = [
  "match",
  ["get", "route_category"],
  "1",
  "#f4a13a",
  "2",
  "#f4a13a",
  "3",
  "#f7b563",
  "4",
  "#f4a13a",
  "5",
  "#d9a066",
  "#bfbfbf",
];

// 低ズームでは控えめに、高ズームでは鮮明になるよう不透明度をズーム連動させる。
const LINE_OPACITY_BY_ZOOM = [
  "interpolate",
  ["linear"],
  ["zoom"],
  4,
  0.6,
  8,
  0.85,
  12,
  1,
];

export const mapStyle = {
  version: 8,
  glyphs: "https://fonts.openmaptiles.org/{fontstack}/{range}.pbf",
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
      id: "lines-casing",
      type: "line",
      source: "lines",
      "source-layer": "lines",
      layout: {
        "line-cap": "round",
        "line-join": "round",
      },
      paint: {
        "line-color": CASING_COLOR,
        "line-width": CASING_WIDTH,
        "line-opacity": LINE_OPACITY_BY_ZOOM,
      },
    },
    {
      id: "lines-fill",
      type: "line",
      source: "lines",
      "source-layer": "lines",
      layout: {
        "line-cap": "round",
        "line-join": "round",
      },
      paint: {
        "line-color": FILL_COLOR,
        "line-width": FILL_WIDTH,
        "line-opacity": LINE_OPACITY_BY_ZOOM,
      },
    },
    {
      id: "route-labels",
      type: "symbol",
      source: "lines",
      "source-layer": "lines",
      layout: {
        "symbol-placement": "line",
        "symbol-spacing": 250,
        "text-field": ["get", "route_name"],
        "text-font": ["Klokantech Noto Sans CJK Regular"],
        "text-size": ["interpolate", ["linear"], ["zoom"], 8, 10, 14, 14],
        "text-letter-spacing": 0.05,
        "text-allow-overlap": false,
        "text-ignore-placement": false,
      },
      paint: {
        "text-color": "#7a3d00",
        "text-halo-color": "#ffffff",
        "text-halo-width": 1.5,
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
