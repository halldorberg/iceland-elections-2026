// ─── 2022 Municipal Election Results ─────────────────────────────────────────
// Source: Wikipedia IS – Sveitarstjórnarkosningar á Íslandi 2022
// Election date: 14 May 2022
//
// Each entry: { pct: number, seats: number, joint?: string }
//   pct    — vote share in % (from Wikipedia; may not sum to 100 when minor
//             parties/independents are excluded from the table)
//   seats  — seats won
//   joint  — if the party ran as part of a joint/coalition list
//
// Municipality-level flags:
//   sjalkjorinn: true  — óbundnar kosningar (unbound/uncontested election
//                        2022; candidates ran individually, no party lists)
//
// Parties absent from a municipality's parties map either:
//   (a) did not compete in 2022 → renders as "Nýtt framboð"
//   (b) ran as part of a joint list (use `joint` property instead)

export const RESULTS_2022 = {

  // ── Höfuðborgarsvæðið ──────────────────────────────────────────────────────

  // Reykjavík · 23 seats · Turnout ~61.1%
  reykjavik: {
    totalSeats: 23,
    parties: {
      D: { pct: 24.5, seats: 6 },
      S: { pct: 20.3, seats: 5 },
      B: { pct: 18.7, seats: 4 },
      P: { pct: 11.6, seats: 3 },
      J: { pct: 7.7,  seats: 2 },
      C: { pct: 5.2,  seats: 1 },
      F: { pct: 4.5,  seats: 1 },
      V: { pct: 4.0,  seats: 1 },
      M: { pct: 2.5,  seats: 0 },
      // A (Vinstrið = VG + Vor til vinstri) is new 2026 coalition → "Nýtt framboð"
    },
  },

  // Kópavogur · 11 seats · Turnout ~58.2%
  kopavogur: {
    totalSeats: 11,
    parties: {
      D: { pct: 33.2, seats: 4 },
      B: { pct: 15.2, seats: 2 },
      C: { pct: 10.7, seats: 1 },
      S: { pct: 8.2,  seats: 1 },
      V: { pct: 5.3,  seats: 0 },
      M: { pct: 2.6,  seats: 0 },
      // J (Sósíalistar) → "Nýtt framboð"
      // P (Píratar) had 9.53% 1 seat but not running 2026
      // Y (Vinir Kópavogs) had 15.31% 2 seats but not running 2026
    },
  },

  // Hafnarfjörður · 11 seats · Turnout ~60.4%
  hafnarfjordur: {
    totalSeats: 11,
    parties: {
      D: { pct: 30.7, seats: 4 },
      S: { pct: 29.0, seats: 4 },
      B: { pct: 13.7, seats: 2 },
      C: { pct: 9.1,  seats: 1 },
      M: { pct: 2.8,  seats: 0 },
      // A (Vinstrið) is new 2026 coalition → "Nýtt framboð"
    },
  },

  // Garðabær · 11 seats · Turnout ~64.0%
  gardabaer: {
    totalSeats: 11,
    parties: {
      D:  { pct: 49.1, seats: 7 },
      GB: { pct: 20.9, seats: 2 },  // Garðabæjarlistinn
      C:  { pct: 13.3, seats: 1 },
      B:  { pct: 13.1, seats: 1 },
      M:  { pct: 4.6,  seats: 0 },
      // S → "Nýtt framboð"
    },
  },

  // Mosfellsbær · 11 seats · Turnout ~62%
  mosfellsbaer: {
    totalSeats: 11,
    parties: {
      B: { pct: 32.2, seats: 4 },
      D: { pct: 27.3, seats: 4 },
      S: { pct: 9.0,  seats: 1 },
      C: { pct: 7.9,  seats: 1 },
      M: { pct: 4.9,  seats: 0 },
      // L (VG): VG ran as separate list with 5.7%, 0 seats
      L: { pct: 5.7, seats: 0, note: 'VG keppti sem sjálfstæður listi 2022' },
      // Vinir Mosfellsbæjar (VG-allied local list) had 13.0%, 1 seat separately
    },
  },

  // Seltjarnarnesbær · 7 seats · Turnout ~70.3%
  seltjarnarnes: {
    totalSeats: 7,
    parties: {
      D:   { pct: 50.1,  seats: 4 },
      SCS: { pct: 40.81, seats: 3, joint: 'Samfylkingin keppti ein 2022' },
      // M → "Nýtt framboð"
    },
  },

  // Kjósarhreppur · 5 seats
  kjosarhreppur: {
    totalSeats: 5,
    parties: {
      KJA: { pct: 48.7, seats: 3 },  // Íbúar í Kjós
      // Saman í sveit had 44.50% 2 seats but not in 2026 partyIds
    },
  },

  // ── Suðurnes ───────────────────────────────────────────────────────────────

  // Reykjanesbær · 11 seats · Turnout ~58.5%
  reykjanesbaer: {
    totalSeats: 11,
    parties: {
      D: { pct: 28.1, seats: 3 },
      B: { pct: 22.6, seats: 3 },
      S: { pct: 22.1, seats: 3 },
      // Bein leið 12.83% 1 seat — not in 2026
      // Umbót 8.43% 1 seat — not in 2026
      // C and M → "Nýtt framboð"
    },
  },

  // Suðurnesjabær · 9 seats
  sudurnesjabaer: {
    totalSeats: 9,
    parties: {
      D: { pct: 29.5, seats: 3 },
      S: { pct: 25.1, seats: 2 },
      B: { pct: 18.9, seats: 2 },
      // Bæjarlistinn 26.52% 2 seats — not in 2026 partyIds
      // M → "Nýtt framboð"
    },
  },

  // Grindavíkurbær · 7 seats
  grindavik: {
    totalSeats: 7,
    parties: {
      M: { pct: 32.4, seats: 3 },
      D: { pct: 24.8, seats: 2 },
      B: { pct: 20.2, seats: 1 },
      // Rödd unga fólksins 13.24% 1 seat — not in 2026
    },
  },

  // Sveitarfélagið Vogar · 7 seats
  vogar: {
    totalSeats: 7,
    parties: {
      D:   { pct: 39.1, seats: 3 },
      VOE: { pct: 37.0, seats: 3 },  // Framboðsfélag E-listans
      VOL: { pct: 23.9, seats: 1 },  // Listi fólksins
      // FYRS → "Nýtt framboð"
    },
  },

  // ── Vesturland ─────────────────────────────────────────────────────────────

  // Akranes · 9 seats — þrennur jafnt
  akranes: {
    totalSeats: 9,
    parties: {
      D: { pct: 36.1, seats: 3 },
      B: { pct: 35.6, seats: 3 },
      S: { pct: 28.3, seats: 3 },
      // C and M → "Nýtt framboð"
    },
  },

  // Borgarbyggð · 9 seats
  borgarbyggd: {
    totalSeats: 9,
    parties: {
      B: { pct: 49.7, seats: 5 },
      D: { pct: 25.4, seats: 2 },
      // S+C joint list (14.42% 1 seat) → BBL is new 2026 list
      // VG (10.54% 1 seat) not in 2026 partyIds
      // M → "Nýtt framboð"
    },
  },

  // Snæfellsbær · 7 seats
  snaefellsbaer: {
    totalSeats: 7,
    parties: {
      D: { pct: 52.8, seats: 4 },
      // Bæjarmálasamtök Snæfellsbæjar 47.16% 3 seats — not in 2026
    },
  },

  // Sveitarfélagið Stykkishólmur · 7 seats
  stykkisholmur: {
    totalSeats: 7,
    parties: {
      FLS: { pct: 54.7, seats: 4 },  // Listi framfarasinna (H-listinn)
      IBU: { pct: 45.3, seats: 3 },  // Íbúalistinn
    },
  },

  // Grundarfjarðarbær · 7 seats
  grundarfjordur: {
    totalSeats: 7,
    parties: {
      GFD: { pct: 52.0, seats: 4 },  // Sjálfstæðisflokkurinn og óháðir
      GFB: { pct: 48.0, seats: 3 },  // Samstaða bæjarmálafélag
    },
  },

  // Hvalfjarðarsveit — óbundnar kosningar 2022
  hvalfjardarsveit: { sjalkjorinn: true, totalSeats: 7 },

  // Dalabyggð — óbundnar kosningar 2022
  dalabyggd: { sjalkjorinn: true, totalSeats: 7 },

  // Eyja- og Miklaholtshreppur — óbundnar kosningar 2022
  eyjamiklaholts: { sjalkjorinn: true, totalSeats: 5 },

  // ── Vestfirðir ─────────────────────────────────────────────────────────────

  // Ísafjarðarbær · 9 seats · Turnout ~73.8%
  // S, C, VG and independents ran as joint Í-listi in 2022
  isafjordur: {
    totalSeats: 9,
    parties: {
      B: { pct: 24.4, seats: 2 },
      D: { pct: 24.7, seats: 2 },
      S: { pct: 46.3, seats: 5, joint: 'Í-lista (S + C + VG + óháðir)' },
      C: { pct: 46.3, seats: 5, joint: 'Í-lista (S + C + VG + óháðir)' },
      // M → "Nýtt framboð"
    },
  },

  // Vesturbyggð · 7 seats
  vesturbyggd: {
    totalSeats: 7,
    parties: {
      NYS: { pct: 51.7, seats: 4 },  // Ný sýn
      STV: { pct: 48.2, seats: 3 },  // Sjálfstæðisflokkurinn
    },
  },

  // Bolungarvíkurkaupstaður · 7 seats
  bolungarvik: {
    totalSeats: 7,
    parties: {
      MMM: { pct: 53.5, seats: 4 },  // Máttur manna og meyja
      BBK: { pct: 46.5, seats: 3 },  // Sjálfstæðisflokkurinn
    },
  },

  // Strandabyggð · 5 seats
  strandabyggd: {
    totalSeats: 5,
    parties: {
      SBD: { pct: 60.2, seats: 3 },  // Strandabandalagið
      // VGV (Vegvísir, X-G) — new 2026 list, NOT a continuation of the
      // 2022 A-list "Almennir borgarar" → "Nýtt framboð"
      // B (Framsókn) — also new 2026 → "Nýtt framboð"
    },
  },

  // Súðavíkurhreppur — óbundnar kosningar 2022
  sudavik: { sjalkjorinn: true, totalSeats: 5 },

  // Reykhólahreppur — óbundnar kosningar 2022
  reykholar: { sjalkjorinn: true, totalSeats: 5 },

  // Kaldrananeshreppur — óbundnar kosningar 2022
  kaldrananes: { sjalkjorinn: true, totalSeats: 5 },

  // Árneshreppur — óbundnar kosningar 2022
  arneshr: { sjalkjorinn: true, totalSeats: 5 },

  // ── Norðurland vestra ──────────────────────────────────────────────────────

  // Sveitarfélagið Skagafjörður · 9 seats · Turnout ~68%
  skagafjordur: {
    totalSeats: 9,
    parties: {
      B:   { pct: 32.3, seats: 3 },
      SFL: { pct: 24.7, seats: 2 },  // Byggðalistinn
      D:   { pct: 22.8, seats: 2 },
      // VG og óháðir 20.19% 2 seats — not in 2026 partyIds
      // M → "Nýtt framboð"
    },
  },

  // Húnabyggð (Blönduós og Húnavatnshreppur) · 9 seats
  hunabyggd: {
    totalSeats: 9,
    parties: {
      D:   { pct: 37.7, seats: 4 },
      B:   { pct: 31.7, seats: 3 },
      HBA: { pct: 17.8, seats: 1 },  // H-listinn
      // Gerum þetta saman 12.74% 1 seat — not in 2026
    },
  },

  // Húnaþing vestra · 7 seats
  hunathing: {
    totalSeats: 7,
    parties: {
      B:   { pct: 34.6, seats: 3 },
      NHV: { pct: 34.1, seats: 2 },  // Nýtt afl í Húnaþingi vestra
      D:   { pct: 31.3, seats: 2 },
    },
  },

  // Sveitarfélagið Skagaströnd — óbundnar kosningar (single list) 2022
  skagastrond: { sjalkjorinn: true, totalSeats: 5 },

  // ── Norðurland eystra ──────────────────────────────────────────────────────

  // Akureyri · 11 seats · Turnout ~65.4%
  akureyri: {
    totalSeats: 11,
    parties: {
      L: { pct: 18.7, seats: 3 },  // Bæjarlisti Akureyrar
      D: { pct: 18.0, seats: 2 },
      B: { pct: 17.0, seats: 2 },
      S: { pct: 11.9, seats: 1 },
      M: { pct: 7.9,  seats: 1 },
      V: { pct: 7.3,  seats: 1 },
      // F (Flokkur fólksins) 12.21% 1 seat — not in 2026
      // C and A → "Nýtt framboð"
    },
  },

  // Norðurþing · 9 seats
  nordurping: {
    totalSeats: 9,
    parties: {
      B:   { pct: 32.8, seats: 3 },  // Framsókn og félagshyggja
      D:   { pct: 24.8, seats: 2 },
      NPV: { pct: 17.6, seats: 2 },  // Vinstri grænt framboð og óháðir
      NPM: { pct: 15.2, seats: 1 },  // Samfélagið
      S:   { pct: 13.5, seats: 1 },
    },
  },

  // Fjallabyggð · 7 seats
  fjallabyggd: {
    totalSeats: 7,
    parties: {
      S: { pct: 33.7, seats: 3 },  // Jafnaðarfólk og óháðir (S-tengdur)
      D: { pct: 30.1, seats: 2 },
      H: { pct: 29.3, seats: 2 },  // Fyrir heildina
    },
  },

  // Dalvíkurbyggð · 7 seats
  dalvikurbyggd: {
    totalSeats: 7,
    parties: {
      DVK: { pct: 32.4, seats: 3 },  // K-listi Dalvíkurbyggðar
      D:   { pct: 24.4, seats: 2 },
      DVA: { pct: 21.9, seats: 2 },  // Framsókn og félagshyggjufólk
      // B → "Nýtt framboð" (separate list in 2026)
    },
  },

  // Þingeyjarsveit og Skútustaðahreppur · 9 seats
  thingeyjarsveit: {
    totalSeats: 9,
    parties: {
      THVA: { pct: 54.6, seats: 5 },  // E-listi
      THVL: { pct: 44.6, seats: 4 },  // K-listi
      // THVN → "Nýtt framboð"
    },
  },

  // Eyjafjarðarsveit · 7 seats
  eyjafjardarsveit: {
    totalSeats: 7,
    parties: {
      EJF: { pct: 57.9, seats: 4 },  // F-listi
      EJK: { pct: 40.3, seats: 3 },  // K-listi
    },
  },

  // Hörgársveit · 5 seats
  horgarsv: {
    totalSeats: 5,
    parties: {
      HGH: { pct: 57.0, seats: 3 },  // Gróska
      HGG: { pct: 35.8, seats: 2 },  // H-listi Hörgársveitar
      // D → "Nýtt framboð"
    },
  },

  // Svalbarðsstrandarhreppur · 5 seats
  svalbardsstrond: {
    totalSeats: 5,
    parties: {
      SVSS: { pct: 52.7, seats: 3 },  // Strandarlistinn
      SVSH: { pct: 47.3, seats: 2 },  // Ströndungur
      // SVSO → "Nýtt framboð"
    },
  },

  // Grýtubakkahreppur — óbundnar kosningar 2022
  grytubakkar: { sjalkjorinn: true, totalSeats: 3 },

  // Tjörneshreppur — einn listi, óbundnar kosningar 2022
  tjornes: { sjalkjorinn: true, totalSeats: 3 },

  // ── Austurland ─────────────────────────────────────────────────────────────

  // Fjarðabyggð · 9 seats · Turnout ~63.6%
  fjardabyggd: {
    totalSeats: 9,
    parties: {
      D: { pct: 32.1, seats: 4 },
      B: { pct: 23.7, seats: 3 },
      // Fjarðarlistinn 18.41% 2 seats — not in 2026 partyIds
      // V (VG) 4.81% 0 seats — not in 2026
      // M and S → "Nýtt framboð"
    },
  },

  // Múlaþing · 11 seats
  mulathing: {
    totalSeats: 11,
    parties: {
      D: { pct: 23.9, seats: 3 },
      B: { pct: 20.5, seats: 3 },
      L: { pct: 16.4, seats: 2 },  // Austurlistinn
      V: { pct: 13.7, seats: 2 },  // Vinstri græn
      M: { pct: 7.2,  seats: 1 },
    },
  },

  // Vopnafjarðarhreppur · 7 seats
  // In 2026, B og Vopnafjarðarlistinn run as single merged list VOP
  vopnafjordur: {
    totalSeats: 7,
    parties: {
      // VOP (merger of B + Vopnafjarðarlistinn formed for 2026) → "Nýtt framboð"
    },
  },

  // Fljótsdalshreppur — óbundnar kosningar 2022
  fljotsdalshr: { sjalkjorinn: true, totalSeats: 3 },

  // ── Suðurland ──────────────────────────────────────────────────────────────

  // Sveitarfélagið Árborg · 11 seats
  arborg: {
    totalSeats: 11,
    parties: {
      D: { pct: 35.1, seats: 6 },
      B: { pct: 14.6, seats: 2 },
      S: { pct: 11.6, seats: 2 },
      // Áfram Árborg 5.96% 1 seat — not in 2026
      // M 3.77% 0, V 4.50% 0 — not in 2026
      // C → "Nýtt framboð"
    },
  },

  // Vestmannaeyjar · 9 seats · Turnout ~67.2%
  vestmannaeyjar: {
    totalSeats: 9,
    parties: {
      D: { pct: 35.1, seats: 4 },
      E: { pct: 16.0, seats: 2 },  // Eyjalistinn
      // Fyrir Heimaey 28.40% 3 seats — not in 2026 partyIds
      // M → "Nýtt framboð"
    },
  },

  // Hveragerðisbær · 7 seats
  hveragerdi: {
    totalSeats: 7,
    parties: {
      OKH: { pct: 27.8, seats: 3 },  // Okkar Hveragerði
      D:   { pct: 23.0, seats: 2 },
      B:   { pct: 19.3, seats: 2 },
      // S → "Nýtt framboð"
    },
  },

  // Sveitarfélagið Ölfus · 7 seats
  olfus: {
    totalSeats: 7,
    parties: {
      D: { pct: 38.6, seats: 4 },
      // Framfarasinnar (B-tengdur) 21.03% 2 seats — not in 2026
      // Íbúalisti 9.44% 1 seat — not in 2026
      // S → "Nýtt framboð"
    },
  },

  // Rangárþing eystra · 7 seats
  rangarthingeystra: {
    totalSeats: 7,
    parties: {
      D:   { pct: 38.3, seats: 3 },
      B:   { pct: 32.8, seats: 3 },
      NRE: { pct: 19.3, seats: 1 },  // Nýi óháði listinn
    },
  },

  // Rangárþing ytra · 7 seats
  rangarthingytra: {
    totalSeats: 7,
    parties: {
      RYA: { pct: 50.8, seats: 4 },  // Áhugafólk um sveitarstjórnarmál
      D:   { pct: 49.6, seats: 3 },
    },
  },

  // Bláskógabyggð · 7 seats
  blaskogabyggd: {
    totalSeats: 7,
    parties: {
      BST: { pct: 70.2, seats: 5 },  // T-listinn
      BSP: { pct: 29.8, seats: 2 },  // Þ-listinn
    },
  },

  // Hrunamannahreppur · 5 seats
  hrunamannahreppur: {
    totalSeats: 5,
    parties: {
      D:   { pct: 55.9, seats: 3 },
      HRL: { pct: 43.0, seats: 2 },  // L-listinn í Hrunamannahreppi
    },
  },

  // Mýrdalshreppur · 5 seats
  myrdalshr: {
    totalSeats: 5,
    parties: {
      MYA: { pct: 53.3, seats: 3 },  // Framsókn og óháðir
      MYZ: { pct: 46.7, seats: 2 },  // Listi allra
    },
  },

  // Flóahreppur · 5 seats
  floahreppur: {
    totalSeats: 5,
    parties: {
      FLI: { pct: 66.4, seats: 3 },  // Framfaralistinn
      FLT: { pct: 33.6, seats: 2 },  // T-listinn í Flóahreppi
    },
  },

  // Skeiða- og Gnúpverjahreppur · 5 seats
  skeidagnup: {
    totalSeats: 5,
    parties: {
      SGL: { pct: 52.9, seats: 3 },  // Samvinnulistinn
      SGE: { pct: 32.7, seats: 1 },  // Uppbygging
      // Umhyggja, umhverfi, uppbygging 19.38% 1 seat — not in 2026
    },
  },

  // Grímsnes- og Grafningshreppur · 5 seats
  grimsnesgrafningur: {
    totalSeats: 5,
    parties: {
      GGA: { pct: 51.0, seats: 3 },  // E-listinn (Óháðir lýðræðissinnar)
      GGO: { pct: 49.0, seats: 2 },  // G-listinn (Framboðslisti um framsýni)
    },
  },

  // Skaftárhreppur · 5 seats
  skaftarhreppur: {
    totalSeats: 5,
    parties: {
      SKO: { pct: 74.1, seats: 4 },  // Öflugt samfélag
      D:   { pct: 26.0, seats: 1 },
    },
  },

  // Ásahreppur — óbundnar kosningar 2022
  asahr: { sjalkjorinn: true, totalSeats: 3 },

};
