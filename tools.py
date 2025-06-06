#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 28 11:36:58 2025

@author: kamen
"""

import socket
def print_my_ip():
    """Prints self ip address. """
    print([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1],
          [[(s.connect(('8.8.8.8', 53))
            ,s.getsockname()[0], 
             s.close()) for s in [socket.socket(socket.AF_INET, 
             socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
            ,end="")
                                                
import serial.tools.list_ports

def serial_ports_list():
    """Prints list of available serial ports
       and return list with them.
       Returns
       -------
           ports : list of serial ports 
           ... ports[0].device
           ... ports[0].manufacturer
    """
    ports = serial.tools.list_ports.comports()
    print("\n")
    for i,p in enumerate(ports):
        print(f"{i}.   {p.manufacturer}   {p.device}")
    
    print("")    
    return ports       

def search_by_manufacturer(ports, mnfact):
    """Search dev/comport by manufacturer 
       Parameters:
       ----------
          [ports], 
           mnfact - manicacturer name witten on the USB dongle
        Returns
        -------
        dev/name  or None
    """
    ret_val = None 
    for p in ports:
       if(str(p.manufacturer).startswith(mnfact)):
           ret_val = p.device
           break
           
    return ret_val