"""Collect readings and report all active limit violations."""
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32, String

def classify(altitude, battery, temperature):
    if any(value is None for value in (altitude, battery, temperature)):
        return 'WAITING FOR SENSOR DATA'
    problems = []
    if battery < 20.0:
        problems.append('LOW BATTERY')
    if temperature > 60.0:
        problems.append('OVERHEATING')
    if altitude > 30.0:
        problems.append('ALTITUDE LIMIT EXCEEDED')
    return ', '.join(problems) if problems else 'NORMAL'

class TelemetryMonitor(Node):
    def __init__(self):
        super().__init__('drone_telemetry_monitor')
        self.values = {'altitude': None, 'battery': None, 'temperature': None}
        self.subscriptions_ = [self.create_subscription(Float32, '/drone/' + name,
                               lambda msg, key=name: self.update(key, msg.data), 10)
                               for name in self.values]
        self.status_pub = self.create_publisher(String, '/drone/status', 10)
        self.timer = self.create_timer(1.0, self.publish_status)

    def update(self, name, value):
        self.values[name] = value

    def publish_status(self):
        a, b, t = (self.values[k] for k in ('altitude', 'battery', 'temperature'))
        status = classify(a, b, t)
        if status == 'WAITING FOR SENSOR DATA':
            self.get_logger().info(status)
        else:
            self.get_logger().info(f'Drone Telemetry | Altitude: {a:.1f} m | Battery: {b:.1f}% | Temperature: {t:.1f} C | Status: {status}')
        msg = String()
        msg.data = status
        self.status_pub.publish(msg)

def main(args=None):
    rclpy.init(args=args)
    node = TelemetryMonitor()
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
