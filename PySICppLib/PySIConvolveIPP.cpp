#include "fir.h"
#include "IntelFilters.h"
#include "vector.h"

extern "C" __declspec(dllexport) void PySIConvolve(int numValues,float *valueP, int numTaps, float *tapsP, float*resultP)
{
    int numResults=numValues-numTaps+1;

	static bool fastWay = true;

	if (fastWay)
	{
		Vector<double,double> vTaps(numTaps);
		for (int k=0; k < numTaps; ++k) vTaps[k]=tapsP[k];

		IntelFilter intelFilter
		(
			FIR_FILTER(vTaps),
			IntelFilter::FilterLibraryIPP,
			IntelFilter::FilterCoefficientTypeFloat,
			IntelFilter::FilterNumericTypeFloat,
			IntelFilter::FilterTopologyFIR,
			IntelFilter::FilterDirectTypeDirect
		);

		for (int k=0; k < numTaps-1; ++k) intelFilter.Output(valueP[k]);	// prime the filter

		intelFilter.Output(valueP+numTaps-1,resultP,numResults); // filter it
	}
	else
	{ // slow way
		for (int k=0; k < numResults; ++k)
		{
			float acc=0.0;
			for (int m=0; m < numTaps; ++m)
				acc=acc+valueP[k+numTaps-1-m]*tapsP[m];
			resultP[k]=acc;
		}
	}
}