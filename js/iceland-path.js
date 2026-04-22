// Simplified Iceland coastline - [lat, lng] pairs, clockwise from SW Reykjanes
export const ICELAND_OUTLINE = [
  // SW Reykjanes peninsula
  [63.82, -22.69],
  [63.87, -22.45],
  [63.97, -22.63],
  [64.03, -22.73],
  // W coast / Reykjavík area
  [64.10, -22.86],
  [64.17, -22.52],
  [64.25, -22.30],
  // Hvalfjörður
  [64.35, -21.96],
  [64.46, -22.17],
  [64.55, -21.96],
  [64.60, -21.64],
  // Borgarnes / Snæfellsnes
  [64.68, -21.89],
  [64.75, -21.97],
  [64.87, -22.30],
  [64.80, -23.05],
  [64.92, -23.77],  // Snæfellsjökull tip
  [64.99, -23.42],
  [65.06, -23.06],  // Grundarfjörður
  [65.08, -22.73],  // Stykkishólmur
  // Breiðafjörður / Westfjords approach
  [65.20, -22.45],
  [65.38, -22.70],
  [65.52, -23.12],
  // Westfjords outer
  [65.63, -24.18],
  [65.82, -24.47],
  [66.08, -24.44],
  [66.22, -23.89],
  // Ísafjörður / Westfjords complex
  [66.28, -23.18],
  [66.06, -22.54],
  [66.13, -22.23],
  [65.95, -21.73],
  [65.70, -21.45],  // Drangsnes
  // Húnaflói / N Iceland west
  [65.60, -20.65],
  [65.68, -20.37],
  [65.85, -20.05],
  // Skagafjörður
  [65.92, -19.55],
  [65.76, -19.65],
  [65.88, -19.07],
  // Siglufjörður / N coast
  [66.15, -18.91],
  [66.18, -18.46],
  [66.38, -17.95],
  [66.45, -17.60],
  [66.53, -16.25],  // NE Iceland
  [66.41, -15.60],
  // East Iceland
  [65.75, -14.00],
  [65.27, -13.57],  // Seyðisfjörður
  [64.94, -13.75],
  [64.66, -14.30],  // Djúpivogur
  [64.25, -15.20],  // Höfn
  // SE Iceland / glacial coast
  [63.95, -16.20],
  [63.68, -17.35],
  [63.55, -18.25],  // Vík
  [63.42, -18.99],
  // S coast back W
  [63.47, -20.23],
  [63.65, -21.00],
  [63.75, -21.92],
  [63.82, -22.69],  // back to start
];

// Bounding box with padding for the projection
export const BOUNDS = {
  latMin: 62.5,
  latMax: 67.2,
  lngMin: -26.0,
  lngMax: -12.0,
};
