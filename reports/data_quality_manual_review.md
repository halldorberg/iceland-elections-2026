# Data quality flags — needs manual review

These flags surfaced during the bio-research scans (batches 1–8). Each one
needs source verification (party kjörstjórn list, local news, etc.) before
we change names or occupations in `js/data/candidates.js`. Listed in priority
order.

## High priority — ballot-position / name discrepancies

### F-list Reykjavík — positions 6 and 7
- Our data: `#6 Lilja Sigríður Steingrímsdóttir`, `#7 Sigurður Rúnarsson`
- Status: `flokkurfolksins.is/reykjavik/frambjodendur.html` only publishes the
  top 5 ("Efstu 5 sætin"); positions 6+ are filled by "þingmenn og stofnendur
  flokksins" (MPs and party founders). Bio-research agent A claimed the names
  don't match, but the public page doesn't include positions 6+ to check.
- Action: verify against the official kjörstjórn-filed list (e.g. via
  reykjavik.is/kosningar or kosningasaga.wordpress.com).

### RTY Á-listinn (RYA) — position 4
- Our data: `#4 Viðar M. Þorsteinsson`, `#5 Eiríkur Vilhelm Sigurðsson`
- Source conflict: alisti.is shows Viðar at #5; sunnlenska.is and dfs.is say
  #4. (Bio agent M flagged.)
- Action: verify against kjörstjórn announcement.

### RTE Sjálfstæðis (D) — position 5
- Our data: `#5 Bjarki Freyr Sigurjónsson`
- Source conflict: sunnlenska.is reports Bjarki at #9 with Helgi Valur
  Smárason at #5. May be an outdated revision.
- Action: verify against kjörstjórn announcement.

### SNB Miðflokkurinn (M) — list not yet published
- Our data: `#4 Sigríður Rós Jónatansdóttir`, `#5 Ólafur Fannar Þórhallsson`
  (both have photos)
- Status: kosningasaga article from 2026-04-07 says "M-deild Suðurnesjabæjar
  undirbýr framboð" but the list hasn't been posted on xs.is. Names + photos
  are in our data but not externally verifiable.
- Action: re-check xs.is and Miðflokkurinn pages closer to election.

## Medium priority — single-field corrections

### SFJ.D.4 Rósanna — name spelling + occupation
- Our data: `Rósanna Valdimársdóttir`, `Vélstjóri og reiðkennari`
- Bio agent J's claim: name should be `Rosanna Valdimarsdóttir` (no acute on
  second 'a'), occupation should be `Rekstraraðili og reiðkennari` per xd.is
  list and her own Feykir article.
- Status: I couldn't surface either via DDG or curl on xd.is/skagafjordur in
  this session.
- Action: check xd.is Skagafjörður D-list page and feykir.is article directly.

### RNB.D.6 Guðlaug Sunna — first name shortening
- Our data: `Guðlaug Sunna Gunnarsdóttir`, `Náms- og starfsráðgjafi í
  Fjölbrautaskóla Suðurnesja`
- Bio agent P's claim: xd.is + mbl.is call her "Sunna Gunnarsdóttir" (without
  Guðlaug). Occupation matches.
- Possibility: she goes by "Sunna" publicly but legal name has both. Some
  Icelanders use middle names as their public name.
- Action: confirm preferred public name; if "Sunna" only, update.

### HGS.D.5 Björg Ingadóttir — occupation
- Our data: `Lagastúdent`
- Bio agent N's claim: kaffid.is describes her as "nemi til lögg.
  fasteignasala" (real-estate licensure trainee), not law student.
- Action: verify against kaffid.is article + xd.is list.

### HAF.D.9 Júlíus Freyr Bjarnason — occupation
- Our data: `Vélfræðingur`
- Bio agent P's claim: xd.is Hafnarfjörður lists him as
  "framkvæmdarstjóri/eigandi", not vélfræðingur. May be outdated.
- Action: verify against xd.is/folkid.

### NPG.D.3 Kristján Friðrik Sigurðsson — occupation
- Our data: `Fiskvísindamaður` (fish scientist)
- Bio agent G's claim: party source says "fiskeldisfræðingur" (aquaculturist).
- Action: verify on xd.is Norðurþing list.

## Low priority — bio confidence concerns

### VOG.D.3 Hulda Birna Helgadóttir Blöndal — workplace unverifiable
- Our data lists her as "Deildarstjóri hjá Klettabæ" — bio agent H couldn't
  find any preschool/service called "Klettabær" in Vogar (possibly a typo for
  another facility, or she's based in Reykjanesbær/Suðurnesjabær).
- Action: verify workplace name via Vogar D-list publication.

### F-list Reykjavík #6, #7 (re-listed) — see top entry above.
