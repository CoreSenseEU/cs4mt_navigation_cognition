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

///// Main orchestrator node for Navigation cognition at least now for the Manufacturing testbed use-case ///

#include "cs4home_core/Master.hpp"
#include "cs4home_core/Flow.hpp"
#include "lifecycle_msgs/srv/change_state.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_lifecycle/lifecycle_node.hpp"
#include "std_msgs/msg/bool.hpp"
#include <map>
#include <memory>
#include <thread>
#include <chrono>
#include <vector>
#include <string>
#include <algorithm>

using namespace std::chrono_literals;
using namespace std::placeholders;

class MTNavigationCognitiveMaster : public cs4home_core::Master {
public:
  explicit MTNavigationCognitiveMaster(
      const rclcpp::NodeOptions &options = rclcpp::NodeOptions())
      : cs4home_core::Master("mt_navigation_cognitive_master", options) {
    RCLCPP_INFO(this->get_logger(), "🎯 MTNavigationCognitiveMaster initialized");
    RCLCPP_INFO(this->get_logger(), "Node name: %s", this->get_name());
  }

  using CallbackReturnT = rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn;

  CallbackReturnT on_configure(const rclcpp_lifecycle::State &state) override {
    RCLCPP_INFO(this->get_logger(), "=== NAVIGATION COGNITIVE MASTER CONFIGURE ===");
    
    auto result = cs4home_core::Master::on_configure(state);
    
    if (result == CallbackReturnT::SUCCESS) {
      // Load basic configuration
      if (!load_basic_configuration()) {
        return CallbackReturnT::FAILURE;
      }
      
      RCLCPP_INFO(this->get_logger(), "✅ Configuration complete");
    }
    
    return result;
  }

  CallbackReturnT on_activate(const rclcpp_lifecycle::State &state) override {
    RCLCPP_INFO(this->get_logger(), "=== NAVIGATION COGNITIVE MASTER ACTIVATE ===");
    
    auto result = cs4home_core::Master::on_activate(state);
    
    if (result == CallbackReturnT::SUCCESS) {
      if (!flows_.empty()) {
        RCLCPP_INFO(this->get_logger(), "📋 Active Flows:");
        
        for (const auto &flow : flows_) {
          std::string key = flow.first;
          auto value = flow.second;
          
          RCLCPP_INFO(this->get_logger(), "🔗 %s:", key.c_str());
          
          for (const auto &node : value->get_flow()) {
            RCLCPP_INFO(this->get_logger(), "    🔧 %s", node.c_str());
          }
        }
        
        // Extract all unique nodes from flows
        extract_nodes_from_flows();
        
        if (!all_nodes_to_launch_.empty()) {
          RCLCPP_INFO(this->get_logger(), "🚀 Launching %zu nodes...", all_nodes_to_launch_.size());
          
          // Launch nodes using node name = executable name
          launch_all_nodes_by_name();
          
          // Start lifecycle management
          management_timer_ = this->create_wall_timer(
            3s, std::bind(&MTNavigationCognitiveMaster::manage_all_lifecycles, this));
        } else {
          RCLCPP_WARN(this->get_logger(), "⚠️  No nodes found in flows!");
        }
        
        print_operational_summary();
        
      } else {
        RCLCPP_WARN(this->get_logger(), "No flow :(");
      }
    }
    
    return result;
  }

  CallbackReturnT on_deactivate(const rclcpp_lifecycle::State &state) override {
    RCLCPP_INFO(this->get_logger(), "=== NAVIGATION COGNITIVE MASTER DEACTIVATE ===");
    cleanup_all_nodes();
    return cs4home_core::Master::on_deactivate(state);
  }

  CallbackReturnT on_cleanup(const rclcpp_lifecycle::State &state) override {
    RCLCPP_INFO(this->get_logger(), "=== NAVIGATION COGNITIVE MASTER CLEANUP ===");
    lifecycle_clients_.clear();
    all_nodes_to_launch_.clear();
    return cs4home_core::Master::on_cleanup(state);
  }

  CallbackReturnT on_shutdown(const rclcpp_lifecycle::State &state) override {
    RCLCPP_INFO(this->get_logger(), "=== NAVIGATION COGNITIVE MASTER SHUTDOWN ===");
    cleanup_all_nodes();
    return cs4home_core::Master::on_shutdown(state);
  }

private:
  // Configuration - from parameters
  std::string package_name_;
  
  // Management
  std::map<std::string, rclcpp::Client<lifecycle_msgs::srv::ChangeState>::SharedPtr> lifecycle_clients_;
  std::vector<std::string> all_nodes_to_launch_;
  rclcpp::TimerBase::SharedPtr management_timer_;

  bool load_basic_configuration() {
    RCLCPP_INFO(this->get_logger(), "📋 Loading basic configuration...");
    
    // Load package name - where executables are located
    this->declare_parameter("package_name", std::string("cs4mt_navigation_cognition"));
    package_name_ = this->get_parameter("package_name").as_string();
    
    RCLCPP_INFO(this->get_logger(), "📋 Package: %s", package_name_.c_str());
    
    return true;
  }
  
  void extract_nodes_from_flows() {
    RCLCPP_INFO(this->get_logger(), "🔍 Extracting unique nodes from flows...");
    
    for (const auto &flow : flows_) {
      auto value = flow.second;
      
      for (const auto &node : value->get_flow()) {
        // Add unique nodes only
        if (std::find(all_nodes_to_launch_.begin(), all_nodes_to_launch_.end(), node) == 
            all_nodes_to_launch_.end()) {
          all_nodes_to_launch_.push_back(node);
          RCLCPP_INFO(this->get_logger(), "➕ Will launch: %s → %s", node.c_str(), node.c_str());
        }
      }
    }
    
    RCLCPP_INFO(this->get_logger(), "🎯 Total nodes to launch: %zu", all_nodes_to_launch_.size());
  }
  
