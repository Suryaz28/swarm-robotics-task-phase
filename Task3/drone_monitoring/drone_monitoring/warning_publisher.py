"""Convert each received status into a warning message."""
import rclpy
from rclpy.node import Node
from std_msgs.msg import String

def warnings_for(status):
    if status == 'NORMAL':
        return 'No active warnings'
    if status == 'WAITING FOR SENSOR DATA':
        return 'Waiting for telemetry'
    known = {'LOW BATTERY': 'Battery level is critically low!',
             'OVERHEATING': 'Drone temperature exceeds safe limit!',
             'ALTITUDE LIMIT EXCEEDED': 'Drone altitude exceeded the configured limit!'}
    parts = [part.strip() for part in status.split(',')]
    return '\n'.join('[WARNING] ' + known.get(part, 'Unknown status: ' + part) for part in parts)

class WarningPublisher(Node):
    def __init__(self):
        super().__init__('drone_warning_publisher')
        self.publisher = self.create_publisher(String, '/drone/warnings', 10)
        self.subscription = self.create_subscription(String, '/drone/status', self.handle_status, 10)

    def handle_status(self, msg):
        warning = warnings_for(msg.data)
        output = String()
        output.data = warning
        self.publisher.publish(output)
        self.get_logger().info(warning)

def main(args=None):
    rclpy.init(args=args)
    node = WarningPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
