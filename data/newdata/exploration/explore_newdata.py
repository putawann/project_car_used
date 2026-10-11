"""Profile the used-car files in this folder before cleaning.

usage: python explore_newdata.py [data_folder]   (default: the parent folder, data/newdata)
writes explore_report.md next to this script and prints the same report.
Standard library only.
"""
import collections
import csv
import os
import re
import statistics as st
import sys

sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
FOLDER = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(HERE)
FILES = {
    'one2car_v1': 'used_car_clean_one2car_v1.csv',
    'one2car_v2': 'used_car_clean_one2car_v2.csv',
    'kaidee': 'kaidee_cleandata.csv',
}
TEXT_COLS = {'seller_comments', 'url', 'source_url', 'title', 'scraped_at'}  # free text: skip value counts
CURRENT_YEAR = 2026

out = []


def p(line=''):
    out.append(line)


def load(path):
    with open(path, encoding='utf-8-sig', newline='') as fh:
        return list(csv.DictReader(fh))


# ---------- parsing helpers ----------
def to_num(v):
    """'62,000 กม.' -> 62000.0 ; '' / text -> None"""
    v = (v or '').strip()
    if not v:
        return None
    m = re.fullmatch(r'[^\d\-]*(-?[\d,]*\.?\d+)\s*[^\d]*', v)
    if not m:
        return None
    try:
        return float(m.group(1).replace(',', ''))
    except ValueError:
        return None


def kind(values):
    """numeric if >= 95% of non-empty values parse as numbers"""
    filled = [v for v in values if v.strip()]
    if not filled:
        return 'empty'
    nums = sum(to_num(v) is not None for v in filled)
    plain = sum(bool(re.fullmatch(r'-?\d+(\.\d+)?', v.strip())) for v in filled)
    if plain / len(filled) >= 0.95:
        return 'numeric'
    if nums / len(filled) >= 0.95:
        return 'numeric-with-text'  # e.g. '62,000 กม.' needs parsing
    return 'text'


def iqr_bounds(xs):
    q = st.quantiles(xs, n=4)
    lo, hi = q[0] - 3 * (q[2] - q[0]), q[2] + 3 * (q[2] - q[0])
    return lo, hi


def table(headers, rows):
    p('| ' + ' | '.join(headers) + ' |')
    p('|' + '---|' * len(headers))
    for r in rows:
        p('| ' + ' | '.join(str(x).replace('|', '/') for x in r) + ' |')
    p()


# ---------- generic profile ----------
def profile(name, rows):
    cols = list(rows[0])
    n = len(rows)
    p(f'## {name}  ({n:,} rows x {len(cols)} columns)')
    p()
    p('### Columns')
    info = []
    kinds = {}
    for c in cols:
        vals = [r[c] or '' for r in rows]
        k = 'text' if c in TEXT_COLS else kind(vals)
        kinds[c] = k
        empty = sum(not v.strip() for v in vals)
        uniq = len(set(vals))
        sample = ', '.join(list(dict.fromkeys(v[:25] for v in vals if v.strip()))[:3])
        info.append((c, k, f'{empty:,} ({empty / n:.1%})', f'{uniq:,}', sample))
    table(['column', 'type', 'empty', 'unique', 'examples'], info)

    p('### Numeric columns')
    stats = []
    outliers = {}
    for c in cols:
        if not kinds[c].startswith('numeric') or c in ('listing_id',) or c in TEXT_COLS:
            continue
        xs = [to_num(r[c]) for r in rows]
        xs = [x for x in xs if x is not None]
        if len(xs) < 4:
            continue
        lo, hi = iqr_bounds(xs)
        bad = [x for x in xs if x < lo or x > hi] if hi > lo else None  # IQR 0: rule meaningless
        outliers[c] = (lo, hi)
        stats.append((c, f'{min(xs):,.0f}', f'{st.quantiles(xs, n=4)[0]:,.0f}', f'{st.median(xs):,.0f}',
                      f'{st.quantiles(xs, n=4)[2]:,.0f}', f'{max(xs):,.0f}', f'{len(bad):,}' if bad is not None else '- (IQR = 0)'))
    table(['column', 'min', 'p25', 'median', 'p75', 'max', 'outliers (3xIQR)'], stats)

    p('### Category columns (top values)')
    for c in cols:
        if c in TEXT_COLS or kinds[c].startswith('numeric'):
            continue
        cnt = collections.Counter((r[c] or '').strip() for r in rows)
        if len(cnt) > 300:
            p(f'- **{c}**: {len(cnt):,} distinct values (high cardinality); top: ' +
              ', '.join(f'{k or "∅"} ({v:,})' for k, v in cnt.most_common(8)))
            continue
        p(f'- **{c}** ({len(cnt)} values): ' + ', '.join(f'{k or "∅"} ({v:,})' for k, v in cnt.most_common(25)))
        # labels that differ only by case/spacing, e.g. 'Light Blue' vs 'Light blue'
        groups = collections.defaultdict(list)
        for k in cnt:
            groups[re.sub(r'[\s_\-]', '', k.lower())].append(k)
        dup = [g for g in groups.values() if len(g) > 1]
        if dup:
            p(f'  - ⚠ same label, different spelling: ' + '; '.join(' / '.join(g) for g in dup))
    p()

    p('### Duplicates')
    key = 'listing_id' if 'listing_id' in cols else 'source_url'
    keys = collections.Counter(r[key] for r in rows)
    full = collections.Counter(tuple(r.values()) for r in rows)
    p(f'- duplicate `{key}`: {sum(v - 1 for v in keys.values() if v > 1):,}')
    p(f'- fully identical rows: {sum(v - 1 for v in full.values() if v > 1):,}')
    p()
    return kinds, outliers


