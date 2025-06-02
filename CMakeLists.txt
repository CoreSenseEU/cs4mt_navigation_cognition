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





## First add master similar to sound project- but in there they just had a file called master.cpp.
## TODO: Clarify if this is the right approach
# Master executable, see
add_executable(MTNavigationCognitiveMaster
  src/MTNavigationCognitiveMaster.cpp
)
ament_target_dependencies(MTNavigationCognitiveMaster ${dependencies})
#ament_target_dependencies(mt_navigation_cognitive_master ${dependencies})
# Create the executable from your source file
## Follow the same naming convention as the params.yaml in the modules -> Discuss and ask if this is unified way
add_executable(MTNavigationCognitiveModule 
  src/MTNavigationCognitiveModule.cpp
)
ament_target_dependencies(MTNavigationCognitiveModule ${dependencies})
# Uncomment and add more executables as needed:
# add_executable(SoundSupervisionCognitiveModule 
#   src/${PROJECT_NAME}/SoundSupervisionCognitiveModule.cpp
# )
# Goal Cognition executable
add_executable(nav_goal_cognition
  src/MTNavigationGoalCognitiveModule.cpp
)
ament_target_dependencies(nav_goal_cognition ${dependencies})

# Dynamic Reconfigure Nav executable  
add_executable(dynamic_reconfigure_nav
  src/MTDynamicReconfigureNavModule.cpp
)
ament_target_dependencies(dynamic_reconfigure_nav ${dependencies})

## I am adding setparate executables just so that I can keep trakc later integrate into one shingle 
# Goal Cognition executable
# add_executable(nav_goal_cognition_module src/MTNavigationGoalCognitionModule.cpp)
# ament_target_dependencies(nav_goal_cognition_module ${dependencies})
# install(TARGETS nav_goal_cognition_module
#   DESTINATION lib/${PROJECT_NAME}
# )

# # Dynamic Reconfigure Nav executable
# add_executable(dynamic_reconfigure_nav_module src/DynamicReconfigureNavModule.cpp)
# ament_target_dependencies(dynamic_reconfigure_nav_module ${dependencies})
# install(TARGETS dynamic_reconfigure_nav_module
#   DESTINATION lib/${PROJECT_NAME}
# )


# Install directories
install(DIRECTORY
  config
  DESTINATION share/${PROJECT_NAME}
)

install(DIRECTORY
  launch/
  DESTINATION share/${PROJECT_NAME}/launch/
)

# Install the executable
install(TARGETS MTNavigationCognitiveModule
  nav_goal_cognition
  MTNavigationCognitiveMaster
  dynamic_reconfigure_nav
  DESTINATION lib/${PROJECT_NAME}
)



if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
