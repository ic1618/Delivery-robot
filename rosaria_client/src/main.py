from logging import raiseExceptions
import rospy
import actionlib
import tf
from geometry_msgs.msg import Point, Pose, Twist, Vector3, Quaternion
from move_base_msgs.msg import MoveBaseAction, MoveBaseGoal
from tf.transformations import quaternion_from_euler
from math import pi, atan2

# speech
import speech_recognition as sr
import pyttsx3
import os
import time
from random import randint
import smtplib, ssl

class Pipeline:
    def __init__(self):
        self.cord = None
        self.goal = None
        self.quaternion = None
        self.trans = None
        self.rot = None
        self.loop_rate = rospy.Rate(30)
        self.twist_forward = Twist(Vector3(0.50, 0.00, 0.00), Vector3(0.00, 0.00, 0.00))
        self.twist_rotate = Twist(Vector3(0.00, 0.00, 0.00), Vector3(0.00, 0.00, 15 * pi / 180))
        self.twist_rotate_anti = Twist(Vector3(0.00, 0.00, 0.00), Vector3(0.00, 0.00, -15 * pi / 180))
        self.twist_stop = Twist(Vector3(0.00, 0.00, 0.00), Vector3(0.00, 0.00, 0.00))
        self.move_base = actionlib.SimpleActionClient("move_base", MoveBaseAction)
        rospy.Subscriber('/OAKD/CloestPerson3D', Point, self.callback_spatialCord)
        self.pub_cmd_vel = rospy.Publisher(
            'RosAria/cmd_vel',
            Twist,
            queue_size=1000
        )
        self.listener = tf.TransformListener()

        # speech
        self.tts_engine= pyttsx3.init()
        self.email_to='catalin_receiver1234@gmail.com'
        #self.email_to='icatalincraciun@gmail.com'
        #self.email_to='yw14218@ic.ac.uk'
        self.secret_code = self.generate_password_and_email()
        self.recipient_person_found = False
	
            
    def callback_spatialCord(self, data):
        self.cord = data

    def goal_pose(self):
        goal_pose = MoveBaseGoal()
        goal_pose.target_pose.header.frame_id = 'map'
        goal_pose.target_pose.header.stamp = rospy.Time.now()

        self.listener.waitForTransform('/OAK_D_link','/map',rospy.Time(), rospy.Duration(10.0))
        try:
             (self.trans, self.rot) = self.listener.lookupTransform('/OAK_D_link', 'map', rospy.Time(0))
        except (tf.LookupException, tf.ConnectivityException, tf.ExtrapolationException):
             print("tf error")
            
        print("camera to map translation: ", self.trans)
        print("camera to map rotation: ", self.rot)
        self.goal = Point(self.cord.z + self.trans[0], self.cord.x + self.trans[1], self.trans[2]) 
        x, y, z, w = quaternion_from_euler(0, 0, atan2(self.cord.z, self.cord.x)).tolist()
        self.quaternion = Quaternion(x + self.rot[0], y + self.rot[1], z + self.rot[2], w + self.rot[3])
        goal_pose.target_pose.pose = Pose(self.goal, self.quaternion)
        print(goal_pose)
        return goal_pose

    def rotate_clockwise(self):
        self.pub_cmd_vel.publish(self.twist_rotate)
        
    def rotate_anticlockwise(self):
        self.pub_cmd_vel.publish(self.twist_rotate_anti)

    def stop_robot(self):
        self.pub_cmd_vel.publish(self.twist_stop)
        
    def drive_forward(self):
        self.pub_cmd_vel.publish(self.twist_forward)
        
    def drive(self):
        goal_pose = MoveBaseGoal()
        goal_pose.target_pose.header.frame_id = 'map'
        goal_pose.target_pose.header.stamp = rospy.Time.now()
        point = Point(15.441, -1.106, 0.00)
        quaternion = Quaternion(0.0, 0.0, 0.0, 1.0)
        goal_pose.target_pose.pose = Pose(point, quaternion)
        self.tts_engine.say("Greeting human, I am now going to demonstrate social navigation!")
        self.tts_engine.runAndWait()
        self.move_base.send_goal(goal_pose)
        self.move_base.wait_for_result()
        
    def find_person(self):
        person_done = False
        self.tts_engine.say("Greeting human, I am now going to find a person!")
        self.tts_engine.runAndWait()
        while not person_done:
            if self.cord is not None:
                self.tts_engine.say("Greeting human, I have found a person, I am now going to face towards you!")
                self.tts_engine.runAndWait()
                while abs(self.cord.x) > 0.1:
                    if self.cord.x > 0:
                        self.rotate_anticlockwise()
                    else:
                        self.rotate_clockwise()
                self.stop_robot()
                self.tts_engine.say("Greeting human, I believe you are now infront of me, I am now going to deliver your food!")
                self.tts_engine.runAndWait()
                while abs(self.cord.z > 0.9):
                    if self.cord is None:
                        self.stop_robot()
                    self.drive_forward()
                self.stop_robot()
                self.recipient_person_found = self.encountered_person_pipeline()
                person_done = True
            else:
                self.rotate_anticlockwise()
                             
        
    def start(self):        
        while not rospy.is_shutdown() or self.recipient_person_found == False:
        
            if self.cord is not None and self.cord.z > 0.5:
                self.stop_robot()
                # self.move_base.wait_for_server()
                goal = self.goal_pose()
                self.move_base.send_goal(goal)
                print("-----Approaching a person-----")
                self.move_base.wait_for_result()   
                print("-----Approached a person-----")
                # invoking ros speech service
                for i in range (3):
                    self.stop_robot()
                self.recipient_person_found = self.encountered_person_pipeline()
                self.cord = None
                
            else:          
                #print("-----Rotating the robot-----")
                #self.rotate_clockwise()
                pass
            self.loop_rate.sleep()
   
    def generate_password_and_email(self):

        secret_code = randint(1000, 9999)     # randint is inclusive at both ends
        email_from = 'catalin_sender1234@gmail.com'
        password = 'myzwe9-ruxMut-qosbap'

        # Connect to Gmail's SMTP Outgoing Mail server with such context
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            # Provide Gmail's login information
            smtp.ehlo()
            smtp.starttls()
            smtp.ehlo()
            smtp.login(email_from, password)
            # Send mail with from_addr, to_addrs, msg, which were set up as variables above
            subject = "Your online order is on the way!"
            body = f"Thanks for your online order. Your secret code to receive the package is {secret_code}"
            email_string = f'Subject: {subject}\n\n {body}'

            smtp.sendmail(email_from, self.email_to, email_string)
            return secret_code
    
    def speech_detection(self, password_detection_mode):

        recogniser = sr.Recognizer()
        #The engine for the text to speech...
        #https://stackoverflow.com/questions/65660897/pyttsx3-unknown-voice-id
        #voices = tts_engine.getProperty('voices')
        if password_detection_mode == True:
            self.tts_engine.say("Greeting human, please let me know the secret password to prove you are the intended receipient.")
            self.tts_engine.runAndWait()
        else:
            #self.tts_engine.say("Greeting human, please let me know your answer.")
            #self.tts_engine.runAndWait()
            pass

        try:
            with sr.Microphone() as mic:
                recogniser.adjust_for_ambient_noise(mic,duration=0.2)
                audio=recogniser.listen(mic)

                detected_speech = recogniser.recognize_google(audio)
                detected_speech = detected_speech.lower()

                print(f"Detected speech: {detected_speech}")
                return detected_speech
                
        except sr.UnknownValueError():
            recogniser = sr.Recognizer()
                
        return detected_speech
    
    def encountered_person_pipeline(self):

        encountered_person_password_attempt = self.speech_detection(password_detection_mode=True)
        recipient_person_found = False
        if encountered_person_password_attempt == str(self.secret_code):
            self.tts_engine.say("You are the intended recipient, here is your package!")
            self.tts_engine.runAndWait()
            recipient_person_found = True
        else:
            self.tts_engine.say("Incorrect password, please try again")
            self.tts_engine.runAndWait()
            time.sleep(1)

            answer = self.speech_detection(password_detection_mode=False)
            if answer == str(self.secret_code):
                    self.tts_engine.say("You are the intended recipient, here is your package!")
                    self.tts_engine.runAndWait()
                    recipient_person_found = True
            else:
                self.tts_engine.say("Incorrect again, please leave the room!")
                self.tts_engine.runAndWait()
                time.sleep(5)

        return recipient_person_found
        
if __name__ == '__main__':
    rospy.init_node('main', anonymous=True)
    pipeline = Pipeline()
    pipeline.drive()
    while pipeline.recipient_person_found is not True:
    	pipeline.find_person()
    if pipeline.recipient_person_found == True:
        print("Pipiline finishes, aborted.")
    