# ---------- domain checks ----------
def check_one2car(name, rows):
    p(f'### Domain checks: {name}')
    issues = collections.Counter()
    examples = collections.defaultdict(list)

    def flag(tag, r, detail=''):
        issues[tag] += 1
        if len(examples[tag]) < 3:
            examples[tag].append(f"{r['listing_id']} {r['title'][:50]} {detail}")

    shared = collections.Counter(r.get('seller_comments', '') for r in rows)  # column may be stripped
    for r in rows:
        price, km, cc = to_num(r['price_thb']), to_num(r['mileage_km']), to_num(r['engine_capacity_cc'])
        year = to_num(r['prod_year'])
        if price is not None and price < 20000:
            flag('price < 20,000 THB (placeholder?)', r, f'price={price:,.0f}')
        if km is not None and km <= 5000 and year and year <= CURRENT_YEAR - 2:
            flag('mileage <= 5,000 km on car >= 2 years old', r, f'km={km:,.0f}')
        if km is not None and km > 1_000_000:
            flag('mileage > 1,000,000 km', r, f'km={km:,.0f}')
        if year and (year < 1950 or year > CURRENT_YEAR):
            flag('year out of range', r, f'year={year:.0f}')
        ty = r['title'][:4]
        if ty.isdigit() and year and int(ty) - year not in (0, 1):
            flag('title year differs from prod_year by >1', r, f'title={ty} prod={year:.0f}')
        tl = re.search(r'\s(\d\.\d)\s', r['title'])
        if tl and cc and abs(float(tl.group(1)) * 1000 - cc) > 100:
            flag('engine_capacity_cc differs from litres in title', r, f'title={tl.group(1)} cc={cc:.0f}')
        if r['fuel_type'] in ('EV', 'Electric') and cc:
            flag('labelled EV/Electric but has engine cc', r, f'cc={cc:.0f}')
        if not r['engine_capacity_cc'] and r['fuel_type'] not in ('EV', 'Electric'):
            flag('engine cc missing on non-EV', r)
        if km is not None and km % 5000 == 2500:
            issues['mileage is a bucket midpoint (x2500/x7500)'] += 1
        if r.get('seller_comments') and shared[r['seller_comments']] > 1:
            issues['seller_comments reused by other listings (dealer template)'] += 1
    rows_out = [(k, f'{v:,}', '<br>'.join(examples[k])) for k, v in issues.most_common()]
    table(['check', 'rows', 'examples'], rows_out)


def check_kaidee(rows):
    p('### Domain checks: kaidee')
    issues = collections.Counter()
    examples = collections.defaultdict(list)

    def flag(tag, r, detail=''):
        issues[tag] += 1
        if len(examples[tag]) < 3:
            examples[tag].append(f"{r['source_url'].rsplit('-', 1)[-1]} {r['brand']} {r['model']} {r['submodel'][:30]} {detail}")

    units = collections.Counter(re.sub(r'[\d,.\s]', '', r['mileage']) for r in rows)
    p('- mileage unit text: ' + ', '.join(f'`{k or "∅"}` ({v:,})' for k, v in units.most_common()))
    for r in rows:
        eng, km, year, price = to_num(r['engine']), to_num(r['mileage']), to_num(r['year']), to_num(r['price'])
        sub = re.match(r'\s*(\d\.\d)', r['submodel'])
        if sub and eng is not None and abs(float(sub.group(1)) - eng) > 0.05:
            flag('engine differs from litres in submodel', r, f'engine={r["engine"]}')
        if eng is not None and eng > 10:
            flag('engine looks like cc, not litres', r, f'engine={r["engine"]}')
        if not r['mileage'].strip() or not re.search(r'กม', r['mileage']):
            flag('mileage without unit text', r, f'mileage={r["mileage"]!r}')
        if not r['submodel'].strip():
            flag('submodel empty', r)
        if price is not None and price < 20000:
            flag('price < 20,000 THB', r, f'price={price:,.0f}')
        if km is not None and km > 1_000_000:
            flag('mileage > 1,000,000 km', r, f'km={km:,.0f}')
        if km is not None and km <= 5000 and year and year <= CURRENT_YEAR - 2:
            flag('mileage <= 5,000 km on car >= 2 years old', r, f'km={km:,.0f}')
        if year and (year < 1950 or year > CURRENT_YEAR):
            flag('year out of range (Buddhist year?)', r, f'year={year:.0f}')
    rows_out = [(k, f'{v:,}', '<br>'.join(examples[k])) for k, v in issues.most_common()]
    table(['check', 'rows', 'examples'], rows_out)


