/**
 * i18n.js — UI string translations
 * Covers all hardcoded interface text. Data translations live in
 * js/data/candidates.en.js and js/data/candidates.pl.js.
 */

// Icelandic dative ("í <staður>") for every muni. Used by the cleavages
// compare-modal title and anywhere else that needs natural Icelandic
// phrasing. Hand-mapped — there is no general grammar rule that works
// for compound names ("Sveitarfélagið Hornafjörður" → "Hornafirði" needs
// stripping the prefix; "Vestmannaeyjar" → "Vestmannaeyjum" is irregular plural).
export const MUNI_DATIVE_IS = {
  reykjavik:           'Reykjavík',
  kopavogur:           'Kópavogi',
  hafnarfjordur:       'Hafnarfirði',
  gardabaer:           'Garðabæ',
  mosfellsbaer:        'Mosfellsbæ',
  akureyri:            'Akureyri',
  arborg:              'Árborg',
  akranes:             'Akranesi',
  isafjordur:          'Ísafjarðarbæ',
  nordurping:          'Norðurþingi',
  fjardabyggd:         'Fjarðabyggð',
  vestmannaeyjar:      'Vestmannaeyjum',
  borgarbyggd:         'Borgarbyggð og Skorradalshreppi',
  hornafjordur:        'Hornafirði',
  fjallabyggd:         'Fjallabyggð',
  seltjarnarnes:       'Seltjarnarnesbæ',
  reykjanesbaer:       'Reykjanesbæ',
  vogar:               'Vogum',
  grindavik:           'Grindavík',
  sudurnesjabaer:      'Suðurnesjabæ',
  stykkisholmur:       'Stykkishólmi',
  grundarfjordur:      'Grundarfirði',
  bolungarvik:         'Bolungarvík',
  sudavik:             'Súðavík',
  vesturbyggd:         'Vesturbyggð',
  strandabyggd:        'Strandabyggð',
  reykholar:           'Reykhólahreppi',
  hveragerdi:          'Hveragerði',
  rangarthingeystra:   'Rangárþingi eystra',
  rangarthingytra:     'Rangárþingi ytra',
  olfus:               'Ölfusi',
  skaftarhreppur:      'Skaftárhreppi',
  myrdalshr:           'Mýrdalshreppi',
  blaskogabyggd:       'Bláskógabyggð',
  floahreppur:         'Flóahreppi',
  hrunamannahreppur:   'Hrunamannahreppi',
  grimsnesgrafningur:  'Grímsnes- og Grafningshreppi',
  skeidagnup:          'Skeiða- og Gnúpverjahreppi',
  dalvikurbyggd:       'Dalvíkurbyggð',
  eyjafjardarsveit:    'Eyjafjarðarsveit',
  horgarsv:            'Hörgársveit',
  hunabyggd:           'Húnabyggð',
  hunathing:           'Húnaþingi vestra',
  skagafjordur:        'Skagafirði',
  skagastrond:         'Skagaströnd',
  mulathing:           'Múlaþingi',
  thingeyjarsveit:     'Þingeyjarsveit',
  svalbardsstrond:     'Svalbarðsstrandarhreppi',
  hvalfjardarsveit:    'Hvalfjarðarsveit',
  snaefellsbaer:       'Snæfellsbæ',
  kjosarhreppur:       'Kjósarhreppi',
  vopnafjordur:        'Vopnafjarðarhreppi',
  tjornes:             'Tjörneshreppi',
  grytubakkar:         'Grýtubakkahreppi',
  arneshr:             'Árneshreppi',
  kaldrananes:         'Kaldrananeshreppi',
  dalabyggd:           'Dalabyggð',
  eyjamiklaholts:      'Eyja- og Miklaholtshreppi',
  asahr:               'Ásahreppi',
  fljotsdalshr:        'Fljótsdalshreppi',
  langanesbyggd:       'Langanesbyggð',
};

