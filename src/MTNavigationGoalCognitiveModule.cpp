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

#include "rclcpp/rclcpp.hpp"
#include "std_msgs/msg/bool.hpp"

class NavGoalCognitionModule : public rclcpp::Node {
private:
    // Subscriber for critical goal flag
    rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr critical_goal_sub_;
    
    // Publisher for goal criticality (for downstream modules)
    rclcpp::Publisher<std_msgs::msg::Bool>::SharedPtr goal_criticality_pub_;

public:
    explicit NavGoalCognitionModule(
        const rclcpp::NodeOptions &options = rclcpp::NodeOptions())
        : rclcpp::Node("nav_goal_cognition", options) { // Pay close attention, the "nav_goal_cognition" name should match
        //with params.yaml in config, be careful and dont fuck up
        
        RCLCPP_INFO(this->get_logger(), "Goal Cognition Module initialized (criticality pass-through)");
        
        // Create subscriber for critical goal flag immediately
        critical_goal_sub_ = this->create_subscription<std_msgs::msg::Bool>(
            "/critical_goal", 10,
            std::bind(&NavGoalCognitionModule::critical_goal_callback, this, std::placeholders::_1));
        
        // Create publisher for goal criticality immediately  
        goal_criticality_pub_ = this->create_publisher<std_msgs::msg::Bool>("/goal_criticality", 10);
        
        RCLCPP_INFO(this->get_logger(), "Navigation Goal Cognition Module activated");
        RCLCPP_INFO(this->get_logger(), "📥 Listening on: /critical_goal");
        RCLCPP_INFO(this->get_logger(), "📤 Publishing to: /goal_criticality");
        RCLCPP_INFO(this->get_logger(), "🚀 READY FOR TESTING!");
    }

private:
    void critical_goal_callback(const std_msgs::msg::Bool::SharedPtr msg) {
        RCLCPP_INFO(this->get_logger(), "🔥 === RECEIVED CRITICALITY: %s ===", 
                   msg->data ? "CRITICAL" : "NORMAL");
        
        // Simply pass through the criticality flag
        auto criticality_msg = std_msgs::msg::Bool();
        criticality_msg.data = msg->data;
        goal_criticality_pub_->publish(criticality_msg);
        
        RCLCPP_INFO(this->get_logger(), "✅ Published goal criticality: %s", 
                   msg->data ? "CRITICAL" : "NORMAL");
    }
};

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<NavGoalCognitionModule>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}