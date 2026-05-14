// ─── Recent Polls ────────────────────────────────────────────────────────────
// Per-municipality polling data. Each muni maps to an *array* of polls, sorted
// **newest first**. The UI renders the first poll by default and lets the user
// scroll horizontally back to older ones.
//
// Each poll entry: { source: {...}, totalSeats, parties: { LETTER: {pct, seats} } }
//   source.pollster — e.g. 'Maskína'
//   source.pollsterGen — Icelandic genitive ("Maskínu") for the label line
//   source.period   — human-readable date range (kept in IS by default; the
//                     UI label is i18n-aware around it)
//   source.sample   — n (or null)
//   source.url      — link back to the article reporting the poll
//   source.url_en   — optional EN translation of the article
//   source.url_pl   — optional PL translation of the article
//   parties.X.pct   — poll vote share in %
//   parties.X.seats — seats projected via D'Hondt against `totalSeats`
//
// Only parties present in the poll appear here. Any party absent from this
// map for a given municipality renders no poll block on its splash page.

export const POLLS = {

  // ── Reykjavík · 23 seats ────────────────────────────────────────────────────
  // Newest first.
  reykjavik: [
    {
      // Kosningaspá Vísis (Baldur Héðinsson), uppfærð 14. maí 2026 miðað við
      // nýjustu könnun Maskínu.
      // https://www.visir.is/g/20262883168d/kosningaspa-visis-stodug-leiki-ad-komast-a-fylgi-i-borginni
      // Numbers read exactly from the embedded Infogram bar chart
      // ("kosningaspa sulur BORGIN v5 - 14. maí 2026",
      //  https://e.infogram.com/d5209162-36b5-47ae-ba1d-f4bc10b644f9).
      // Sum of all 11 lists = 100.0.
      // D'Hondt vs 23 seats: D 7 · S 5 · A 3 · C 3 · M 2 · B 1 · J 1 · P 1
      // Matches the article's narrative: "Sjö sjálfstæðismenn, fimm
      // samfylkingarmenn"; Vinstrið með mestar líkur á þremur fulltrúum.
      totalSeats: 23,
      source: {
        pollster:    'Kosningaspá Vísis',
        pollsterGen: 'Kosningaspár Vísis',
        period:      '14. maí 2026',
        period_en:   'May 14, 2026',
        period_pl:   '14 maja 2026',
        sample:      null,
        url:         'https://www.visir.is/g/20262883168d/kosningaspa-visis-stodug-leiki-ad-komast-a-fylgi-i-borginni',
      },
      parties: {
        D: { pct: 28.4, seats: 7 },
        S: { pct: 19.9, seats: 5 },
        A: { pct: 12.5, seats: 3 },
        C: { pct: 11.4, seats: 3 },
        M: { pct:  8.7, seats: 2 },
        B: { pct:  5.2, seats: 1 },
        J: { pct:  4.2, seats: 1 },
        P: { pct:  4.2, seats: 1 },
        F: { pct:  3.2, seats: 0 },
        R: { pct:  1.3, seats: 0 },
        G: { pct:  1.0, seats: 0 },
      },
    },
    {
      // Maskína via Vísir, 29. apríl – 6. maí 2026 (n ekki tilgreint).
      // https://www.visir.is/g/20262879317d/sjalfstaedisflokkur-eykur-forskotid-a-samfylkingu-i-reykjavik
      // Numbers read from the embedded Infogram chart in the article
      // (https://e.infogram.com/319e63a6-75e6-4ec2-b0c7-328c07d78317).
      // Sum of all 11 lists = 99.9 (rounding).
      totalSeats: 23,
      source: {
        pollster:    'Maskína',
        pollsterGen: 'Maskínu',
        period:      '29. apríl – 6. maí 2026',
        period_en:   'April 29 – May 6, 2026',
        period_pl:   '29 kwietnia – 6 maja 2026',
        sample:      null,
        url:         'https://www.visir.is/g/20262879317d/sjalfstaedisflokkur-eykur-forskotid-a-samfylkingu-i-reykjavik',
      },
      parties: {
        D: { pct: 27.9, seats: 8 },
        S: { pct: 18.0, seats: 5 },
        A: { pct: 13.2, seats: 3 },
        C: { pct: 12.6, seats: 3 },
        M: { pct:  6.7, seats: 1 },
        B: { pct:  5.7, seats: 1 },
        J: { pct:  5.1, seats: 1 },
        P: { pct:  4.9, seats: 1 },
        F: { pct:  2.8, seats: 0 },
        R: { pct:  1.6, seats: 0 },
        G: { pct:  1.4, seats: 0 },
      },
    },
    {
      // Maskína via Vísir, 17.–24. apríl 2026, n=973
      // https://www.visir.is/g/20262873819d/bilid-a-milli-turnanna-breikkar
      // Seat projection: D'Hondt against 23 seats (two exact ties at this snapshot:
      // J vs P at 5,200, and C-3rd vs B-1st at 3,900 — would be drawn by lot
      // if the actual election landed on these numbers).
      totalSeats: 23,
      source: {
        pollster:    'Maskína',
        pollsterGen: 'Maskínu',
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
  ],

  // ── Hafnarfjörður · 11 seats ────────────────────────────────────────────────
  hafnarfjordur: [
    {
      // Maskína fyrir fréttastofu Vísis, 22.–27. apríl 2026 (n ekki tilgreint).
      // https://www.visir.is/g/20262876013d/vidreisn-upp-fyrir-sjalfstaedisflokk-og-framsokn-baetir-vid-sig
      // D'Hondt vs 11 seats: S 3 · C 3 · D 2 · B 2 · M 1 · A 0
      // Meirihluti D + B (2 + 2 = 4) er kolfallinn.
      totalSeats: 11,
      source: {
        pollster:    'Maskína',
        pollsterGen: 'Maskínu',
        period:      '22.–27. apríl 2026',
        period_en:   'April 22–27, 2026',
        period_pl:   '22–27 kwietnia 2026',
        sample:      null,
        url:         'https://www.visir.is/g/20262876013d/vidreisn-upp-fyrir-sjalfstaedisflokk-og-framsokn-baetir-vid-sig',
      },
      parties: {
        S: { pct: 24.2, seats: 3 },
        C: { pct: 22.4, seats: 3 },
        D: { pct: 22.1, seats: 2 },
        B: { pct: 14.9, seats: 2 },
        M: { pct:  9.7, seats: 1 },
        A: { pct:  6.8, seats: 0 },
      },
    },
  ],

  // ── Akureyri · 11 seats ─────────────────────────────────────────────────────
  akureyri: [
    {
      // Maskína fyrir DV, 17.–24. apríl 2026, n=629
      // https://www.dv.is/frettir/2026/4/26/ny-konnun-akureyri-samfylkingin-storsiglingu-en-oljost-hverjir-geta-myndad-meirihluta/
      // (Vísir summary: https://www.visir.is/g/20262874388d/samfylkingin-staerst-a-akureyri)
      // Seat distribution per article: S 3 · D 2 · L 2 · B 1 · C 1 · M 1 · V 1.
      // Akureyrarlistinn (AL) measures at 6 % and would not get a seat.
      totalSeats: 11,
      source: {
        pollster:    'Maskína',
        pollsterGen: 'Maskínu',
        period:      '17.–24. apríl 2026',
        period_en:   'April 17–24, 2026',
        period_pl:   '17–24 kwietnia 2026',
        sample:      629,
        url:         'https://www.dv.is/frettir/2026/4/26/ny-konnun-akureyri-samfylkingin-storsiglingu-en-oljost-hverjir-geta-myndad-meirihluta/',
      },
      parties: {
        S:  { pct: 18.4, seats: 3 },
        L:  { pct: 17.2, seats: 2 },
        D:  { pct: 16.7, seats: 2 },
        B:  { pct: 11.5, seats: 1 },
        V:  { pct: 11.5, seats: 1 },
        M:  { pct: 10.6, seats: 1 },
        C:  { pct:  8.1, seats: 1 },
        AL: { pct:  6.0, seats: 0 },
      },
    },
  ],

  // ── Kópavogur · 11 seats ────────────────────────────────────────────────────
  // Newest first.
  kopavogur: [
    {
      // Maskína fyrir Vísi, 29. apríl – 4. maí 2026 (n ekki tilgreint).
      // https://www.visir.is/g/20262878554d/ny-konnun-i-kopavogi-meirihlutinn-heldur-en-samfylking-a-siglingu
      // Seat distribution per article: D 5 · S 3 · C 1 · M 1 · B 1 (D+B meirihluti heldur með 6 sætum)
      totalSeats: 11,
      source: {
        pollster:    'Maskína',
        pollsterGen: 'Maskínu',
        period:      '29. apríl – 4. maí 2026',
        period_en:   'April 29 – May 4, 2026',
        period_pl:   '29 kwietnia – 4 maja 2026',
        sample:      null,
        url:         'https://www.visir.is/g/20262878554d/ny-konnun-i-kopavogi-meirihlutinn-heldur-en-samfylking-a-siglingu',
      },
      parties: {
        D: { pct: 37.3, seats: 5 },
        S: { pct: 23.2, seats: 3 },
        C: { pct: 11.7, seats: 1 },
        M: { pct: 11.2, seats: 1 },
        B: { pct:  8.0, seats: 1 },
        V: { pct:  5.3, seats: 0 },
        J: { pct:  3.3, seats: 0 },
      },
    },
    {
      // Eldri könnun: Maskína fyrir DV, apríl 2026 (article 25. apríl 2026;
      // chart label "Könnun apríl 2026"; n ekki tilgreint).
      // https://www.visir.is/g/20262874098d/samfylking-og-midflokkur-a-flugi-i-kopavogi
      // Seat distribution per article: D 4 · S 3 · C 2 · B 1 · M 1
      totalSeats: 11,
      source: {
        pollster:    'Maskína',
        pollsterGen: 'Maskínu',
        period:      'apríl 2026',
        period_en:   'April 2026',
        period_pl:   'kwiecień 2026',
        sample:      null,
        url:         'https://www.visir.is/g/20262874098d/samfylking-og-midflokkur-a-flugi-i-kopavogi',
      },
      parties: {
        D: { pct: 31.7, seats: 4 },
        S: { pct: 24.5, seats: 3 },
        C: { pct: 14.9, seats: 2 },
        M: { pct: 11.0, seats: 1 },
        B: { pct:  8.7, seats: 1 },
        V: { pct:  5.0, seats: 0 },
        J: { pct:  4.1, seats: 0 },
      },
    },
  ],

};
