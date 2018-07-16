from serial_interface import SerialStream



serial = SerialStream()
serial.configure()
serial.run()

def main():

	good_packets = 0
	bad_packets = 0

	packet = get_packet()
	
	if packet == -1:
		print str(packet)
		exit()
	else:
		previous_event_number = get_event_number(packet)

	while(True):
		packet = get_packet()
		
		if packet == -1:
			#bad 
			previous_event_number+=1
			continue
		else:
			event_number = get_event_number(packet)
				

		if event_number == previous_event_number + 1:
			good_packets+=1
		else:
			bad_packets += event_number - previous_event_number -1
			good_packets+=1
			
		previous_event_number = event_number
		
		print "Good: " + str(good_packets) + ", Bad:" + str(bad_packets)
		print "Packet Loss:" + str(calc_packet_loss(good_packets,bad_packets))
		

def get_event_number(packet):
	return int(packet[1])
        
def get_packet():
	line = serial.readStream().replace('\r','')
	packet = line.split(",")
	if len(packet) != 2:
		return -1
	elif packet[0] != "Packet Number":
		return -1	
	return packet

def calc_packet_loss(good,bad):
	return float(bad)/float(good+bad)
main()

