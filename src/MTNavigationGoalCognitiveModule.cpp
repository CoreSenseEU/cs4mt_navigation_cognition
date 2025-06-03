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
#include "rclcpp_lifecycle/lifecycle_node.hpp"
#include "std_msgs/msg/bool.hpp"

/**
 * @brief Modular Navigation Goal Cognitive Module
 * Uses parameters for all configuration - NO HARDCODING
 */
class NavGoalCognitionModule : public rclcpp_lifecycle::LifecycleNode {
private:
    // Subscriber for goal input
    rclcpp::Subscription<std_msgs::msg::Bool>::SharedPtr goal_input_sub_;
    
    // Publisher for goal criticality output
    rclcpp_lifecycle::LifecyclePublisher<std_msgs::msg::Bool>::SharedPtr goal_output_pub_;
    
    // Processing timer for cognitive functions
    rclcpp::TimerBase::SharedPtr processing_timer_;
    
    // Configuration parameters - NO HARDCODING
    std::string input_topic_;
    std::string output_topic_;
    int processing_rate_ms_;
    bool enable_cognitive_processing_;
    
    // State variables
    std_msgs::msg::Bool::SharedPtr last_goal_msg_;

public:
    explicit NavGoalCognitionModule(
        const rclcpp::NodeOptions &options = rclcpp::NodeOptions())
        : rclcpp_lifecycle::LifecycleNode("nav_goal_cognition", options) {
        
        RCLCPP_INFO(this->get_logger(), "Modular Navigation Goal Cognitive Module initialized");
    }

    using CallbackReturnT = rclcpp_lifecycle::node_interfaces::LifecycleNodeInterface::CallbackReturn;

    CallbackReturnT on_configure(const rclcpp_lifecycle::State &) override {
        RCLCPP_INFO(this->get_logger(), "🔧 Configuring Navigation Goal Cognitive Module");
        
        // Declare and load parameters - ZERO HARDCODING
        this->declare_parameter("input_topic", std::string("/critical_goal"));
        this->declare_parameter("output_topic", std::string("/goal_criticality"));
        this->declare_parameter("processing_rate_ms", 100);
        this->declare_parameter("enable_cognitive_processing", true);
        
        input_topic_ = this->get_parameter("input_topic").as_string();
        output_topic_ = this->get_parameter("output_topic").as_string();
        processing_rate_ms_ = this->get_parameter("processing_rate_ms").as_int();
        enable_cognitive_processing_ = this->get_parameter("enable_cognitive_processing").as_bool();
        
        RCLCPP_INFO(this->get_logger(), "📋 Configuration loaded:");
        RCLCPP_INFO(this->get_logger(), "  📥 Input topic: %s", input_topic_.c_str());
        RCLCPP_INFO(this->get_logger(), "  📤 Output topic: %s", output_topic_.c_str());
        RCLCPP_INFO(this->get_logger(), "  ⏱️  Processing rate: %d ms", processing_rate_ms_);
        RCLCPP_INFO(this->get_logger(), "  🧠 Cognitive processing: %s", 
                   enable_cognitive_processing_ ? "ENABLED" : "DISABLED");
        
        // Create subscriber using parameter-defined topic
        goal_input_sub_ = this->create_subscription<std_msgs::msg::Bool>(
            input_topic_, 10,
            std::bind(&NavGoalCognitionModule::goal_input_callback, this, std::placeholders::_1));
        
        // Create lifecycle publisher using parameter-defined topic
        goal_output_pub_ = this->create_publisher<std_msgs::msg::Bool>(output_topic_, 10);
        
        // Create processing timer with parameter-defined rate
        processing_timer_ = this->create_wall_timer(
            std::chrono::milliseconds(processing_rate_ms_),
            std::bind(&NavGoalCognitionModule::cognitive_processing_callback, this));
        processing_timer_->cancel(); // Start inactive
        
        RCLCPP_INFO(this->get_logger(), "✅ Navigation Goal Cognitive Module configured");
        return CallbackReturnT::SUCCESS;
    }

    CallbackReturnT on_activate(const rclcpp_lifecycle::State &) override {
        RCLCPP_INFO(this->get_logger(), "🟢 Activating Navigation Goal Cognitive Module");
        
        // Activate publisher
        goal_output_pub_->on_activate();
        
        // Start cognitive processing timer if enabled
        if (enable_cognitive_processing_) {
            processing_timer_->reset();
            RCLCPP_INFO(this->get_logger(), "🧠 Cognitive processing timer started");
        }
        
        RCLCPP_INFO(this->get_logger(), "🚀 Navigation Goal Cognitive Module ACTIVE");
        RCLCPP_INFO(this->get_logger(), "📥 Listening on: %s", input_topic_.c_str());
        RCLCPP_INFO(this->get_logger(), "📤 Publishing to: %s", output_topic_.c_str());
        RCLCPP_INFO(this->get_logger(), "🚀 READY FOR COGNITIVE PROCESSING!");
        
        return CallbackReturnT::SUCCESS;
    }

