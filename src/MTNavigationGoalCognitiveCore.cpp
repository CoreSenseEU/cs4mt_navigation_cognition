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

#include "cs4home_core/Core.hpp"
#include "cs4home_core/macros.hpp"
#include "std_msgs/msg/bool.hpp"
#include "rclcpp/macros.hpp"
#include "rclcpp_lifecycle/lifecycle_node.hpp"
#include "rclcpp_components/register_node_macro.hpp"

#include <unordered_map>
#include <chrono>

using std::placeholders::_1;
using namespace std::chrono_literals;

/**
 * @class NavigationGoalCognition
 * @brief Core component that processes incoming goal criticality messages
 * and applies cognitive analysis for navigation decision making.
 */
class NavigationGoalCognitiveCore : public cs4home_core::Core {
public:
  RCLCPP_SMART_PTR_DEFINITIONS(NavigationGoalCognitiveCore)

  /**
   * @brief Constructs a NavigationGoalCognition object and initializes the parent
   * lifecycle node.
   * @param parent Shared pointer to the lifecycle node managing this
   * NavigationGoalCognition instance.
   */
  explicit NavigationGoalCognitiveCore(rclcpp_lifecycle::LifecycleNode::SharedPtr parent)
      : Core("nav_goal_cognitive_core", parent) {
    RCLCPP_DEBUG(parent_->get_logger(), "Core created: [nav_goal_cognitive_core]");
    
    // Initialize cognitive processing parameters
    // Template from Sound module 
    this->last_check_ = parent_->get_clock()->now();
    this->goal_history_.clear();
    this->current_criticality_ = false; // I am defining this to see if the goal being critical for inflation radius
    
    // Cognitive thresholds and parameters
    this->COGNITIVE_PROCESSING_INTERVAL = 1.0; // seconds
    this->GOAL_PERSISTENCE_THRESHOLD = 3.0;    // seconds
    this->CRITICALITY_CONFIDENCE_THRESHOLD = 0.8;
    
    RCLCPP_INFO(parent_->get_logger(), "🧠 NavigationGoalCognition core initialized");
  }

  /**
   * @brief Process incoming goal criticality data with cognitive analysis
   * @param goal_msg The incoming goal criticality message
   */
  void process_goal_data(std::shared_ptr<std_msgs::msg::Bool> goal_msg) {
    auto now = parent_->get_clock()->now();
    
    // Store goal in history for cognitive analysis
    GoalEvent goal_event;
    goal_event.timestamp = now;
    goal_event.is_critical = goal_msg->data;
    goal_event.confidence = 1.0; // Initial confidence
    
    goal_history_.push_back(goal_event);
    
    // Keep history within reasonable bounds (last 100 goals)
    if (goal_history_.size() > 100) {
      goal_history_.erase(goal_history_.begin());
    }
    
    RCLCPP_INFO(parent_->get_logger(), 
               "🎯 [NavigationGoalCognition] Processing goal: %s",
               goal_msg->data ? "CRITICAL" : "NORMAL");
    
    // Apply cognitive processing
    bool enhanced_criticality = apply_cognitive_enhancement(goal_msg->data, now);
    
    // Create and publish enhanced goal message
    auto enhanced_goal = std::make_shared<std_msgs::msg::Bool>();
    enhanced_goal->data = enhanced_criticality;
    
    // Publish through efferent component
    // TODO uncomment this
    //efferent_->publish(0, enhanced_goal);
    
    RCLCPP_INFO(parent_->get_logger(),
               "📤 [NavigationGoalCognition] Published enhanced criticality: %s",
               enhanced_criticality ? "CRITICAL" : "NORMAL");
    
    this->last_check_ = now;
    this->current_criticality_ = enhanced_criticality;
  }

  /**
   * @brief Apply cognitive enhancement to goal criticality
   * @param raw_criticality The original criticality value
   * @param timestamp Current timestamp
   * @return Enhanced criticality after cognitive processing
   */
  bool apply_cognitive_enhancement(bool raw_criticality, const rclcpp::Time& timestamp) {
    // Cognitive Enhancement Algorithm:
    // 1. Goal persistence analysis
    // 2. Pattern recognition
    // 3. Context-aware adjustment
    // 4. Confidence-based filtering
    
    bool enhanced_criticality = raw_criticality;
    
    // 1. Goal Persistence Analysis
    double persistence_factor = analyze_goal_persistence(timestamp);
    
    // 2. Pattern Recognition
    double pattern_confidence = analyze_goal_patterns();
    
    // 3. Context-Aware Adjustment
    bool context_adjustment = apply_context_awareness(raw_criticality);
    
    // 4. Combine cognitive factors
    if (pattern_confidence < CRITICALITY_CONFIDENCE_THRESHOLD) {
      // Low confidence in pattern - be more conservative
      if (!raw_criticality && persistence_factor > GOAL_PERSISTENCE_THRESHOLD) {
        // Promote to critical if persistent non-critical goals detected
        enhanced_criticality = true;
        RCLCPP_INFO(parent_->get_logger(),
                   "🧠 [Cognitive] Promoting to CRITICAL due to persistence");
      }
    }
    
    // Apply context adjustment
    enhanced_criticality = enhanced_criticality || context_adjustment;
    
    RCLCPP_DEBUG(parent_->get_logger(),
                "🧠 [Cognitive] Raw: %s, Enhanced: %s (persistence: %.2f, confidence: %.2f)",
                raw_criticality ? "CRITICAL" : "NORMAL",
                enhanced_criticality ? "CRITICAL" : "NORMAL",
                persistence_factor, pattern_confidence);
    
    return enhanced_criticality;
  }

