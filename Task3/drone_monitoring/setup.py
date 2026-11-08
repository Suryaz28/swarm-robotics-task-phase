from setuptools import setup

package_name = 'drone_monitoring'
setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Task phase participant',
    maintainer_email='maintainer@example.com',
    description='Simulated drone telemetry and warnings',
    license='Apache-2.0',
    entry_points={'console_scripts': [
        'drone_sensor_publisher = drone_monitoring.sensor_publisher:main',
        'drone_telemetry_monitor = drone_monitoring.telemetry_monitor:main',
        'drone_warning_publisher = drone_monitoring.warning_publisher:main',
    ]},
)
