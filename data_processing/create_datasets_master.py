# let's define the area to examine

minLong = -118.0
maxLong = -116.0
minLat = 34
maxLat = 36

# how many slices do we want in each direction?
numSlices = 100 # means that each image slice will be around 1.1km in each direction

# use Alex's library of function to create labelled 'y' vector which will be (100x100) x 1 matrix boolean which represents if this
# image was on fire in the subsequent month
y = somefunc()

# pull images off of Google Earth Engine to create an 'X' tensor that will be (100x100) x IMG_HEIGHT x IMG_WIDTH x NUM_CHANNELS