# ---------- cross-file ----------
def cross(data):
    p('## Cross-file comparison')
    p()
    v1, v2, kd = data['one2car_v1'], data['one2car_v2'], data['kaidee']
    a = {r['listing_id']: r for r in v1}
    b = {r['listing_id']: r for r in v2}
    both = a.keys() & b.keys()
    p(f'- one2car listing_id: v1 {len(a):,}, v2 {len(b):,}, in both {len(both):,}, only v1 {len(a.keys() - b.keys()):,}, only v2 {len(b.keys() - a.keys()):,}')
    p(f'- union of one2car + kaidee ≈ {len(a.keys() | b.keys()) + len(kd):,} rows (kaidee has no shared id)')
    p()
    p('### Same listing, different value (v1 vs v2)')
    diffs = []
    for c in ['brand', 'model', 'prod_year', 'price_thb', 'mileage_km', 'engine_capacity_cc', 'transmission',
              'fuel_type', 'exterior_color', 'body_type', 'seats', 'seller_type']:
        d = collections.Counter((a[i][c], b[i][c]) for i in both if a[i][c] != b[i][c])
        diffs.append((c, f'{sum(d.values()):,}', ', '.join(f'{x}→{y} ({n})' for (x, y), n in d.most_common(4))))
    table(['column', 'rows differ', 'most common (v1→v2)'], diffs)
    swapped = [(i, a[i]['brand'] + ' ' + a[i]['model'], b[i]['brand'] + ' ' + b[i]['model']) for i in sorted(both)
               if a[i]['brand'] != b[i]['brand'] or re.sub(r'[\s\-]', '', a[i]['model']) != re.sub(r'[\s\-]', '', b[i]['model'])
               and not (a[i]['model'] in b[i]['model'] or b[i]['model'] in a[i]['model'])]
    p(f'- ⚠ same listing_id but a different car in v1 and v2 (id reused or wrong data): {len(swapped)}'
      + ('; e.g. ' + ', '.join(f'{i}: {x} → {y}' for i, x, y in swapped[:5]) if swapped else ''))
    p()
    p('Price differences between scrapes are expected (price drops); label differences such as Grey→Grey Bronze are a vocabulary mismatch.')
    p()

    p('### Category vocabularies to harmonise')
    pairs = [('brand', 'brand', 'brand'), ('transmission', 'transmission', 'gear'), ('fuel_type', 'fuel_type', 'fuel'),
             ('exterior_color', 'exterior_color', 'color'), ('body_type', 'body_type', 'car_type')]
    for label, c12, ck in pairs:
        s1 = collections.Counter(r[c12] for r in v1)
        s2 = collections.Counter(r[c12] for r in v2)
        sk = collections.Counter(r[ck] for r in kd)
        p(f'- **{label}**')
        p(f'  - v1: ' + ', '.join(f'{k} ({v:,})' for k, v in s1.most_common(15)))
        p(f'  - v2: ' + ', '.join(f'{k} ({v:,})' for k, v in s2.most_common(15)))
        p(f'  - kaidee `{ck}`: ' + ', '.join(f'{k} ({v:,})' for k, v in sk.most_common(15)))
        if label == 'brand':
            up = lambda s: {k.upper().replace(' ', '-') for k in s}
            only_k = sorted(up(sk) - up(s1) - up(s2))
            p(f'  - brands only in kaidee: {", ".join(only_k) or "-"}')
    p()

    p('### Model names: kaidee vs one2car (same brand)')
    o_models = collections.defaultdict(set)
    for r in v1 + v2:
        o_models[r['brand'].upper()].add(re.sub(r'[\s\-]', '', r['model'].upper()))
    miss = collections.Counter()
    for r in kd:
        if re.sub(r'[\s\-]', '', r['model'].upper()) not in o_models.get(r['brand'].upper(), set()):
            miss[f"{r['brand']} {r['model']}"] += 1
    p(f'- kaidee rows whose brand+model is not spelled the same in one2car: {sum(miss.values()):,}')
    p('  - top: ' + ', '.join(f'{k} ({v})' for k, v in miss.most_common(20)))
    p()


def main():
    data = {}
    p('# Used-car data exploration')
    p()
    for name, fn in FILES.items():
        path = os.path.join(FOLDER, fn)
        size = os.path.getsize(path) / 1e6
        data[name] = load(path)
        p(f'- `{fn}` ({size:,.1f} MB) → **{name}**')
    p()
    for name, rows in data.items():
        profile(name, rows)
        if name.startswith('one2car'):
            check_one2car(name, rows)
        else:
            check_kaidee(rows)
    cross(data)
    report = '\n'.join(out)
    with open(os.path.join(HERE, 'explore_report.md'), 'w', encoding='utf-8') as fh:
        fh.write(report)
    print(report)


if __name__ == '__main__':
    main()
