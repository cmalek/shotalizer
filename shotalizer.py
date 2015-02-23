#!/srv/ads/python/ve/shotalizer/bin/python

from PIL import Image

test_image = "test.jpg"
original = Image.open(test_image)
original.show()

width, height = original.size   # Get dimensions
left = width / 4
top = height / 4
right = 3 * (width / 4)
bottom = 3 * (height / 4)

cropped_example = original.crop((left, top, right, bottom))

cropped_example.save('crop.jpg')
