# Human-Centered Robotics Send-a-bot 2022

Welcome to the Send-a-bot repository! For our Year 4 MEng Electrical and Electronics Engineering HCR coursework at Imperial College London, we have developed a robot system that delivers to people via computer vision, speech interaction and navigation.

## Requirements

- Linux machine (20.04)
- [ROS noetic](http://wiki.ros.org/noetic)
- [Pioneer3-AT](https://www.generationrobots.com/media/Pioneer3AT-P3AT-RevA-datasheet.pdf)
- [Intel® RealSense™ LiDAR Camera L515](https://www.intelrealsense.com/lidar-camera-l515/)
- [OAK—D Camera](https://store.opencv.ai/products/oak-d)
- [Snowball Ice Blue Microphones](https://www.bluemic.com/en-gb/products/snowball/)

## Assembly

The send-a-bot is assembled as following and is controlled via a laptop

![Alt Text](https://github.com/ic1618/Delivery-robot/blob/main/doc/thumbnail_Image.jpg)

## Install

Copy the project on the catkin workspace

> Install wiki page works well: http://www.ros.org/wiki/melodic/Installation/Ubuntu
> Select the -desktop-full package.
https://docs.google.com/document/d/1-HmQuTe955WDy5t9Q70rw00o4WJjFePuAhqxbgarA1Q/edit

### Workspace Setup:

> Check the ROS website for installing and setting up the workspace
```
$ cd catkin_ws
$ cd src
$ git clone
```

Install depenancies

``` 
$ rosdep update
$ cd ..
$ rosdep update rosdep install --rosdistro noetic --ignore-src --from-paths src
$ catkin_make
```

## Repository structure
This repository involves many submodules since local changes are made in the original source code. The main dev place is within [ros-pioneer3at] and [rosaria_client]

For your interest, I will briefly outline the purpose of each package:
- [depthai-python] dependencies for OAK-D camera
- [depthimage_to_laserscan] and [pointcloud_to_laserscan] ros packages used to convert l515 camera PointClouds into LaserScans, depthimage_to_laser scan is more efficient, but less accurate
- [ira_laser_tools] ros package used to merge LaserScans generated by the left and right l515 cameras
- [modelplace-api] and [oak-model-samples] APIs and trained neuron network blobs for the OAK-D camera
- [robot_localization] and [robot_pose_ekf] packages used to perform kalman filtering on the odometry published from the wheel encoder and the vision odometry published from the RGBD vo node
- [rosaria] driver for P3-AT, you should comment out the tf odom->baselink if you don't want to use wheel odometry, which is not very accurate
- [rosaria_client] client and server, main entrance scripts to interact with send-a-bot for functions such as social navigation and object delivery
- [rtabmap_ros] ros package used to generate vision odometry from the two l515 cameras and perform vision-Lidar SLAM, this SLAM technique is not ideal for hallway environments due to repetitive patterns and lack of visual features 
- [slam_gmapping] ros package used to perform 2D Lidar SLAM

## Computer vision

To start the computer vision node, connect to the OAK-D camera and run:
```
$ roslaunch pioneer3at cv.launch
```
This node runs a mobilenet for object detection, cropping rois, aligning depth frames, generating coordinates and publishing the processed message over the topic '/OAKD/CloestPerson3D', which is the closest person's spatial coordinates in the OAK-D camera frame

## Speech recognition

To start the speech node, connect to an external microphone and run:
```
$ rosrun rosaria_client speech_processing.py
```

## Odometry

P3-AT uses wheel encoders to publish odometry informaiton, however, it is not very accurate and often drifts. To improve performance, we can use the l515 cameras to generate RGBD visual odometry and fuse it with the wheel odometry via a kalman filter. This improves the robustness of the odometry and helps localization, but occupies many computational resources if a GPU is not used

```
$ roslaunch pioneer3at vo.launch
$ roslaunch pioneer3at od_fusion.launch
```

## SLAM

To start the mapping node, we have to first start the two l515 cameras. We use camera manager nodelets to improve latency performance
```
$ roslaunch pioneer3at l515s_nodelet.launch
```

Both Lidar-SLAM and V-SLAM are configured, using [gmapping](http://wiki.ros.org/gmapping) and [rtab-map](http://introlab.github.io/rtabmap/)

In order to perform Lidar-SLAM with the two l515 cameras, we need to transfer either the depth images or the cloud points into laser scans and merge them into a single one, using depth images are more efficient:
```
$ roslaunch pioneer3at lidar_scan.launch
$ roslaunch pioneer3at gmapping_merge.launch
```

An example map build from a narrow hallway is shown as below: 
![Alt Text](https://github.com/ic1618/Delivery-robot/blob/main/doc/8.png)

To perform V-SLAM mixed with Lidar scans, sync the cameras to generate RGBD images and launch the rtabmap node
```
$ roslaunch pioneer3at lidar_scan_depth.launch
$ roslaunch pioneer3at l515s_sync.launch
$ roslaunch pioneer3at map.launch

```

An example map build from a extended narrow hallway is shown as below, there appears to be many noise, and the path is curved due to odometry drifts. In addition, due to inexact camera calibration / transform the is built twice by the two camera seperately. Multi Lidar calibration is recommended in beforehand

![Alt Text](https://github.com/ic1618/Delivery-robot/blob/main/doc/12.png)

## Navigation

To perform navigation, launch [amcl](http://wiki.ros.org/amcl) with an offline or online map for localization, and start the move_base node for path planning

```
$ roslaunch pioneer3at amcl.launch
$ roslaunch pioneer3at move_base.launch
$ rosrun rviz rviz -d $(find pioneer3at)/config/p4.rviz
```

We should see something like this:

![Alt Text](https://github.com/ic1618/Delivery-robot/blob/main/doc/2.png)

Note that due to minimum range of the l515 cameras, objects which are closer than 25cm may not get detected, it is recommendated to use P3-AT's sonar for the purposes of local path planning. The sonar is enabled if the topic is subscribed:

![Alt Text](https://github.com/ic1618/Delivery-robot/blob/main/doc/4.png)

## Demostration

To launch a demostration for social navigation and person approaching, run:

```
$ roslaunch pioneer3at send_a_bot_no_kf.launch
$ roslaunch rosaria_client main.py
```

Or if you have a powerful GPU for visual odometry and wants to apply sensor fusion, run instead:

```
$ roslaunch pioneer3at send_a_bot.launch
$ roslaunch rosaria_client main.py
```

### Obstacle avoidance:

![Alt Text](https://github.com/ic1618/Delivery-robot/blob/main/doc/20.gif)



### Person approaching:

![Alt Text](https://github.com/ic1618/Delivery-robot/blob/main/doc/21.gif)


## Future work:

- Improve odometry by including an extra [IMU](https://en.wikipedia.org/wiki/Inertial_measurement_unit) for sensor fusing
- On-board processor such as [Jetson Xavier NX](https://developer.nvidia.com/embedded/jetson-xavier-nx-devkit) to split computaion
- [Hokuyu sensor](https://www.hokuyo-aut.jp/) to replace l515 as the sources for lasers and environment perception
- Add a lightweight robot arm such as [myCobot](https://github.com/elephantrobotics/pymycobot) for grasping and handling 
- Remote control through ssh with a tablet for more convinient testing and better user interaction  



