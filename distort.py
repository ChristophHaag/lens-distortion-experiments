#!/usr/bin/env python3
import PIL
import math
from PIL import Image, ImageDraw

imagefn = "maxresdefault.jpg"
aImage: Image.Image = Image.open(imagefn)

newImage: Image.Image = Image.new('RGB', (aImage.width, aImage.height))

#for i in range (1000):
#    newImage.putpixel((i,i), (255,50,50))

distortion_k = 1.318397, -1.490242, 0.663824, 0.508021
aberration_k = 1.00010147892, 1.000, 1.00019614479

width, height = aImage.width, aImage.height
centercol, centerrow = width // 2, height // 2

print(aImage.height, aImage.width)

pixels = list(aImage.getdata())
pixels = [pixels[i * aImage.width:(i + 1) * aImage.width] for i in range(aImage.height)]

print("Got pixels")

draw: ImageDraw.ImageDraw = ImageDraw.Draw(newImage)

for row in range(height):
    for col in range(width):
        #print(row,col)
        index = col, row
        pixel = pixels[row][col]
        #newImage.putpixel((index), (pixel[0], 0,0))

        # distance of this pixel from center, the norm
        realxdist = col - centercol
        realydist = row - centerrow

        # normalized = divide by max value which we know to be half the image
        xdist = realxdist / centercol
        ydist = realydist / centerrow
        radius = math.sqrt(xdist * xdist + ydist * ydist)

        # still normalized
        new_distances = (
            xdist *
                 (distortion_k[3] +
                 distortion_k[2] * radius +
                 distortion_k[1] * radius * radius +
                 distortion_k[0] * radius * radius * radius
                 ),
            ydist *
                (distortion_k[3] +
                 distortion_k[2] * radius +
                 distortion_k[1] * radius * radius +
                 distortion_k[0] * radius * radius * radius
                 )
        )

        new_pixel_r = (
            int(centercol + aberration_k[0] + new_distances[0] * centerrow),
            int(centerrow + aberration_k[0] + new_distances[1] * centerrow)
        )
        new_pixel_g = (
            int(centercol + aberration_k[1] + new_distances[0] * centerrow),
            int(centerrow + aberration_k[1] + new_distances[1] * centerrow)
        )
        new_pixel_b = (
            int(centercol + aberration_k[2] + new_distances[0] * centerrow),
            int(centerrow + aberration_k[2] + new_distances[1] * centerrow)
        )

        #print(index, xdist, ydist, radius, new_pixel)

        newIndex_r = (new_pixel_r[0], new_pixel_r[1])
        newIndex_g = (new_pixel_g[0], new_pixel_g[1])
        newIndex_b = (new_pixel_b[0], new_pixel_b[1])

        r = pixel[0], 0, 0
        g = 0, pixel[1], 0
        b = 0, 0, pixel[2]

        draw.point(newIndex_r, fill=r)
        #draw.point(newIndex_g, fill=g)
        #draw.point(newIndex_b, fill=b)

Image._show(newImage)