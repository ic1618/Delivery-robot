import rospy
from geometry_msgs.msg import Point

def callback(data):
    print(type(data))
    print(data.x)
    print(data.y)
    print(data.z)

 
if __name__ == '__main__':
	print ('main start')
	while not rospy.is_shutdown():
            rospy.init_node('listener', anonymous=True)
            rospy.Subscriber('/OAKD/CloestPerson3D', Point, callback)
            rospy.spin()
