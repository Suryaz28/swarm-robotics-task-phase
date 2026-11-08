"""Publish simulated telemetry at 1 Hz; parameters enable repeatable tests."""
import math
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

class SensorPublisher(Node):
    def __init__(self):
        super().__init__('drone_sensor_publisher')
        self.declare_parameter('initial_altitude', 15.0)
        self.declare_parameter('initial_battery', 100.0)
        self.declare_parameter('initial_temperature', 35.0)
        self.declare_parameter('vary_readings', True)
        self.altitude = float(self.get_parameter('initial_altitude').value)
        self.battery = min(100.0, max(0.0, float(self.get_parameter('initial_battery').value)))
        self.temperature = float(self.get_parameter('initial_temperature').value)
        self.vary = self.get_parameter('vary_readings').value
        self.tick = 0
        self.publishers_ = {name: self.create_publisher(Float32, '/drone/' + name, 10)
                            for name in ('altitude', 'battery', 'temperature')}
        self.timer = self.create_timer(1.0, self.publish_readings)

    def publish_readings(self):
        self.tick += 1
        if self.vary:
            altitude = max(0.0, self.altitude + 5.0 * math.sin(self.tick / 8.0))
            battery = max(0.0, self.battery - 0.1 * self.tick)
            temperature = self.temperature + 3.0 * math.sin(self.tick / 10.0)
        else:
            altitude, battery, temperature = self.altitude, self.battery, self.temperature
        for name, value in (('altitude', altitude), ('battery', battery), ('temperature', temperature)):
            msg = Float32()
            msg.data = float(value)
            self.publishers_[name].publish(msg)
        self.get_logger().info(f'Altitude: {altitude:.1f} m | Battery: {battery:.1f}% | Temperature: {temperature:.1f} C')

def main(args=None):
    rclpy.init(args=args)
    node = SensorPublisher()
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
