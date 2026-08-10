"""
Find candidates with non-election news articles not yet in scan-review.html
Parses candidates.js with regex since it's JS not JSON.
"""
import re

# Election keywords to filter out
ELECTION_KEYWORDS = [
    'framboðslisti', 'framboðslista', 'framboð', 'boðar fram', 'gefur kost',
    'leiðir lista', 'leiðir listann', 'kynnir lista', 'kynnir framboð',
    'prófkjör', 'profkjor',
    'sveitarstjórnarkosning', 'kosningar', 'kosning',
    'oddvitakjör', 'kjörinn oddviti',
    'fullskipaður framboðslisti',
    'í fyrsta sæti', 'í öðru sæti', 'í þriðja sæti',
    'sækist eftir 1.', 'sækist eftir 2.', 'sækist eftir 3.',
    'vill leiða lista', 'verður oddviti', 'nýr oddviti', 'nýjan oddvita',
    'kosningaskrifstofu', 'kosningaskrifstofa',
    'tilkynna framboð', 'tilkynnir framboð',
    'frambjóðendur', 'frambjóðandi',
    'Framboðslisti', 'Framboð', 'Kosningar',
    'leiðir D-lista', 'leiðir B-lista', 'leiðir S-lista', 'leiðir M-lista',
    'leiðir V-lista', 'leiðir C-lista', 'leiðir lista',
    'oddviti Sjálfstæðis', 'oddviti Framsóknar', 'oddviti Samfylkingar',
    'oddviti Viðreisnar', 'oddviti Miðflokks',
]

def is_election_article(title):
    title_lower = title.lower()
    for kw in ELECTION_KEYWORDS:
        if kw.lower() in title_lower:
            return True
    return False

