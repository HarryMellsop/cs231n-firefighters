import ee

ee.Authenticate()
ee.Initialize()

image = ee.Image('srtm90_v4')
print(image.getInfo())