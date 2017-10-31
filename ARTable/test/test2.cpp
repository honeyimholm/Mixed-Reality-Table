#include <iostream>
#include <stdio.h>
#include <iomanip>
#include <time.h>
#include <signal.h>
#include <opencv2/opencv.hpp>

#include <libfreenect2/libfreenect2.hpp>
#include <libfreenect2/frame_listener_impl.h>
#include <libfreenect2/registration.h>
#include <libfreenect2/packet_pipeline.h>
#include <libfreenect2/logger.h>
//! [headers]

using namespace std;
using namespace cv;

bool protonect_shutdown = false; // Whether the running application should shut down.
Mat orig_rgb, orig_depth;

void sigint_handler(int s)
{ 
  protonect_shutdown = true;
}

void computeContoursRGB(Mat gray) {
    Mat gray_blur, thresh;

    GaussianBlur(gray-orig_rgb, gray_blur, Size(45,45), 0, 0);
    threshold(gray_blur, thresh, 0, 255, CV_THRESH_BINARY+CV_THRESH_OTSU);

    std::vector<std::vector<cv::Point> > contours;
    cv::Mat contourOutput = thresh.clone();
    cv::findContours(contourOutput, contours, CV_RETR_LIST, CV_CHAIN_APPROX_NONE);
    cv::Mat contourImage(thresh.size(), CV_8UC3, cv::Scalar(0,0,0));
    cv::Scalar colors[3];
    colors[0] = cv::Scalar(255, 0, 0);
    colors[1] = cv::Scalar(0, 255, 0);
    colors[2] = cv::Scalar(0, 0, 255);

    for (size_t i = 0; i < contours.size(); i++) {
        cv::drawContours(contourImage, contours, i, colors[i % 3]);
    }

    //cv::imshow("rgb", rgbmat);
    cv::imshow("gray", gray);
    cv::imshow("orig_rgb", orig_rgb);
    //cv::imshow("gray_blur", gray_blur);
    //cv::imshow("thresh", thresh);
    cv::imshow("contours", contourImage);
    //printing convtours to the stdout
    vector< vector<cv::Point> >::iterator row;
    vector<cv::Point>::iterator col;

    for(row = contours.begin(); row!=contours.end(); row++) {
        cout<<"contour:";
        for(col = row->begin() ;col!=row->end(); col++) {
            std::cout<<"x: ";
            std::cout<<col->x;
        }
    }
}

void computeContoursDepth(Mat depthmat) {
    Mat depth_blur, depth_thresh, depth_contours;

    vector<vector<Point>> contours;
    vector<vector<Point>> contours_poly(contours.size());
    vector<Rect> boundRect(contours.size());

    GaussianBlur((orig_depth - depthmat) / 4096.0f, depth_blur, Size(25, 25), 0, 0);
    threshold(depth_blur, depth_thresh, 0.05, 255, CV_THRESH_BINARY);

    // Debug depth image
    cv::imshow("threshold", depth_thresh);
    cv::imshow("blur", depth_blur);

    /*
    // Calculate contours
    findContours(depth_thresh, depth_contours, CV_RETR_LIST, CV_CHAIN_APPROX_NONE);
    for(int i = 0; i < contours.size(); i++) {
        approxPolyDP( Mat(contours[i]), contours_poly[i], 3, true );
        boundRect[i] = boundingRect( Mat(contours_poly[i]) );
    }

    // Draw polygonal contour + bonding rects + circles
    Mat drawing = Mat::zeros( depth_thresh.size(), CV_8UC3 );
    Scalar color = Scalar( 255, 0, 0 );
    for( int i = 0; i < contours.size(); i++ ) {
        drawContours( drawing, contours_poly, i, color, 1, 8, vector<Vec4i>(), 0, Point() );
        rectangle( drawing, boundRect[i].tl(), boundRect[i].br(), color, 2, 8, 0 );
    }

    // Show in a window
    imshow( "Contours", drawing );
    */
}

