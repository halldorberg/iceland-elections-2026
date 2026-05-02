# SEO Plan — lydraedisveislan.is

The site is a discovery tool for the 2026 Icelandic municipal elections.
Most search-driven traffic will come from people Googling a specific
**municipality** ("Garðabær kosningar 2026"), a specific **party-in-muni**
("Samfylkingin Garðabær"), or a specific **candidate** ("Kjartan Atli
Kjartansson"). The site already has the data; the SEO problem is making it
findable and presentable to Google in those specific search contexts.

This plan is structured in three parts:

1. **What the user asked for** — URL scheme, dynamic titles, dynamic meta
   descriptions, content for front page.
2. **Standard SEO checklist** — the things any modern SEO plan should
   cover, ordered by impact.
3. **Phased implementation roadmap** — what to build first.

---

## 1. URL architecture

### Goal

Replace the current query-parameter URLs with human-readable paths.

| Today | Proposed |
|---|---|
| `/municipality.html?id=gardabaer` | `/gardabaer` |
| `/municipality.html?id=gardabaer&party=S` | `/samfylkingin-i-gardabae` |
| `/municipality.html?id=gardabaer&party=S&candidate=1` | `/samfylkingin-i-gardabae/kjartan-atli-kjartansson` |
| `/municipality.html?id=gardabaer&candidate=...` | `/gardabaer/<candidate-slug>` (only if no party context) |

### Slug rules

- **ASCII-only**: strip Icelandic diacritics for URLs. `Garðabær → gardabaer`,
  `Þórshöfn → thorshofn`, `Hörgársveit → horgarsveit`. (Keep diacritics for
  display titles and meta tags — only the URL path is ASCII.)
- **Hyphens, not underscores**. Google explicitly recommends hyphens as
  word separators. (Your example used `_` but `-` is the standard.)
- **Lowercase**. Mixed case in URLs is treated as different paths by some
  systems; keep it consistent.
- **No trailing slash inconsistency**. Pick one (with or without) and 301
  the other.

### URL recommendation summary

```
/                                        landing
/<muni>                                  e.g. /gardabaer
/<muni>/<party>                          e.g. /gardabaer/samfylkingin
/<muni>/<party>/<candidate-slug>         e.g. /gardabaer/samfylkingin/kjartan-atli-kjartansson
```

I recommend the **hierarchical scheme** (with the muni prefix) over a flat
"samfylkingin-i-gardabae" path, for three reasons:

1. **Breadcrumbs**: hierarchical URLs make breadcrumb structured data
   trivial — Google shows breadcrumbs in search results, increasing CTR.
2. **Disambiguation**: every muni has its own Samfylkingin chapter; a flat
   scheme buries that hierarchy in the slug.
3. **Sitemap clarity**: nested routes group cleanly in the sitemap and in
   internal linking patterns.

The flat form (e.g. `/samfylkingin-i-gardabae`) is fine if you prefer; we'd
then 301-redirect the hierarchical alternative to it. **Pick one and stick
with it** — duplicate content is the bigger SEO risk than slug aesthetics.

### How to actually serve these URLs on GitHub Pages

GitHub Pages has no server-side rewrites. Two viable approaches:

**Option A: Pre-rendered static HTML per route (recommended).** A build
script reads `candidates.js` and emits `/gardabaer/index.html`,
`/gardabaer/samfylkingin/index.html`, etc. — each pre-populated with the
right title, meta description, structured data, and a server-rendered
copy of the visible content. Then the existing client-side JS hydrates
on top for interactive features. This is the **only** approach that fully
satisfies Google's crawler; everything else is a workaround.

  - ~64 munis + ~180 party-in-muni + ~640 top-6 candidate pages = ~880
    HTML files. At ~10 KB each, ~9 MB total. Fine for GitHub Pages.
  - Build step: a Python script that reads `candidates.js`, the EN/PL
    overlays, and writes per-route HTML files. Runs whenever data changes.
  - The existing `municipality.html` becomes a template; the build output
    fills in `<title>`, `<meta name="description">`, the OG tags, and
    optionally a `<noscript>` rendering of the candidate list for
    JS-disabled crawlers.

**Option B: 404.html SPA fallback.** A `404.html` script that parses the
URL, sets `window.history.replaceState(...)`, and renders client-side.
Works for users but is bad for SEO — Google initially sees a 404 and may
de-prioritise the URL. **Do not use this option for the primary scheme.**

### The language question

> Would it be problematic to have URLs change with the language?

**No, the opposite — language-distinct URLs are preferred by Google.**
The standard pattern is:

```
/gardabaer         → Icelandic (default)
/en/gardabaer      → English
/pl/gardabaer      → Polish
```

Each variant gets a `<link rel="alternate" hreflang="...">` block in `<head>`
pointing at the other language versions. This is unambiguous and Google
indexes all three correctly.

**Avoid these patterns:**
- `/gardabaer?lang=en` — Google may treat `?lang=en` as a duplicate or as
  faceted navigation; weaker signal than a path-based variant.
- Cookie-based language switching with the same URL — Googlebot doesn't
  carry cookies; it would only ever see one language version.

**Recommended hreflang block** (place in `<head>` of every page):

```html
<link rel="alternate" hreflang="is" href="https://lydraedisveislan.is/gardabaer" />
<link rel="alternate" hreflang="en" href="https://lydraedisveislan.is/en/gardabaer" />
<link rel="alternate" hreflang="pl" href="https://lydraedisveislan.is/pl/gardabaer" />
<link rel="alternate" hreflang="x-default" href="https://lydraedisveislan.is/gardabaer" />
```

The current `?lang=en` query param can stay as an internal toggle but
should redirect (or canonicalise) to the path-based URL.

---

## 2. Page metadata

### Title tag

Currently every page is `Sveitarfélag – Kosningar 2026`. Make it dynamic
per route, in the page's language.

| Route | IS title | EN title | PL title |
|---|---|---|---|
| `/gardabaer` | `Garðabær – Kosningar 2026` | `Garðabær – 2026 Local Elections` | `Garðabær – Wybory lokalne 2026` |
| `/gardabaer/samfylkingin` | `Samfylkingin í Garðabæ – Kosningar 2026` | `Samfylkingin in Garðabær – 2026 Local Elections` | `Samfylkingin w Garðabær – Wybory 2026` |
| `/gardabaer/samfylkingin/kjartan-atli-kjartansson` | `Kjartan Atli Kjartansson – Samfylkingin Garðabæ` | `Kjartan Atli Kjartansson – Samfylkingin Garðabær` | (same pattern) |

**Length target**: 50–60 chars (Google truncates around 60). The IS form
is naturally short; the EN form often runs long — measure and trim
("2026 Local Elections" → "2026 Elections" if needed).

### Meta description

Currently `Flokkar og frambjóðendur í sveitarstjórnarkosningum 2026.` —
the same on every page.

Make it dynamic, route-specific, **150–160 chars**, written for humans
(this is what Google shows under the title in the SERP):

- **Muni page**: "Sjáðu öll framboðin í {Garðabæ} fyrir sveitarstjórnarkosningarnar 16. maí 2026 — frambjóðendur, áherslumál og fréttir á einum stað."
- **Party page**: "Stefnumál og frambjóðendur {Samfylkingarinnar} í {Garðabæ} fyrir kosningar 2026. Berðu listann saman við önnur framboð."
- **Candidate page**: "{Kjartan Atli Kjartansson} skipar 1. sætið hjá {Samfylkingunni í Garðabæ} í sveitarstjórnarkosningum 2026. Sjá æviágrip, áherslur og samfélagsmiðla."

Same structure in EN and PL; switch the entity names but keep the
language.

### Open Graph (already partially in place)

The current OG tags are static. Make them dynamic per route — Google
doesn't use OG directly for ranking, but Facebook/LinkedIn/Twitter
previews drive social-share traffic which feeds back into ranking signals.

```html
<meta property="og:title" content="<dynamic title>" />
<meta property="og:description" content="<dynamic description>" />
<meta property="og:image" content="<candidate photo OR muni map OR site default>" />
<meta property="og:url" content="<canonical URL>" />
<meta property="og:locale" content="is_IS" /> <!-- or en_US, pl_PL -->
<meta property="og:locale:alternate" content="en_US" />
<meta property="og:locale:alternate" content="pl_PL" />
```

For candidate pages, the `og:image` should be the candidate's portrait
photo (resized to 1200×630, or at least a 16:9 crop). For muni/party
pages, generate a composite image (party logo + muni name) at build time,
or fall back to the existing site OG image.

---

## 3. Content for indexability

### Front-page hero text

Currently the front page is mostly an interactive map with minimal text
content. Add a paragraph that:

- Captures the search intent that should land here
- Introduces the site's purpose in the page's language
- Uses the keywords searchers actually type

**IS** (above the fold, after the hero map):

> Finndu út allt um öll framboð í þínu sveitarfélagi fyrir
> sveitarstjórnarkosningar 16. maí 2026. Sjáðu frambjóðendur, stefnumál
> og fréttir um öll 64 sveitarfélögin á Íslandi á einum stað — algerlega
> ókeypis og án innskráningar.

**EN** (a separate paragraph for the EN-locale page):

> Moved to Iceland and trying to figure out the 2026 municipal elections?
> Look up your municipality, see every party that's running, compare
> their platforms and meet the candidates — all in one place, in English.

**PL** (same pattern, Polish):

> Przeprowadzasz się do Islandii lub mieszkasz tu od dawna i chcesz
> zorientować się w wyborach samorządowych 2026? Znajdź swoją gminę,
> zobacz listę kandydatów, porównaj programy partii — w języku polskim.

These paragraphs do three things at once:
1. Give Google clear, indexable text about what the site is.
2. Surface the **intent variants** (Icelander wanting overview vs. expat
   needing onboarding) — both groups search differently.
3. Provide natural locale-targeted content for hreflang variants.

### Per-page introductory copy

Every muni / party / candidate page should have at least 1–2 sentences of
indexable text near the top of the body, beyond the data fields. Examples:

- **Muni page**: One sentence describing the muni (population, region)
  followed by "X framboð bjóða fram til sveitarstjórnar í {muni} 2026."
- **Party page**: First-line copy that pulls the tagline + lead candidate
  + ballot-1's quick credentials.
- **Candidate page**: The first sentence of the bio is fine (and we have
  bios for ballot 1–6 candidates after the recent scan).

This isn't decoration — pages with <100 words of indexable text are
weighted lower by Google.

---

## 4. Standard SEO checklist (what else)

### Crawlability

- **`robots.txt`** at `/robots.txt`. Allow everything; declare sitemap
  location.
- **`sitemap.xml`** at `/sitemap.xml`. List every muni / party / candidate
  URL with `<lastmod>`, `<changefreq>weekly</changefreq>`. Include
  hreflang annotations per URL. Re-generate after every data change.
- **Submit to Google Search Console** and **Bing Webmaster Tools**. This
  is how you verify the site is being crawled and see which queries land
  on which pages.
- **Canonical URL** on every page: `<link rel="canonical" href="..." />`.
  Prevents accidental duplicate-content from query strings, trailing
  slashes, www vs non-www.

### Structured data (Schema.org)

This is what gives you those rich SERP results — breadcrumbs,
"Knowledge Panel"-style summaries, candidate cards. JSON-LD blocks in
`<head>`:

- **Site-wide**: `WebSite` with `potentialAction.SearchAction` (lets
  users search the site from Google's results bar).
- **Muni page**: `BreadcrumbList` (Home → Garðabær), plus an `Event`
  marking the election with type `PoliticalEvent`.
- **Party page**: `Organization` (type `PoliticalParty`), with
  `member` listing candidates as `Person` references.
- **Candidate page**: `Person` with `affiliation` (the party), `jobTitle`,
  optional `image` (the portrait), `sameAs` (links to social profiles
  from `social` array). Maybe `Politician` extended type if structured
  data spec allows.

Test with [Google's Rich Results Test](https://search.google.com/test/rich-results)
during development.

### Internal linking

- Every page has a clear path back: candidate → party → muni → home.
  Currently the back button works; add visible breadcrumb HTML so it's
  also crawlable.
- Cross-links between siblings: from a party page, link to the other
  parties in the same muni. From a candidate, link to siblings on the
  same list. This **distributes ranking authority** ("PageRank flow") and
  helps users.
- The home page should have a list (or grid) of all 64 municipalities as
  internal links. Currently the map fulfils visual UX but Googlebot
  doesn't click map markers.

### Image SEO

- **Alt text** on every candidate photo: `alt="<Name> – <Party> í <Muni>"`.
  Currently many `<img alt="">` are empty in the rendered output.
- **File names** matter less than alt text but: prefer `kjartan-atli.jpg`
  over `da7ff8d6f508600a.jpg` if regenerating. (Hashes are fine for
  cache-bust; this is a marginal optimisation.)
- **Lazy-load**: `<img loading="lazy">` for everything below the fold.
  Already partially in place; verify on the candidate grid.
- **width/height attributes** on every `<img>` to prevent CLS (Cumulative
  Layout Shift, a Core Web Vitals metric).

### Performance / Core Web Vitals

These are direct Google ranking factors as of 2021+. Measure with
[PageSpeed Insights](https://pagespeed.web.dev/).

- **LCP (Largest Contentful Paint)** ≤ 2.5s. The map is likely the LCP
  element — compress / optimise the basemap tiles.
- **INP (Interaction to Next Paint)** ≤ 200ms. The accordion expand
  animation should stay snappy; profile if there's noticeable lag on
  big munis (Reykjavík has 11 parties).
- **CLS (Cumulative Layout Shift)** ≤ 0.1. Image dimensions on every
  `<img>` is the easiest win.

### Mobile

- Already responsive. Run [Mobile-Friendly Test](https://search.google.com/test/mobile-friendly).
- Verify tap targets aren't too small on candidate cards.

### Local relevance

- Every muni page is geographically anchored. Add structured data
  `Place` with `geo` (lat/lng) — we have polygon data. This signals to
  Google that searches like "kosningar nálægt mér" or "Garðabær elections"
  should match.
- Hreflang for `is-IS`, `en-IS`, `pl-IS` (Icelandic-Polish-in-Iceland) —
  if you want to be precise about region targeting. The plain `en` /
  `pl` codes are usually fine.

### Monitoring

- **Google Search Console**: register, submit sitemap, watch the
  "Performance" panel for impressions / clicks / CTR / position over time.
- **Google Analytics** (already loaded as `G-KVRHXCHYLV`). Set up custom
  dimensions for `muni` and `party` so you can see which combinations get
  the most organic traffic.
- **Coverage** report in GSC: catches indexing problems (404s, soft 404s,
  blocked pages, JS-rendering failures).

---

## 5. Phased implementation roadmap

Order of operations matters; some changes feed into others.

### Phase 1 — Foundations (1 day)

These are low-risk and high-impact; do them first.

1. Add dynamic `<title>` and `<meta name="description">` via JS at page
   load (read URL params, set in head). Same for `og:title`, `og:image`,
   `og:url`. **No URL change yet** — same routes, just better head tags.
2. Add `<link rel="canonical">` to each page.
3. Generate and serve `sitemap.xml` (write a script that reads
   `candidates.js` and emits all current `?id=...&party=...` URLs).
4. Add `robots.txt`.
5. Verify in Google Search Console.
6. Add front-page hero copy in IS / EN / PL.

After Phase 1, Google can index the data with proper context. The URL
scheme is still query-param-based but works.

### Phase 2 — URL scheme (2–3 days)

This is the bigger lift because it requires a build step and route
handling.

1. Build script: read `candidates.js`, emit `/<muni>/index.html`,
   `/<muni>/<party>/index.html`, `/<muni>/<party>/<candidate>/index.html`
   for each route, in IS / EN / PL.
2. Each generated HTML has the right `<title>`, meta, OG, canonical,
   hreflang, and includes a `<noscript>` block with the visible content
   (so Googlebot's "fetch as Google" sees something even without JS).
3. Existing client-side JS continues to hydrate the page for interactive
   bits.
4. Add 301 redirects from old query-param URLs to new path-based URLs
   (via meta refresh or a small JS shim, since GitHub Pages can't do
   real 301s).
5. Update `sitemap.xml` to use new URLs.
6. Resubmit to Google.

### Phase 3 — Structured data + breadcrumbs (1 day)

Add JSON-LD blocks for `BreadcrumbList`, `Person`, `Organization`,
`Event`. Render visible breadcrumbs above each non-home page. Test in
Google's Rich Results Test.

### Phase 4 — Polish & monitor (ongoing)

- Image alt text everywhere
- Width/height on all `<img>`
- PageSpeed audit and fix CLS / LCP regressions
- Watch Search Console for crawl errors
- Add per-page intro copy where it's still thin

---

## 6. What's intentionally not in this plan

- **Backlink building / outreach** — usually the backbone of SEO plans
  for commercial sites, but for a 4-week-lifespan civic-info site the
  ROI isn't there. Organic news pickup and party-list link-back is
  enough.
- **Ads / SEM** — out of scope.
- **Multi-region targeting** — the entire site is Iceland-focused; no
  need to compete in other countries' search results.

---

## 7. Open decisions (need a call from you)

- **Slug separator**: hyphen or underscore? (Recommend hyphen.)
- **URL hierarchy**: flat (`/samfylkingin-i-gardabae`) or nested
  (`/gardabaer/samfylkingin`)? (Recommend nested.)
- **Pre-rendering build step**: agree to add a Python build script that
  emits the ~880 HTML files? Without this, the URL-scheme change only
  half-works.
- **EN/PL muni/party copy**: write these yourself, or have an LLM draft
  them and you proofread?
- **Slug for places with diacritics**: strip aggressively (`Hörgársveit
  → horgarsveit`) or keep one-letter approximations (`hoergaarsveit`)?
  (Recommend strip aggressively — matches what users would actually
  type into Google.)
