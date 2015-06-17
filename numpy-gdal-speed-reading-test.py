import gc
import numpy as np
import numpy.ma as ma
from osgeo import gdal
from osgeo.gdalconst import *
import time
import rasterio

f = "2014.05.09.tif"


print "EXEC VERSION ----------"
#the whole thing
t = time.time()
dataset = gdal.Open(f, GA_ReadOnly)
band = dataset.GetRasterBand(1)
exec("array = dataset.ReadAsArray(0, 0, band.XSize, band.YSize)")
print "Reading all (exec), load time = " + str(round(time.time() - t,4))
dataset = None
exec("del array")

gc.collect()
gc.collect()

#now in a cycle
cols = 43000
rows = band.YSize
slice_width = 200   #i.e. 200*17000=3400000 is number of pixels to read in with each slice
num_slices =  10      #cols/slice_width

dataset = gdal.Open(f, GA_ReadOnly)
band = dataset.GetRasterBand(1)
for x in range(num_slices):
    t = time.time()
    dataset_def = " = dataset.ReadAsArray(" + str(x*slice_width) + ", 0, " + str(x*slice_width + slice_width) + ", band.YSize)"
    exec("array" + dataset_def)
    print('- Reading ' + str(x*slice_width) + "-" + str(x*slice_width + slice_width) + ' (exec), ' + "load time = " + str(round(time.time() - t,4)))
    exec("del array")
    
dataset = None
print('\n')
#bails at 5800-6000, i.e. 6000*17000=102000000 is number of pixels read

gc.collect()
gc.collect()



print "ReadAsArray VERSION ----------"
#try reading without exec - whole
t = time.time()
dataset = gdal.Open(f, GA_ReadOnly)
band = dataset.GetRasterBand(1)
array = dataset.ReadAsArray(0, 0, band.XSize, band.YSize)
dataset = None
print "Reading all (no exec), load time = " + str(round(time.time() - t,4))
print('\n')

gc.collect()
gc.collect()

#try reading without exec - pieces
dataset = gdal.Open(f, GA_ReadOnly)
band = dataset.GetRasterBand(1)
for x in range(num_slices):
    t = time.time()
    array = dataset.ReadAsArray(x*slice_width, 0, x*slice_width + slice_width, rows)
    print('- Reading ' + str(x*slice_width) + "-" + str(x*slice_width + slice_width) + ' (no exec), ' + "load time = " + str(round(time.time() - t,4)))
    del array
    
dataset = None
print('\n')

gc.collect()
gc.collect()


print "RASTERIO VERSION ----------"
#try reading with rasterio
t = time.time()
with rasterio.open(f) as src:
    d = src.read()
print "Reading all (rasterio), load time = " + str(round(time.time() - t,4))
print('\n')

gc.collect()
gc.collect()

#try reading without rasterio - pieces
with rasterio.open(f) as src:
    for x in range(num_slices):
        t = time.time()
        array = src.read(1, window=((0, rows), (x*slice_width, x*slice_width + slice_width)))
        print('- Reading ' + str(x*slice_width) + "-" + str(x*slice_width + slice_width) + ' (rasterio), ' + "load time = " + str(round(time.time() - t,4)))
        del array

gc.collect()
gc.collect()