  void launch_all_nodes_by_name() {
    RCLCPP_INFO(this->get_logger(), "🚀 === LAUNCHING NODES BY NAME ===");
    
    for (const auto& node_name : all_nodes_to_launch_) {
      launch_node_by_name(node_name);
      std::this_thread::sleep_for(1s);  // Stagger launches
    }
    
    // Wait for nodes to initialize
    RCLCPP_INFO(this->get_logger(), "⏳ Waiting for nodes to initialize...");
    std::this_thread::sleep_for(3s);
    
    create_all_lifecycle_clients();
  }
  
  void launch_node_by_name(const std::string& node_name) {
    // executable name = node name
    std::string executable_name = node_name;
    
    RCLCPP_INFO(this->get_logger(), "🔧 Launching %s", node_name.c_str());
    
    // Launch command using node name as executable name
    std::thread([this, node_name, executable_name]() {
      std::string command = "ros2 run " + package_name_ + " " + executable_name + " &";
      
      RCLCPP_INFO(this->get_logger(), "💻 Command: %s", command.c_str());
      
      int result = std::system(command.c_str());
      if (result == 0) {
        RCLCPP_INFO(this->get_logger(), "✅ Successfully launched %s", node_name.c_str());
      } else {
        RCLCPP_ERROR(this->get_logger(), "❌ Failed to launch %s (exit code: %d)", 
                    node_name.c_str(), result);
      }
    }).detach();
  }
  
  void create_all_lifecycle_clients() {
    RCLCPP_INFO(this->get_logger(), "🔗 Creating lifecycle clients for %zu nodes", all_nodes_to_launch_.size());
    
    for (const auto& node_name : all_nodes_to_launch_) {
      std::string service_name = "/" + node_name + "/change_state";
      lifecycle_clients_[node_name] = 
        this->create_client<lifecycle_msgs::srv::ChangeState>(service_name);
      
      RCLCPP_INFO(this->get_logger(), "🔗 Client for %s → %s", node_name.c_str(), service_name.c_str());
    }
  }
  
  void manage_all_lifecycles() {
    static bool all_activated = false;
    
    if (!all_activated) {
      RCLCPP_INFO(this->get_logger(), "🔄 Managing lifecycle for %zu nodes...", lifecycle_clients_.size());
      
      int success_count = 0;
      for (auto& [node_name, client] : lifecycle_clients_) {
        if (configure_and_activate_node(node_name, client)) {
          success_count++;
        }
      }
      
      if (success_count == static_cast<int>(lifecycle_clients_.size())) {
        all_activated = true;
        RCLCPP_INFO(this->get_logger(), "🎯 === ALL %d NODES OPERATIONAL ===", success_count);
        
        if (management_timer_) management_timer_->cancel();
      } else {
        RCLCPP_WARN(this->get_logger(), "⚠️  Only %d/%zu nodes activated, retrying...", 
                   success_count, lifecycle_clients_.size());
      }
    }
  }
  
  bool configure_and_activate_node(const std::string& node_name,
                                rclcpp::Client<lifecycle_msgs::srv::ChangeState>::SharedPtr client) {
    if (!client->wait_for_service(1s)) {
      RCLCPP_WARN(this->get_logger(), "⚠️  Service unavailable: %s", node_name.c_str());
      return false;
    }
    
    // Configure
    auto configure_req = std::make_shared<lifecycle_msgs::srv::ChangeState::Request>();
    configure_req->transition.id = 1; // configure
    
    RCLCPP_INFO(this->get_logger(), "⚙️  Configuring %s...", node_name.c_str());
    auto config_future = client->async_send_request(configure_req);
    
    auto status = config_future.wait_for(5s);
    if (status != std::future_status::ready) {
      RCLCPP_ERROR(this->get_logger(), "❌ Failed to configure %s (timeout)", node_name.c_str());
      return false;
    }
    
    auto config_response = config_future.get();
    if (!config_response || !config_response->success) {
      RCLCPP_ERROR(this->get_logger(), "❌ Failed to configure %s", node_name.c_str());
      return false;
    }
    
    // Activate
    auto activate_req = std::make_shared<lifecycle_msgs::srv::ChangeState::Request>();
    activate_req->transition.id = 3; // activate
    
    RCLCPP_INFO(this->get_logger(), "🟢 Activating %s...", node_name.c_str());
    auto activate_future = client->async_send_request(activate_req);
    
    status = activate_future.wait_for(5s);
    if (status == std::future_status::ready) {
      auto activate_response = activate_future.get();
      if (activate_response && activate_response->success) {
        RCLCPP_INFO(this->get_logger(), "✅ %s ACTIVATED", node_name.c_str());
        return true;
      }
    }
    
    RCLCPP_ERROR(this->get_logger(), "❌ Failed to activate %s", node_name.c_str());
    return false;
  }

  void print_operational_summary() {
    RCLCPP_INFO(this->get_logger(), "🎯 === COGNITIVE NAVIGATION SYSTEM OPERATIONAL ===");
    RCLCPP_INFO(this->get_logger(), "🚀 Ready to process cognitive flows!");
  }
  
  void cleanup_all_nodes() {
    if (management_timer_) {
      management_timer_->cancel();
      management_timer_.reset();
    }
    RCLCPP_INFO(this->get_logger(), "🛑 Cleanup complete");
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