  /**
   * @brief Analyze goal persistence over time
   * @param current_time Current timestamp
   * @return Persistence factor (higher = more persistent)
   */
  double analyze_goal_persistence(const rclcpp::Time& current_time) {
    if (goal_history_.empty()) return 0.0;
    
    // Count goals in recent history
    int recent_goals = 0;
    double time_window = 5.0; // seconds
    
    for (const auto& goal : goal_history_) {
      double time_diff = (current_time - goal.timestamp).seconds();
      if (time_diff <= time_window) {
        recent_goals++;
      }
    }
    
    // Higher frequency indicates higher persistence
    return static_cast<double>(recent_goals) / time_window;
  }

  /**
   * @brief Analyze patterns in goal history
   * @return Pattern confidence (0.0 - 1.0)
   */
  double analyze_goal_patterns() {
    if (goal_history_.size() < 3) return 0.5; // Neutral confidence
    
    // Simple pattern analysis: consistency in recent goals
    int critical_count = 0;
    int total_recent = std::min(10, static_cast<int>(goal_history_.size()));
    
    for (int i = goal_history_.size() - total_recent; i < goal_history_.size(); i++) {
      if (goal_history_[i].is_critical) {
        critical_count++;
      }
    }
    
    // Calculate pattern consistency
    double critical_ratio = static_cast<double>(critical_count) / total_recent;
    
    // High consistency (very low or very high ratio) = high confidence
    // Mixed patterns = lower confidence
    if (critical_ratio < 0.2 || critical_ratio > 0.8) {
      return 0.9; // High confidence in pattern
    } else {
      return 0.3; // Low confidence in mixed patterns
    }
  }

  /**
   * @brief Apply context-aware adjustments
   * @param raw_criticality Original criticality
   * @return Context adjustment (additional criticality)
   */
  bool apply_context_awareness(bool raw_criticality) {
    // Context factors that might influence criticality:
    // - Time of day
    // - Goal frequency
    // - System load
    // - Historical performance
    
    auto now = parent_->get_clock()->now();
    
    // Example: If we've been getting many goals recently, 
    // increase criticality awareness
    double recent_goal_rate = analyze_goal_persistence(now);
    
    if (recent_goal_rate > 2.0 && !raw_criticality) {
      // High goal rate but not marked critical - apply context adjustment
      RCLCPP_DEBUG(parent_->get_logger(),
                  "🧠 [Context] High goal rate detected: %.2f goals/sec",
                  recent_goal_rate);
      return true; // Context suggests increased criticality
    }
    
    return false; // No context adjustment needed
  }

  /**
   * @brief Timer callback function that retrieves goal messages and processes them.
   *
   * This function is called periodically and attempts to retrieve a goal
   * message from the afferent component. If a message is received, it is
   * passed to `process_goal_data`.
   */
  void timer_callback() {
    // Get goal message from afferent component
    auto goal_msg = afferent_->get_msg<std_msgs::msg::Bool>(0);
    
    if (goal_msg) {
      RCLCPP_DEBUG(parent_->get_logger(), "[NavigationGoalCognition] Processing goal message");
      process_goal_data(goal_msg);
    }
    
    // Perform periodic cognitive maintenance
    perform_cognitive_maintenance();
  }

  /**
   * @brief Perform periodic cognitive maintenance tasks
   */
  void perform_cognitive_maintenance() {
    auto now = parent_->get_clock()->now();
    double time_since_last_check = (now - last_check_).seconds();
    
    if (time_since_last_check >= COGNITIVE_PROCESSING_INTERVAL) {
      // Perform background cognitive tasks:
      // - Clean old history
      // - Update learning models
      // - Adjust parameters
      
      cleanup_old_history(now);
      update_cognitive_parameters();
      
      RCLCPP_DEBUG(parent_->get_logger(),
                  "🧠 [Maintenance] Cognitive maintenance completed");
    }
  }

