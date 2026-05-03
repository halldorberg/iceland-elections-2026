/**
 * i18n.js — UI string translations
 * Covers all hardcoded interface text. Data translations live in
 * js/data/candidates.en.js and js/data/candidates.pl.js.
 */

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

    // Party splash
    noPlatformTitle:  'Stefnuskrá ekki til staðar',
    noPlatformDesc:   'Við höfum ekki fundið staðfesta stefnuskrá þessa framboðs og birtum því engar áherslugreinar.',
    noPlatformCTA:    'Ertu frambjóðandi? Hafðu samband! →',
    platformSource:   (host) => `Heimild: ${host}`,

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

    // Disclaimer
    disclaimerTitle:  'Upplýsingar og fyrirvari',
    disclaimerText:   'Umsjónarmaður síðunnar er <a href="mailto:halldor.berg@inno.link" class="disclaimer-link">Halldór Berg Harðarson</a>.<br><br>Efnið er tekið saman með aðstoð gervigreindar úr opinberum heimildum á netinu. Við leggjum metnað okkar í að sannreyna hvert einasta atriði — hver staðhæfing er borin saman við frumheimildir og yfirfarin handvirkt af fólki — en mistök geta engu að síður leynst.<br><br>Bestu upplýsingarnar koma frá samfélaginu sjálfu, og allar ábendingar eru ekki bara vel þegnar heldur gegna lykilhlutverki við að halda upplýsingum réttum og lifandi. Ábendingar eru settar í beinan forgang.',

    // Share / toast
    shareToastCopied: '✓ Hlekkur afritaður!',
    shareToastFailed: 'Gat ekki afritað hlekk',
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

    seeMore:          'See more →',
    candidates:       'Candidates',
    ageLabel:         'years old',
    aboutCandidate:   'About the candidate',
    policyFocus:      'Policy focus areas',
    socialMedia:      'Social media',
    news:             'News',
    source:           'Source',
    noInfo:           'No further information about this candidate is available yet.',

    disclaimerTitle:  'About this site & disclaimer',
    disclaimerText:   'The site is curated by <a href="mailto:halldor.berg@inno.link" class="disclaimer-link">Halldór Berg Harðarson</a>.<br><br>Content is compiled with the help of AI from publicly available online sources. We go to great lengths to verify every single item — each statement is cross-checked against primary sources and reviewed manually by a human — but mistakes can still slip through.<br><br>The best information comes from the community itself, and every tip is not just welcome but plays a key role in keeping the information accurate and alive. Tips are given top priority.',

    shareToastCopied: '✓ Link copied!',
    shareToastFailed: 'Could not copy link',
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

    seeMore:          'Zobacz więcej →',
    candidates:       'Kandydaci',
    ageLabel:         'lat',
    aboutCandidate:   'O kandydacie',
    policyFocus:      'Priorytety programowe',
    socialMedia:      'Media społecznościowe',
    news:             'Aktualności',
    source:           'Źródło',
    noInfo:           'Brak dodatkowych informacji o tym kandydacie.',

    disclaimerTitle:  'O stronie i zastrzeżenie',
    disclaimerText:   'Stroną opiekuje się <a href="mailto:halldor.berg@inno.link" class="disclaimer-link">Halldór Berg Harðarson</a>.<br><br>Treść jest zestawiana z pomocą sztucznej inteligencji ze źródeł publicznie dostępnych w internecie. Dokładamy wszelkich starań, aby zweryfikować każdy szczegół — każde stwierdzenie jest porównywane ze źródłami pierwotnymi i sprawdzane ręcznie przez człowieka — ale błędy nadal mogą się pojawić.<br><br>Najlepsze informacje pochodzą od samej społeczności, a każda uwaga nie tylko jest mile widziana, lecz odgrywa kluczową rolę w utrzymywaniu informacji aktualnymi i prawdziwymi. Uwagi są traktowane priorytetowo.',

    shareToastCopied: '✓ Link skopiowany!',
    shareToastFailed: 'Nie udało się skopiować linku',
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
