#include <unistd.h>
#include <stdio.h>
#include <stdarg.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <dirent.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <dirent.h>
#include <string.h>
#include <opencv2/opencv.hpp>
//#include <opencv/cv.h>
//#include <opencv/highgui.h>
//#include <opencv/highgui.h>
#include <list>
#include <vector>
#include <map>
#include "matio.h"
#include <stdarg.h>
#include <memory>

using namespace std;
using namespace cv;



// Run example: ./main <image_path>

int main(int argc, char **argv) {

    const char* image_path = argv[1];

    Ptr<CLAHE> clahe = createCLAHE(2.0);
    Mat rawImage = imread(string() + image_path, CV_LOAD_IMAGE_COLOR);
    if (rawImage.rows > 0 && rawImage.cols > 0) {
        Mat image = rawImage.clone();
        vector<Mat> RGB;
        split(image, RGB);
        vector<Mat> newRGB;
        newRGB.push_back(RGB[0]);
        newRGB.push_back(RGB[1]);
        newRGB.push_back(RGB[2]);
        clahe->apply(RGB[0], newRGB[0]);
        clahe->apply(RGB[1], newRGB[1]);
        clahe->apply(RGB[2], newRGB[2]);
        merge(newRGB, image);
        vector<int> compression_params;
        compression_params.push_back(CV_IMWRITE_JPEG_QUALITY);
        compression_params.push_back(100);
        unlink((string() + image_path).c_str());
        imwrite(string() + image_path, image, compression_params);
    }
  
    return EXIT_SUCCESS;
}


