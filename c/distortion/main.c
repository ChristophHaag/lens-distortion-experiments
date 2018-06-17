#include <stdio.h>
#include <stdbool.h>

#define STB_IMAGE_IMPLEMENTATION
#include <stb_image.h>

#define STB_IMAGE_WRITE_IMPLEMENTATION
#include <stb_image_write.h>

float distortion_k[] = {1.318397, -1.490242, 0.663824, 0.508021};
float aberration_k[] = {1.00010147892, 1.000, 1.00019614479};

// r, g, b need to be taken from different origin pixels because of chromatic aberration
typedef struct {
	int r_x;
	int r_y;
	int g_x;
	int g_y;
	int b_x;
	int b_y;
} distorted_pixel;

// x = col, y = row
distorted_pixel get_location_after_dist(int y, int x, int height, int width) {
	int centerx = width / 2;
	int centery = height / 2;
	float xdist_screenspace = x - centerx;
	float ydist_screenspace = y - centery;

	// normalized means [0,1], and since we measure the distance from the center of the image, it maxes out at half the image
	float xdist_normalized = xdist_screenspace / (width/2);
	float ydist_normalized = ydist_screenspace / (height/2);

	float radius_normalized = sqrt(xdist_normalized * xdist_normalized + ydist_normalized * ydist_normalized);

	float distorted_xdist_normalized = xdist_normalized *
		(distortion_k[3] +
		 distortion_k[2] * radius_normalized +
		 distortion_k[1] * radius_normalized * radius_normalized +
		 distortion_k[0] * radius_normalized * radius_normalized * radius_normalized);

	float distorted_ydist_normalized = ydist_normalized *
		(distortion_k[3] +
		 distortion_k[2] * radius_normalized +
		 distortion_k[1] * radius_normalized * radius_normalized +
		 distortion_k[0] * radius_normalized * radius_normalized * radius_normalized);

	distorted_pixel ret;

	ret.r_x = round((width/2) + aberration_k[0] * distorted_xdist_normalized * (width/2));
	ret.r_y = round((height/2) + aberration_k[0] * distorted_ydist_normalized * (height/2));

	ret.g_x = round((width/2) + aberration_k[1] * distorted_xdist_normalized * (width/2));
	ret.g_y = round((height/2) + aberration_k[1] * distorted_ydist_normalized * (height/2));

	ret.b_x = round((width/2) + aberration_k[2] * distorted_xdist_normalized * (width/2));
	ret.b_y = round((height/2) + aberration_k[2] * distorted_ydist_normalized * (height/2));

	return ret;
}

bool outside(int x, int y, int width, int height) {
	return
		x < 0 ||
		x >= width - 1 ||
		y < 0 ||
		y >= height - 1
	;
}

int main(int argc, char **argv) {
	int width, height, bpp;
	// assume we are in lens-distortion-experiments/c/distortion/build
	// file is in lens-distortion-experiments/
	unsigned char* rgb = stbi_load( "../../../maxresdefault.jpg", &width, &height, &bpp, 3 );
	int memsize = width * height * 3 * sizeof(char);
	unsigned char* out = malloc(memsize);
	printf("Loaded image %dx%d\n", width, height);

	for (int row = 0; row < height; row++) {
		for (int col = 0; col < width; col++) {
			//unsigned char* pixelOffset = rgb + (row + height * col) * 3;
			//unsigned char r = pixelOffset[0];
			//unsigned char g = pixelOffset[1];
			//unsigned char b = pixelOffset[2];
			//printf("r c %d %d\n", row, col);

			unsigned char* outpixelOffset = out + (width * row + col) * 3;

			distorted_pixel distorted_pixel_origin = get_location_after_dist(row, col, height, width);
			if (!outside(distorted_pixel_origin.r_x, distorted_pixel_origin.r_y, width, height)) {
				unsigned char* distorted_pixelOffset_r = rgb + (width * distorted_pixel_origin.r_y + distorted_pixel_origin.r_x) * 3;
				outpixelOffset[0] = distorted_pixelOffset_r[0];
			};
			if (!outside(distorted_pixel_origin.g_x, distorted_pixel_origin.g_y, width, height)) {
				unsigned char* distorted_pixelOffset_g = rgb + (width * distorted_pixel_origin.g_y + distorted_pixel_origin.g_x) * 3;
				outpixelOffset[1] = distorted_pixelOffset_g[1];
			};
			if (!outside(distorted_pixel_origin.b_x, distorted_pixel_origin.b_y, width, height)) {
				unsigned char* distorted_pixelOffset_b = rgb + (width * distorted_pixel_origin.b_y + distorted_pixel_origin.b_x) * 3;
				outpixelOffset[2] = distorted_pixelOffset_b[2];
			};
		}
	}

	int success = stbi_write_jpg("result.jpg", width, height, 3, out, 80);
	printf("Write: %d\n", success);

	stbi_image_free( rgb );
	stbi_image_free( out );
    return 0;
}
