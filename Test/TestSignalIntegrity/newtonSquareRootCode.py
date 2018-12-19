def newtonSquareRoot(Y):
    if Y<=0.0: raise ValueError('math domain error')
    if Y<=1e-32: return 0.0
    # in practice, exponent is directly extracted from fp number
    E=int(math.ceil(math.log(Y,2.)))
    Eeven=E//2*2==E
    y=Y/pow(2.0,E) # in practice, is the mantissa of the fp number
    seed=[0.72,0.737,0.76,0.78,0.8,0.82,0.84,0.856,0.876,
          0.892,0.91,0.927,0.943,0.961,0.975,0.993]
    # in practice, seed index taken from upper nybble of mantissa
    si=int(math.floor(y*32))-16
    x=seed[si]
    for _ in range(3): x=(x+y/x)/2.0
    x=x*pow(2.0,E//2)*(1.4142135623730951 if not Eeven else 1.0)
    return x
