#!/usr/bin/env python3
import PIL
import math
from PIL import Image, ImageDraw

imagefn = "maxresdefault.jpg"
aImage: Image.Image = Image.open(imagefn)


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

def do_distortion():
    newImage: Image.Image = Image.new('RGB', (aImage.width, aImage.height))
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


def clamp(col, row):
    c = col
    r = row
    if c < 0:
        c = 0
    if c >= width - 1:
        c = width - 1
    if r < 0:
        r = 0
    if r >= height - 1:
        r = height - 1
    return c, r


def create_distortion_maps():
    m_r = {}
    m_g =  {}
    m_b = {}
    for row in range(height):
        for col in range(width):

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

            # to get the actual pixel position we need to
            # 1. get from normalized [0-1] space by multiplying with the max, which is still half the size
            # 2. scale that position with abberation scale for each color
            # 3. add this x and y distance to the original center point
            new_pixel_r = (
                int(centercol + aberration_k[0] * new_distances[0] * centerrow),
                int(centerrow + aberration_k[0] * new_distances[1] * centerrow)
            )
            new_pixel_g = (
                int(centercol + aberration_k[1] * new_distances[0] * centerrow),
                int(centerrow + aberration_k[1] * new_distances[1] * centerrow)
            )
            new_pixel_b = (
                int(centercol + aberration_k[2] * new_distances[0] * centerrow),
                int(centerrow + aberration_k[2] * new_distances[1] * centerrow)
            )

            #print(index, xdist, ydist, radius, new_pixel)

            newIndex_r = (new_pixel_r[0], new_pixel_r[1])
            newIndex_g = (new_pixel_g[0], new_pixel_g[1])
            newIndex_b = (new_pixel_b[0], new_pixel_b[1])

            m_r[clamp(*newIndex_r)] = col, row
            m_g[clamp(*newIndex_g)] = col, row
            m_b[clamp(*newIndex_b)] = col, row

    return m_r, m_g, m_b


def reverse_distort():
    m_r, m_g, m_b = create_distortion_maps()
    newImage: Image.Image = Image.new('RGB', (aImage.width, aImage.height))
    draw: ImageDraw.ImageDraw = ImageDraw.Draw(newImage)
    new_pixels = {}
    for distorted, undistorted in m_r.items():
        pixel = pixels[distorted[1]][distorted[0]]
        if undistorted not in new_pixels:
            new_pixels[undistorted] = [pixel[0],0,0]
        else:
            new_pixels[undistorted][0] = pixel[0]
    for distorted, undistorted in m_g.items():
        pixel = pixels[distorted[1]][distorted[0]]
        if undistorted not in new_pixels:
            new_pixels[undistorted] = [0, pixel[1], 0]
        else:
            new_pixels[undistorted][1] = pixel[1]
    for distorted, undistorted in m_b.items():
        pixel = pixels[distorted[1]][distorted[0]]
        if undistorted not in new_pixels:
            new_pixels[undistorted] = [0, 0, pixel[2]]
        else:
            new_pixels[undistorted][2] = pixel[2]

    for undistorted, rgb in new_pixels.items():
        draw.point((undistorted[0], undistorted[1]), fill=tuple(rgb))
    Image._show(newImage)


reverse_distort()