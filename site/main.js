// MapLibre GL JSでPMTiles（路線・地点）を読み込み、背景地図なしで
// 高速道路レイヤーのみを描画する。
//
// OpenSpec Change: highway-facility-map
// tasks.md: 5.1, 5.2, 5.3

import {
  Map,
  NavigationControl,
  Popup,
  addProtocol,
} from "https://cdn.jsdelivr.net/npm/maplibre-gl@6.2.0/dist/maplibre-gl.mjs";
import { mapStyle } from "./style/map-style.js";

// 接合部種別（point_type）を人が読める種別名に変換する（design.md 決定3）。
const POINT_TYPE_LABELS = {
  1: "一般インターチェンジ",
  2: "スマートインターチェンジ",
  3: "ジャンクション",
  4: "その他の接合部",
};

// pmtilesは index.html 内の通常のscriptタグ（依存関係を内包したグローバル
// バンドル）で読み込まれ、window.pmtiles として参照できる。
const protocol = new window.pmtiles.Protocol();
addProtocol("pmtiles", protocol.tile);

const map = new Map({
  container: "map",
  style: mapStyle,
  // 日本全体の高速道路網が収まる初期表示範囲・ズーム（URLにハッシュ
  // パラメータが含まれる場合はそちらが優先される）
  center: [137.5, 36.5],
  zoom: 4.3,
  // ズーム・中心緯度経度・回転・傾きをURLハッシュに同期し、ハッシュ付き
  // URLからその表示状態で初期化できるようにする
  hash: true,
  // MapLibreはデフォルトで漢字等の表意文字をクライアント側のシステムフォント
  // でローカル描画し帯域を節約するが、利用者の環境にCJKフォントが無いと文字
  // が表示されない。路線名・地点名を確実に表示するため無効化し、style側の
  // `glyphs`（CJK対応のSDFフォント）から取得させる。
  localIdeographFontFamily: false,
});

map.addControl(new NavigationControl(), "top-right");

// 地点（IC・JCT等）のクリック時に、地点名・種別ラベルを表示するポップアップ
// を出す。`points`レイヤーのみをリッスンするため、地点以外のクリックでは
// 発火しない（design.md 決定3）。
map.on("click", "points", (event) => {
  const feature = event.features?.[0];
  if (!feature) {
    return;
  }

  const coordinates = feature.geometry.coordinates.slice();
  const { point_name, point_type } = feature.properties;

  const container = document.createElement("div");
  const nameEl = document.createElement("div");
  nameEl.textContent = point_name;
  const typeEl = document.createElement("div");
  typeEl.textContent = POINT_TYPE_LABELS[point_type] ?? point_type;
  container.append(nameEl, typeEl);

  // innerHTMLへのプロパティ直接埋め込みは行わず、DOM APIでテキストノード
  // として組み立てた要素をポップアップに渡す（design.md 決定3）。
  new Popup().setLngLat(coordinates).setDOMContent(container).addTo(map);
});

// 地点マーカーへのホバー時にカーソルをpointerに変更する。
map.on("mouseenter", "points", () => {
  map.getCanvas().style.cursor = "pointer";
});
map.on("mouseleave", "points", () => {
  map.getCanvas().style.cursor = "";
});