export const UI = {
  is: {
    // Nav / header
    backToMap:        'Til baka á kort',
    share:            'Deila',
    openParty:        'Opna',
    language:         'Tungumál',
    breadcrumbHome:   'Heim',

    // Map page
    heroTitle:        'Velkomin í <span>lýðræðisveisluna!</span>',
    heroSubtitle:     'Smelltu á sveitarfélag á kortinu til að bera saman á einum stað alla flokka, frambjóðendur og stefnur þeirra.',
    heroIntro:        'Finndu út allt um öll framboð fyrir sveitarstjórnarkosningarnar 16. maí 2026 á einum stað. Sjáðu frambjóðendur, stefnumál og fréttir í þínu sveitarfélagi.',
    heroIntroEmphasis:'Taktu upplýsta ákvörðun fyrir kjördag.',
    pageTitleHome:    'Lýðræðisveislan 2026 — Sveitarstjórnarkosningar á Íslandi',
    pageDescHome:     'Sjáðu öll framboð, frambjóðendur og stefnumál fyrir sveitarstjórnarkosningarnar 16. maí 2026 á Íslandi á einum stað. Berðu saman flokka og kjóstu upplýst.',
    statMunicipalities: 'Sveitarfélög',
    statParties:      'Framboðslistar',
    statCandidates:   'Frambjóðendur',
    mapOverlayTitle:  'Veldu sveitarfélag',
    mapOverlayDesc:   'Sveipa yfir merkið til að sjá upplýsingar · Smelltu til að fara inn',
    legendTitle:      'Flokkar',
    instrHover:       'Sveipa yfir merkið til að sjá upplýsingar',
    instrClick:       'Smelltu til að fara inn í sveitarfélagið',
    instrZoom:        'Þys inn og út á kortinu',
    muniSearchPlaceholder: 'Leita að sveitarfélagi…',
    electionDate:     'Kosningar 16. maí 2026',
    cdDays: 'dagar', cdHours: 'klst', cdMins: 'mín', cdSecs: 'sek',
    cdElectionDay:    '🗳️ Kosningadagur!',
    mapTooltipCTA:    'Smelltu til að sjá nánar',
    unboundNote:      'Allir kjörgengar einstaklingar geta boðið sig fram — engar formlegar listur.',

    // Municipality page
    population:       'íbúar',
    region:           'Landshluti',
    randomTooltipOpen: (name) => `Opnaði ${name} af handahófi`,

    // Election type notices
    unboundBadge:     'Óbundnar kosningar',
    unboundTitle:     (name) => `Óbundnar kosningar í ${name}`,
    unboundDesc:      'Í þessum kosningum eru engar formlegar framboðslistur. Allir kjörgengar einstaklingar í sveitarfélaginu teljast sjálfkrafa frambjóðendur nema þeir afþakki sérstaklega. Kjósendur gefa atkvæði með persónulegri atkvæðagreiðslu fremur en að kjósa eftir listum — það þýðir að hægt er að greiða atkvæði til hvaða kjörgengs einstaklings sem er í sveitarfélaginu.',
    unopposedBadge:   'Sjálfkjörið',
    unopposedTitle:   (name) => `Sjálfkjörið í ${name}`,
    unopposedDesc:    'Aðeins einn framboðslisti bauð sig fram og var hann samþykktur án kosninga. Þegar fjöldi frambjóðenda á einum lista samsvarar fjölda sæta í sveitarstjórn — eða er færri — er engin ástæða til kosninga og meðlimir listans fara sjálfkrafa inn í sveitarstjórnina. Hægt er að skoða listann hér að neðan.',

    // Results 2022
    results2022Label:  '📊 Kosningaúrslit 2022',
    votes:             'atkvæða',
    noSeats:           'Engin sæti',
    ofSeats:           (n) => `af ${n} sætum`,
    resultsNew:        '✨ Nýtt framboð — tók ekki þátt árið 2022',
    resultsUncontested2022: '🤝 Óbundnar kosningar — engir listar 2022',
    resultsJoint:      (name) => `Keppti sem hluti af ${name}`,

    // Recent poll
    pollLabel:         (pollster, pollsterGen) => `📈 Skoðanakönnun ${pollsterGen || pollster}`,
    pollSource:        (pollster, period, n) => `Heimild: ${pollster}, ${period}${n ? ` (n=${n})` : ''}`,
    pollSeatsHint:     'Sæti reiknuð skv. d\'Hondt-reglu',
    olderPollTag:      'Eldri könnun',
    olderPollNav:      'Sjá eldri könnun',
    newerPollNav:      'Sjá nýrri könnun',
    pollCarouselHint:  'Smellið á örvarnar til að skoða eldri kannanir',
    electedFrameLabel: 'Kæmist inn samkvæmt nýjustu skoðanakönnun',

    // Party splash
    noPlatformTitle:  'Stefnuskrá ekki til staðar',
    noPlatformDesc:   'Við höfum ekki fundið staðfesta stefnuskrá þessa framboðs og birtum því engar áherslugreinar.',
    noPlatformCTA:    'Ertu frambjóðandi? Hafðu samband! →',
    platformSource:   (host) => `Heimild: ${host}`,

    // Cleavages carousel — RÚV kosningapróf
    cleavagesHeader:    'Klofningsmál samkvæmt kosningaprófi Rúv',
    cleavagesScrollL:   'Skruna til vinstri',
    cleavagesScrollR:   'Skruna til hægri',
    cleavagesNoStance:  'Tók ekki afstöðu',
    cleavagesCompareCTA:    'Bera saman alla flokka',
    // Pass muni dative-cased name in (see MUNI_DATIVE_IS below).
    cleavagesCompareTitle:  (muniDative) => `Afstaða flokka í ${muniDative}`,
    cleavagesCompareSub:    'Hvernig svöruðu flokkarnir umdeildum spurningum í kosningaprófi RÚV.',
    cleavagesCompareTopicCol: 'Klofningsmál',
    cleavagesCompareClose:  'Loka',
    stanceA:            'Mjög ósammála',
    stanceB:            'Ósammála',
    stanceC:            'Sammála',
    stanceD:            'Mjög sammála',

    // Candidate card / modal
    seeMore:          'Sjá nánar →',
    candidates:       'Frambjóðendur',
    ageLabel:         'ára',
    aboutCandidate:   'Um frambjóðandann',
    policyFocus:      'Áætluð áherslumál',
    socialMedia:      'Samfélagsmiðlar',
    news:             'Fréttir',
    source:           'Heimild',
    noInfo:           'Nánari upplýsingar um þennan frambjóðanda eru ekki tiltækar ennþá.',

    // Per-muni notices
    mulathingNoticeTitle: 'Sérstaða Múlaþings: kosið til heimastjórna',
    mulathingNoticeText:  'Samhliða sveitarstjórnarkosningunum 16. maí er einnig kosið til fjögurra heimastjórna — fastanefnda fyrir <em>Borgarfjörð</em>, <em>Djúpavog</em>, <em>Fljótsdalshérað</em> og <em>Seyðisfjörð</em> sem starfa í umboði sveitarstjórnar. Allir á kjörskrá á viðkomandi svæði eru sjálfkrafa kjörgengir og engir formlegir framboðslistar — kjósendur skrifa fullt nafn og heimilisfang á kjörseðilinn og þeir tveir sem fá flest atkvæði verða aðalmenn í þriggja manna heimastjórn (sveitarstjórn skipar þann þriðja).',

    // Disclaimer
    disclaimerTitle:  'Upplýsingar og fyrirvari',
    disclaimerText:   'Umsjónarmaður síðunnar er <a href="mailto:halldor.berg@inno.link" class="disclaimer-link">Halldór Berg Harðarson</a>.<br><br>Efnið er tekið saman með aðstoð gervigreindar úr opinberum heimildum á netinu. Við leggjum metnað okkar í að sannreyna hvert einasta atriði — hver staðhæfing er borin saman við frumheimildir og yfirfarin handvirkt af fólki — en mistök geta engu að síður leynst.<br><br>Bestu upplýsingarnar koma frá samfélaginu sjálfu, og allar ábendingar eru ekki bara vel þegnar heldur gegna lykilhlutverki við að halda upplýsingum réttum og lifandi. Ábendingar eru settar í beinan forgang.',

    // Share / toast
    shareToastCopied: '✓ Hlekkur afritaður!',
    shareToastFailed: 'Gat ekki afritað hlekk',

    // Coalition strip (RVK only for now)
    coalitionBannerTitle:    'Líklegustu meirihlutarnir',
    coalitionIntro:          'Samstöðueinkunn byggð á svörum úr Kosningaprófi RÚV',
    coalitionPollSourceLabel:'Könnun',
    coalitionPollAverage:    'Meðaltal',
    coalitionPollMaskina:    'Maskína 15. maí',
    coalitionPollGallup:     'Gallup 15. maí',
    coalitionPollVisir:      'Vísir 14. maí',
    coalitionPollAverageTip: 'Meðaltal Maskínu 15. maí, Gallups 15. maí og Kosningaspár Vísis 14. maí',
    coalitionPollMaskinaTip: 'Lokakönnun Maskínu 12.–15. maí 2026',
    coalitionPollGallupTip:  'Lokakönnun Gallups 15. maí 2026',
    coalitionPollVisirTip:   'Kosningaspá Vísis 14. maí 2026',
    coalitionScaleLabel:     'Kvarði',
    coalitionScaleLinear:    'Línulegur kvarði',
    coalitionScaleLeap:      'Aukinn munur á sammála/ósammála',
    coalitionScaleLinearTip: 'A=1, B=2, C=3, D=4 — sömu millibil milli allra þrepa',
    coalitionScaleLeapTip:   'A=1, B=2, C=4, D=5 — gildið 3 er sleppt, sem gerir muninn milli sammála og ósammála tvöfalt stærri en innri stigsmun á hvorri hlið',
    coalitionShareTip:       'Afrita hlekk á þessa yfirlitssíðu',
    coalitionEmpty:          'Engin meirihlutamyndun möguleg.',
    coalitionPartyCount:     (n) => n === 1 ? '1 flokkur' : `${n} flokkar`,
    coalitionScoreLabel:     'Samstaða',
    coalitionScoreTooltip:   'Samrýming við kosningapróf RÚV (0–100). Því hærra, því minni innbyrðis munur á afstöðu frambjóðenda flokkanna.',
    coalitionScoreUnknown:   'Engin afstöðugögn fyrir þessa samsetningu.',
    coalitionFrictionHeader: 'Mestur munur á afstöðu',
    coalitionMethodH:        'Hvernig er <em>Samstaða</em> reiknuð?',
    coalitionMethodP1:       'Samstaða (0–100) er mælikvarði á hversu lík afstaða frambjóðenda flokkanna er í <a href="https://kosningaprof.ruv.is/" target="_blank" rel="noopener">kosningaprófi RÚV</a>. Hærri tala þýðir minni innbyrðis munur, og þ.a.l. meiri möguleika á samkomulagi um stefnumál.',
    coalitionMethodP2:       'Hver frambjóðandi gaf afstöðu á fjögurra þrepa kvarða (mjög ósammála → mjög sammála) við þær 30 fullyrðingar sem áttu við Reykjavík. Fyrir hvern flokk er reiknað meðaltal allra hans frambjóðenda á hverri fullyrðingu. Samstaða meirihlutans blandar þrennu:',
    coalitionMethodB1:       '<strong>Bil (50%):</strong> meðalmunur milli flokks með hæstu og lægstu afstöðu á hverri fullyrðingu.',
    coalitionMethodB2:       '<strong>Versti hlekkur (30%):</strong> mesti meðalfjarlægð milli tveggja flokka í meirihlutanum yfir allar fullyrðingar — meirihluti er aldrei sterkari en hans veikasta samband.',
    coalitionMethodB3:       '<strong>Áhersluvegið bil (20%):</strong> sami bilmælikvarði, en með auknu vægi á fullyrðingar sem flokkarnir sjálfir merktu sem mikilvægar.',
    coalitionMethodP3:       'Það sem birtist undir <em>„Mestur munur á afstöðu"</em> þegar smellt er á spjald eru þær þrjár fullyrðingar þar sem munur milli flokka meirihlutans er mestur — helstu líkleg ágreiningsmál ef meirihlutinn yrði myndaður.',
    coalitionMethodNote:     '131 frambjóðandi af 11 listum í Reykjavík svaraði kosningaprófinu; sumir flokkar með færri svör hafa minni nákvæmni í meðaltali. Sætafjöldi byggir á efstu könnun í þessari síðu (sjá flokk fyrir uppruna).',
    coalitionDetailLink:       'Sjá útreikning →',
    coalitionDetailClose:      'Loka',
    coalitionDetailBreakdownH: 'Útreikningur (0–100 á hvern hluta)',
    coalitionDetailBreakdownB1: 'Bil (50%)',
    coalitionDetailBreakdownB2: 'Versti hlekkur (30%)',
    coalitionDetailBreakdownB3: 'Áhersluvegið bil (20%)',
    coalitionDetailScoreTotal: 'Samtals',
    // Plain-language explanation shown between title and formula on each
    // breakdown card.
    coalitionDetailExplB1:     'Meðalmunur milli flokks með hæstu og lægstu afstöðu á hverri fullyrðingu. Lágt bil þýðir að flokkarnir séu sammála í megindráttum.',
    coalitionDetailExplB2:     'Mesta meðalfjarlægðin milli tveggja flokka í meirihlutanum yfir allar fullyrðingar. Meirihluti er aldrei sterkari en veikasta samband hans.',
    coalitionDetailExplB3:     'Sami bilmælikvarði og að ofan, en með auknu vægi á þær fullyrðingar sem flokkarnir sjálfir merktu sem mikilvægar.',
    coalitionDetailExplTotal:  'Lokastig fæst með því að blanda þremur þáttunum að ofan í tilteknum vægishlutföllum.',
    coalitionDetailTableH:     'Allar fullyrðingar',
    coalitionDetailTableHint:  'Brosmerki sýna opinbera afstöðu flokksins skv. kosningaprófi RÚV. <strong>Bil</strong> = munur milli flokks með hæstu og lægstu afstöðu (0–3). Stjarna ★ undir brosmerki merkir að flokkurinn sjálfur merkti fullyrðinguna sem mikilvæga.',
    coalitionDetailQuestionCol:'Fullyrðing',
    coalitionDetailSpreadCol:  'Bil',
    coalitionDetailImpHint:    'Flokkurinn merkti þessa fullyrðingu sem mikilvæga',
    coalitionDetailPairsH:     'Fjarlægðir milli flokka',
    coalitionDetailPairsHint:  'Meðalfjarlægð á fullyrðingu fyrir hvern flokkapör. 0 = sammála á öllu, 3 = mjög ósammála á öllu. Versta parið er „veikasti hlekkurinn" sem dregur stigið niður.',
  },

  en: {
    backToMap:        'Back to map',
    share:            'Share',
    openParty:        'Open',
    language:         'Language',
    breadcrumbHome:   'Home',

    heroTitle:        'Welcome to the <span>democracy feast!</span>',
    heroSubtitle:     'Click a municipality on the map to compare parties, candidates and their platforms all in one place.',
    heroIntro:        "Moved to Iceland recently and trying to figure out the local elections? Here's every party running in your municipality on May 16, 2026 — candidates, platforms, and news, all in English.",
    heroIntroEmphasis:"If you've lived here for at least three years, you can vote, even without Icelandic citizenship. Find out who's worth your vote.",
    pageTitleHome:    "Lýðræðisveislan 2026 — Iceland's Local Elections",
    pageDescHome:     "Find every party, candidate and platform for Iceland's 2026 local elections on May 16. Compare them all in one place — in English, Icelandic or Polish.",
    statMunicipalities: 'Municipalities',
    statParties:      'Party lists',
    statCandidates:   'Candidates',
    mapOverlayTitle:  'Select a municipality',
    mapOverlayDesc:   'Hover over a marker to see details · Click to enter',
    legendTitle:      'Parties',
    instrHover:       'Hover over a marker to see details',
    instrClick:       'Click to enter the municipality',
    instrZoom:        'Zoom in and out on the map',
    muniSearchPlaceholder: 'Search for a municipality…',
    electionDate:     'Elections 16 May 2026',
    cdDays: 'days', cdHours: 'hrs', cdMins: 'min', cdSecs: 'sec',
    cdElectionDay:    '🗳️ Election day!',
    mapTooltipCTA:    'Click to view details',
    unboundNote:      'Any eligible individual may run — no formal party lists.',

    population:       'residents',
    region:           'Region',
    randomTooltipOpen: (name) => `Opened ${name} at random`,

    unboundBadge:     'Open election',
    unboundTitle:     (name) => `Open election in ${name}`,
    unboundDesc:      'This election has no formal party lists. All eligible residents are automatically considered candidates unless they opt out. Voters cast ballots for individuals rather than parties — meaning you can vote for any eligible person in the municipality.',
    unopposedBadge:   'Uncontested',
    unopposedTitle:   (name) => `Uncontested in ${name}`,
    unopposedDesc:    'Only one party list registered and was accepted without an election. When the number of candidates on a list equals or is fewer than the number of seats on the council, there is no need for an election and all candidates automatically take their seats. You can view the list below.',

    results2022Label:  '📊 2022 Election results',
    pollLabel:         (pollster /* , pollsterGen */) => `📈 ${pollster} opinion poll`,
    pollSource:        (pollster, period, n) => `Source: ${pollster}, ${period}${n ? ` (n=${n})` : ''}`,
    pollSeatsHint:     "Seats calculated using D'Hondt method",
    olderPollTag:      'Older poll',
    olderPollNav:      'See older poll',
    newerPollNav:      'See newer poll',
    pollCarouselHint:  'Tap the arrows to see older polls',
    electedFrameLabel: 'Would be elected per the latest poll',
    votes:             'votes',
    noSeats:           'No seats',
    ofSeats:           (n) => `of ${n} seats`,
    resultsNew:        '✨ New party — did not run in 2022',
    resultsUncontested2022: '🤝 Open election in 2022 — no party lists',
    resultsJoint:      (name) => `Ran as part of ${name}`,

    noPlatformTitle:  'Platform not available',
    noPlatformDesc:   'We have not found a confirmed policy platform for this party and are therefore not showing any agenda items.',
    noPlatformCTA:    'Are you a candidate? Get in touch! →',
    platformSource:   (host) => `Source: ${host}`,

    // Cleavages carousel — note: question text itself stays in Icelandic
    // because it's quoted verbatim from RÚV's kosningapróf.
    cleavagesHeader:    'Topics where the parties disagree (RÚV poll)',
    cleavagesScrollL:   'Scroll left',
    cleavagesScrollR:   'Scroll right',
    cleavagesNoStance:  'Did not respond',
    cleavagesCompareCTA:    'Compare all parties',
    cleavagesCompareTitle:  (muni) => `Party positions in ${muni}`,
    cleavagesCompareSub:    'How each party answered the contested questions in the RÚV election test.',
    cleavagesCompareTopicCol: 'Topic',
    cleavagesCompareClose:  'Close',
    stanceA:            'Strongly disagree',
    stanceB:            'Disagree',
    stanceC:            'Agree',
    stanceD:            'Strongly agree',

    seeMore:          'See more →',
    candidates:       'Candidates',
    ageLabel:         'years old',
    aboutCandidate:   'About the candidate',
    policyFocus:      'Policy focus areas',
    socialMedia:      'Social media',
    news:             'News',
    source:           'Source',
    noInfo:           'No further information about this candidate is available yet.',

    mulathingNoticeTitle: "Múlaþing extra vote: heimastjórn district committees",
    mulathingNoticeText:  'Alongside the May 16 municipal election, voters in each of the four historical sub-areas — <em>Borgarfjörður</em>, <em>Djúpavogur</em>, <em>Fljótsdalshérað</em> and <em>Seyðisfjörður</em> — also elect members to a three-seat <em>heimastjórn</em>, a local committee that handles planning, environment, culture, agriculture and other neighbourhood matters on behalf of the city council. Anyone on the local voter roll is automatically a candidate; voters write a name + address on the ballot and the two top vote-getters are elected (the city council appoints the third member).',

    disclaimerTitle:  'About this site & disclaimer',
    disclaimerText:   'The site is curated by <a href="mailto:halldor.berg@inno.link" class="disclaimer-link">Halldór Berg Harðarson</a>.<br><br>Content is compiled with the help of AI from publicly available online sources. We go to great lengths to verify every single item — each statement is cross-checked against primary sources and reviewed manually by a human — but mistakes can still slip through.<br><br>The best information comes from the community itself, and every tip is not just welcome but plays a key role in keeping the information accurate and alive. Tips are given top priority.',

    shareToastCopied: '✓ Link copied!',
    shareToastFailed: 'Could not copy link',

    // Coalition strip (RVK only for now)
    coalitionBannerTitle:    'Most plausible majorities',
    coalitionIntro:          'Alignment score based on answers from RÚV\'s election quiz',
    coalitionPollSourceLabel:'Poll',
    coalitionPollAverage:    'Average',
    coalitionPollMaskina:    'Maskína May 15',
    coalitionPollGallup:     'Gallup May 15',
    coalitionPollVisir:      'Vísir May 14',
    coalitionPollAverageTip: 'Average of Maskína May 15, Gallup May 15 and Vísir\'s Kosningaspá May 14',
    coalitionPollMaskinaTip: 'Final Maskína poll, 12–15 May 2026',
    coalitionPollGallupTip:  'Final Gallup poll, 15 May 2026',
    coalitionPollVisirTip:   'Vísir Kosningaspá forecast, 14 May 2026',
    coalitionScaleLabel:     'Scale',
    coalitionScaleLinear:    'Linear scale',
    coalitionScaleLeap:      'Larger agree/disagree gap',
    coalitionScaleLinearTip: 'A=1, B=2, C=3, D=4 — equal steps between all stances',
    coalitionScaleLeapTip:   'A=1, B=2, C=4, D=5 — value 3 is skipped, making the agree/disagree gap twice the gradient gap on each side',
    coalitionShareTip:       'Copy a link to this overview',
    coalitionEmpty:          'No majority coalition is possible.',
    coalitionPartyCount:     (n) => n === 1 ? '1 party' : `${n} parties`,
    coalitionScoreLabel:     'Alignment',
    coalitionScoreTooltip:   'Alignment with the RÚV election quiz (0–100). Higher means smaller policy gaps between the parties\' candidates.',
    coalitionScoreUnknown:   'No quiz data for this combination.',
    coalitionFrictionHeader: 'Biggest disagreements',
    coalitionMethodH:        'How is <em>Alignment</em> computed?',
    coalitionMethodP1:       'Alignment (0–100) measures how similar the candidates\' positions are in <a href="https://kosningaprof.ruv.is/" target="_blank" rel="noopener">RÚV\'s 2026 election quiz</a>. A higher score means smaller gaps between parties — and therefore more room to agree on policy.',
    coalitionMethodP2:       'Each candidate placed every applicable statement on a 4-point scale (strongly disagree → strongly agree). For each party we average all of its candidates\' answers per statement. The coalition\'s Alignment score blends three signals:',
    coalitionMethodB1:       '<strong>Spread (50%):</strong> the average gap between the highest- and lowest-positioned party on each statement.',
    coalitionMethodB2:       '<strong>Weakest link (30%):</strong> the largest average distance between any pair of coalition parties — a coalition is only as stable as its most strained pairing.',
    coalitionMethodB3:       '<strong>Importance-weighted spread (20%):</strong> the same spread measure, weighted by how many coalition parties flagged the statement as important.',
    coalitionMethodP3:       'The three items shown under <em>"Biggest disagreements"</em> when you open a card are the statements with the largest within-coalition spread — the likely flashpoints if that coalition were formed.',
    coalitionMethodNote:     '131 candidates across 11 lists in Reykjavík answered the quiz; parties with fewer respondents have less reliable averages. Seat counts are taken from the topmost poll on this page (see the party block for the source).',
    coalitionDetailLink:       'See breakdown →',
    coalitionDetailClose:      'Close',
    coalitionDetailBreakdownH: 'Score breakdown (0–100 per component)',
    coalitionDetailBreakdownB1: 'Spread (50%)',
    coalitionDetailBreakdownB2: 'Weakest link (30%)',
    coalitionDetailBreakdownB3: 'Importance-weighted (20%)',
    coalitionDetailScoreTotal: 'Total',
    coalitionDetailExplB1:     'Average gap between the highest- and lowest-positioned party on each proposition. A low spread means the parties broadly agree.',
    coalitionDetailExplB2:     'The largest average distance between any pair of coalition parties across all propositions. A coalition is only as stable as its weakest pairing.',
    coalitionDetailExplB3:     'The same spread measure as above, weighted by the propositions each party flagged as important.',
    coalitionDetailExplTotal:  'The final score blends the three components above using the weights shown.',
    coalitionDetailTableH:     'All propositions',
    coalitionDetailTableHint:  'Smileys show the party\'s official stance from RÚV\'s election quiz. <strong>Spread</strong> = gap between the highest- and lowest-positioned party on this proposition (0–3). A ★ under a smiley means the party itself flagged this proposition as important.',
    coalitionDetailQuestionCol:'Proposition',
    coalitionDetailSpreadCol:  'Spread',
    coalitionDetailImpHint:    'The party flagged this proposition as important',
    coalitionDetailPairsH:     'Pairwise distances',
    coalitionDetailPairsHint:  'Average per-proposition distance for each party pair. 0 = agree on everything, 3 = strongly disagree on everything. The worst pair is the "weakest link" pulling the score down.',
  },

  pl: {
    backToMap:        'Powrót do mapy',
    share:            'Udostępnij',
    openParty:        'Otwórz',
    language:         'Język',
    breadcrumbHome:   'Strona główna',

    heroTitle:        'Witaj na <span>uczcie demokracji!</span>',
    heroSubtitle:     'Kliknij gminę na mapie, aby porównać partie, kandydatów i ich programy w jednym miejscu.',
    heroIntro:        'Mieszkasz w Islandii i chcesz zrozumieć wybory lokalne? Zobacz wszystkie partie kandydujące w Twojej gminie 16 maja 2026 — kandydatów, programy i aktualności, w języku polskim.',
    heroIntroEmphasis:'Jeśli mieszkasz w Islandii od co najmniej trzech lat, masz prawo głosu — nawet bez obywatelstwa. Sprawdź, kto reprezentuje Twoje sprawy: mieszkanie, przedszkola, szkoły, integrację.',
    pageTitleHome:    'Lýðræðisveislan 2026 — Wybory samorządowe w Islandii',
    pageDescHome:     'Wszystkie partie, kandydaci i programy w wyborach samorządowych 16 maja 2026 w Islandii. W jednym miejscu — po polsku, islandzku lub angielsku.',
    statMunicipalities: 'Gminy',
    statParties:      'Listy partyjne',
    statCandidates:   'Kandydaci',
    mapOverlayTitle:  'Wybierz gminę',
    mapOverlayDesc:   'Najedź na znacznik, aby zobaczyć szczegóły · Kliknij, aby wejść',
    legendTitle:      'Partie',
    instrHover:       'Najedź na znacznik, aby zobaczyć szczegóły',
    instrClick:       'Kliknij, aby wejść do gminy',
    instrZoom:        'Powiększ i pomniejsz mapę',
    muniSearchPlaceholder: 'Szukaj gminy…',
    electionDate:     'Wybory 16 maja 2026',
    cdDays: 'dni', cdHours: 'godz', cdMins: 'min', cdSecs: 'sek',
    cdElectionDay:    '🗳️ Dzień wyborów!',
    mapTooltipCTA:    'Kliknij, aby zobaczyć szczegóły',
    unboundNote:      'Każdy uprawniony mieszkaniec może kandydować — brak formalnych list partyjnych.',

    population:       'mieszkańców',
    region:           'Region',
    randomTooltipOpen: (name) => `Otwarto ${name} losowo`,

    unboundBadge:     'Wybory otwarte',
    unboundTitle:     (name) => `Wybory otwarte w ${name}`,
    unboundDesc:      'W tych wyborach nie ma formalnych list partyjnych. Wszyscy uprawnieni mieszkańcy gminy są automatycznie kandydatami, chyba że zrezygnują. Wyborcy głosują na osoby, a nie na partie.',
    unopposedBadge:   'Bez głosowania',
    unopposedTitle:   (name) => `Bez głosowania w ${name}`,
    unopposedDesc:    'Tylko jedna lista partyjna zarejestrowała się i została przyjęta bez wyborów. Gdy liczba kandydatów na liście jest równa lub mniejsza od liczby mandatów w radzie gminy, wybory nie są konieczne. Listę można zobaczyć poniżej.',

    results2022Label:  '📊 Wyniki wyborów 2022',
    pollLabel:         (pollster /* , pollsterGen */) => `📈 Sondaż ${pollster}`,
    pollSource:        (pollster, period, n) => `Źródło: ${pollster}, ${period}${n ? ` (n=${n})` : ''}`,
    pollSeatsHint:     'Mandaty obliczone metodą d\'Hondta',
    olderPollTag:      'Starszy sondaż',
    olderPollNav:      'Zobacz starszy sondaż',
    newerPollNav:      'Zobacz nowszy sondaż',
    pollCarouselHint:  'Stuknij strzałki, aby zobaczyć starsze sondaże',
    electedFrameLabel: 'Otrzymałby mandat według najnowszego sondażu',
    votes:             'głosów',
    noSeats:           'Brak mandatów',
    ofSeats:           (n) => `z ${n} mandatów`,
    resultsNew:        '✨ Nowa partia — nie startowała w 2022 r.',
    resultsUncontested2022: '🤝 Wybory otwarte w 2022 — brak list partyjnych',
    resultsJoint:      (name) => `Startowała jako część ${name}`,

    noPlatformTitle:  'Program niedostępny',
    noPlatformDesc:   'Nie znaleźliśmy potwierdzonego programu wyborczego tej partii i dlatego nie wyświetlamy żadnych punktów programowych.',
    noPlatformCTA:    'Jesteś kandydatem? Skontaktuj się z nami! →',
    platformSource:   (host) => `Źródło: ${host}`,

    // Cleavages carousel — pytania pozostają w islandzkim, bo są
    // dosłownymi cytatami z sondażu kosningapróf RÚV.
    cleavagesHeader:    'Tematy sporne według sondażu RÚV',
    cleavagesScrollL:   'Przewiń w lewo',
    cleavagesScrollR:   'Przewiń w prawo',
    cleavagesNoStance:  'Nie zajął stanowiska',
    cleavagesCompareCTA:    'Porównaj wszystkie partie',
    cleavagesCompareTitle:  (muni) => `Stanowiska partii w gminie ${muni}`,
    cleavagesCompareSub:    'Jak każda partia odpowiedziała na sporne pytania w sondażu wyborczym RÚV.',
    cleavagesCompareTopicCol: 'Temat',
    cleavagesCompareClose:  'Zamknij',
    stanceA:            'Zdecydowanie się nie zgadza',
    stanceB:            'Nie zgadza się',
    stanceC:            'Zgadza się',
    stanceD:            'Zdecydowanie się zgadza',

    seeMore:          'Zobacz więcej →',
    candidates:       'Kandydaci',
    ageLabel:         'lat',
    aboutCandidate:   'O kandydacie',
    policyFocus:      'Priorytety programowe',
    socialMedia:      'Media społecznościowe',
    news:             'Aktualności',
    source:           'Źródło',
    noInfo:           'Brak dodatkowych informacji o tym kandydacie.',

    mulathingNoticeTitle: 'Múlaþing — dodatkowe wybory do heimastjórn',
    mulathingNoticeText:  'Równolegle z wyborami samorządowymi 16 maja mieszkańcy każdego z czterech historycznych obszarów — <em>Borgarfjörður</em>, <em>Djúpavogur</em>, <em>Fljótsdalshérað</em> i <em>Seyðisfjörður</em> — wybierają również członków trzyosobowej <em>heimastjórn</em>, lokalnej komisji zajmującej się planowaniem, środowiskiem, kulturą, rolnictwem i innymi sprawami sąsiedztwa w imieniu rady miejskiej. Każda osoba z miejscowej listy wyborców jest automatycznie kandydatem; wyborcy wpisują imię i adres na karcie wyborczej, a dwie osoby z największą liczbą głosów zostają wybrane (trzeciego członka mianuje rada miejska).',

    disclaimerTitle:  'O stronie i zastrzeżenie',
    disclaimerText:   'Stroną opiekuje się <a href="mailto:halldor.berg@inno.link" class="disclaimer-link">Halldór Berg Harðarson</a>.<br><br>Treść jest zestawiana z pomocą sztucznej inteligencji ze źródeł publicznie dostępnych w internecie. Dokładamy wszelkich starań, aby zweryfikować każdy szczegół — każde stwierdzenie jest porównywane ze źródłami pierwotnymi i sprawdzane ręcznie przez człowieka — ale błędy nadal mogą się pojawić.<br><br>Najlepsze informacje pochodzą od samej społeczności, a każda uwaga nie tylko jest mile widziana, lecz odgrywa kluczową rolę w utrzymywaniu informacji aktualnymi i prawdziwymi. Uwagi są traktowane priorytetowo.',

    shareToastCopied: '✓ Link skopiowany!',
    shareToastFailed: 'Nie udało się skopiować linku',

    // Coalition strip (RVK only for now)
    coalitionBannerTitle:    'Najbardziej prawdopodobne większości',
    coalitionIntro:          'Wynik zgodności na podstawie odpowiedzi z testu wyborczego RÚV',
    coalitionPollSourceLabel:'Sondaż',
    coalitionPollAverage:    'Średnia',
    coalitionPollMaskina:    'Maskína 15 maja',
    coalitionPollGallup:     'Gallup 15 maja',
    coalitionPollVisir:      'Vísir 14 maja',
    coalitionPollAverageTip: 'Średnia sondażu Maskína z 15 maja, Gallup z 15 maja i prognozy Kosningaspá Vísis z 14 maja',
    coalitionPollMaskinaTip: 'Sondaż końcowy Maskína, 12–15 maja 2026',
    coalitionPollGallupTip:  'Sondaż końcowy Gallup, 15 maja 2026',
    coalitionPollVisirTip:   'Prognoza wyborcza Vísis, 14 maja 2026',
    coalitionScaleLabel:     'Skala',
    coalitionScaleLinear:    'Skala liniowa',
    coalitionScaleLeap:      'Większa różnica zgoda/niezgoda',
    coalitionScaleLinearTip: 'A=1, B=2, C=3, D=4 — równe odstępy między wszystkimi stanowiskami',
    coalitionScaleLeapTip:   'A=1, B=2, C=4, D=5 — wartość 3 pominięta, dystans między „zgadzam się" a „nie zgadzam się" dwukrotnie większy niż wewnątrz każdej strony',
    coalitionShareTip:       'Skopiuj link do tego zestawienia',
    coalitionEmpty:          'Żadna większość nie jest możliwa.',
    coalitionPartyCount:     (n) => {
      // Polish plural: 1 → "1 partia"; 2-4 → "2 partie"; 5+/ends 0,1,12-14 → "5 partii"
      if (n === 1) return '1 partia';
      const last = n % 10, last2 = n % 100;
      if (last >= 2 && last <= 4 && (last2 < 12 || last2 > 14)) return `${n} partie`;
      return `${n} partii`;
    },
    coalitionScoreLabel:     'Zgodność',
    coalitionScoreTooltip:   'Zgodność z testem wyborczym RÚV (0–100). Wyższy wynik = mniejsze różnice w stanowiskach kandydatów partii.',
    coalitionScoreUnknown:   'Brak danych testowych dla tego zestawienia.',
    coalitionFrictionHeader: 'Największe różnice w stanowiskach',
    coalitionMethodH:        'Jak liczona jest <em>Zgodność</em>?',
    coalitionMethodP1:       'Zgodność (0–100) mierzy, na ile podobne są stanowiska kandydatów partii w <a href="https://kosningaprof.ruv.is/" target="_blank" rel="noopener">teście wyborczym RÚV 2026</a>. Wyższa wartość oznacza mniejsze różnice między partiami i większą szansę na porozumienie w sprawach programowych.',
    coalitionMethodP2:       'Każdy kandydat oznaczył każde stwierdzenie na czterostopniowej skali (zdecydowanie się nie zgadzam → zdecydowanie się zgadzam) — w Reykjavíku obowiązywało 30 stwierdzeń. Dla każdej partii obliczana jest średnia odpowiedzi jej kandydatów na każde stwierdzenie. Zgodność większości łączy trzy sygnały:',
    coalitionMethodB1:       '<strong>Rozpiętość (50%):</strong> średnia różnica między partią o najwyższym i najniższym stanowisku w każdym stwierdzeniu.',
    coalitionMethodB2:       '<strong>Najsłabsze ogniwo (30%):</strong> największa średnia odległość między dowolną parą partii koalicyjnych — koalicja jest tak silna jak jej najsłabsze połączenie.',
    coalitionMethodB3:       '<strong>Rozpiętość ważona ważnością (20%):</strong> ta sama miara rozpiętości, ale ze zwiększoną wagą stwierdzeń, które partie oznaczyły jako ważne.',
    coalitionMethodP3:       'To, co pojawia się pod <em>„Największe różnice w stanowiskach"</em> po kliknięciu karty, to trzy stwierdzenia, w których różnica między partiami koalicji jest największa — prawdopodobne pola sporu, gdyby koalicja powstała.',
    coalitionMethodNote:     'Test wyborczy wypełniło 131 kandydatów z 11 list w Reykjavíku; partie z mniejszą liczbą odpowiedzi mają mniej wiarygodne średnie. Liczba mandatów pochodzi z najnowszego sondażu w tej sekcji (źródło widoczne przy konkretnej partii).',
    coalitionDetailLink:       'Zobacz obliczenie →',
    coalitionDetailClose:      'Zamknij',
    coalitionDetailBreakdownH: 'Składowe wyniku (0–100 na składnik)',
    coalitionDetailBreakdownB1: 'Rozpiętość (50%)',
    coalitionDetailBreakdownB2: 'Najsłabsze ogniwo (30%)',
    coalitionDetailBreakdownB3: 'Rozpiętość ważona (20%)',
    coalitionDetailScoreTotal: 'Razem',
    coalitionDetailExplB1:     'Średnia różnica między partią o najwyższym i najniższym stanowisku w każdym stwierdzeniu. Niska rozpiętość oznacza, że partie zgadzają się w większości spraw.',
    coalitionDetailExplB2:     'Największa średnia odległość między dowolną parą partii koalicyjnych we wszystkich stwierdzeniach. Koalicja jest tak silna jak jej najsłabsze połączenie.',
    coalitionDetailExplB3:     'Ta sama miara rozpiętości, ale ważona stwierdzeniami, które partie same oznaczyły jako ważne.',
    coalitionDetailExplTotal:  'Wynik końcowy to ważona mieszanka trzech składników powyżej.',
    coalitionDetailTableH:     'Wszystkie stwierdzenia',
    coalitionDetailTableHint:  'Emotki pokazują oficjalne stanowisko partii w teście wyborczym RÚV. <strong>Rozpiętość</strong> = różnica między partią o najwyższym i najniższym stanowisku w danym stwierdzeniu (0–3). Gwiazdka ★ pod emotką oznacza, że sama partia oznaczyła to stwierdzenie jako ważne.',
    coalitionDetailQuestionCol:'Stwierdzenie',
    coalitionDetailSpreadCol:  'Rozpiętość',
    coalitionDetailImpHint:    'Partia oznaczyła to stwierdzenie jako ważne',
    coalitionDetailPairsH:     'Odległości między partiami',
    coalitionDetailPairsHint:  'Średnia odległość na stwierdzenie dla każdej pary partii. 0 = zgodność we wszystkim, 3 = całkowita niezgodność we wszystkim. Najgorsza para to "najsłabsze ogniwo" obniżające wynik.',
  },
};

