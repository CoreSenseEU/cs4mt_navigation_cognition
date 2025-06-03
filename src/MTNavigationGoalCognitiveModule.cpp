////////////////////////////////////////////////////////////////////

// Copyright 2025 IMR Robotics & Automation Group
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//See the License for the specific language governing permissions and
// limitations under the License.
////////////////////////////////////////////////////////////////////

#include "cs4home_core/CognitiveModule.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_lifecycle/lifecycle_node.hpp"

class MTNavigationGoalCognitiveModule : public cs4home_core::CognitiveModule {
public:
  explicit MTNavigationGoalCognitiveModule(
      const rclcpp::NodeOptions &options = rclcpp::NodeOptions())
      : cs4home_core::CognitiveModule("nav_goal_cognitive_module", options) {
    RCLCPP_INFO(this->get_logger(), "Navigation Cognitive module for MT - initialized");
  }
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  
  /* 
  Fun stuff from Claude for visualization, ocmmeint it for now
  */
  RCLCPP_INFO(rclcpp::get_logger("main"), 
            "🚀 Starting MT Navigation Goal Cognitive Module (CS4Home)");
  
  
  auto node = std::make_shared<MTNavigationGoalCognitiveModule>();

  
 
  RCLCPP_INFO(rclcpp::get_logger("main"), 
             "🧠 Navigation Goal Cognitive Module created, spinning...");
  
  rclcpp::spin(node->get_node_base_interface());

   
   RCLCPP_INFO(rclcpp::get_logger("main"), 
               "🛑 Navigation Goal Cognitive Module shutdown");
  
  
  rclcpp::shutdown();

  return 0;
}
