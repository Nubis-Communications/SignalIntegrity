PySIConvolve.so : PySIConvolve.o
	i686-w64-mingw32-gcc -shared -Wl,-soname,PySIConvolve.so -o PySIConvolve.so PySIConvolve.o -lstdc++

PySIConvolve.o : PySIConvolve.cpp
	i686-w64-mingw32-gcc PySIConvolve.cpp -o PySIConvolve.o -c

clean :
	rm PySIConvolve.o PySIConvolve.so