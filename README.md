# SatelliteDataPlot (SABER, NetCDF)
A basic script to read data from NetCDF-4 files and generate a contour plot. It builds a 2-D histogram of temperature first, then plots its contour.

NetCDF files stores sensor measurement data collected at various SABER satellites. SABER Satellite Data is freely available at http://saber.gats-inc.com/browse_data.php .
This program reads a bunch of NetCDF files in the current directory and generates a contour plot of the temperature, varying latitude, longitude or altitude in the x and y axes.
![An example contour plot](https://github.com/eyeabhi/SatelliteDataPlot/blob/master/Figure-contour.png)
