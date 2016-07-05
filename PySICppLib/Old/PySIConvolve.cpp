extern "C"
{
	void PySIConvolve(int numValues,float *valueP, int numTaps, float *tapsP, float*resultP)
    {
        int numResults=numValues-numTaps+1;
        for (int k=0; k < numResults; ++k)
        {
            float acc=0.0;
            for (int m=0; m < numTaps; ++m)
                acc=acc+valueP[k+numTaps-1-m]*tapsP[m];
            resultP[k]=acc;
        }
    }
}
