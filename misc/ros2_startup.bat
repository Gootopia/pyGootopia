@ECHO OFF
ECHO === Executing ROS Setup Batch File (%ROS2_STARTUP%) ===
call c:\dev\ros2_galactic\local_setup.bat
echo === ROS2 (%ROS_DISTRO%), Default WS (%ROS2_DEFAULT_WS%) ===
cd %ROS2_DEFAULT_WS%

