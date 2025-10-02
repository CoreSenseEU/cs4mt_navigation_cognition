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
#include "std_msgs/msg/bool.hpp"
#include "rcl_interfaces/srv/set_parameters.hpp"
#include "rcl_interfaces/msg/parameter.hpp"
#include "rcl_interfaces/msg/parameter_value.hpp"

class DynamicReconfigureNavModule : public rclcpp::Node {
private:
    // Subscriber for goal criticality
    rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr goal_criticality_sub_;
    
    // Service clients for parameter setting
    rclcpp::Client<rcl_interfaces::srv::SetParameters>::SharedPtr global_costmap_client_;
    rclcpp::Client<rcl_interfaces::srv::SetParameters>::SharedPtr local_costmap_client_;
    
    // Parameters
    double normal_inflation_radius_;
    double critical_inflation_radius_;
    double recovery_inflation_radius_;

public:
    explicit DynamicReconfigureNavModule(
        const rclcpp::NodeOptions &options = rclcpp::NodeOptions())
        : rclcpp::Node("dynamic_reconfigure_nav", options) {
        
        RCLCPP_INFO(this->get_logger(), "Dynamic Reconfigure Nav Module initialized (costmap only)");
        
        // Declare and get parameters
        this->declare_parameter("normal_inflation_radius", 0.55);
        this->declare_parameter("critical_inflation_radius", 0.40);
        this->declare_parameter("recovery_inflation_radius", 0.40);
        
        normal_inflation_radius_ = this->get_parameter("normal_inflation_radius").as_double();
        critical_inflation_radius_ = this->get_parameter("critical_inflation_radius").as_double();
        recovery_inflation_radius_ = this->get_parameter("recovery_inflation_radius").as_double();
        
        RCLCPP_INFO(this->get_logger(), "Configured inflation radii:");
        RCLCPP_INFO(this->get_logger(), "  Normal: %.3fm", normal_inflation_radius_);
        RCLCPP_INFO(this->get_logger(), "  Critical: %.3fm", critical_inflation_radius_);
        RCLCPP_INFO(this->get_logger(), "  Recovery: %.3fm", recovery_inflation_radius_);
        
        // Create subscriber immediately
        goal_criticality_sub_ = this->create_subscription<std_msgs::msg::Bool>(
            "/goal_criticality", 10,
            std::bind(&DynamicReconfigureNavModule::goal_criticality_callback, this, std::placeholders::_1));
        
        // Create service clients immediately
        global_costmap_client_ = this->create_client<rcl_interfaces::srv::SetParameters>(
            "/global_costmap/global_costmap/set_parameters");
        local_costmap_client_ = this->create_client<rcl_interfaces::srv::SetParameters>(
            "/local_costmap/local_costmap/set_parameters");
        
        RCLCPP_INFO(this->get_logger(), "Dynamic Reconfigure Nav Module activated");
        RCLCPP_INFO(this->get_logger(), "📥 Listening on: /goal_criticality");
        RCLCPP_INFO(this->get_logger(), "🔧 Will adjust: global_costmap & local_costmap inflation_radius");
        RCLCPP_INFO(this->get_logger(), "🚀 READY FOR TESTING!");
    }

private:
    void goal_criticality_callback(const std_msgs::msg::Bool::SharedPtr msg) {
        RCLCPP_INFO(this->get_logger(), "🔥 === GOAL CRITICALITY UPDATE: %s ===", 
                   msg->data ? "CRITICAL" : "NORMAL");
        
        double target_radius;
        if (msg->data) {
            // Critical goal - use tight inflation radius
            target_radius = critical_inflation_radius_;
            RCLCPP_WARN(this->get_logger(), "⚠️  CRITICAL GOAL: Setting tight inflation radius %.3fm", target_radius);
        } else {
            // Normal goal - use standard inflation radius
            target_radius = normal_inflation_radius_;
            RCLCPP_INFO(this->get_logger(), "ℹ️  NORMAL GOAL: Setting standard inflation radius %.3fm", target_radius);
        }
        
        // Apply to both global and local costmaps
        set_costmap_inflation_radius(target_radius);
    }

    void set_costmap_inflation_radius(double radius) {
        // Set global costmap inflation radius
        set_single_costmap_inflation_radius(global_costmap_client_, "GLOBAL", radius);
        
        // Set local costmap inflation radius  
        set_single_costmap_inflation_radius(local_costmap_client_, "LOCAL", radius);
    }
    
    void set_single_costmap_inflation_radius(
        rclcpp::Client<rcl_interfaces::srv::SetParameters>::SharedPtr client,
        const std::string& costmap_name,
        double radius) {
        
        if (!client->wait_for_service(std::chrono::seconds(5))) {
            RCLCPP_ERROR(this->get_logger(), "❌ %s costmap service not available after 5 seconds", costmap_name.c_str());
            return;
        }
        
        auto request = std::make_shared<rcl_interfaces::srv::SetParameters::Request>();
        
        rcl_interfaces::msg::Parameter param;
        param.name = "inflation_layer.inflation_radius";
        param.value.type = rcl_interfaces::msg::ParameterType::PARAMETER_DOUBLE;
        param.value.double_value = radius;
        request->parameters.push_back(param);
        
        // Send request and wait for response
        auto future = client->async_send_request(request);
        
        // Wait for the response with timeout
        auto status = future.wait_for(std::chrono::seconds(3));
        if (status == std::future_status::ready) {
            auto response = future.get();
            if (!response->results.empty() && response->results[0].successful) {
                RCLCPP_INFO(this->get_logger(), "✅ Successfully set %s costmap inflation_radius: %.3fm", 
                           costmap_name.c_str(), radius);
            } else {
                RCLCPP_ERROR(this->get_logger(), "❌ Failed to set %s costmap inflation_radius: %s", 
                            costmap_name.c_str(), 
                            response->results.empty() ? "no response" : response->results[0].reason.c_str());
            }
        } else {
            RCLCPP_ERROR(this->get_logger(), "❌ Timeout waiting for %s costmap parameter set response", costmap_name.c_str());
        }
    }
};

int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<DynamicReconfigureNavModule>();
    rclcpp::spin(node);
    rclcpp::shutdown();
    return 0;
}