int main()
{
    std::cout << "Streaming from Kinect One sensor!" << std::endl;

    //! [context]
    libfreenect2::Freenect2 freenect2;
    libfreenect2::Freenect2Device *dev = 0;
    libfreenect2::PacketPipeline *pipeline = new libfreenect2::OpenCLPacketPipeline();
    //! [context]

    //! [discovery]
    if(freenect2.enumerateDevices() == 0)
    {
        std::cout << "no device connected!" << std::endl;
        return -1;
    }

    string serial = freenect2.getDefaultDeviceSerialNumber();

    std::cout << "SERIAL: " << serial << std::endl;

    if(pipeline)
    {
        //! [open]
        dev = freenect2.openDevice(serial, pipeline);
        //! [open]
    } else {
        dev = freenect2.openDevice(serial);
    }

    if(dev == 0)
    {
        std::cout << "failure opening device!" << std::endl;
        return -1;
    }

    signal(SIGINT, sigint_handler);
    protonect_shutdown = false;

    //! [listeners]
    libfreenect2::SyncMultiFrameListener listener(libfreenect2::Frame::Color |
                                                  libfreenect2::Frame::Depth |
                                                  libfreenect2::Frame::Ir);
    libfreenect2::FrameMap frames;

    dev->setColorFrameListener(&listener);
    dev->setIrAndDepthFrameListener(&listener);
    //! [listeners]

    //! [start]
    dev->start();

    std::cout << "device serial: " << dev->getSerialNumber() << std::endl;
    std::cout << "device firmware: " << dev->getFirmwareVersion() << std::endl;
    //! [start]

    //! [registration setup]
    libfreenect2::Registration* registration = new libfreenect2::Registration(dev->getIrCameraParams(), dev->getColorCameraParams());
    libfreenect2::Frame undistorted(512, 424, 4), registered(512, 424, 4), depth2rgb(1920, 1080 + 2, 4); // check here (https://github.com/OpenKinect/libfreenect2/issues/337) and here (https://github.com/OpenKinect/libfreenect2/issues/464) why depth2rgb image should be bigger
    //! [registration setup]

    Mat  gray, rgbmat, depthmat;
    bool start = true;

    //! [loop start]
    int iter = 0;
    while(!protonect_shutdown)
    {
        iter++;
        listener.waitForNewFrame(frames);
        libfreenect2::Frame *rgb = frames[libfreenect2::Frame::Color];
        //libfreenect2::Frame *ir = frames[libfreenect2::Frame::Ir];
        libfreenect2::Frame *depth = frames[libfreenect2::Frame::Depth];
        //! [loop start]

        cv::Mat(rgb->height, rgb->width, CV_8UC4, rgb->data).copyTo(rgbmat);
        cv::resize(rgbmat, rgbmat, cv::Size(960,540));
        //cv::Mat(ir->height, ir->width, CV_32FC1, ir->data).copyTo(irmat);
        cv::Mat(depth->height, depth->width, CV_32FC1, depth->data).copyTo(depthmat);
        cvtColor(rgbmat, gray, CV_BGR2GRAY);

        //Set original background/calibration mat
        if (start) {
          start = false;
          orig_rgb = gray.clone();
          orig_depth = depthmat.clone();
        }

        //computeContoursRGB(gray);
        computeContoursDepth(depthmat);

        //! [registration]
        //registration->apply(rgb, depth, &undistorted, &registered, true, &depth2rgb);
        //! [registration]

        /*
        cv::Mat(undistorted.height, undistorted.width, CV_32FC1, undistorted.data).copyTo(depthmatUndistorted);
        cv::Mat(registered.height, registered.width, CV_8UC4, registered.data).copyTo(rgbd);
        cv::Mat(depth2rgb.height, depth2rgb.width, CV_32FC1, depth2rgb.data).copyTo(rgbd2);


        cv::imshow("undistorted", depthmatUndistorted / 4096.0f);
        cv::imshow("registered", rgbd);
        cv::imshow("depth2RGB", rgbd2 / 4096.0f);
        */

        int key = cv::waitKey(1);
        protonect_shutdown = protonect_shutdown || (key > 0 && ((key & 0xFF) == 27)); // shutdown on escape
        
        listener.release(frames);
    }

    dev->stop();
    dev->close();

    delete registration;

    std::cout << "Streaming Ends!" << std::endl;
    return 0;
}