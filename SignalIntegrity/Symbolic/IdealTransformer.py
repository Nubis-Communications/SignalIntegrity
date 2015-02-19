def IdealTransformer(a):
    denom=a+'^2+1'
    one='\\frac{1}{'+denom+'}'
    a2='\\frac{'+a+'^2}{'+denom+'}'
    a1='\\frac{'+a+'}{'+denom+'}'
    na='-\\frac{'+a+'}{'+denom+'}'
    return [[one,a2,a1,na],[a2,one,na,a1],[a1,na,a2,one],[na,a1,one,a2]]
