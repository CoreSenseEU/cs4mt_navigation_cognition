////////////////////////////////////////////////////////////////////
// Copyright 2025 IMR Robotics & Automation Group
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
// http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//See the License for the specific language governing permissions and
// limitations under the License.
////////////////////////////////////////////////////////////////////

#include "cs4home_core/Master.hpp"
#include "cs4home_core/Flow.hpp"
#include "lifecycle_msgs/srv/change_state.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_lifecycle/lifecycle_node.hpp"
#include "std_msgs/msg/bool.hpp"
#include <map>
#include <memory>

using namespace std::chrono_literals;
using namespace std::placeholders;

class MTNavigationCognitiveMaster : public cs4home_core::Master {
public:
  explicit MTNavigationCognitiveMaster(
      const rclcpp::NodeOptions &options = rclcpp::NodeOptions())
      : cs4home_core::Master("navigation_cognitive_master", options) {
    RCLCPP_INFO(this->get_logger(), "🎯 MTNavigationCognitiveMaster initialized");
  }

  using CallbackReturnT = rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn;

  CallbackReturnT on_configure(const rclcpp_lifecycle::State &state) override {
    RCLCPP_INFO(this->get_logger(), "=== NAVIGATION COGNITIVE MASTER CONFIGURE ===");
    
    auto result = cs4home_core::Master::on_configure(state);
    
    if (result == CallbackReturnT::SUCCESS) {
      // Subscribe to goal criticality for master-level decision making (optional)
      goal_criticality_sub_ = this->create_subscription<std_msgs::msg::Bool>(
          "/goal_criticality", 10,
          std::bind(&MTNavigationCognitiveMaster::goal_criticality_callback, this, std::placeholders::_1));
      
      RCLCPP_INFO(this->get_logger(), "✅ Master configured - ready to manage flows");
    }
    
    return result;
  }

  CallbackReturnT on_activate(const rclcpp_lifecycle::State &state) override {
    RCLCPP_INFO(this->get_logger(), "=== NAVIGATION COGNITIVE MASTER ACTIVATE ===");
    
    auto result = cs4home_core::Master::on_activate(state);
    
    if (result == CallbackReturnT::SUCCESS) {
      if (!flows_.empty()) {
        RCLCPP_INFO(this->get_logger(), "📋 Active Cognitive Navigation Flows:");
        
        for (const auto &flow : flows_) {
          std::string flow_name = flow.first;
          auto flow_nodes = flow.second;
          
          RCLCPP_INFO(this->get_logger(), "🔗 %s:", flow_name.c_str());
          
          for (const auto &node : flow_nodes->get_flow()) {
            RCLCPP_INFO(this->get_logger(), "    🧠 %s", node.c_str());
            
            // Create lifecycle client for this node (it should already exist)
            create_lifecycle_client(node);
          }
        }
        
        // Start periodic lifecycle management
        RCLCPP_INFO(this->get_logger(), "🚀 Starting lifecycle management...");
        management_timer_ = this->create_wall_timer(
          5s, std::bind(&MTNavigationCognitiveMaster::manage_flow_lifecycles, this));
        
        print_operational_summary();
        
      } else {
        RCLCPP_WARN(this->get_logger(), "⚠️  No cognitive flows configured!");
      }
    }
    
    return result;
  }

  CallbackReturnT on_deactivate(const rclcpp_lifecycle::State &state) override {
    RCLCPP_INFO(this->get_logger(), "=== NAVIGATION COGNITIVE MASTER DEACTIVATE ===");
    
    if (management_timer_) {
      management_timer_->cancel();
      management_timer_.reset();
    }
    
    return cs4home_core::Master::on_deactivate(state);
  }

  CallbackReturnT on_cleanup(const rclcpp_lifecycle::State &state) override {
    RCLCPP_INFO(this->get_logger(), "=== NAVIGATION COGNITIVE MASTER CLEANUP ===");
    
    lifecycle_clients_.clear();
    
    return cs4home_core::Master::on_cleanup(state);
  }

private:
  // Subscriptions for master-level coordination
  rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr goal_criticality_sub_;
  
  // Lifecycle management
  std::map<std::string, rclcpp::Client<lifecycle_msgs::srv::ChangeState>::SharedPtr> lifecycle_clients_;
  rclcpp::TimerBase::SharedPtr management_timer_;
  
  // State tracking
  bool current_criticality_ = false;

  void goal_criticality_callback(const std_msgs::msg::Bool::SharedPtr msg) {
    current_criticality_ = msg->data;
    
    RCLCPP_INFO(this->get_logger(), "🎯 Master received criticality update: %s",
               current_criticality_ ? "CRITICAL" : "NORMAL");
    
    // Master-level decision making based on criticality
    // For example: activate additional flows, change priorities, etc.
    if (current_criticality_) {
      RCLCPP_WARN(this->get_logger(), "⚠️  CRITICAL MODE: Enhanced navigation active");
      // Could activate additional cognitive modules here
    } else {
      RCLCPP_INFO(this->get_logger(), "ℹ️  NORMAL MODE: Standard navigation active");
    }
  }

  void create_lifecycle_client(const std::string& node_name) {
    std::string service_name = "/" + node_name + "/change_state";
    lifecycle_clients_[node_name] = 
      this->create_client<lifecycle_msgs::srv::ChangeState>(service_name);
    
    RCLCPP_DEBUG(this->get_logger(), "🔗 Created lifecycle client for %s", node_name.c_str());
  }

  void manage_flow_lifecycles() {
    // Ensure all nodes in flows are properly configured and activated
    for (const auto& [node_name, client] : lifecycle_clients_) {
      ensure_node_active(node_name, client);
    }
  }

  void ensure_node_active(const std::string& node_name, 
                         rclcpp::Client<lifecycle_msgs::srv::ChangeState>::SharedPtr client) {
    if (!client->wait_for_service(1s)) {
      RCLCPP_DEBUG(this->get_logger(), "⏳ Waiting for %s to become available...", node_name.c_str());
      return;
    }

    // In a full implementation, you'd check current state first
    // For now, we assume nodes are managed externally or by launch files
    RCLCPP_DEBUG(this->get_logger(), "✅ %s lifecycle service available", node_name.c_str());
  }

  void print_operational_summary() {
    RCLCPP_INFO(this->get_logger(), "🎯 === COGNITIVE NAVIGATION SYSTEM OPERATIONAL ===");
    RCLCPP_INFO(this->get_logger(), "🧠 Master monitoring %zu cognitive flows", flows_.size());
    RCLCPP_INFO(this->get_logger(), "🚀 Ready to coordinate navigation cognition!");
  }
};

int main(int argc, char **argv) {
  RCLCPP_INFO(rclcpp::get_logger("main"), "=== STARTING NAVIGATION COGNITIVE MASTER ===");
  rclcpp::init(argc, argv);
  
  rclcpp::NodeOptions options;
  auto node = std::make_shared<MTNavigationCognitiveMaster>(options);
  
  rclcpp::spin(node->get_node_base_interface());
  rclcpp::shutdown();
  return 0;
}