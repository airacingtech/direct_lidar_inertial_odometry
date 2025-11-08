# launch/bringup_all.launch.py
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare

def generate_launch_description():
    pkg_dlio = FindPackageShare('direct_lidar_inertial_odometry')

    # Paths to your existing config files
    dlio_yaml_path = PathJoinSubstitution([pkg_dlio, 'cfg', 'dlio.yaml'])
    dlio_params_yaml_path = PathJoinSubstitution([pkg_dlio, 'cfg', 'params.yaml'])
    rviz_cfg = PathJoinSubstitution([pkg_dlio, 'launch', 'dlio.rviz'])

    # Launch arguments (override on the command line if needed)
    rviz = LaunchConfiguration('rviz')
    pointcloud_topic = LaunchConfiguration('pointcloud_topic')
    imu_topic = LaunchConfiguration('imu_topic')
    baselink_frame = LaunchConfiguration('baselink_frame')
    imu_frame = LaunchConfiguration('imu_frame')
    lidar_frame = LaunchConfiguration('lidar_frame')
    publish_map_odom = LaunchConfiguration('publish_map_odom')

    return LaunchDescription([
        DeclareLaunchArgument('rviz', default_value='true', description='Launch RViz2'),
        DeclareLaunchArgument('pointcloud_topic', default_value='points_raw'),
        DeclareLaunchArgument('imu_topic', default_value='imu_raw'),
        DeclareLaunchArgument('baselink_frame', default_value='base_link'),
        DeclareLaunchArgument('imu_frame', default_value='imu_link'),
        DeclareLaunchArgument('lidar_frame', default_value='lidar_link'),
        DeclareLaunchArgument('publish_map_odom', default_value='true'),
        

        # ---------------- DLIO nodes ----------------
        Node(
            package='direct_lidar_inertial_odometry',
            executable='dlio_odom_node',
            output='screen',
            parameters=[dlio_yaml_path, dlio_params_yaml_path],
            remappings=[
                ('pointcloud', pointcloud_topic),
                ('imu', imu_topic),
                ('odom', 'dlio/odom_node/odom'),
                ('pose', 'dlio/odom_node/pose'),
                ('path', 'dlio/odom_node/path'),
                ('kf_pose', 'dlio/odom_node/keyframes'),
                ('kf_cloud', 'dlio/odom_node/pointcloud/keyframe'),
                ('deskewed', 'dlio/odom_node/pointcloud/deskewed'),
            ],
        ),
        Node(
            package='direct_lidar_inertial_odometry',
            executable='dlio_map_node',
            output='screen',
            parameters=[dlio_yaml_path, dlio_params_yaml_path],
            remappings=[
                ('keyframes', 'dlio/odom_node/pointcloud/keyframe'),
            ],
        ),

        # ---------------- RViz ----------------
        Node(
            package='rviz2',
            executable='rviz2',
            name='dlio_rviz',
            arguments=['-d', rviz_cfg],
            output='screen',
            condition=IfCondition(rviz)
        ),

        #------------GPS------------------
        Node(
            package='lidar_retime',
            executable='gps_pose_to_path',
            name='gps_pose_to_path',
            output='screen',
            parameters=[{
                'pose_topic': '/gps/pose',      
                'path_topic': '/gps/path',
                'fixed_frame': 'odom'
            }],
        ),


    ])
