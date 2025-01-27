# -*- coding: utf-8 -*-
"""
Serves Arduino with krystioMag firmware
---------------------------------------



kamen.p.kamenov@gmail.com
hello
megaatmega2560
Krastio Magnet
"""


#import serial
#import serial.tools.list_ports 
#Terminal on /dev/ttyACM0 | 115200 8-N-1
from pykiba import which_comport_to_use 
from pykiba import Pykiba
import inspect
import jsonpickle
import sys





class KrystioMagnet():
    
    def __init__(self, speed, comport = None):
        
        self.serial_interface = Pykiba(baudrate = s_speed, port_device = comport)
        self.serial_interface.command('mode', 3) # the first command always is faulty
        self.serial_interface.command('mode', 3) # led blinks 3 times on connection
        self.channels_number = len(self.uv())           
        self.poly_dict = {
                          "equ" :  [1,0],
                          "volts" :  [1.0/1000.0,0]}


    def __del__(self):
        self.serial_interface.close()


    def hello(self, *args):
           my_name = inspect.stack()[0][3] #returns name of the function 
           return self.serial_interface.command(my_name, *args) 
                                                
    def mode(self, *args):
           my_name = inspect.stack()[0][3] #returns name of the function 
           return self.serial_interface.command(my_name, *args)
                                                 
    def aur(self, *args):
        my_name = inspect.stack()[0][3] #returns name of the function 
        return self.serial_interface.command(my_name, *args)    

    def auv(self, *args):
        my_name = inspect.stack()[0][3] #returns name of the function 
        return self.serial_interface.command(my_name, *args)
    
    def ur(self, *args):
        my_name = inspect.stack()[0][3] #returns name of the function 
        return self.serial_interface.command(my_name, *args)
                                             
    def uv(self, *args):
       my_name = inspect.stack()[0][3] #returns name of the function 
       return self.serial_interface.command(my_name, *args)

    def calibtoee(self, *args):
       my_name = inspect.stack()[0][3] #returns name of the function 
       return self.serial_interface.command(my_name, *args)

    def calibfromee(self, *args):
       my_name = inspect.stack()[0][3] #returns name of the function 
       return self.serial_interface.command(my_name, *args)

    def setvref(self, *args):
        my_name = inspect.stack()[0][3] #returns name of the function 
        return self.serial_interface.command(my_name, *args)
    
    
    def vref(self, *args):
        my_name = inspect.stack()[0][3] #returns name of the function 
        
        if(len(args) == 2):
            retval = self.serial_interface.command(my_name, *args)
            
        elif(len(args) == 1):
            for i in range(self.channels_number):
                retval = self.serial_interface.command(my_name, i, args[0])  
                
        else:
               retval = self.serial_interface.command(my_name, *args)    
    
        return  retval 
    
   
    def polynom(self, name_of_coef, arg):
        
        coef = self.poly_dict.get(name_of_coef, self.poly_dict["equ"])
        sum =0
        for tmpi,tmpcc in enumerate(reversed(coef)):
            sum = sum + (pow(arg,tmpi)*tmpcc) 
        
        return sum
    
    def add_polynom(self, polynom_name, coef):
        self.poly_dict.update({polynom_name : coef})
        
    def polynoms_list(self):   
        tmpstr=""
        for key  in self.poly_dict:
            tmpstr+= (f"{key}:{self.poly_dict[key]} , ") 
        return tmpstr
            
    def polynoms_to_file(self, file_name):
        # save dictionary to person_data.pkl file
        with open(file_name, 'w', newline='') as f:
            print(f"file is opened as {f}") 
            f.write(jsonpickle.encode(self.poly_dict, indent=4 ))
            #f.write("bozakosmata txt")
            f.flush()
        
    def polynoms_from_file(self, file_name):
        # save dictionary to person_data.pkl file
        with open(file_name,'r') as f:
             
             string = f.read()
             self.poly_dict = jsonpickle.decode(string)

    #def __call__(self, channel, calib = None, raw = False):
    
    
    def read(self, pin = None, calib = None, raw = False):
        if pin != None:
            if raw:
                tmp_val = self.ur(pin)[1]

            else:
                tmp_val = self.uv(pin)
                
            if calib:
                    tmp_val = self.polynom(calib, tmp_val)
        
        else:
            if raw:
                tmp_val = [inp[1] for inp in self.ur()]
                

            else:
                tmp_val = self.uv()
            
            if calib:
                tmp_val = [self.polynom(calib, inp) for inp in tmp_val]
               
        return  tmp_val 
            
        
            
            
        

import socket
def print_my_ip():
   print([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0],end="")

if __name__ == '__main__':
  
    import zerorpc
    filename = './polynom.json'
    fname = 'Arduino (www.arduino.cc)'
    hellostr = b'Krastio Magnet\r\n'
    #s_speed = 115200
    s_speed = 9600

              
    #comport = which_comport_to_use(s_speed,  fname, hellostr )
    comport = which_comport_to_use(s_speed,  fname )
    serving = False
    
    
    
    if serving:
        if comport:
            print(f"n\n\n Connecting { hellostr } seria interface \n Made by '{fname}' \n on port {comport}")
            print(f" With baudrate {s_speed} ... \n\n")
            #vlt = KrystioMagnet(s_speed, comport)
        
        else:
            print("Connection feilure!")
            print("Exitting")
            sys.exit(0)
        
        
        print("Startin zerorpc server ...")
        print("To IP address")
        print_my_ip()
        print(":4242")
        
        s = zerorpc.Server(KrystioMagnet(s_speed, comport))
        s.bind("tcp://0.0.0.0:4242")
        s.run()
       
    
    else:         
        if comport:
            print(f"n\n\n Connecting { hellostr } seria interface \n Made by '{fname}' \n on port {comport}")
            print(f" With baudrate {s_speed} ... \n\n")
            vlt = KrystioMagnet(s_speed, comport)
            
            """test polynoms
            
            vlt.add_polynom("squ", [2,1,1])
            
            for tmpint in range(0,10):
                res = vlt.polynom("squ", tmpint)
                print(f'{tmpint}    --- {res}')
            """
            
            
        else:
            print("Connection feilure!")
            print("Exitting")
            sys.exit(0)
        
        #del vlt
        pass
     
   
        
    
   
   
    
   

