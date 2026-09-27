def Tee(P=None):
    if P is None: P=3
    return [[(2.-P)/P if r==c else 2./P for c in range(P)] for r in range(P)]
