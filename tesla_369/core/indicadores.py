def sma(v, p):
    if len(v) < p: return None
    return round(sum(x['close'] for x in v[-p:]) / p, 6)

def bollinger(v, p=20, d=2):
    if len(v) < p: return None, None, None
    c = [x['close'] for x in v[-p:]]; m = sum(c) / p
    dp = (sum((x-m)**2 for x in c) / p) ** 0.5
    return round(m+d*dp, 6), round(m, 6), round(m-d*dp, 6)

def rsi(v, p=9):
    if len(v) < p+1: return None
    g, l = [], []
    for i in range(1, len(v)):
        d = v[i]['close'] - v[i-1]['close']
        g.append(d if d > 0 else 0); l.append(abs(d) if d < 0 else 0)
    if sum(l) == 0: return 100
    return round(100 - (100 / (1 + sum(g) / sum(l))), 2)

def macd(v, r=12, l=26):
    if len(v) < l: return None
    c = [x['close'] for x in v]; er = c[0]; el = c[0]
    for x in c[1:]:
        er = x*(2/(r+1)) + er*(1-2/(r+1))
        el = x*(2/(l+1)) + el*(1-2/(l+1))
    return round(er-el, 8)

def estocastico(v, p=14):
    if len(v) < p: return None
    c = [x['close'] for x in v]
    h = [max(x['open'], x['close']) for x in v]
    l = [min(x['open'], x['close']) for x in v]
    hh, ll = max(h[-p:]), min(l[-p:])
    if hh == ll: return 50
    return round(((c[-1]-ll)/(hh-ll))*100, 2)
