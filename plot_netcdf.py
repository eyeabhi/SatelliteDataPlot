# This is a script to read satellite data from NetCDF-4 file
# and generate 'contour plots'. It plots contour of
# temperature with 'earth-altitude' on the Y-axis and
# latitude or longitude on the X-axis
# This program is interesting because it generates 2-D histogram

from netCDF4 import Dataset
from random import randrange
import numpy as np
import numpy.ma as ma
import matplotlib.pyplot as plt
import os, sys

# A global variable for convenience
figcount = randrange(999)

# This function reads NetCDF data file and return 4 arrays in a tuple:
# (latitude, longitude, altitude, temperature)
def readNetCDF(filename):
    # Open and read NetCDF file
    data = Dataset(filename, 'r')
    print("---- Reading file: '"+ filename + "'")
    print(data.variables.keys())
    print(data.dimensions)

    # Extract each variable as a MaskedArray
    event = data.variables['event']
    tplongitude = data.variables['tplongitude']
    tplongitude_top = data.variables['tplongitude_top']
    tpaltitude = data.variables['tpaltitude']
    tpaltitude_top = data.variables['tpaltitude_top']
    tplatitude = data.variables['tplatitude']
    tplatitude_top = data.variables['tplatitude_top']
    ktemp = data.variables['ktemp']

    # Copy the entire array to a new variable (MaskedArray)
    #longi = ma.concatenate([tplongitude[:], tplongitude_top[:]])
    longi = tplongitude[:]
    #alti = ma.concatenate([tpaltitude[:], tpaltitude_top[:]])
    alti = tpaltitude[:]
    #lati = ma.concatenate([tplatitude[:], tplatitude_top[:]])
    lati = tplatitude[:]
    #temp = ma.concatenate([ktemp[:], ktemp[:]])
    temp = ktemp[:]

    # To get a sense of where on earth we are investigating
    print("Average latitude: ", np.average(lati))
    print("Average longitude: ", np.average(longi))

    return (lati, longi, alti, temp);


# Directory listing routine, looks for "*.nc" files
def listAllNetCDFInDir(dirname):
    files = os.listdir(dirname)
    datafiles = []
    for name in files :
        if(name.endswith('.nc')):
            datafiles.append(dirname + os.path.sep + name)
            #print(dirname + os.path.sep + name)
    return datafiles;


# Creates a 2-D histogram and plots its contour
# X, Y are the x and y-axis values, simple 1-D array
# Z is another 1-D array. Each point in Z is a function
# of the corresponding points in X and Y
def plotHistogramContour(X, Y, Z, xlabel="",ylabel=""):
    # Number of bins in each axis in the histogram
    bins = 40

    # Range of x and y-axis, respectively
    r = [[np.min(X), np.max(X)], [np.min(Y), np.max(Y)]]
    print('Plotting contour... valid data-points: ', len(Z))
    print('[X-range, Y-range] : ', r)

    # Weights are temperatures. H is the sum of all temperature at point (X, Y)
    H, xedges, yedges = np.histogram2d(X, Y, bins=(bins, bins*5), range=r, weights=Z)
    # N is the number of data-points in the bins at position (X, Y)
    N, xedges, yedges = np.histogram2d(X, Y, bins=(bins, bins*5), range=r, weights=None)
    # Some sanity check and finally taking the average of temperatures
    H = ma.masked_less(H, 100)
    S = ma.divide(H, N, where=N>0)      # S is average temperature as each (X,Y)
    S = ma.masked_greater(S, 300)
    #print('H: ', H)
    #print('N: ', N)
    #print('S: ', S)
    #print("Shape of S: ", np.shape(S), " max: ", np.max(S), " min: ", np.min(S))

    # We had 'buckets' in the histogram for x and y-axis,
    # but we need a 'single value' for each bucket. We take their midpoint.
    ## Using list comprehension :)
    xpoints = [(xedges[i]+xedges[i+1])/2.0 for i in range(len(xedges)-1)]
    ypoints = [(yedges[i]+yedges[i+1])/2.0 for i in range(len(yedges)-1)]

    # Standard for plotting contour, create a meshgrid
    (P,Q) = np.meshgrid(xpoints, ypoints)
    plt.figure(figsize=(9,9))
    # The contour lines at the following temperature will be labeled
    V = (140, 180, 200, 220, 240, 260, 280)
    # Plot a line contour
    contours = plt.contour(P, Q, S.T, V, colors='0.20', corner_mask=True)
    # We use transpose of S as S.T because that's what histogram2d() returns
    # Plot a filled contour
    plt.contourf(P, Q, S.T, 128, cmap=plt.cm.jet)
    plt.clabel(contours, inline=True, fontsize=8)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title("Temperature Contour")
    plt.autoscale()
    plt.colorbar()
    print('Done plotting.')

    # Save the contour plot as a high resolution EPS file
    global figcount
    if(figcount != -1):
        savefile = 'contour-%d.eps' %(figcount)
        plt.savefig(savefile, format='eps')
        figcount = figcount + 1
        print("File '%s' saved in the current working directory." %(savefile))


# Main program starts here

datadirectory = '.'  # default data directory is current working directory
# Process command line input for data-source directory
if(len(sys.argv) == 2):
    datadirectory = sys.argv[1]

# Figure file number-if you want to save contour plot as a EPS file
# -1 indicates file will not be saved
figcount = -1

# Search for NetCDF files (*.nc) in the data source
datafilenames = listAllNetCDFInDir(datadirectory)
latilist = []
longilist = []
altilist = []
templist = []

# Read data from each file, we only need 4 variables
# Each variable is reshaped as a simple 1-D array
for file in datafilenames:
    (lati, longi, alti, temp) = readNetCDF(file)
    latilist.append(ma.masked_array.reshape(lati, -1))
    longilist.append(ma.masked_array.reshape(longi, -1))
    altilist.append(ma.masked_array.reshape(alti, -1))
    templist.append(ma.masked_array.reshape(temp, -1))

# All the stored 1-D arrays from each file are concatenated
# For each variable, we have one very long 1-D array
latitudes = ma.concatenate(latilist)
longitudes = ma.concatenate(longilist)
altitudes = ma.concatenate(altilist)
temperatures = ma.concatenate(templist)
print('Total data-points: ', len(temperatures),
      '\tTemp-max: ', np.max(temperatures), '  Temp-min: ', np.min(temperatures))

# We plot 3 arrays. We only count data-points which are valid in all 3 of them
# We get the array-mask and 'OR' them to find common masked values
# And we explicitly mask it in all three arrays (four actually)
commonmask = ma.getmask(latitudes) | ma.getmask(longitudes) | ma.getmask(temperatures) | ma.getmask(altitudes)
latitudes[commonmask] = ma.masked
altitudes[commonmask] = ma.masked
longitudes[commonmask] = ma.masked
temperatures[commonmask] = ma.masked

# Get rid of the invalid masked values. The array is compressed with only valid entries.
latitudes = ma.compressed(latitudes)
altitudes = ma.compressed(altitudes)
longitudes = ma.compressed(longitudes)
temperatures = ma.compressed(temperatures)

# Plot a contour of the 2-D histogram of given data
plotHistogramContour(latitudes, altitudes, temperatures, "Latitude", "Altitude")
plotHistogramContour(longitudes, altitudes, temperatures, "Longitude", "Altitude")
plt.show()
