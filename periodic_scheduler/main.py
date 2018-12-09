import sys
import copy

def main():
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
    
    if not schedule(task_list):
        print "Task Set is Unscheduleable"
        sys.exit()
    
    tested_task_list = copy.deepcopy(task_list)
        
    if energy_efficent:
    
        while(True):
            
            if not schedule(task_list):
                print "Unscheduleable at this power level"
                break
            else:

                #copy tested task list
                tested_task_list = copy.deepcopy(task_list)
            
                #check if we are at the absolute minimum power level
                total_power_level = 0
                for task in task_list:
                    total_power_level+=task.power_level
                if total_power_level == 0:                
                    break
                    
                #sort taks by utilization
                task_list.sort(key=lambda x: x.utilization())
                
                #reduce power of lowest util task
                i = 0
                while (not task_list[i].reduce_power()):               
                    i+=1
            
                print "Reducing power level: ", task_list[i].name, task_list[i].power_level+1, "->",  task_list[i].power_level
    
    
    exececution_list = schedule(tested_task_list)
    
    if (exececution_list != False):
        print "\nSchedule:"
        total_energy = 0
        for execution in exececution_list:
            total_energy+=execution.energy_use
            print execution
        print "Total Energy Use: ", total_energy, "J"
    
    else:
        print_error("Scheduling Error")
        
def schedule (tested_task_list):
    print "\nRunning...",
    
    global params
    global clock
    
    clock = 1

    release_list = copy.deepcopy(tested_task_list)
    suspended_list = []
    schedule_list = []
    
    release_list.sort()
    missed_deadline = False   
    
    cpu = CPU(release_list.pop())
    new_task = False

    ## Main Loop ##
    # 1. check for missed deadlines
    # 2. release tasks tasks when ready
    # 3. if released task(s) are higher priority than current task or task is done 
        # a. suspend current task
        # b. move task to appropriate list
        # c. log excution to schedule
        # d. select new task
        # e. give new task to CPU
    # 4. execute CPU for one time unit
    # 5. increment clock
    # 6. return to step 1
        
    while (clock < params.total_exec_time):
            
        # 1. check for missed deadlines
        for task in release_list + [cpu.active_task]:
            if task.deadline < clock:
                print "Missed deadline: ", task.name, " @ ", clock
                missed_deadline = True
        if missed_deadline:
            break
        
        # 2. release tasks tasks when ready
        for task in suspended_list:
            if task.is_ready():
                suspended_list.remove(task)
                task.release()
                release_list.sort()
                release_list.append(task)
                if  cpu.active_task < task:
                    new_task = True
                                    
        # 3. if released task(s) are higher priority than current task or task is done 
        if (cpu.active_task.is_done() or new_task):
            new_task = False    
            if release_list:
                suspended_task = cpu.context_switch(release_list.pop())
            else:
                suspended_task = cpu.context_switch(Idle())
                
                
            if (suspended_task.__class__.__name__ != "Idle"):               
                if suspended_task.is_done():
                    suspended_list.append(suspended_task)
                else:
                    release_list.append(suspended_task)
                            

        # 4. execute CPU for one time unit       
        cpu.run()      
         
        # 5. increment clock         
        clock+=1
    
    #terminate
    cpu.context_switch(Idle())
    
    if not missed_deadline:
        print "Success"
        return cpu.execution_list
    else:
        return False
   
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
            "IDLE":int(split[6]),
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
        self.period = int( split[1] )       
        self.WCET = {
            1188:int(split[2]),
            918:int(split[3]),
            648:int(split[4]),
            384:int(split[5]),   
        }
        self.release_time = self.period
        self.deadline = self.period
        self.remaining_time = None
        self.power_level = 3
        self.freqs = [384, 648, 918, 1188]
    
    def schedule(self, freq):
        if self.remaining_time == None:
            self.remaining_time = self.WCET[freq]
        else:
            pass
    
    def release(self):
        global clock 
        self.deadline = clock + self.period
        self.release_time = clock + self.period
        self.remaining_time = None
        
    def execute(self):
        self.remaining_time -=1
               
    def suspend(self):
        pass
                
    def is_ready(self):
        global clock      
        if (clock >= self.release_time):
            return True
        else:
            return False
    
    def is_done(self):        
        if self.remaining_time <= 0:
            return True
        else:
            return False

    @property
    def freq(self):
        return self.freqs[self.power_level]
    
    def utilization(self):
        return  self.WCET[self.freqs[self.power_level]] / float(self.period)
    
    def reduce_power(self):
        if self.power_level != 0:
            self.power_level+=-1
            return True
        else:
            return False
        
    def increase_power(self):
        if self.power_level < 3:
            self.power_level+=1
            return True
        else:
            return False
            
#Subclasses define the sorting behavior for scheduling               
class RM_Task(Task):                         
    def __gt__(self, b):
        if self.period < b.period:
            return True
        else:
            return False
    def __str__(self):
        return "Task: " + self.name + ", Period: " + str(self.period) + ", Remaining: " + str(self.remaining_time)     
    

    
class EDF_Task(Task):    
    def __gt__(self, b):
        global clock
        global params        
        if (self.deadline < b.deadline):
            return True
        else:
            return False
    def __str__(self):
        return "Task: " + self.name + ", Deadline: " + str(self.deadline) + ", Remaining: " + str(self.remaining_time) 
        
class Idle(Task):
    
    def __init__(self):
        global params
        self.name = "IDLE"
        self.deadline = params.total_exec_time
        self.period = params.total_exec_time
        self.freq = "IDLE"
        
    def schedule(self, freq):
        pass
         
    def suspend(self):
        pass
    
    def execute(self):
        pass
        
    def is_done(self):
        return False
        
    def __str__(self):    
        return "Task: " + self.name
       
    def __lt__(self, b):
        return True

    def __gt__(self, b):
        return False   

        
class CPU():

    def __init__(self, task):
        self.active_task = task
        self.execution_list = []

        ## schedule
        self.execution = Execution(task, task.freq)
        self.active_task.schedule(task.freq)
        
    def context_switch(self, next_task):
        
        ##log cpu time
        self.execution_list.append(self.execution)
        
        ##suspend
        self.active_task.suspend()
        suspended_task = self.active_task
               
        ## schedule
        self.active_task = next_task
        self.execution = Execution(self.active_task, self.active_task.freq)
        self.active_task.schedule(self.active_task.freq)
        
        return suspended_task
                  
    def run(self):
        self.execution.cpu_time+=1        
        self.active_task.execute()
    
class Execution:
    
    def __init__(self, task, freq):
        global clock
        self.init_time = clock
        self.task = task
        self.cpu_time = 0
        self.freq = freq
        
    def __str__(self):
        return str(self.init_time) + "\t" \
           + str(self.task.name) + "\t" \
           + str(self.freq) + "\t" \
           + str(self.cpu_time) + "\t" \
           + str(self.energy_use) + "J"
    
    @property
    def energy_use(self):
        global params
        return params.power[self.freq]*self.cpu_time
                 
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

def print_debug(msg):
    if (True): print msg
    
main()
