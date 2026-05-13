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
  // Mapped local lists (declared name)
  GB:  'gardabaejarlistinn',
  AL:  'akureyrarlistinn',
  L:   'l-listinn',
  K:   'kex-frambod',
  E:   'eyjalisti',
  H:   'h-listinn',
  VM:  'vinir-mosfellsbaejar',
  OKH: 'okkar-hveragerdi',
  SCS: 'seltjarnarneslistinn',
  BBL: 'borgarbyggdarlisti',
  G:   'godan-daginn',
  R:   'okkar-borg',
  // Per-muni local lists. Real declared names get a name slug; bare
  // letter-listi entries get '<letter>-listinn'.
  FYRS: 'fyrir-samfelagid',          // Vogar — Fyrir samfélagið
  VOE:  'e-listinn',                 // Vogar — E-listinn
  VOL:  'l-listinn',                 // Vogar — L-listinn
  NPM:  'm-listi-samfelagsins',      // Norðurþing — M-Listi Samfélagsins
  NBO:  'oskalistinn',               // Norðurþing — Óskalistinn
  NPV:  'v-listi-velferdar',         // Norðurþing — V-listi Velferðar
  NRE:  'nytt-sjalfstaett-frambod',  // Rangárþing eystra — Nýtt sjálfstætt framboð
  RYA:  'a-listinn',                 // Rangárþing ytra — Á-listinn
  SKO:  'oflugt-samfelag',           // Skaftárhreppur — Öflugt samfélag
  MYA:  'listi-allra',               // Mýrdalshreppur — Listi allra
  MYZ:  'listi-samfelagsins',        // Mýrdalshreppur — Listi Samfélagsins
  BST:  't-listinn',                 // Bláskógabyggð — T-listinn
  BSP:  'th-listinn',                // Bláskógabyggð — Þ-listinn
  FLI:  'framfaralistinn',           // Flóahreppur — Framfaralistinn
  FLT:  't-listinn-floa',            // Flóahreppur — T-listinn Flóa
  HRL:  'l-listinn',                 // Hrunamannahreppur — L-listinn
  GGA:  'a-listinn',                 // Grímsnes/Grafningur — A-listinn
  GGO:  'o-listinn-betri-sveit',     // Grímsnes/Grafningur — Ö-listinn Betri sveit
  SGE:  'uppbyggingarlistinn',       // Skeiða- og Gnúpverjahreppur — Uppbyggingarlistinn
  SGL:  'samvinnulistinn',           // Skeiða- og Gnúpverjahreppur — Samvinnulistinn
  EJF:  'f-listinn',                 // Eyjafjarðarsveit — F-listinn
  EJK:  'k-listinn',                 // Eyjafjarðarsveit — K-listinn
  HGG:  'groska',                    // Hörgársveit — Gróska
  HGH:  'h-listinn',                 // Hörgársveit — H-listi
  HBA:  'oll-saman',                 // Húnabyggð — Öll saman
  NHV:  'ny-ofl',                    // Húnaþing vestra — Ný öfl
  SFL:  'byggdalistinn',             // Skagafjörður — Byggðalistinn
  HFJK: 'kex-frambod',               // Hornafjörður — Kex Framboð
  FLS:  'framfaralisti-stykkisholms',// Stykkishólmur — Framfaralisti
  IBU:  'ibualistinn',               // Stykkishólmur — Íbúalistinn
  GFB:  'framsokn-samfylking',       // Grundarfjörður — Framsókn og Samfylking
  GFD:  'sjalfstaedi-ohadir',        // Grundarfjörður — Sjálfstæðisflokkur og óháðir
  MMM:  'mattur-meyja-og-manna',     // Bolungarvík — Máttur meyja og manna
  BBK:  'betri-bolungarvik',         // Bolungarvík — Betri Bolungarvík
  FJL:  'fjardarlistinn',            // Súðavík — Fjarðarlistinn
  FTL:  'framtidarlistinn',          // Súðavík — Framtíðarlistinn
  NYS:  'nyrra-synar',               // Vesturbyggð — Nýrra sýnar
  STV:  'sterkari-vesturbyggd',      // Vesturbyggð — Sterkari Vesturbyggð
  VGV:  'vegvisir',                  // Strandabyggð — Vegvísir
  SBD:  'strandabandalagid',         // Strandabyggð — Strandabandalagið
  ROA:  'raddir-okkar-allra',        // Reykhólar — Raddir okkar allra
  THVA: 'a-listinn',                 // Þingeyjarsveit — A-listi
  THVL: 'l-listinn',                 // Þingeyjarsveit — L-listi
  THVN: 'n-listinn',                 // Þingeyjarsveit — N-listi
  HVA:  'samhent-sveit',             // Hvalfjarðarsveit — Samhent sveit
  HVB:  'ibuahreyfingin',            // Hvalfjarðarsveit — Íbúahreyfingin
  SVSS: 's-listinn',                 // Svalbarðsstrandarhr. — S-listi
  SVSH: 'strond-til-framtidar',      // Svalbarðsstrandarhr. — Strönd til framtíðar
  SVSO: 'strondungur',               // Svalbarðsstrandarhr. — Ströndungur
  KJA:  'ibuar-i-kjos',              // Kjósarhreppur — Íbúar í Kjós
  VOP:  'eitt-frambod',              // Vopnafjörður — eitt framboð
  TJN:  'eitt-frambod',              // Tjörnes — Eitt framboð
  ARNA: 'a-listinn',                 // Árneshreppur — Á-listi
  ARNS: 's-listinn',                 // Árneshreppur — S-listi
};

export function partySlug(code) {
  return PARTY_CODE_TO_SLUG[code] || code.toLowerCase();
}

// Reverse map (built lazily). One slug can map to MULTIPLE codes — e.g.
// 'h-listinn' is shared by the global H code and per-muni local lists
// like HGH (Hörgársveit). So we keep ALL candidate codes per slug and
// filter by `knownCodes` (the muni's partyIds) at lookup time so the
// caller always gets the code that actually exists in their muni.
let _slugToCodesCache = null;
export function partyCodeFromSlug(slug, knownCodes = null) {
  if (!_slugToCodesCache) {
    _slugToCodesCache = {};
    for (const [code, s] of Object.entries(PARTY_CODE_TO_SLUG)) {
      if (!_slugToCodesCache[s]) _slugToCodesCache[s] = [];
      _slugToCodesCache[s].push(code);
    }
  }
  const candidates = _slugToCodesCache[slug] || [];
  // If we have a muni's known codes, pick the one that actually belongs.
  if (knownCodes && knownCodes.length) {
    for (const c of candidates) if (knownCodes.includes(c)) return c;
    // Fallback: try uppercasing the slug (per-muni codes use lowercased-code as slug)
    const upper = slug.toUpperCase();
    if (knownCodes.includes(upper)) return upper;
  }
  // No muni filter — return the first cached candidate, else upper.
  if (candidates.length) return candidates[0];
  return slug.toUpperCase();
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
