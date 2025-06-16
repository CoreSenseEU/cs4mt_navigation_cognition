cmake_minimum_required(VERSION 3.8)
project(cs4mt_navigation_cognition)

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_lifecycle REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(rclcpp_components REQUIRED)
find_package(behaviortree_cpp_v3 REQUIRED)
find_package(cs4home_core REQUIRED) 
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(lifecycle_msgs REQUIRED)
find_package(rcl_interfaces REQUIRED) 
find_package(nav2_msgs REQUIRED) 

set(dependencies
  rclcpp
  rclcpp_lifecycle
  rcl_interfaces
  rclcpp_action
  rclcpp_components
  behaviortree_cpp_v3
  cs4home_core  
  geometry_msgs
  tf2
  tf2_ros
  tf2_geometry_msgs 
  std_msgs
  visualization_msgs
  lifecycle_msgs
  nav2_msgs
)

## COMPONENT LIBRARIES FOR cs4home_core

# CORE
add_library(nav_goal_cognitive_core SHARED src/MTNavigationGoalCognitiveCore.cpp)
ament_target_dependencies(nav_goal_cognitive_core ${dependencies} ${test_dependencies})
target_link_libraries(nav_goal_cognitive_core)

# AFFERENT
add_library(nav_goal_cognitive_input SHARED src/MTNavigationGoalCognitiveInput.cpp)
ament_target_dependencies(nav_goal_cognitive_input ${dependencies} ${test_dependencies})
target_link_libraries(nav_goal_cognitive_input)

# EFFERENT (when you create it)
add_library(nav_goal_cognitive_output SHARED src/MTNavigationGoalCognitiveOutput.cpp)
ament_target_dependencies(nav_goal_cognitive_output ${dependencies})
target_link_libraries(nav_goal_cognitive_core)

## EXECUTABLES

# Goal Cognition module - Executable
add_executable(nav_goal_cognitive_module
  src/MTNavigationGoalCognitiveModule.cpp
)
ament_target_dependencies(nav_goal_cognitive_module ${dependencies} ${test_dependencies})

# MASTER
add_executable(navigation_cognitive_master
  src/MTNavigationCognitiveMaster.cpp
)
ament_target_dependencies(navigation_cognitive_master ${dependencies} ${test_dependencies})

## INSTALLATION

# Install component libraries
install(TARGETS
  nav_goal_cognitive_core
  nav_goal_cognitive_input
  nav_goal_cognitive_output
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

# Install executables
# Modules and master file are executables
install(TARGETS
  nav_goal_cognitive_module
  navigation_cognitive_master
  DESTINATION lib/${PROJECT_NAME}
)

# Install directories
install(DIRECTORY
  config
  DESTINATION share/${PROJECT_NAME}
)

install(DIRECTORY
  launch/
  DESTINATION share/${PROJECT_NAME}/launch/
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
