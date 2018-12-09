import sys
import os
from quaternion import Quaternion

sys.path.append("/data/")

preamble = "Packet:"
QUAT = 1
IMU = 2
COMPASS = 4

EULER_CALC = 0
MAG_SAMPLER = 1

MODE = MAG_SAMPLER

def main():
    file_list = []
    
    try:        
        if MODE == EULER_CALC:    
            f = open("data_log_auto_cal.csv","r")
            file_list.append(f)
            
        elif MODE == MAG_SAMPLER:        
            path = os.getcwd() + "/data2/"
            dirs = os.listdir( path )
            for file in dirs:               
                file_list.append(path + file)

    except IOError:
        print "bad file name"
        sys.exit()
    
    try:        
        if MODE == EULER_CALC:    
            g = open("euler.csv","w")
        elif MODE == MAG_SAMPLER:
            g = open("mag_data_out.csv","w")

    except IOError:
        print "Couldn't create file g"
        sys.exit()
    
    compass_sample_num = 0
    
    for file in file_list:
        print file
        f = open(file,"r")
        
        i = 0
        for line in f:
            
            if i == 0:
                distance = float(line.replace("\n","").replace(",",""))
                i=1
                continue
                
            split = line.split(",")
            
            if len(split) < 5:
                print_line_error("bad length")
                continue
                
            if preamble not in split[0]:
                print_line_error("bad preamble")        
                continue
                
            packet_num = split[0].replace(preamble,"")
            
            try:
                data_type = int(split[1])
            except Exception:
                print_line_error("data type not int")                
                continue
                
            if data_type == QUAT:
            
                try:
                    q0 = int(split[2])
                    q1 = int(split[3])
                    q2 = int(split[4])
                    q3 = int(split[5])
                    
                except Exception:
                    print_line_error("Can't convert quat")                
                    continue
                              
                quat = Quaternion(q0,q1,q2,q3)
                
                if MODE == EULER_CALC:    
                    g.write(str(packet_num) + "," + str(quat) + "\n")    
                    
            elif data_type == IMU:

                try:
                    gx = int(split[2])
                    gy = int(split[3])
                    gz = int(split[4])
                    ax = int(split[5])
                    ay = int(split[6])
                    az = int(split[7]) 
                    
                except Exception:
                    print_line_error("Can't convert IMU")                
                    continue

            
            elif data_type == COMPASS:
                compass_sample_num+=1
                try:
                    cx = int(split[2])
                    cy = int(split[3])
                    cz = int(split[4])
                                   
                except Exception:
                    print_line_error("Can't convert Compass")                
                    continue       
            
                if MODE == MAG_SAMPLER:
                    g.write(str(compass_sample_num) + "," + str(distance) + "," + str(cx) + "," + str(cy) + "," + str(cz) + "\n")

        f.close()

    g.close()
    print "Done"

def print_line_error(msg):
    print "Line Error: ", msg


    
main()