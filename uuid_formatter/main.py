def main():

    while(True):
        raw_string = raw_input("Enter UUID: ")
        string = raw_string.replace("-","")
        
        if len(string) != 32:
            print "invalid entry"
            continue
         
        list = [string[i:i+2] for i in range(0, len(string), 2)]
        list.reverse()
        
        output = ""
        output += "{"
        
        i = 0
        for byte in list:
            output += "0x" + byte 
            i+=1
            if not i==16:
                output += ","
            else:
                output += "}"
            
        
        
        print output
        
    

main()