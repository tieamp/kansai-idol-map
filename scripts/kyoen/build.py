import json, math, re, unicodedata, collections, itertools, sys, os, datetime
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PT = lambda *a: os.path.join(ROOT, *a)
G = json.load(open(PT('data','groups.json'), encoding='utf-8'))
reg = {g['name']: g for g in G['groups']}
def norm(s):
    s = unicodedata.normalize('NFKC', s).lower()
    return re.sub(r'[\s　]+', '', s).replace('’',"'")
nreg = {norm(n): n for n in reg}
events = []
for line in open(PT('data','kyoen','events.txt'), encoding='utf-8'):
    line = line.rstrip('\n')
    if not line or line.startswith('#'): continue
    d, eid, title, venue, pref, acts = line.split('|')
    names = []
    for a in acts.split('/'):
        a = a.strip()
        if not a: continue
        a = nreg.get(norm(a), a)
        if a not in names: names.append(a)
    url = None
    if eid.isdigit(): url = f'https://www.eventernote.com/events/{eid}'
    elif eid.startswith('T'): url = 'https://tiget.net/events/' + re.sub(r'\D','',eid)
    events.append(dict(d=d, t=title, v=venue, p=pref, a=names, u=url))
events.sort(key=lambda e: (e['d'], e['t']), reverse=True)
ids = {}
acts = []
def aid(n):
    if n not in ids:
        ids[n] = len(acts)
        g = reg.get(n)
        acts.append(dict(n=n, r=1 if g else 0, x=(g or {}).get('x'), f=(g or {}).get('xFollowers'),
                         ar=(g or {}).get('area'), ag=(g or {}).get('agency')))
    return ids[n]
for e in events: e['a'] = [aid(n) for n in e['a']]
# 共演は「日」単位で数える（同日の昼夜公演の二重計上を避ける）。重みは小規模イベントほど大きい。
def w(n): return 1/math.log2(n) if n > 2 else 1.0
days = collections.defaultdict(set)
pair = collections.defaultdict(dict)   # (a,b) -> {date: maxweight}
for e in events:
    n = len(e['a'])
    for a in e['a']: days[a].add(e['d'])
    for a, b in itertools.combinations(sorted(e['a']), 2):
        cur = pair[(a, b)]
        cur[e['d']] = max(cur.get(e['d'], 0), w(n))
for i, a in enumerate(acts):
    a['d'] = len(days[i]); a['e'] = sum(1 for e in events if i in e['a'])
P = []
for (a, b), dd in pair.items():
    c = len(dd); ws = sum(dd.values())
    s = ws / math.sqrt(len(days[a]) * len(days[b]))
    P.append([a, b, c, round(ws, 2), round(s, 3)])
out = dict(updated=datetime.date.today().isoformat(), acts=acts, events=events)
js = json.dumps(out, ensure_ascii=False, separators=(',', ':'))
open(PT('data','kyoen','kyoen.json'), 'w', encoding='utf-8').write(js)
# 引数に出力先を渡すとページ(HTML)も生成する: python3 scripts/kyoen/build.py out.html
if len(sys.argv) > 1:
    t = open(PT('scripts','kyoen','template.html'), encoding='utf-8').read()
    page = t.replace('__DATA__', js.replace('</', '<\\/'))
    # 単体ページにする（doctypeとhead、マップ本体へ戻るリンクを足す）
    page = page.replace('<h1>関西アイドル共演マップ</h1>', '<a class="back" href="./">← 関西アイドルマップ</a>\n  <h1>関西アイドル共演マップ</h1>', 1)
    page = page.replace('<meta name="claude:viewport-fit-sides" content="cover">\n', '', 1)
    page = page.replace('</style>', '.back{align-self:flex-start;font-size:13px;font-weight:700;color:var(--accent);text-decoration:none}\n[hidden]{display:none!important}\n</style>', 1)
    page = '<!doctype html>\n<html lang="ja">\n<head>\n<meta charset="utf-8">\n<meta name="viewport" content="width=device-width,initial-scale=1">\n' + page + '\n'
    page = page.replace('</script>', '</script>\n</body>\n</html>', 1) if False else page
    open(sys.argv[1], 'w', encoding='utf-8').write(page)
r = [a for a in acts if a['r']]; u = [a for a in acts if not a['r']]
print('events', len(events), 'acts', len(acts), 'registered matched', len(r), '/', len(reg))
print('データなしの登録グループ:', [n for n in reg if n not in ids])
print('未登録で3日以上出演:', sorted([(a['d'], a['n']) for a in u if a['d'] >= 3], reverse=True))
