def ShuntZ(P,Z):
    if P==2:
        return ShuntZTwoPort(Z)
    elif P==3:
        return ShuntZThreePort(Z)
    elif P==4:
        return ShuntZFourPort(Z)

def ShuntZFourPort(Z):
    D='2\\cdot \\left('+Z+'+Z0\\right)'
    return [['\\frac{-Z0}{'+D+'}','\\frac{Z0}{'+D+'}','\\frac{2\\cdot '+Z+'+Z0}{'+D+'}','\\frac{Z0}{'+D+'}'],
            ['\\frac{Z0}{'+D+'}','\\frac{-Z0}{'+D+'}','\\frac{Z0}{'+D+'}','\\frac{2\\cdot '+Z+'+Z0}{'+D+'}'],
            ['\\frac{2\\cdot '+Z+'+Z0}{'+D+'}','\\frac{Z0}{'+D+'}','\\frac{-Z0}{'+D+'}','\\frac{Z0}{'+D+'}'],
            ['\\frac{Z0}{'+D+'}','\\frac{2\\cdot '+Z+'+Z0}{'+D+'}','\\frac{Z0}{'+D+'}','\\frac{-Z0}{'+D+'}']]

def ShuntZThreePort(Z):
    D='2\\cdot '+Z+'+3\\cdot Z0'
    return [['\\frac{-Z0}{'+D+'}','\\frac{2\\cdot '+Z+'+2\\cdot Z0}{'+D+'}','\\frac{2\\cdot Z0}{'+D+'}'],
            ['\\frac{2\\cdot '+Z+'+2\\cdot Z0}{'+D+'}','\\frac{-Z0}{'+D+'}','\\frac{2\\cdot Z0}{'+D+'}'],
            ['\\frac{2\\cdot Z0}{'+D+'}','\\frac{2\\cdot Z0}{'+D+'}','\\frac{2\\cdot '+Z+'-Z0}{'+D+'}']]

def ShuntZTwoPort(Z):
    D='2\\cdot \\left('+Z+'+Z0\\right)'
    return [['\\frac{-Z0}{'+D+'}','\\frac{Z0}{'+D+'}','\\frac{2\\cdot '+Z+'+Z0}{'+D+'}','\\frac{Z0}{'+D+'}'],
            ['\\frac{Z0}{'+D+'}','\\frac{-Z0}{'+D+'}','\\frac{Z0}{'+D+'}','\\frac{2\\cdot '+Z+'+Z0}{'+D+'}'],
            ['\\frac{2\\cdot '+Z+'+Z0}{'+D+'}','\\frac{Z0}{'+D+'}','\\frac{-Z0}{'+D+'}','\\frac{Z0}{'+D+'}'],
            ['\\frac{Z0}{'+D+'}','\\frac{2\\cdot '+Z+'+Z0}{'+D+'}','\\frac{Z0}{'+D+'}','\\frac{-Z0}{'+D+'}']]
