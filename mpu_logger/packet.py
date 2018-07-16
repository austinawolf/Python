class Packet():


    def __init__(self, line):

        #init variables
        self.event_num = None
        self.q0 = None
        self.q1 = None
        self.q2 = None
        self.q3 = None
        self.acc_x = None
        self.acc_y = None
        self.acc_z = None
        self.gyro_x = None
        self.gyro_y = None
        self.gyro_z = None
        self.err_code = None
        self.roll = None
        self.pitch = None
        self.yaw = None
        self.status = -1
	
        #check for packet header
        if "Packet:" not in line:
            self.status = -2
            return
		
        #remove header and split up data into list
        data = line.replace("Packet:","").replace("\r","").replace("\n","")
        split = data.split(",")
		
        #check for list length
        if len(split) != 12:
            self.status = -3
            return
		
		#try to convert string to proper types and store
        try:
            self.event_num = int(split[0])
            self.q0 = int(split[1])
            self.q1 = int(split[2])
            self.q2 = int(split[3])
            self.q3 = int(split[4])
            self.acc_x = int(split[5])
            self.acc_y = int(split[6])
            self.acc_z = int(split[7])
            self.gyro_x = int(split[8])
            self.gyro_y = int(split[9])
            self.gyro_z = int(split[10])
            self.err_code = int(split[11])
       
        except Exception as ex:
            print ex
            self.status = -4
            return
        
        self.status = 0
        return
		
    def __str__(self):
        return  str(self.event_num) + "," \
                + str(self.q0) + "," \
                + str(self.q1) + "," \
                + str(self.q2) + "," \
                + str(self.q3) + "," \
                + str(self.acc_x) + "," \
                + str(self.acc_y) + "," \
                + str(self.acc_z) + "," \
                + str(self.gyro_x) + "," \
                + str(self.gyro_y) + "," \
                + str(self.gyro_z) + "," \
                + str(self.err_code) + "," \
                + str(self.roll) + "," \
                + str(self.pitch) + "," \
                + str(self.yaw) + "," \
                + str(self.status) + "," \
                + "\n"					
					