/** Active language detection.
 *  Path-based URLs:  /<lang>/... → use that lang prefix; otherwise IS.
 *                   localStorage is intentionally NOT consulted here, because
 *                   the path is the source of truth — once we're on
 *                   /gardabaer/, we want IS even if the user previously
 *                   visited /en/akureyri/.
 *  Legacy /*.html URLs: check ?lang= then localStorage as fallbacks. */
export function getLang() {
  const seg = window.location.pathname.split('/').filter(Boolean)[0];
  if (seg && UI[seg]) return seg;
  if (window.location.pathname.endsWith('.html')) {
    const p = new URLSearchParams(window.location.search).get('lang');
    if (p && UI[p]) return p;
    const s = localStorage.getItem('lang');
    if (s && UI[s]) return s;
  }
  return 'is';
}

/** Return UI strings for the active language */
export function t() {
  return UI[getLang()] || UI.is;
}

/** Switch language — rewrites URL to use the new path prefix (or strips it
 *  for IS), persists choice to localStorage, then navigates. */
export function setLang(lang) {
  if (!UI[lang]) return;
  localStorage.setItem('lang', lang);
  const url = new URL(window.location.href);
  // Drop legacy ?lang= param if present
  url.searchParams.delete('lang');
  // Strip an existing leading /en/ or /pl/ from path
  let path = url.pathname.replace(/^\/(en|pl)(\/|$)/, '/');
  if (lang !== 'is') {
    // Add /en/ or /pl/ prefix
    path = `/${lang}` + (path === '/' ? '/' : path);
  }
  url.pathname = path;
  window.location.href = url.toString();
}