  /**
   * @brief Clean up old goal history entries
   * @param current_time Current timestamp
   */
  void cleanup_old_history(const rclcpp::Time& current_time) {
    double max_history_age = 30.0; // seconds
    
    goal_history_.erase(
      std::remove_if(goal_history_.begin(), goal_history_.end(),
        [&](const GoalEvent& event) {
          return (current_time - event.timestamp).seconds() > max_history_age;
        }),
      goal_history_.end());
  }

  /**
   * @brief Update cognitive processing parameters based on learning
   */
  void update_cognitive_parameters() {
    // Adaptive parameter adjustment based on system performance
    // This could include machine learning updates in a full implementation
    
    if (goal_history_.size() > 50) {
      // Adjust thresholds based on historical data
      double avg_criticality = calculate_average_criticality();
      
      if (avg_criticality > 0.8) {
        // High criticality environment - be more sensitive
        CRITICALITY_CONFIDENCE_THRESHOLD = std::max(0.6, CRITICALITY_CONFIDENCE_THRESHOLD - 0.05);
      } else if (avg_criticality < 0.2) {
        // Low criticality environment - be more conservative
        CRITICALITY_CONFIDENCE_THRESHOLD = std::min(0.9, CRITICALITY_CONFIDENCE_THRESHOLD + 0.05);
      }
    }
  }

  /**
   * @brief Calculate average criticality over recent history
   * @return Average criticality ratio
   */
  double calculate_average_criticality() {
    if (goal_history_.empty()) return 0.0;
    
    int critical_count = 0;
    for (const auto& goal : goal_history_) {
      if (goal.is_critical) critical_count++;
    }
    
    return static_cast<double>(critical_count) / goal_history_.size();
  }

  /**
   * @brief Configures the NavigationGoalCognition component.
   * @return True if configuration is successful.
   */
  bool configure() override {
    RCLCPP_INFO(parent_->get_logger(), "🔧 [NavigationGoalCognition] Core configured");
    
    // Load cognitive parameters from ROS parameters
    parent_->declare_parameter("cognitive_processing_interval", COGNITIVE_PROCESSING_INTERVAL);
    parent_->declare_parameter("goal_persistence_threshold", GOAL_PERSISTENCE_THRESHOLD);
    parent_->declare_parameter("criticality_confidence_threshold", CRITICALITY_CONFIDENCE_THRESHOLD);
    
    COGNITIVE_PROCESSING_INTERVAL = parent_->get_parameter("cognitive_processing_interval").as_double();
    GOAL_PERSISTENCE_THRESHOLD = parent_->get_parameter("goal_persistence_threshold").as_double();
    CRITICALITY_CONFIDENCE_THRESHOLD = parent_->get_parameter("criticality_confidence_threshold").as_double();
    
    RCLCPP_INFO(parent_->get_logger(),
               "🧠 Cognitive parameters: interval=%.2fs, persistence=%.2fs, confidence=%.2f",
               COGNITIVE_PROCESSING_INTERVAL, GOAL_PERSISTENCE_THRESHOLD, CRITICALITY_CONFIDENCE_THRESHOLD);
    
    return true;
  }

  /**
   * @brief Activates the NavigationGoalCognition component by initializing a timer.
   *
   * The timer is set to call `timer_callback` every 100 milliseconds.
   *
   * @return True if activation is successful.
   */
  bool activate() override {
    timer_ = parent_->create_wall_timer(
        100ms, std::bind(&NavigationGoalCognitiveCore::timer_callback, this));
    
    RCLCPP_INFO(parent_->get_logger(), "🟢 [NavigationGoalCognition] Core activated");
    return true;
  }

  /**
   * @brief Deactivates the NavigationGoalCognition component by disabling the timer.
   *
   * The timer is reset to null, stopping periodic message processing.
   *
   * @return True if deactivation is successful.
   */
  bool deactivate() override {
    timer_ = nullptr;
    RCLCPP_INFO(parent_->get_logger(), "🔴 [NavigationGoalCognition] Core deactivated");
    return true;
  }

private:
  /**
   * @brief Structure to store goal event history for cognitive analysis
   */
  struct GoalEvent {
    rclcpp::Time timestamp;
    bool is_critical;
    double confidence;
  };

  rclcpp::TimerBase::SharedPtr timer_; /**< Timer for periodic execution of `timer_callback`. */
  
  // Cognitive processing state
  std::vector<GoalEvent> goal_history_;
  rclcpp::Time last_check_;
  bool current_criticality_;
  
  // Cognitive parameters (adjustable)
  double COGNITIVE_PROCESSING_INTERVAL;
  double GOAL_PERSISTENCE_THRESHOLD;
  double CRITICALITY_CONFIDENCE_THRESHOLD;
};

/// Registers the NavigationGoalCognition component with the ROS 2 class loader
CS_REGISTER_COMPONENT(NavigationGoalCognitiveCore)