import sys

def main():
    global clock
    global params 
    
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
    
    if scheduler == "RM":
        for i in range(params.num_of_tasks):
            task_list.append(RM_Task(f.readline()))
    elif scheduler == "EDF":
        for i in range(params.num_of_tasks):
            task_list.append(EDF_Task(f.readline()))
    else:
        print_error("Invalid Scheduler")
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
    if release_list:            
        release_list.sort()    
        active_task = release_list.pop()
        
    else:
        active_task = Idle_Task(suspended_list)

    #select freq
    freq = 1188
    
    #schdule next task
    active_task.schedule(freq)
    schedule_list.append(Schedule(active_task, freq)) 

    ## Main Loop ##
    # 1. check for missed deadlines
    # 2. release tasks tasks when ready
    # 3. context switch when task is done 
        # a. move tasked to suspend list if not the idle "task"
        # b. find next task to schedule from release list
        # c. if release list empty schedule an idle "task"
        # d. select appropriate frequency
        # e. schedule next task
    # 4. execute active task
    # 5. increment clock
    # 6. return to step 1
        
    while (clock < params.total_exec_time):
    
        print "Clock = ", clock
        
        # 1. check for missed deadlines
        for task in release_list:
            if task.deadline < clock:
                print "\tMissed deadline: "
                print "\t", task
                print "\nSchedule:"
                for schedule in schedule_list:
                    print schedule
                sys.exit()
        
         # 2. release tasks tasks when ready
        for task in suspended_list:
            if task.is_ready():
                suspended_list.remove(task)
                task.release()
                release_list.append(task)
                print "\tReleasing Task: ", task.name
                            
        # 3. suspend taks when ready, then schedule new
        if (active_task.is_done()):

            # a. move tasked to suspend list if not the idle "task"
            active_task.suspend()
            if (active_task.__class__.__name__ != "Idle_Task"):
                print "\tSuspending Task: ", active_task.name
                suspended_list.append(active_task)
            else:
                print "\tIdle Done"

                
            # b. find next task to schedule from release list 
            if release_list:            
                release_list.sort()    
                active_task = release_list.pop()
            # c. if release list empty schedule an idle "task"    
            else:
                active_task = Idle_Task(suspended_list)

            # d. select appropriate frequency
            if (active_task.__class__.__name__ == "Idle_Task"):
                freq = 0           
            elif energy_efficent:
                freq = 918
            else:
                freq = 1188
            
            #e. schedule next task
            active_task.schedule(freq)
            schedule_list.append(Schedule(active_task, freq))  
                      
            print "\tNext Task: ", active_task.name
            
        # 4. execute active task
        active_task.execute()

        # 5. increment clock
        clock+=1
        
    # print schedule
    print "\nSchedule: "
    for schedule in schedule_list:
        print schedule      
    total_energy = 0
    for schedule in schedule_list: total_energy += schedule.energy_use
    print "Total Energy Use: ", total_energy, "J"
    
#end of main
    
class Params:
        
    def __init__(self, file_line):
    
        split = file_line.replace("\n","").split(" ")
        if (len(split) < 7):
            print_error("bad file (line 1)")
            
        self.num_of_tasks =     int( split[0] )
        self.total_exec_time =  int( split[1] )
        self.power = {
            1188:int(split[2]),
            918:int(split[3]),
            648:int(split[4]),
            384:int(split[5]),   
            0:int(split[6]),
        }
      
    def __str__(self):
    
        return "Number of Tasks: " + str(self.num_of_tasks) \
               + "\nExecution time: " + str(self.total_exec_time) \
    
class Task:

    def __init__(self, file_line):

        split = file_line.replace("\n","").split(" ")
        if (len(split) < 6):
            print split
            print_error("bad file")
            
        self.name = split[0]           
        self.period =       int( split[1] )       
        self.WCET = {
            1188:int(split[2]),
            918:int(split[3]),
            648:int(split[4]),
            384:int(split[5]),   
        }
        self.release_time = 0
        self.deadline = self.period
    
    def schedule(self, freq):
        global clock
        self.execution = self.WCET[freq]
    
    def release(self):
        global clock 
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
        return "Task: " + self.name + ", Period: " + str(self.period) \

class CPU:

    def __init__(self):
        pass
   
    def context_switch(self, task, freq):
        ##log cpu time
        
        ##suspend
        
        ##load new execution
        self.execution = Execution(task, freq)
    
    def execute(self):
        self.execution.cpu_time+=1
    
class Execution:
    
    def __init__(self, task, freq):
        global clock
        self.init_time = clock
        self.cpu_time = 0
        self.freq = freq
        
#Subclasses define the sorting behavior for scheduling               
class RM_Task(Task):                         
    def __gt__(self, b):
        if self.period < b.period:
            return True
        else:
            return False
            
class EDF_Task(Task):    
    def __gt__(self, b):
        global clock
        global params        
        if (self.deadline < b.deadline):
            return True
        else:
            return False

class Idle_Task(Task):
    
    def __init__(self, task_list):
        global clock
        global params         
        min_release_time = params.total_exec_time
        for task in task_list:
            if task.release_time <  min_release_time:
                min_release_time = task.release_time
                
        self.name = "IDLE"
        self.execution = min_release_time - clock
        self.release_time = 0
        self.deadline = 0

    def schedule(self, freq):
        global clock
        global params
        self.deadline = params.total_exec_time
         
    def suspend(self):
        pass

    def __str__(self):    
        return "Task: " + self.name \
               + "\nPeriod: " + str(self.period) \
               + "\nWCET: " \
        
class Schedule:

    def __init__(self, task, freq):
        global clock
        global params
        self.init_time = clock
        self.task = task
        self.freq = freq
        self.exec_time = task.execution
        if (params.total_exec_time - clock < self.exec_time):
            self.exec_time = params.total_exec_time - clock
        
        self.energy_use = self.exec_time * params.power[freq] /1000.0
    
    def __str__(self):
        return str(self.init_time) + "\t" \
               + str(self.task.name) + "\t" \
               + str(self.freq) + "\t" \
               + str(self.exec_time) + "\t" \
               + str(self.energy_use) + "J"
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

def print_error(error):
    print "Error: ", error
    sys.exit()
    
main()