    CallbackReturnT on_deactivate(const rclcpp_lifecycle::State &) override {
        RCLCPP_INFO(this->get_logger(), "🔴 Deactivating Navigation Goal Cognitive Module");
        
        // Deactivate publisher
        goal_output_pub_->on_deactivate();
        
        // Stop processing timer
        processing_timer_->cancel();
        
        return CallbackReturnT::SUCCESS;
    }

    CallbackReturnT on_cleanup(const rclcpp_lifecycle::State &) override {
        RCLCPP_INFO(this->get_logger(), "🧹 Cleaning up Navigation Goal Cognitive Module");
        
        goal_input_sub_.reset();
        goal_output_pub_.reset();
        processing_timer_.reset();
        last_goal_msg_.reset();
        
        return CallbackReturnT::SUCCESS;
    }

private:
    /**
     * @brief Callback for incoming goal messages from Input component
     */
    void goal_input_callback(const std_msgs::msg::Bool::SharedPtr msg) {
        RCLCPP_INFO(this->get_logger(), "🎯 === RECEIVED GOAL: %s ===", 
                   msg->data ? "CRITICAL" : "NORMAL");
        
        // Store for cognitive processing
        last_goal_msg_ = msg;
        
        // Immediate processing and forwarding
        process_and_publish_goal(msg);
    }

    /**
     * @brief Periodic cognitive processing callback
     * Runs at parameter-defined rate for continuous cognitive functions
     */
    void cognitive_processing_callback() {
        if (!enable_cognitive_processing_) return;
        
        // Perform ongoing cognitive analysis
        if (last_goal_msg_) {
            // Example cognitive processing: 
            // - Goal persistence analysis
            // - Context-aware criticality adjustment
            // - Learning from goal patterns
            
            RCLCPP_DEBUG(this->get_logger(), "🧠 Cognitive processing: analyzing goal state");
            
            // For now, reprocess the last goal with potential cognitive enhancement
            perform_cognitive_enhancement();
        }
    }

    /**
     * @brief Core goal processing and publishing logic
     */
    void process_and_publish_goal(const std_msgs::msg::Bool::SharedPtr input_msg) {
        if (!input_msg) return;
        
        // Cognitive processing logic - modular and configurable
        bool processed_criticality = apply_cognitive_processing(input_msg->data);
        
        // Create and publish output message
        auto output_msg = std::make_unique<std_msgs::msg::Bool>();
        output_msg->data = processed_criticality;
        
        goal_output_pub_->publish(std::move(output_msg));
        
        RCLCPP_INFO(this->get_logger(), "📤 Published goal criticality: %s", 
                   processed_criticality ? "CRITICAL" : "NORMAL");
    }

    /**
     * @brief Apply cognitive processing to goal criticality
     * @param input_criticality Raw criticality from input
     * @return Processed criticality after cognitive analysis
     */
    bool apply_cognitive_processing(bool input_criticality) {
        if (!enable_cognitive_processing_) {
            // Simple pass-through if cognitive processing disabled
            return input_criticality;
        }
        
        // Cognitive enhancement logic:
        // - Context analysis
        // - Historical pattern recognition
        // - Situational awareness
        // - Risk assessment
        
        // For now, simple pass-through with logging
        RCLCPP_DEBUG(this->get_logger(), "🧠 Applying cognitive processing to criticality");
        
        // TODO: Add actual cognitive algorithms here
        // Example: Learning-based criticality adjustment
        // Example: Multi-factor risk analysis
        // Example: Temporal pattern recognition
        
        return input_criticality; // Enhanced processing result
    }

    /**
     * @brief Perform ongoing cognitive enhancement
     */
    void perform_cognitive_enhancement() {
        // Ongoing cognitive functions:
        // - Pattern learning
        // - Context building
        // - Predictive analysis
        // - System optimization
        
        RCLCPP_DEBUG(this->get_logger(), "🧠 Performing cognitive enhancement");
        
        // TODO: Implement learning algorithms
        // TODO: Implement pattern recognition
        // TODO: Implement predictive modeling
    }
};

/**
 * @brief Main function - creates modular lifecycle node
 */
int main(int argc, char **argv) {
    rclcpp::init(argc, argv);
    auto node = std::make_shared<NavGoalCognitionModule>();
    rclcpp::spin(node->get_node_base_interface());
    rclcpp::shutdown();
    return 0;
}