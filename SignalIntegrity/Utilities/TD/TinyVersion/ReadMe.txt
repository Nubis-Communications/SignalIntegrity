usage: TD [-h] [-ln LANE_NUMBER] [-of OUTPUT_FILE] [-debug] [-p] [-v] [-fe END_FREQUENCY] [-n FREQUENCY_POINTS]
          [filename]

Thunder IC measurement calculator

                        Calculates a calibrated thunder IC measurement

The single-ended s-parameter file is read in and converted to the differential mode.  Then a calibrated version is calculated according to the lane number (-ln) specified using
the end frequency (-fe) and number of points (-n) specified.

Note, the port ordering the input single-ended s-parameter file is ip,in,op,on, where i means input, o means output, p means positive, and n means negative.


positional arguments:
  filename              s-parameter file name

options:
  -h, --help            show this help message and exit
  -ln LANE_NUMBER, --lane_number LANE_NUMBER
                        (required) lane number
  -of OUTPUT_FILE, --output_file OUTPUT_FILE
                        (optional) output file
                        no matter how this file is specified, it will have .s2p as an extension
  -debug, --debug       shows debug information and plots as the computation proceeds
  -p, --profile         profiles the software
  -v, --verbose         prints information as calculation proceeds.
                        this should not be set if you are relying on stdout for the return value.
  -fe END_FREQUENCY, --end_frequency END_FREQUENCY
                        (optional) end frequency to resample to.
  -n FREQUENCY_POINTS, --frequency_points FREQUENCY_POINTS
                        (optional) number of frequency points to resample to.
