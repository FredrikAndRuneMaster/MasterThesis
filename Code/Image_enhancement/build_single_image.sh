#!/usr/bin/env bash
rm -f ./main
g++ -I/home/user/opencv/build/dist/include -L/home/user/opencv/build/dist/lib -std=gnu++11 -O3 -Wno-unused-result single_image.cc -lpthread -lopencv_core -lopencv_highgui -lopencv_imgproc -lopencv_photo -lopencv_imgcodecs -lmatio -o single_image
