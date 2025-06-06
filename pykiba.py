#!/usr/bin/env python
# coding: utf-8
# pykiba V3.0  initially pykibaNew
#     added timeout before a command sending
#     re.split instead .slplit(',')
#     added '\n' whiele sending 
# no Walrus operator!
# Completible with old functions, but renewed 
# V3.1 - added  def install_arduino_commands(self):
import serial
import re
import time
from tools import print_my_ip, search_by_manufacturer, serial_ports_list


def prepare_line_to_send(*args):
    """Turns All in b'string'
    """ 
    output_buffer =[]
    for word in args:
        if type(word) is int:
            word = str(word).encode()
        
        elif type(word) is float: 
            word = int(word*1000)
            word = str(word).encode()
            word = word + b' -3'
        
        elif type(word) is str:
            word = word.encode()

        if word[-1] ==  13:   # b'\r'
            word = word[:-1]
                                  
        output_buffer.append(word)
        output_buffer.append(b' ')
        
    output_buffer.pop(-1)
    output_buffer.append(b'\r')
        
    return b''.join(output_buffer)
    

def parse_line(line):
    """ Parse int and floats from a line.
    If not a number stais us it is.
    Parameters
    ----------
       line :a b''line 
    Returns:
    ----------
           list[prset strings, parsed ints or floats]
           or
           a float or int nubber 
    """
    line = line.decode().strip()
    #line = line.split(',')
    #line = re.split(r"[, \-!?:]+",line)  # Will be splitting on: , <space> - ! ? :
    line = re.split(r"[, ;#!?:]+",line)   #\- # ; 
   
    output_val = [] 
    for word in line:   
        try:
            output_val.append(int(word))
            continue    
        except ValueError:
            pass
    
        try:
            output_val.append(float(word))
            continue
        except ValueError:
            pass
    
        output_val.append(word)  
    
    if len( output_val) == 1:
        output_val = output_val[0]
    
    elif  output_val == []:
        output_val = None
    
    return output_val




class Pykiba(serial.Serial):
    """Class Pykiba, 
       It coresponds with the arduino serial command interpret
       written by Akiba.
       Extends Serial...   
    """
    def __init__(self, **kargs):
        """ Constructor 
        Parameters
        ----------
            port : device name  e.q. string with /dev/... or comport
            baudrate : int, optional
            The default is 9600.    
        Returns
        -------
        None.
        """ 
        super().__init__(**kargs) 
        self.string_rep = f"Connected on {kargs} \n\n"
        self.timeout = 5
        #self.command("hello")
        _= self.read_all()
        #time.sleep(2)
       
                
    def write_line(self,*args):     
        """Send a string to arduino
        Parameters
        ----------
        buffer : string, bytearray, optional
                 The default is None. Aditional a number can be added.
                 Number will be translated to b'.....' and added to the
                 string.       
        Returns
        -------
        None.
        """
        line_for_sending = prepare_line_to_send(*args)
        #time.sleep(0.15)
        while  self.out_waiting:
            pass    
        
        self.echo_of_the_command =  line_for_sending    # + b'\n'
        self.write(line_for_sending)
        self.flush()    
                      
        
    def raw_lines(self, *args, timeout =5):
        """ Send a string to arduino, return a list with raw lines receved.
        Parameters
        ----------
        bytes__ : bytes, string, optional
                  string to be send. The default is None.     
        timeout : float in seconds, optional
                  how many time to wait for response. 
                  The default is 0.5.
        Returns
        -------
        bytes
            list with received lines in b'....'.
        """
        tmp_timeout = self.timeout
        self.timeout = timeout   
        _ = self.read_all()
        self.write_line(*args)
        ninput=self.readlines()
        self.timeout = tmp_timeout
        return ninput
    
    
    
    def command(self, *args, timeout = 2.5):
        """Sends a string with a command to arduino and receives 
        it number responce. Parse int, floats from response
        Parameters
        ----------
        *args  : bytes, string, int,float, Optional
                 A command to be send. The default is None.
            
        timeout: fload in seconds , optional
                 Whow many time to wait for a line. The default is 0.1.
        Returns
        -------
        return_value : float,int or list floats,ints or list of lists floats. 
        Every line is parsed in a list, all received lines are in 
        larger.
        """     
        tmp_timeout = self.timeout
        self.timeout = timeout
        #time.sleep(0.5)   #command overwrite prompt
        self.flush()
        while self.out_waiting:
            pass
            
        time.sleep(0.25)
        _ = self.read_all()      
        self.write_line(*args)
        return_value = []
        #while (line := self.readline()):
        while True:
            line = self.readline()
            if not line:
                break
 
            if self.echo_of_the_command in line: #command overwrite prompt
                continue    
        
            if b'>>' in line: #command overwrite prompt
                continue   
            
            line = parse_line(line)
            return_value.append(line)
            if '' in  return_value:
                return_value.remove('')
                break
     
        if len(return_value) == 1:
            return_value = return_value[0]
        
        elif return_value == []:
            return_value = None
         
        self.echo_of_the_command = None    
        self.timeout = tmp_timeout
        return return_value
    
        
    def __repr__(self):
        return self.string_rep
       
    def __str__(self):
        return self.string_rep
    

    def __del__(self):
         self.close()     
         
         
         
class PykiDev(Pykiba):
    """Altomaticaly installs commands of the Arduino if it support 'help' cmd""" 
    def __init__(self,  **kargs):
        """
            The constructor of the class
            Parameters:
            **kargs :
                port = for an example '/dev/ttyACM0' or COM3, 
                baudrate = 9600 or 19200 ...
        Returns
        -------
        None.
        """
        super().__init__(**kargs)
        time.sleep(1) # must be!
        self.install_arduino_commands()
        
            
    def install_arduino_commands(self):
        """ If cmd support command "help":
            1. Read all commands with help. 
            2. For all available commands defines a functions:
                CMD>>command arg0 arg1 ... -> obj.command(arg1, arg2 ...) 
            *** bug *** The first defined command missing !!!
            Parameters:
            ----------
            None
            
            Returns:
            -------           
            None
        """
        command_list = self.command("help")
        for cmd in command_list:
            def function_template( *args, captured_name = cmd):
                return self.command( captured_name, *args)
        
            setattr(self, cmd, function_template)
              
        for cmd in self.command('help'):
           self.string_rep = self.string_rep + cmd + '\n'
        
             
    

if __name__ == '__main__':
    serving = False
    #serving = True
    #print_my_ip()
    usb_manifacturer_name = 'Arduino'
    baudrate = 9600
    #
    if not serving:
        lstedPorts = serial_ports_list()
        prt = search_by_manufacturer(lstedPorts , usb_manifacturer_name)
        ard = PykiDev(port =  prt, baudrate = baudrate)  # install_cmd = True        
        #ard.install_arduino_commands()
        #print(ard.hello())        
        #ard.mode(1) 
        print(ard)
    else:
        import zerorpc
        lstedPorts = serial_ports_list()
        prt = search_by_manufacturer(lstedPorts , usb_manifacturer_name)
        print(f"Board with name {usb_manifacturer_name} connected dev {prt}")
        print("Startin zerorpc server ...")
        print("To IP address")
        print_my_ip()
        print(":4242")  
        s = zerorpc.Server(Pykiba(port =  prt, baudrate = baudrate, install_cmd = True))
        s.bind("tcp://0.0.0.0:4242")
        s.run()
    
    
  