import os
import numpy as np
import matplotlib.pyplot as plt

#define
SUCCESS = 0
ERROR = -1
ON = 1
OFF = 0
A_to_mA = 1000
us_to_s = 1/1000000.0
mV_to_V = 1/1000.0
#config
ch1_offset = 0.036
r1 = 10.0
threshold = 1.5
Vdd = 3.21

def main():
    local_file_list = os.listdir(os.getcwd())
    for filename in local_file_list:
        
        ret, name, sample_rate, conn_interval, number = get_experiment_info(filename)
        if (ret == ERROR):
            continue
            
        experiment = Experiment(name, sample_rate, conn_interval, number)
        try:
            f = open(filename,"r")
            line1 = f.readline()
            line2 = f.readline()
            line3 = f.readline()
            
            for line in f:
                ret, sample = line_to_sample(line)
                
                if ret == ERROR:
                    print "Sample Error"
                    continue
                experiment.append(sample)
                
            f.close()
        except IOError:
            print "File Error"
            continue
    
        experiment.calc_statistics()
        experiment.plot()
        
    
class Sample:

    def __init__(self, _timestamp, _current, _cpu_status, _sample_num):
        self.timestamp = _timestamp
        self.current = _current
        self.cpu_status = _cpu_status
        self.sample_num = _sample_num
        self.power = _current * Vdd
        

class Experiment:

    def __init__(self, _name, _sample_rate, _conn_interval, _number):
        self.name = _name
        self.sample_rate = _sample_rate
        self.conn_interval = _conn_interval
        self.number = _number
        self.sample_list = []
        print "Experiment: " + self.name,
        print "Sample Rate (Hz): " + str(self.sample_rate),
        print "Number: " + str(self.number),
        print "Conn. Interval: " + str(self.conn_interval)
    
    
    def append(self, sample):
        self.sample_list.append(sample)
        
    def calc_statistics(self):
        self.total_samples = 0
        self.total_energy = 0
        self.time_elapsed = 0
        self.cpu_util_sum = 0.0
        self.current_sum = 0.0
        
        for sample in self.sample_list:
            
            self.total_samples += 1
            
            #energy calc
            self.time_elapsed += sample.timestamp
            self.current_sum += sample.current
            self.total_energy += sample.power * sample.timestamp
            
            #cpu util
            self.cpu_util_sum += sample.cpu_status 
            
        
        self.cpu_util = self.cpu_util_sum / self.total_samples
        self.current_mean = self.current_sum / self.total_samples
        
        print "Total Samples: ", self.total_samples
        print "Time Elapsed(s): ", self.time_elapsed
        print "CPU Util: ", self.cpu_util
        print "Current Mean (mA): ", self.current_mean * A_to_mA

    def plot(self):

        sample_time_list = []
        sample_power_list = []
        sample_cpu_status_list = []
        
        plot_start = 0
        plot_end = 1000
        
        sample_time_current = 0.0
        for sample in self.sample_list:
            
            sample_time_list.append(sample_time_current*1000)
            sample_power_list.append(sample.power*1000)
            sample_cpu_status_list.append(sample.cpu_status)
                       
            sample_time_current += sample.timestamp

            
    
        fig, ax1 = plt.subplots()
        t = sample_time_list[plot_start:plot_end]
        y1 = sample_power_list[plot_start:plot_end]
        y2 = sample_cpu_status_list[plot_start:plot_end]
       
        ax1.plot(t, y1, 'b-')
        ax1.set_xlabel('time (ms)')
        # Make the y-axis label, ticks and tick labels match the line color.
        ax1.set_ylabel('Power (mW)', color='b')
        ax1.tick_params('y', colors='b')

        ax2 = ax1.twinx()
        ax2.plot(t, y2, 'r-')
        ax2.set_ylabel('CPU Status', color='r')
        ax2.tick_params('y', colors='r')
        ax2.set_ylim([-1,20])
        fig.tight_layout()
        
        mu = -0.41
        median = -0.81
        sigma = 29.64
        
        textstr = '\n'.join((
            r'$CPU\ Util=%.2f $' % (self.cpu_util, ),
            r'$Average\ Current=%.2f\ mA$ ' % (self.current_mean * A_to_mA, ),
            r'$Average\ Power=%.2f\ mW$ ' % (self.current_mean * A_to_mA * Vdd, )))
            
        props = dict(boxstyle='round', facecolor='wheat', alpha=0.5) 
            
        ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=14,
            verticalalignment='top', bbox=props)        
        
        plt.yticks([OFF,ON], ['OFF', 'ON'])
        plt.title('Power Analysis at ' + str(self.sample_rate) + " Hz / " + str(self.conn_interval) + " ms Connection Interval")
        plt.show()

def get_experiment_info(filename):
    if ".txt" not in filename:
        return ERROR, None, None, None, None
    filename = filename.replace(".txt","")
    split = filename.split("_")
    
    if len(split) != 4:
        return ERROR, None, None, None, None
        
    name = split[0]
    
    sample_rate_string = split[1]
    if "hz" not in split[1]:
        return ERROR, None, None, None, None
    sample_rate = int(sample_rate_string.replace("hz",""))
    
    conn_interval_string = split[2]
    if "ms" not in split[2]:
        return ERROR, None, None, None, None
    conn_interval = int(conn_interval_string.replace("ms",""))    
    
    number = int(split[3])
    
    return SUCCESS, name, sample_rate, conn_interval, number
    
    
def line_to_sample(line):
    split = line.split("\t")
    if len(split) != 6:
        return ERROR, None

    #timestamp
    timestamp_string = split[0]
    if "us" not in timestamp_string:
        return ERROR, None
    timestamp = float(timestamp_string.replace("us","").replace(" ","")) * us_to_s

    #ch1
    ch1_string = split[1]
    if "mV" in ch1_string:
        ch1 = float(split[1].replace("mV","")) * mV_to_V - ch1_offset
    elif "V" in ch1_string:
        ch1 = float(split[1].replace("V","")) - ch1_offset
    else:
        return ERROR, None
        
    current = ch1 / r1
    
    #ch2
    ch2_string = split[2]
    if "mV" in ch2_string:
        ch2 = float(ch2_string.replace("mV","")) * mV_to_V
    elif "V" in ch2_string:
        ch2 = float(ch2_string.replace("V",""))
    else:
        return ERROR, None
        
    if ch2 > threshold:
        cpu_status = OFF
    else:
        cpu_status = ON
    
    #sample number
    sample_num = int(split[5].replace("\n",""))
    
    sample = Sample(timestamp, current, cpu_status, sample_num)
    return SUCCESS, sample
    
main()    