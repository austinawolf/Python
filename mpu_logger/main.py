from quaternion import Quaternion
from packet import Packet
from serial_interface import SerialStream

serial = SerialStream()
serial.configure()
serial.run()

f = open("orientation_data.csv","w")
f.write("event,q0,q1,q2,q3,acc_x,acc_y,acc_z,gyro_x,gyro_y,gyro_z,err_code,roll,pitch,yaw\n")
f.close()

def main():

    print("Running...")
    while(True):
        line = get_line()
        print line

        packet = Packet(line)

        if packet.status != 0: continue

        try:
            
            quat = Quaternion(packet.q0, packet.q1, packet.q2, packet.q3)
            packet.roll = quat.roll
            packet.pitch = quat.pitch
            packet.yaw = quat.yaw
            print "Roll:", packet.roll
            print "Pitch:", packet.pitch
            print "Yaw:", packet.yaw
                        
            
        except Exception:
            packet.status = -1

        f = open("orientation_data.csv","a")
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


	