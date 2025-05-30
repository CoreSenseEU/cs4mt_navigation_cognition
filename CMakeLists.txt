cmake_minimum_required(VERSION 3.8)
project(cs4mt_navigation_cognition)

# Find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_lifecycle REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(rclcpp_components REQUIRED)
find_package(behaviortree_cpp_v3 REQUIRED)
find_package(cs4home_core REQUIRED)  # Add this - you're using it
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
# find_package(sound_msgs REQUIRED)  # Uncomment if you have this

set(dependencies
  rclcpp
  rclcpp_lifecycle
  rclcpp_action
  rclcpp_components
  behaviortree_cpp_v3
  cs4home_core  
  geometry_msgs
  # sound_msgs  # Uncomment if you have this
  tf2
  tf2_ros
  tf2_geometry_msgs 
  std_msgs
  visualization_msgs
)

# Create the executable from your source file
add_executable(MTNavigationCognitiveModule 
  src/MTNavigationCognitiveModule.cpp
)

## I am adding setparate executables just so that I can keep trakc later integrate into one shingle 
# Goal Cognition executable
add_executable(goal_cognition_module src/MTNavigationGoalCognitionModule.cpp)
ament_target_dependencies(goal_cognition_module ${dependencies})
install(TARGETS goal_cognition_module
  DESTINATION lib/${PROJECT_NAME}
)

# Dynamic Reconfigure Nav executable
add_executable(dynamic_reconfigure_nav_module src/DynamicReconfigureNavModule.cpp)
ament_target_dependencies(dynamic_reconfigure_nav_module ${dependencies})
install(TARGETS dynamic_reconfigure_nav_module
  DESTINATION lib/${PROJECT_NAME}
)
# Link dependencies to the executable
ament_target_dependencies(MTNavigationCognitiveModule ${dependencies})

# Install directories
install(DIRECTORY
  config
  DESTINATION share/${PROJECT_NAME}
)

install(DIRECTORY
  launch/
  DESTINATION share/${PROJECT_NAME}/launch/
)

# Install the executable (CORRECTED)
install(TARGETS MTNavigationCognitiveModule
  DESTINATION lib/${PROJECT_NAME}
)

# Uncomment and add more executables as needed:
# add_executable(SoundSupervisionCognitiveModule 
#   src/${PROJECT_NAME}/SoundSupervisionCognitiveModule.cpp
# )
# ament_target_dependencies(SoundSupervisionCognitiveModule ${dependencies})
# install(TARGETS SoundSupervisionCognitiveModule
#   DESTINATION lib/${PROJECT_NAME}
# )

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