/**
 * Inject a compact language switcher into the given container element.
 * Uses inline SVG flags so rendering is consistent across all browsers/OS.
 */
export function renderLangSwitcher(container) {
  if (!container) return;
  const cur = getLang();

  // Inline SVG flags — viewBox 0 0 20 14, rendered at 18×13
  const FLAG = {
    is: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 14" width="18" height="13" aria-hidden="true" style="display:block;border-radius:2px;flex-shrink:0">
      <rect width="20" height="14" fill="#003897"/>
      <rect x="5"     y="0"    width="3"   height="14" fill="#fff"/>
      <rect x="0"     y="5.5"  width="20"  height="3"  fill="#fff"/>
      <rect x="5.75"  y="0"    width="1.5" height="14" fill="#D72828"/>
      <rect x="0"     y="6.25" width="20"  height="1.5" fill="#D72828"/>
    </svg>`,
    en: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 14" width="18" height="13" aria-hidden="true" style="display:block;border-radius:2px;flex-shrink:0">
      <rect width="20" height="14" fill="#012169"/>
      <line x1="0"  y1="0"  x2="20" y2="14" stroke="#fff"    stroke-width="4.5"/>
      <line x1="20" y1="0"  x2="0"  y2="14" stroke="#fff"    stroke-width="4.5"/>
      <line x1="0"  y1="0"  x2="20" y2="14" stroke="#C8102E" stroke-width="2.5"/>
      <line x1="20" y1="0"  x2="0"  y2="14" stroke="#C8102E" stroke-width="2.5"/>
      <rect x="0"   y="5"   width="20" height="4"   fill="#fff"/>
      <rect x="8"   y="0"   width="4"  height="14"  fill="#fff"/>
      <rect x="0"   y="5.9" width="20" height="2.2" fill="#C8102E"/>
      <rect x="8.9" y="0"   width="2.2" height="14" fill="#C8102E"/>
    </svg>`,
    pl: `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 14" width="18" height="13" aria-hidden="true" style="display:block;border-radius:2px;flex-shrink:0">
      <rect width="20" height="7"  fill="#fff"/>
      <rect y="7"  width="20" height="7"  fill="#DC143C"/>
    </svg>`,
  };

  const langs = [
    { code: 'is', label: 'Íslenska' },
    { code: 'en', label: 'English'  },
    { code: 'pl', label: 'Polski'   },
  ];
  container.className = 'lang-switcher';
  container.innerHTML = langs.map(l =>
    `<button class="lang-btn${l.code === cur ? ' lang-btn--active' : ''}"
             data-lang="${l.code}"
             title="${l.label}"
             aria-label="${l.label}${l.code === cur ? ' (active)' : ''}">
       ${FLAG[l.code]}<span class="lang-code">${l.code.toUpperCase()}</span>
     </button>`
  ).join('');
  container.querySelectorAll('.lang-btn').forEach(btn => {
    btn.addEventListener('click', () => setLang(btn.dataset.lang));
  });
}
