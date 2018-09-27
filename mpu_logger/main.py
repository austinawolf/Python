from quaternion import Quaternion
from packet import Packet
from serial_interface import SerialStream
from datetime import datetime 
import math
serial = SerialStream()
serial.configure()
serial.run()



def main():
    #Get Experiment Details
    experiment_name = raw_input("Experiment Name:")
    experiment_num = raw_input("Experiment Num:")

    #Create File
    filename = experiment_name + "_" + str(experiment_num) + ".csv"
    f = open(filename,"a")

    #Write Header
    f.write("Experiment Name,")
    f.write(experiment_name)
    f.write("\n")
    f.write("Experiment Number,")
    f.write(str(experiment_num))  
    f.write("\n")
    f.write("Date/Time,")
    f.write(str(datetime.now()))
    f.write("\n")    
    f.write("event,timestamp,q0,q1,q2,q3,acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z,err_code,roll,pitch,yaw,Sensor ID, status\n")

    
    f.close()

    raw_input("Press Enter when ready.")

    
    print("Running...")
    while(True):
        line = get_line()
        #print line

        packet = Packet(line)

        if packet.status != 0:
            continue

        packet.mag_mag = math.sqrt(math.pow(packet.mag_x,2) + math.pow(packet.mag_y,2) +  math.pow(packet.mag_z,2))
    
        try:
            
            quat = Quaternion(packet.q0, packet.q1, packet.q2, packet.q3)
            packet.roll = quat.roll
            packet.pitch = quat.pitch
            packet.yaw = quat.yaw
            print ("Roll: %6.2f," % (packet.roll)),
            print ("Pitch: %6.2f," % (packet.pitch)),
            print ("Yaw: %6.2f," % (packet.yaw)),
            print ("Field Strength: %6.2f" % packet.mag_mag)
                        
            
        except Exception as e:
            packet.status = -1
            print e
        f = open(filename,"a")
        f.write( str(packet) )
        f.close()

def get_line():
    while(True):
        line = serial.readStream()
        if line != "": return line

def roll(q0,q1,q2,q3):
        phi = math.atan2(2*(q0*q1 + q2*q3), 1 - 2 * (q1*q1 + q2*q2))
        return phi
        

def pitch(q0,q1,q2,q3):
        theta = math.asin(2*(q0*q2 - q3*q1))
        return theta

def yaw(q0,q1,q2,q3):
        psi = math.atan2(2*(q0*q3 + q1*q2), 1 - 2 * (q2*q2 + q3*q3))
        return psi		
		
main()


	