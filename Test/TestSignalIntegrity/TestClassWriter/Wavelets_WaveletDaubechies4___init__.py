class WaveletDaubechies4(Wavelet):
    def __init__(self):
        Wavelet.__init__(self,[h*math.sqrt(2.)/2
            for h in [0.6830127,1.1830127,0.3169873,-0.1830127]])