# Read candidates.js
with open(r'F:\Claude Projects\iceland-elections\js\data\candidates.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Read scan-review.html
with open(r'F:\Claude Projects\iceland-elections\scan-review.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Get existing names in scan-review
existing_names = set(re.findall(r'<div class="card-title">([^<]+)</div>', html))
print(f"Names already in scan-review.html: {len(existing_names)}")

# Parse municipality blocks
# Each municipality is like: const RVK = { ... list: [ ... ] }
# or embedded in CANDIDATES_DATA

# Strategy: find all name+news pairs using regex
# Pattern: candidate name followed by their news array
# List entries look like: [1, 'Name', 'occupation', 'image', { news: [...], ... }]
# or just [seat, 'Name', ...] with a news property somewhere

# Better approach: find all news arrays with their context
# Search for patterns like: 'Name', '...', '...', '...', { news: [
# or: news: [ {title: '...', url: '...'}, ...]

results = []

# Find all municipality blocks
# Municipalities are defined as: const XXX = { ... } or within CANDIDATES_DATA
# Let's find candidate list entries: [number, 'Name', occupation, image, {news:[...]}]

# Match list entries with news
# Pattern: [digit, 'CandidateName', ..., {... news: [{title: '...', url: '...'},...] ...}]
# This is complex JS, so let's do it line-by-line context search

# Find all occurrences of news arrays
news_pattern = re.compile(
    r"news:\s*\[(.*?)\]",
    re.DOTALL
)

# Find candidate name entries (they appear as list entries)
# [1, 'Hildur Björnsdóttir', 'Borgarfulltrúi', 'images/...', {
list_entry_pattern = re.compile(
    r"\[\s*(\d+)\s*,\s*'([^']+)'\s*,\s*'([^']*)'\s*,\s*'([^']*)'\s*,\s*\{",
)

# Also match double-quoted names
list_entry_pattern2 = re.compile(
    r'\[\s*(\d+)\s*,\s*"([^"]+)"\s*,\s*"([^"]*)"\s*,\s*"([^"]*)"\s*,\s*\{',
)

# Find municipality name from nearby context
# const RVK = { or 'Reykjavík' or name: 'Reykjavík'
muni_pattern = re.compile(r"(?:const\s+(\w+)\s*=|name:\s*['\"]([^'\"]+)['\"])")

# Map const names to municipality display names
CONST_TO_MUNI = {
    'RVK': 'Reykjavík', 'KOP': 'Kópavogur', 'HAF': 'Hafnarfjörður',
    'GAR': 'Garðabær', 'MOS': 'Mosfellsbær', 'AKR': 'Akranes',
    'SNB': 'Suðurnesjabær', 'RNB': 'Reykjanesbær', 'GRD': 'Grindavík',
    'VEY': 'Vestmannaeyjar', 'ARB': 'Árborg', 'FLB': 'Flóahreppur',
    'BBG': 'Borgarbyggð', 'SNF': 'Snæfellsbær', 'DAL': 'Dalvíkurbyggð',
    'AKU': 'Akureyri', 'NTH': 'Norðurþing', 'FAX': 'Faxaflói',
    'ISA': 'Ísafjörður', 'FJB': 'Fjarðabyggð', 'MUL': 'Múlaþing',
    'FLH': 'Fljótsdalshérað', 'EYB': 'Eyjafjarðarsveit',
    'HOF': 'Hornafjörður', 'SKF': 'Skaftárhreppur',
}

# Parse the JS file to extract candidate→news mappings
# Strategy: split by list entries and find the nearest news array

# Find all positions of list entries
entries = []
for m in list_entry_pattern.finditer(content):
    entries.append((m.start(), m.group(1), m.group(2)))  # pos, seat, name
for m in list_entry_pattern2.finditer(content):
    entries.append((m.start(), m.group(1), m.group(2)))

entries.sort(key=lambda x: x[0])
print(f"Found {len(entries)} candidate entries in candidates.js")

# For each entry, find the news array that follows it
def find_news_after(pos, content):
    """Find the news array starting after position pos, before the next list entry."""
    # Look ahead up to 3000 chars for a news: [...] block
    chunk = content[pos:pos+3000]
    m = re.search(r'news:\s*\[', chunk)
    if not m:
        return []

    news_start = pos + m.end()
    # Now find the closing ] - need to handle nested objects
    depth = 1
    i = news_start
    while i < len(content) and depth > 0:
        if content[i] == '[':
            depth += 1
        elif content[i] == ']':
            depth -= 1
        i += 1

    news_block = content[news_start:i-1]

    # Extract title/url pairs from news block
    articles = []
    # Match {title: '...', url: '...'} or {url: '...', title: '...'}
    article_pattern = re.compile(
        r'\{[^}]*title:\s*[\'"]([^\'"]*)[\'"][^}]*url:\s*[\'"]([^\'"]*)[\'"][^}]*\}|'
        r'\{[^}]*url:\s*[\'"]([^\'"]*)[\'"][^}]*title:\s*[\'"]([^\'"]*)[\'"][^}]*\}',
        re.DOTALL
    )
    for am in article_pattern.finditer(news_block):
        if am.group(1):
            title, url = am.group(1), am.group(2)
        else:
            url, title = am.group(3), am.group(4)
        if title and url:
            articles.append({'title': title, 'url': url})

    return articles

# Get municipality context for each entry
def get_muni_for_pos(pos, content):
    """Find which municipality this candidate belongs to by looking backwards."""
    chunk = content[max(0, pos-5000):pos]
    # Find last const XXX =
    matches = list(re.finditer(r'const\s+(\w+)\s*=\s*\{', chunk))
    if matches:
        const_name = matches[-1].group(1)
        return CONST_TO_MUNI.get(const_name, const_name)
    # Look for name: 'Municipality'
    name_matches = list(re.finditer(r"name:\s*['\"]([^'\"]+)['\"]", chunk))
    if name_matches:
        return name_matches[-1].group(1)
    return 'Unknown'

# Find party context
def get_party_for_pos(pos, content):
    """Find which party letter this candidate belongs to."""
    chunk = content[max(0, pos-2000):pos]
    # Look for party letter pattern like: D: { or 'D': { or letter: 'D'
    matches = list(re.finditer(r"(?:^|\s)([A-ZÁÉÍÓÚÝÞÆÖ]{1,4}):\s*\{", chunk, re.MULTILINE))
    if matches:
        return matches[-1].group(1)
    matches2 = list(re.finditer(r"letter:\s*['\"]([^'\"]+)['\"]", chunk))
    if matches2:
        return matches2[-1].group(1)
    return '?'

print("\nSearching for candidates with non-election news...\n")

candidates_found = []
for pos, seat, name in entries:
    if name in existing_names:
        continue

    articles = find_news_after(pos, content)
    if not articles:
        continue

    good = [a for a in articles if not is_election_article(a['title'])]
    if not good:
        continue

    muni = get_muni_for_pos(pos, content)
    party = get_party_for_pos(pos, content)

    candidates_found.append({
        'name': name,
        'municipality': muni,
        'party': party,
        'seat': int(seat),
        'articles': good
    })

print(f"Total new candidates with non-election news: {len(candidates_found)}\n")
print("=" * 80)

# Group by municipality
by_muni = {}
for c in candidates_found:
    m = c['municipality']
    by_muni.setdefault(m, []).append(c)

for muni, cands in sorted(by_muni.items()):
    print(f"\n### {muni}")
    for c in sorted(cands, key=lambda x: (x['party'], x['seat'])):
        print(f"  {c['name']} | {c['party']} #{c['seat']} | {len(c['articles'])} articles")
        for a in c['articles']:
            print(f"    [{a['title']}]")
            print(f"     {a['url']}")
