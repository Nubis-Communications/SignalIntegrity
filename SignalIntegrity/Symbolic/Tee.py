def Tee(P=3):
    D=str(P)
    DiagEle='-\\frac{'+str(-(2-P))+'}{'+D+'}'
    OffDiagEle='\\frac{2}{'+D+'}'
    M=[]
    for r in range(P):
        row=[]
        for c in range(P):
            if r==c:
                ele=DiagEle
            else:
                ele=OffDiagEle
            row.append(ele)
        M.append(row)
    return M

def TeeWithZ2(Z2):
    D='3\\cdot Z0^2+2\\cdot Z0\\cdot '+Z2
    return [['\\frac{-Z0^2}{'+D+'}','\\frac{2\\cdot Z0^2}{'+D+'}','\\frac{2\\cdot Z0^2+2\\cdot Z0\\cdot '+Z2+'}{'+D+'}'],
        ['\\frac{2\\cdot Z0^2}{'+D+'}','\\frac{-Z0^2+2\\cdot Z0\\cdot '+Z2+'}{'+D+'}','\\frac{2\\cdot Z0^2}{'+D+'}'],
        ['\\frac{2\\cdot Z0^2+2\\cdot Z0\\cdot '+Z2+'}{'+D+'}','\\frac{2\\cdot Z0^2}{'+D+'}','\\frac{-Z0^2}{'+D+'}']]

def TeeThreePortZ1Z2Z3(Z1,Z2,Z3):
    D='3\\cdot Z0^2+2\\cdot Z0\\cdot\\left('+Z1+'+'+Z2+'+'+Z3+'\\right)+'+Z1+'\\cdot '+Z2+'+'+Z1+'\\cdot '+Z3+'+'+Z2+'\\cdot '+Z3
    return [['\\frac{'+Z1+'\\cdot '+Z2+'+'+Z1+'\\cdot '+Z3+'+2\\cdot '+Z1+'\\cdot Z0+'+Z2+'\\cdot '+Z3+'-Z0^2}{'+D+'}','\\frac{2\\cdot Z0^2+2\\cdot Z0\\cdot '+Z3+'}{'+D+'}','\\frac{2\\cdot Z0^2+2\\cdot '+Z2+'\\cdot Z0}{'+D+'}'],
            ['\\frac{2\\cdot Z0^2+2\\cdot Z0\\cdot '+Z3+'}{'+D+'}','\\frac{'+Z1+'\\cdot '+Z2+'+'+Z2+'\\cdot '+Z3+'+2\\cdot '+Z2+'\\cdot Z0+'+Z1+'\\cdot '+Z3+'-Z0^2}{'+D+'}','\\frac{2\\cdot Z0^2+2\\cdot '+Z1+'\\cdot Z0}{'+D+'}'],
            ['\\frac{2\\cdot Z0^2+2\\cdot '+Z2+'\\cdot Z0}{'+D+'}','\\frac{2\\cdot Z0^2+2\\cdot '+Z1+'\\cdot Z0}{'+D+'}','\\frac{'+Z1+'\\cdot '+Z2+'+'+Z1+'\\cdot '+Z3+'+'+Z2+'\\cdot '+Z3+'+2\\cdot Z0\\cdot '+Z3+'-Z0^2}{'+D+'}']]

def TeeThreePortSafe(Zt):
    D='3\\cdot \\left('+Zt+'+Z0\\right)'
    return [['\\frac{3\\cdot '+Zt+'-Z0}{'+D+'}','\\frac{2\\cdot Z0}{'+D+'}','\\frac{2\\cdot Z0}{'+D+'}'],
        ['\\frac{2\\cdot Z0}{'+D+'}','\\frac{3\\cdot '+Zt+'-Z0}{'+D+'}','\\frac{2\\cdot Z0}{'+D+'}'],
        ['\\frac{2\\cdot Z0}{'+D+'}','\\frac{2\\cdot Z0}{'+D+'}','\\frac{3\\cdot '+Zt+'-Z0}{'+D+'}']]