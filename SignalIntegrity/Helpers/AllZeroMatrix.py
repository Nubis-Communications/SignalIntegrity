def AllZeroMatrix(M):
    for r in range(len(M)):
        for c in range(len(M[r])):
            try:
                if complex(M[r][c]) != 0.:
                    return False
            except ValueError:
                return False
    return True