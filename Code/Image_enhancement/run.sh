#!/usr/bin/env bash
export LD_LIBRARY_PATH=/home/user/opencv/build/dist/lib:$LD_LIBRARY_PATH

if [ $# -ne 2 ]; then
    echo 2 parameters required. Run example: ./run in_folder out_folder
    exit 1
fi

echo Running: ./main $1 $2

./main "$1" "$2"
