# Waveform {#sec:Waveform}

A Waveform consists of a sequence of points representing either voltage or current. It is defined by:

- The *horizontal offset*. The horizontal offset is simply the time of the first point in the waveform.

- The number of points in the waveform.

- The sample rate.

- A sequence of points representing voltage or current.

Thus, for a horizontal offset $h$, a number of points $K$, and a sample rate $Fs$ and a sequence of $K$ points, for $k\in0\ldots K-1$, we have the voltage or current value specified as $v\left[k\right]$ and a time $t\left[k\right]$ where:

$$t\left[k\right]=k\cdot\frac{1}{Fs}+h$$

A waveform file is a text file where the first line contains the horizontal offset, in seconds, the second line contains the integer number of points in the waveform, the third line contains the sample rate in samples per second, and the remaining lines contain the waveform values.

