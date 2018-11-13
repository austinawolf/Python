import sys



def main():
    global clock
    
    input_file, scheduler, energy_efficent = get_args()
    print "Input File: ", input_file
    print "Scheduler: ", scheduler
    print "Energy Efficient: ", energy_efficent
    
    #open file
    try:
        f = open(input_file,"r")
       
    except IOError:
        print_error("invalid input file")
    
    #import scheduling params
    params = Params(f.readline())
    task_list = []
    for i in range(params.num_of_tasks):
        task_list.append(RM_Task(f.readline()))
        
    #done with file
    f.close()
    
    #verify task data import
    print params
    for task in task_list:
        print task

    release_list = task_list
    suspended_list = []
    schedule_list = []
    
    
    clock = 0
    
    #find next task to schedule
    release_list.sort()
    active_task = release_list.pop()
    print "\tNext Task: ", active_task.name

    #select freq
    freq = 1188
    
    #schdule next task
    active_task.schedule(freq)
    schedule_list.append(Schedule(active_task, 1188))    
    
    while (clock < params.total_exec_time):
    
        print "Clock = ", clock
        
        #check if any tasks are ready
        for task in suspended_list:
            if task.is_ready():
                suspended_list.remove(task)
                release_list.append(task)
                print "\tReleasing Task: ", active_task.name
            
                
        #check if active task is done
        if (active_task.is_done()):

            active_task.suspend()
            if (task.name != " Idle"):
                suspended_list.append(active_task)
            else:
                print "Idle Done"
            print "\tSuspending Task: ", active_task.name                

            #find next task to schedule
            if release_list:
            
                release_list.sort()
                active_task = release_list.pop()
                
                #select freq
                freq = 1188
                
  
                
            else:
                
                active_task = Idle_Task(suspended_list)

            #schdule next task
            active_task.schedule(freq)
            schedule_list.append(Schedule(active_task, 1188))  

                
                
                              
            print "\tNext Task: ", active_task.name
            


        #execute task    
        active_task.execute()
           
    
    

            
        clock+=1
        
   
    for schedule in schedule_list:
        print schedule      

def get_args():

    if (len(sys.argv) == 3):

        input_file = sys.argv[1]
        
        if ( sys.argv[2] == "RM" ):
            scheduler = "RM"
        elif ( sys.argv[2] == "EDF" ):
            scheduler = "EDF"        
        else:
            print_error("Invalid Arg")
      
        energy_efficient = False
        
    elif (len(sys.argv) == 4):

        input_file = sys.argv[1]
       
        if ( sys.argv[2] == "RM" ):
            scheduler = "RM"
        elif ( sys.argv[2] == "EDF" ):
            scheduler = "EDF"        
        else:
            print_error("Invalid Arg")
       
        if ( sys.argv[3] == "EE" ):
            energy_efficient = True
        else:
            energy_efficient = False       
            
    else:
        print_error("Invalid Arg")
 
    return input_file, scheduler, energy_efficient

class Schedule:

    def __init__(self, task, freq):
        global clock
        self.init_time = clock
        self.task = task
        self.freq = freq
        self.exec_time = task.WCET_1188
        self.energy_use = 0
    
    def __str__(self):
        return str(self.init_time) + "\t" \
               + str(self.task.name) + "\t" \
               + str(self.freq) + "\t" \
               + str(self.exec_time) + "\t" \
               + str(self.energy_use)
               
               
               
class Params:
        
    def __init__(self, file_line):
    
        split = file_line.replace("\n","").split(" ")
        if (len(split) < 7):
            print_error("bad file (line 1)")
            
        self.num_of_tasks =     int( split[0] )
        self.total_exec_time =  int( split[1] )
        self.power_1188 =       int( split[2] )
        self.power_918 =        int( split[3] )
        self.power_648 =        int( split[4] )
        self.power_384 =        int( split[5] )    
        self.power_idle =       int( split[6] )   
        
    def __str__(self):
    
        return "Number of Tasks: " + str(self.num_of_tasks) \
               + "\nExecution time: " + str(self.total_exec_time) \
               + "\nPower Consumption: " \
               + str(self.power_1188) + ", " \
               + str(self.power_918) + ", "  \
               + str(self.power_648) + ", " \
               + str(self.power_384) + ", "  \
               + str(self.power_idle) + "\n" \
    
class Task:

    def __init__(self, file_line):

    
    
        split = file_line.replace("\n","").split(" ")
        if (len(split) < 6):
            print split
            print_error("bad file")
            
        self.name = split[0]           
        self.period =       int( split[1] )
        self.WCET_1188 =    int( split[2] )
        self.WCET_918 =     int( split[3] )
        self.WCET_648 =     int( split[4] )
        self.WCET_384 =     int( split[5] )
        self.release_time = 0
        self.deadline = 0
    
    def schedule(self, freq):
        global clock
        self.execution = self.WCET_1188
        self.deadline = clock + self.period
    
    def execute(self):
        self.execution -=1 
    
    def suspend(self):
        global clock
        self.release_time += self.period
        
    def is_ready(self):
        global clock
        
        if (clock >= self.release_time):
            return True
        else:
            return False
    
    def is_done(self):
        
        if self.execution == 0:
            return True
        else:
            return False
    
    def __str__(self):
    
        return "Task: " + self.name \
               + "\nPeriod: " + str(self.period) \
               + "\nWCET: " \
               + str(self.WCET_1188) + ", " \
               + str(self.WCET_918) + ", "  \
               + str(self.WCET_648) + ", " \
               + str(self.WCET_384) + "\n" \

               
class RM_Task(Task):             
               
    def __gt__(self, b):
    
        if self.period < b.period:
            return True
        else:
            return False
            
class EDF_Task(Task):
    
    
    
    def __gt__(self, b):
        global clock
        if (True):
            return True
        else:
            return False

class Idle_Task(Task):
    
    def __init__(self, task_list):
        global clock
        
        min_release_time = task_list[0].release_time
        for task in task_list[1:]:
            if task.release_time <  min_release_time:
                min_release_time = task.release_time
                
        self.name = "Idle"
        self.period = -1
        self.WCET_1188 = min_release_time - clock
        self.release_time = 0
        self.deadline = 0

    def schedule(self, freq):
        global clock
        self.execution = self.WCET_1188
        self.deadline = 1000
    
    def execute(self):
        self.execution -=1 
    
    def is_ready(self):
        return False
        
    def suspend(self):
        pass
        
def print_error(error):
    print "Error: ", error
    sys.exit()
               
main()
