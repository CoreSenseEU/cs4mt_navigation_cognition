cmake_minimum_required(VERSION 3.8)
project(cs4mt_navigation_cognition)


find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_lifecycle REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(rclcpp_components REQUIRED)
find_package(behaviortree_cpp_v3 REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)



set(dependencies
  ament_cmake
  rclcpp
  rclcpp_lifecycle
  rclcpp_action
  behaviortree_cpp_v3
  cs4home_core  
  geometry_msgs
  sound_msgs
  tf2
  tf2_ros
  tf2_geometry_msgs 
  std_msgs
  visualization_msgs
)

set(SOURCES
  src/${PROJECT_NAME}/MTNavigationCognitiveModule.cpp
  #src/${PROJECT_NAME}/SoundSupervisionCognitiveModule.cpp
  #src/${PROJECT_NAME}/SoundContextEvaluationCognitiveModule.cpp
  #src/${PROJECT_NAME}/HumanAssistanceCognitiveModule.cpp
  #src/${PROJECT_NAME}/EmergencyCognitiveModule.cpp
  #src/${PROJECT_NAME}/Master.cpp
)

install(DIRECTORY
  config
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
