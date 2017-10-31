g++ test.cpp -std=c++11 -o out `pkg-config opencv --cflags --libs` `pkg-config freenect2 --cflags --libs`
