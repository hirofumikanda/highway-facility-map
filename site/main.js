// MapLibre GL JSでPMTiles（路線・地点）を読み込み、背景地図なしで
// 高速道路レイヤーのみを描画する。
//
// OpenSpec Change: highway-facility-map
// tasks.md: 5.1, 5.2, 5.3

import {
  Map,
  addProtocol,
} from "https://cdn.jsdelivr.net/npm/maplibre-gl@6.2.0/dist/maplibre-gl.mjs";
import { mapStyle } from "./style/map-style.js";

// pmtilesは index.html 内の通常のscriptタグ（依存関係を内包したグローバル
// バンドル）で読み込まれ、window.pmtiles として参照できる。
const protocol = new window.pmtiles.Protocol();
addProtocol("pmtiles", protocol.tile);

new Map({
  container: "map",
  style: mapStyle,
  // 日本全体の高速道路網が収まる初期表示範囲・ズーム
  center: [137.5, 36.5],
  zoom: 4.3,
});
