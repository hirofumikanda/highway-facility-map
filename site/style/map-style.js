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
// そのためinterpolateの各ストップの出力値側で地物属性ベースの倍率を乗算する。
// 路線の線幅（ズーム×路線種別区分）・地点の半径（ズーム×接合部種別）の
// 両方で使う。
function zoomInterpolateWithMultiplier(stops, multiplierExpression, scale = 1) {
  const expression = ["interpolate", ["linear"], ["zoom"]];
  for (const [zoom, base] of stops) {
    expression.push(zoom, ["*", base * scale, multiplierExpression]);
  }
  return expression;
}

const FILL_WIDTH = zoomInterpolateWithMultiplier(
  LINE_WIDTH_STOPS_BY_ZOOM,
  ROUTE_CATEGORY_WIDTH_MULTIPLIER,
);
const CASING_WIDTH = zoomInterpolateWithMultiplier(
  LINE_WIDTH_STOPS_BY_ZOOM,
  ROUTE_CATEGORY_WIDTH_MULTIPLIER,
  1.7,
);

// 路線種別区分に応じたケーシング色・塗り色。高速自動車国道系統は濃い緑、
// 指定都市高速道路・その他は控えめな配色にする（design.md 決定6、
// 高速道路案内標識を想起させる緑系統を基調に、旧オレンジ配色の濃淡構造は
// 維持したまま色相のみ変更）。
const CASING_COLOR = [
  "match",
  ["get", "route_category"],
  "1",
  "#1b7a3d",
  "2",
  "#1b7a3d",
  "3",
  "#2f8f4e",
  "4",
  "#1b7a3d",
  "5",
  "#5a7a5e",
  "#8c8c8c",
];

const FILL_COLOR = [
  "match",
  ["get", "route_category"],
  "1",
  "#4caf6f",
  "2",
  "#4caf6f",
  "3",
  "#7cc494",
  "4",
  "#4caf6f",
  "5",
  "#8fae91",
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

// ズームレベルに応じた地点マーカーの基準半径（Googleマップのピン/POIマーカーを
// 参考に、ズームが上がるほど大きく表示する）。
const POINT_RADIUS_STOPS_BY_ZOOM = [
  [8, 4],
  [10, 4.5],
  [12, 5],
  [14, 6],
];

// 接合部種別（N06_019）に応じた半径の倍率。ジャンクション（3）はやや大きめ、
// 一般インターチェンジ（1）は標準、スマートインターチェンジ（2）はIC系だが
// 区別できるサイズ、その他（4）は控えめにする（design.md 決定9）。
const POINT_TYPE_RADIUS_MULTIPLIER = [
  "match",
  ["get", "point_type"],
  "3",
  1.3,
  "1",
  1,
  "2",
  0.9,
  0.75,
];

const POINT_RADIUS = zoomInterpolateWithMultiplier(
  POINT_RADIUS_STOPS_BY_ZOOM,
  POINT_TYPE_RADIUS_MULTIPLIER,
);

// 接合部種別に応じたマーカー配色。ジャンクションは目立つ配色（赤系）、
// 一般インターチェンジはGoogleマップの標準ピン配色（青）、スマートIC は
// IC系だが区別できる配色（ティール）、その他は控えめな配色（グレー）にする
// （design.md 決定9）。
const POINT_COLOR = [
  "match",
  ["get", "point_type"],
  "3",
  "#d93025",
  "1",
  "#4285f4",
  "2",
  "#00897b",
  "#9aa0a6",
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
    prefectures: {
      type: "vector",
      url: `pmtiles://${TILES_BASE_URL}prefectures.pmtiles`,
    },
  },
  layers: [
    // 都道府県境界は地理院地図の白地図（淡い単色塗り・控えめな行政界線・
    // 注記なし）を参考にした背景レイヤーとして、高速道路の路線・地点
    // レイヤーより下（配列の先頭）に配置する（design.md 決定5）。
    {
      id: "prefectures-fill",
      type: "fill",
      source: "prefectures",
      "source-layer": "prefectures",
      paint: {
        "fill-color": "#f5f5f2",
      },
    },
    {
      id: "prefectures-boundary",
      type: "line",
      source: "prefectures",
      "source-layer": "prefectures",
      layout: {
        "line-cap": "round",
        "line-join": "round",
      },
      paint: {
        "line-color": "#c9c5bb",
        "line-width": ["interpolate", ["linear"], ["zoom"], 4, 0.5, 8, 1],
      },
    },
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
        "text-color": "#1b5e2e",
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
        "circle-radius": POINT_RADIUS,
        "circle-color": POINT_COLOR,
        "circle-stroke-color": "#ffffff",
        "circle-stroke-width": ["interpolate", ["linear"], ["zoom"], 8, 1, 14, 1.5],
      },
    },
    {
      id: "point-labels",
      type: "symbol",
      source: "points",
      "source-layer": "points",
      layout: {
        "text-field": ["get", "point_name"],
        "text-font": ["Klokantech Noto Sans CJK Regular"],
        "text-size": ["interpolate", ["linear"], ["zoom"], 8, 10, 14, 13],
        // マーカー（円）の下にラベルを配置し、重ならないようにする
        "text-anchor": "top",
        "text-offset": [0, 0.6],
        "text-allow-overlap": false,
        "text-optional": true,
      },
      paint: {
        "text-color": "#202124",
        "text-halo-color": "#ffffff",
        "text-halo-width": 1.2,
      },
    },
  ],
};
