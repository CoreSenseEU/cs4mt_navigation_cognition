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
  ament_cmake
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



set(SOURCES
  src/${PROJECT_NAME}/MTNavigationGoalCognitiveModule.cpp
  src/${PROJECT_NAME}/MTNavigationCognitiveMaster.cpp
)


## Same structure as SoundExample

# CORE
add_library(nav_goal_cognitive_core SHARED src/MTNavigationGoalCognitiveCore.cpp)
ament_target_dependencies(nav_goal_cognitive_core  ${dependencies} ${test_dependencies})
target_link_libraries(nav_goal_cognitive_core)



# AFFERENT


add_library(nav_goal_cognitive_input SHARED src/MTNavigationGoalCognitiveInput.cpp)
ament_target_dependencies(nav_goal_cognitive_input  ${dependencies} ${test_dependencies})
target_link_libraries(nav_goal_cognitive_input)



# EFFERENT


#add_library(cs4mt_navigation_cognition_output SHARED src/MTNavigationGoalCognitiveOutput.cpp)
#ament_target_dependencies(cs4mt_navigation_cognition_output  ${dependencies} ${test_dependencies})
#target_link_libraries(cs4mt_navigation_cognition_output)



# META



# COUPLING



# Module 

# Goal Cognition module - Executable
add_executable(nav_goal_cognitive_module
  src/MTNavigationGoalCognitiveModule.cpp
)
ament_target_dependencies(nav_goal_cognitive_module ${dependencies})


# MASTER here
add_executable(navigation_cognitive_master
  src/MTNavigationCognitiveMaster.cpp
)
ament_target_dependencies(navigation_cognitive_master ${dependencies})


# Install directories
install(DIRECTORY
  config
  DESTINATION share/${PROJECT_NAME}
)

install(DIRECTORY
  launch/
  DESTINATION share/${PROJECT_NAME}/launch/
)


# Install libraries here
# Install component libraries (CRITICAL - was missing!)
install(TARGETS
  nav_goal_cognitive_core
  nav_goal_cognitive_input
  # nav_goal_cognitive_output
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

# Install the executable
install(TARGETS
  nav_goal_cognitive_module
  navigation_cognitive_master
  #dynamic_reconfigure_nav
  DESTINATION lib/${PROJECT_NAME}
)


if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
