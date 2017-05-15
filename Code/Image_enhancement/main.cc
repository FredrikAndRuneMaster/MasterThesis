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



// Run example: ./main <in_dir> <out_dir>

int main(int argc, char **argv) {

    const char* in_folder = argv[1];
    const char* out_folder = argv[2];


    mkdir(out_folder, 0775);

    //mkdir("out", 0775);
    DIR *dir;
    struct dirent *ent;
    if ((dir = opendir (in_folder)) != NULL) {
        Ptr<CLAHE> clahe = createCLAHE(2.0);
        while ((ent = readdir (dir)) != NULL) {
            if ((!strcmp(ent->d_name, ".")) || (!strcmp(ent->d_name, ".."))) {
                continue;
            }

            Mat rawImage = imread(string() + in_folder + ent->d_name, CV_LOAD_IMAGE_COLOR);
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
                unlink((string() + out_folder + ent->d_name).c_str());
                imwrite(string() + out_folder + ent->d_name, image, compression_params);
            }
        }
    }
    return EXIT_SUCCESS;
}


