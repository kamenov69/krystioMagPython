#!/usr/bin/env python
# coding: utf-8
# pykiba V2.1
#no Walrus operator!
#Completible with old functions, but renewed 
#import time
import serial
import serial.tools.list_ports
import sys


def which_comport_to_use(serial_speed, manifact_name, name_of_the_device = None):
    """Prints list of available serial ports
    
    Returns
    -------
    device of exact port with krystioMag ../dev/ttyACM1

    """
    ports = serial.tools.list_ports.comports()
    exact_port = None 
    
    for i,p in enumerate(ports):
        #printing all ports
        print(f"{i}.   {p.manufacturer}   {p.device}")

    for p in ports:
        
        if  manifact_name == p.manufacturer:
            
            if name_of_the_device == None:
                exact_port  = p.device
                break
            
            else:
                arduino_port = serial.Serial(p.device, serial_speed)
                arduino_port.timeout = 1     
            
                while  arduino_port.out_waiting:
                    pass    
                
                _ = arduino_port.readlines()
                arduino_port.write(b'hello \r\l')
                arduino_port.flush()  
                input_lines=arduino_port.readlines()
                
                if name_of_the_device in input_lines:
                    exact_port  = p.device
                    arduino_port.close()
                    break

    return exact_port 
 
def serial_ports_list():
    """Prints list of available serial ports
    
    Returns
    -------
    ports : list of serial ports

    """
    ports = serial.tools.list_ports.comports()
    print("\n")
    for i,p in enumerate(ports):
        print(f"{i}.   {p.manufacturer}   {p.device}")
        
    return ports #ret_val        

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
    """ Parse int and floats from a line,
    other stais in str
    
    Parameters
    ----------
       line :a b''line 
       
    Returns:
    ----------
           list[prset strings, parsed ints or floats]
           or
           a float or int nubber 
    
    """
    line = line.decode().strip().split(',')
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
       written by Akiba ...
        
        Extends Serial...
            
    """
    def __init__(self, baudrate, port_device):
        """ Constructor 
        
        For the parameters can be used:
            serial_ports_list()
        
        Parameters
        ----------
        port : string with /dev/USBtty serial port device, optional
               The default is None.
        
        baudrate : int, optional
             The default is 9600.
             
        string optional with manifacturer ID
             The default is None.

        Returns
        -------
        None.
        """            

        if port_device:
            super().__init__(port = port_device, baudrate = baudrate) 
            print(f"Connected on port {port_device}")
            self.timeout = 5
            _= self.read_all()     
                
        else:
            print("Port not found")
            
    
    def __del__(self): 
        self.close()
                 
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
    
    


    def command(self, *args, timeout = 1.5):
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
             
if __name__ == '__main__':
    pass
