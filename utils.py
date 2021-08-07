def get_top_date(x):
    if isinstance(x, str):
        top = x[-4:] if 'Freehold' not in x else 3000
        if top == 'hold':
            top = 100
        return int(top)


def get_floor(x):
    if '-' in x or 'B' in x:
        return 0
    else:
        l, h = x.split(' to ')
        return (int(l) + int(h)) // 2

def get_year(x):
    return int(x[-4:])