/**
 * party_slugs.js — single source of truth for party-code ↔ URL slug mapping.
 *
 * Used by:
 *   - municipality.js (parse path-based URLs, generate share URLs)
 *   - map.js (front page muni shortcut links)
 *   - 404.html SPA fallback
 *   - scripts/build_static_pages.py (mirror this table — keep in sync)
 *
 * For local lists (e.g. BBK, MMM, IBU) the slug = lowercased code. National
 * parties have explicit human-readable slugs.
 */

export const PARTY_CODE_TO_SLUG = {
  D:  'sjalfstaedisflokkurinn',
  B:  'framsoknarflokkurinn',
  S:  'samfylkingin',
  V:  'vinstri-graen',
  A:  'vinstrid',
  P:  'piratar',
  M:  'midflokkurinn',
  F:  'flokkur-folksins',
  C:  'vidreisn',
  J:  'sosialistar',
  // Local lists (slugs are lowercased codes)
  GB: 'gardabaejarlistinn',
  AL: 'akureyrarlistinn',
  L:  'l-listinn',
  K:  'kex-frambod',
  E:  'eyjalisti',
  H:  'h-listinn',
  VM: 'vinir-mosfellsbaejar',
  OKH:'okkar-hveragerdi',
  SCS:'seltjarnarneslistinn',
  BBL:'borgarbyggdarlisti',
  G:  'godir-reykjavik',
  R:  'rodull',
};

export function partySlug(code) {
  return PARTY_CODE_TO_SLUG[code] || code.toLowerCase();
}

// Reverse map (built lazily; many local-list codes use lowercased-code as slug
// so the reverse map covers those by falling back to uppercasing the slug).
let _slugToCodeCache = null;
export function partyCodeFromSlug(slug, knownCodes = null) {
  if (!_slugToCodeCache) {
    _slugToCodeCache = {};
    for (const [code, s] of Object.entries(PARTY_CODE_TO_SLUG)) {
      _slugToCodeCache[s] = code;
    }
  }
  if (_slugToCodeCache[slug]) return _slugToCodeCache[slug];
  // Fallback: try uppercasing the slug (covers local lists where slug=lowercased code)
  const upper = slug.toUpperCase();
  if (knownCodes && knownCodes.includes(upper)) return upper;
  return upper;
}

/**
 * Slugify an Icelandic name for use in a URL.
 *   "Hörgársveit"  → "horgarsveit"
 *   "Þingeyjarsveit" → "thingeyjarsveit"
 *   "Kjartan Atli Kjartansson" → "kjartan-atli-kjartansson"
 *
 * Aggressive diacritic stripping: ð→d, þ→th, æ→ae, ö/ó/ú/ý/í/é/á → o/o/u/y/i/e/a.
 * Non-letters become hyphens; runs of hyphens collapsed; trimmed.
 */
export function slugify(s) {
  if (!s) return '';
  return s
    .toLowerCase()
    .replace(/ð/g, 'd')
    .replace(/þ/g, 'th')
    .replace(/æ/g, 'ae')
    .replace(/ö/g, 'o')
    .replace(/á/g, 'a')
    .replace(/é/g, 'e')
    .replace(/í/g, 'i')
    .replace(/ó/g, 'o')
    .replace(/ú/g, 'u')
    .replace(/ý/g, 'y')
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '');
}
