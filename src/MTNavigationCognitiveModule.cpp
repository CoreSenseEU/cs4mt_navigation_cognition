#include "cs4home_core/CognitiveModule.hpp"
#include "rclcpp/rclcpp.hpp"
#include "rclcpp_lifecycle/lifecycle_node.hpp"

class MTNavigationCognitiveModule : public cs4home_core::CognitiveModule {
public:
  explicit MTNavigationCognitiveModule(
      const rclcpp::NodeOptions &options = rclcpp::NodeOptions())
      : cs4home_core::CognitiveModule("mt_navigation_cognitive_module", options) {
    RCLCPP_INFO(this->get_logger(), "Navigation Cognitive module for MT - initialized");
  }
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  auto node = std::make_shared<MTNavigationCognitiveModule>();
  rclcpp::spin(node->get_node_base_interface());
  rclcpp::shutdown();
  return 0;
}
