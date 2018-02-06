def TLineFourPort(Zc,gamma,Z0):
    """       +-----------------------+
             / \                       \
      1 ----+-  |     Z    Td           +----- 2
             \ /                       /
           +--+-----------------------+--+
           |                             |
      3 ---+                             +---- 4

    ports 1 and 2 are the input and output
    ports 3 and 4 are the outer conductor"""
    p=(Zc-Z0)/(Zc+Z0)
    a=(1.-3.*p)/(p-3.)
    Y=cmath.exp(-gamma)
    D=2.*(1-Y*Y*a*a)
    S1=(1.-Y*Y*a*a+a*(1.-Y*Y))/D
    S2=(1.-a*a)*Y/D
    S3=((1.-Y*Y*a*a)-a*(1.-Y*Y))/D
    return [[S1,S2,S3,-S2],
            [S2,S1,-S2,S3],
            [S3,-S2,S1,S2],
            [-S2,S3,S2,S1]]