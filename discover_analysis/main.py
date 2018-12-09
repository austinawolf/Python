import sys
import os
from quaternion import Quaternion

sys.path.append("/data/")

preamble = "Packet:"
QUAT = 1
IMU = 2
COMPASS = 4
RV = "RV"
EULER_CALC = 0
MAG_SAMPLER = 1

MODE = MAG_SAMPLER

def main():
    file_list = []
    
    try:
        f = open("drift.csv","r")
    except IOError:
        print "bad file name"
        sys.exit()
    try:
        g = open("euler.csv","w")
    except IOError:
        print "Couldn't create file g"
        sys.exit()
        
    sample_num = 0   
    for line in f:
        split = line.split(",")
        if len(split) != 7:
            continue
            
        data_type = split[0]
        
        if data_type == RV:
            sample_num += 1
            try:
                q0 = float(split[1])
                q1 = float(split[2])
                q2 = float(split[3])
                q3 = float(split[4])
                
            except Exception:
                print_line_error("Can't convert quat")                
                continue
                          
            quat = Quaternion(q0,q1,q2,q3)           
            g.write(str(sample_num) + "," + str(quat) + "\n")    
                    
   
    f.close()
    g.close()
    print "Done"

def print_line_error(msg):
    print "Line Error: ", msg


    
main()