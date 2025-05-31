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

using namespace std::chrono_literals;
using namespace std::placeholders;

class MTNavigationCognitiveMaster : public cs4home_core::Master {
private:
  // Flow management
  std::map<std::string, std::shared_ptr<cs4home_core::Flow>> flows_;
  
public:
  explicit MTNavigationCognitiveMaster(
      const rclcpp::NodeOptions &options = rclcpp::NodeOptions())
      : cs4home_core::Master(options) {
    RCLCPP_INFO(this->get_logger(), "Master for Navigation Cognitive module for MT - initialized");
    RCLCPP_INFO(this->get_logger(), "Node name: %s", this->get_name());
  }

  using CallbackReturnT = rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn;

  CallbackReturnT on_configure(const rclcpp_lifecycle::State &state) override {
    RCLCPP_INFO(this->get_logger(), "=== MASTER CONFIGURE STATE ===");
    
    // Call parent's on_configure first
    auto result = cs4home_core::Master::on_configure(state);
    
    // Load flows from parameters
    try {
      std::vector<std::string> flow_names;
      this->declare_parameter("flows", std::vector<std::string>());
      
      if (this->get_parameter("flows", flow_names)) {
        RCLCPP_INFO(this->get_logger(), "Found %zu flows in parameters", flow_names.size());
        
        for (const auto& flow_name : flow_names) {
          RCLCPP_INFO(this->get_logger(), "Loading flow: %s", flow_name.c_str());
          
          // Declare and get the flow nodes
          this->declare_parameter(flow_name, std::vector<std::string>());
          std::vector<std::string> flow_nodes;
          
          if (this->get_parameter(flow_name, flow_nodes)) {
            RCLCPP_INFO(this->get_logger(), "  Flow %s has %zu nodes", flow_name.c_str(), flow_nodes.size());
            
            // Create Flow object
            auto flow = std::make_shared<cs4home_core::Flow>(flow_nodes);
            flows_[flow_name] = flow;
            
            // Print flow nodes
            for (size_t i = 0; i < flow_nodes.size(); ++i) {
              RCLCPP_INFO(this->get_logger(), "    [%zu] %s", i, flow_nodes[i].c_str());
            }
          } else {
            RCLCPP_WARN(this->get_logger(), "Could not load nodes for flow: %s", flow_name.c_str());
          }
        }
      } else {
        RCLCPP_WARN(this->get_logger(), "No 'flows' parameter found");
      }
    } catch (const std::exception& e) {
      RCLCPP_ERROR(this->get_logger(), "Error loading flows: %s", e.what());
      return CallbackReturnT::FAILURE;
    }
    
    RCLCPP_INFO(this->get_logger(), "Configure completed with %zu flows loaded", flows_.size());
    return result;
  }

  CallbackReturnT on_activate(const rclcpp_lifecycle::State &state) override {
    RCLCPP_INFO(this->get_logger(), "=== MASTER ACTIVATE STATE CALLED ===");
    
    // Call parent's on_activate first
    auto result = cs4home_core::Master::on_activate(state);
    
    RCLCPP_INFO(this->get_logger(), "Number of flows loaded: %zu", flows_.size());
    
    if (!flows_.empty()) {
      RCLCPP_INFO(this->get_logger(), "=== FLOWS FOUND ===");
      for (const auto &flow : flows_) {
        std::string key = flow.first;
        auto value = flow.second;
        RCLCPP_INFO(this->get_logger(), "Flow name: '%s'", key.c_str());
        
        if (value) {
          // Note: cs4home_core::Flow doesn't have get_flow() method, we need to access nodes differently
          RCLCPP_INFO(this->get_logger(), "  Flow loaded successfully");
          // Print the flow using the built-in print method
          std::cout << "Flow " << key << ":";
          value->print();
        } else {
          RCLCPP_WARN(this->get_logger(), "  Flow value is null!");
        }
      }
    } else {
      RCLCPP_WARN(this->get_logger(), "=== NO FLOWS FOUND ===");
      RCLCPP_WARN(this->get_logger(), "Check if params.yaml is loaded correctly");
    }
    
    RCLCPP_INFO(this->get_logger(), "=== MASTER ACTIVATE COMPLETED ===");
    return result;
  }

  CallbackReturnT on_deactivate(const rclcpp_lifecycle::State &state) override {
    RCLCPP_INFO(this->get_logger(), "=== MASTER DEACTIVATE STATE ===");
    return cs4home_core::Master::on_deactivate(state);
  }

  CallbackReturnT on_cleanup(const rclcpp_lifecycle::State &state) override {
    RCLCPP_INFO(this->get_logger(), "=== MASTER CLEANUP STATE ===");
    flows_.clear();
    return cs4home_core::Master::on_cleanup(state);
  }

  CallbackReturnT on_shutdown(const rclcpp_lifecycle::State &state) override {
    RCLCPP_INFO(this->get_logger(), "=== MASTER SHUTDOWN STATE ===");
    return cs4home_core::Master::on_shutdown(state);
  }

  // Getter for flows (if needed by other components)
  const std::map<std::string, std::shared_ptr<cs4home_core::Flow>>& get_flows() const {
    return flows_;
  }
};

int main(int argc, char **argv) {
  RCLCPP_INFO(rclcpp::get_logger("main"), "=== STARTING MASTER APPLICATION ===");
  rclcpp::init(argc, argv);
  
  rclcpp::NodeOptions options;
  auto node = std::make_shared<MTNavigationCognitiveMaster>(options);
  
  RCLCPP_INFO(rclcpp::get_logger("main"), "Master node created, starting spin...");
  rclcpp::spin(node->get_node_base_interface());
  
  RCLCPP_INFO(rclcpp::get_logger("main"), "=== SHUTTING DOWN MASTER APPLICATION ===");
  rclcpp::shutdown();
  return 0;
}