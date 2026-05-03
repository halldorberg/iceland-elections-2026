// ─── Recent Polls ────────────────────────────────────────────────────────────
// Per-municipality polling data, rendered alongside the 2022 election results.
// Each muni entry: { source: {...}, totalSeats, parties: { LETTER: {pct, seats} } }
//   source.pollster — e.g. 'Maskína'
//   source.period   — human-readable date range (kept in IS by default; the
//                     UI label is i18n-aware around it)
//   source.sample   — n
//   source.url      — link back to the article reporting the poll
//   source.url_en   — optional EN translation of the article
//   source.url_pl   — optional PL translation of the article
//   parties.X.pct   — poll vote share in %
//   parties.X.seats — seats projected via D'Hondt against `totalSeats`
//
// Only parties present in the poll appear here. Any party absent from this
// map for a given municipality renders no poll block on its splash page.

export const POLLS = {

  // Reykjavík · 23 seats
  // Source: Maskína via Vísir, 17.–24. apríl 2026, n=973
  // https://www.visir.is/g/20262873819d/bilid-a-milli-turnanna-breikkar
  // Seat projection: D'Hondt against 23 seats (two exact ties at this snapshot:
  // J vs P at 5,200, and C-3rd vs B-1st at 3,900 — would be drawn by lot
  // if the actual election landed on these numbers).
  reykjavik: {
    totalSeats: 23,
    source: {
      pollster:    'Maskína',   // nominative (used in source line)
      pollsterGen: 'Maskínu',   // Icelandic genitive (used in 'Skoðanakönnun X' label)
      period:      '17.–24. apríl 2026',
      period_en:   'April 17–24, 2026',
      period_pl:   '17–24 kwietnia 2026',
      sample:      973,
      url:         'https://www.visir.is/g/20262873819d/bilid-a-milli-turnanna-breikkar',
    },
    parties: {
      D: { pct: 25.4, seats: 7 },
      S: { pct: 21.0, seats: 5 },
      C: { pct: 11.7, seats: 3 },
      A: { pct: 10.6, seats: 3 },
      M: { pct: 10.0, seats: 2 },
      J: { pct:  5.2, seats: 1 },
      P: { pct:  5.2, seats: 1 },
      B: { pct:  3.9, seats: 1 },
      F: { pct:  2.8, seats: 0 },
      R: { pct:  2.6, seats: 0 },
      G: { pct:  1.6, seats: 0 },
    },
  },

};
