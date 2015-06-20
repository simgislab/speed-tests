import gc
import numpy as np
import numpy.ma as ma
from osgeo import gdal
from osgeo.gdalconst import *
import time
import rasterio

f = "2014.05.09.tif"

print "EXEC ReadAsArray VERSION ----------"
#exec, whole, GDAL
t = time.time()
dataset = gdal.Open(f, GA_ReadOnly)
band = dataset.GetRasterBand(1)
exec("array = dataset.ReadAsArray(0, 0, band.XSize, band.YSize)")
print "Reading all (exec), load time = " + str(round(time.time() - t,4))
dataset = None
exec("del array")

gc.collect()

#parameters
cols = band.XSize
rows = band.YSize
slice_width = 200   #i.e. 200*17000=3400000 is number of pixels to read in with each slice
num_slices =  10      #cols/slice_width
nBlockXSize = band.GetBlockSize()[0]    #42542
nBlockYSize = band.GetBlockSize()[1]    #1

#exec, custom block, GDAL
dataset = gdal.Open(f, GA_ReadOnly)
for x in range(num_slices):
    t = time.time()
    dataset_def = " = dataset.ReadAsArray(" + str(x*slice_width) + ", 0, " + str(slice_width) + ", " + str(rows) + ")"
    exec("array" + dataset_def)
    print('- Reading ' + str(x*slice_width) + "-" + str(x*slice_width + slice_width) + ' (exec), ' + "load time = " + str(round(time.time() - t,4)))
    exec("del array")
    
dataset = None
#bails at 5800-6000, i.e. 6000*17000=102000000 is number of pixels read

gc.collect()

print('\n')
print "NOEXEC ReadAsArray VERSION ----------"
#no exec, whole, GDAL
t = time.time()
dataset = gdal.Open(f, GA_ReadOnly)
array = dataset.ReadAsArray(0, 0, cols, rows)
dataset = None
print "Reading all (no exec), load time = " + str(round(time.time() - t,4))

gc.collect()

#no exec, custom block, GDAL
dataset = gdal.Open(f, GA_ReadOnly)
for x in range(num_slices):
    t = time.time()
    array = dataset.ReadAsArray(x*slice_width, 0, slice_width, rows)
    print('- Reading ' + str(x*slice_width) + "-" + str(x*slice_width + slice_width) + ' (no exec), ' + "load time = " + str(round(time.time() - t,4)))
    del array
    
dataset = None

gc.collect()

#no exec, native block, GDAL
dataset = gdal.Open(f, GA_ReadOnly)
t = time.time()
for x in range(rows):
    t1 = time.time()
    array = dataset.ReadAsArray(0, x, nBlockXSize, 1)
    del array
    #print "Reading native block (GDAL), load time = " + str(round(time.time() - t1, 4))
    
print "Reading all blocks (native, GDAL), load time = " + str(round(time.time() - t, 4))
dataset = None

gc.collect()

print('\n')
print "RASTERIO VERSION (no blocks)----------"
#rasterio, whole
t = time.time()
with rasterio.open(f) as src:
    d = src.read()
print "Reading all (rasterio), load time = " + str(round(time.time() - t,4))

gc.collect()

#custom blocks, rasterio
with rasterio.open(f) as src:
    for x in range(num_slices):
        t = time.time()
        array = src.read(1, window=((0, rows), (x*slice_width, x*slice_width + slice_width)))
        t1 = time.time() - t
        print('- Reading ' + str(x*slice_width) + "-" + str(x*slice_width + slice_width) + ' (rasterio), ' + "load time = " + str(round(t1,4)))
        del array

gc.collect()

print('\n')
print "RASTERIO VERSION (blocks)----------"
#native blocks, rasterio
t = time.time()
with rasterio.open(f) as src:
    for ji, window in src.block_windows(1):
        t1 = time.time()
        array = src.read(1, window=window)
        del array
        #print "Reading native block (rasterio), load time = " + str(round(time.time() - t1, 4))
    print "Reading all blocks (native, rasterio), load time = " + str(round(time.time() - t, 4))

gc.collect()
