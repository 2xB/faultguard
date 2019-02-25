# Faultguard

[![Build Status](https://travis-ci.com/2xB/faultguard.svg?branch=master)](https://travis-ci.com/2xB/faultguard)
[![GitHub license](https://img.shields.io/github/license/2xB/faultguard.svg)](https://github.com/2xB/faultguard)
[![pypi version](https://img.shields.io/pypi/v/faultguard.svg)](https://pypi.org/project/faultguard/)

Rescuing data from abrubt process termination in python.

## Introduction

If a process experiences e.g. a segmentation fault, it cannot execute further operations to recover. Also, memory of a process is considered inconsistent after a segmentation fault. As soon as a project depends on third party libraries, the appearence of such faults is out of hand. Therefore, to implement a crash handler for important data, an approach to prepare for rescuing data after an abrupt process termination is needed. This module uses the python modules 'pickle', 'multiprocessing' and 'collections', to serialize and deserialize various types of data and provides a dictory-like data type to save and recover important data in the adress space of an independent process.

This module is really simple, although its functionality is very reuseable. If you are versed in this topic, feel encouraged to look into the source code and to contribute through (well documented ;) ) pull requests.

## Installation

This module is available through pip or can be installed manually via setup.py.

## Disclamer

This module is focused on projects that e.g. rely on native libraries and have important data. It will not provide you any help in fixing a segmentation fault and you should feel encouraged to learn about the python module 'faulthandler' and the use of 'gdm' to fix faults in your own code. If you somehow manage to generate a segmentation fault in the faultguard data dictionary, and therefore destroy the guard process, the rescue will of course not work. This module is an additional security option, not an excuse for irresponsible programming!

## Example

It follows a minimal working example for this module:

```python
import faultguard
import numpy as np

def launch(faultguard_data, args):
    """
    Demo software main method
    
    :param faultguard_data: Faultguard data dictionary
    :param args: Data passed from faultguard.start.
    """
    print("Launching demo")
    
    # Some important data
    important_data_1 = np.array([1,2,3])
    important_data_2 = args[0] + " " + args[1]
    
    # Some dummy important data manipulation
    for i in range(10):
        important_data_1[i%3] = i
        important_data_2 += str(i)
        print("important_data_1:", important_data_1)
        print("important_data_2:", important_data_2)
        
        # Sending important data to faultguard process
        faultguard_data["important_data_1"] = important_data_1
        faultguard_data["important_data_2"] = important_data_2
        
        # Generate segfault
        if i == 7:
            import ctypes
            ctypes.string_at(0)
            
def rescue(faultguard_data, exit_code, args):
    """
    Demo rescue handler
    
    :param faultguard_data: Faultguard data dictionary
    :param exit_code: Exit code of occured fault.
    :param args: Data passed from faultguard.start.
    """
    print("Fault occured. Exit code: {}. Rescued data:".format(exit_code))
    
    # Check if fault occurs before data was initialized
    if "important_data_1" not in faultguard_data or "important_data_2" not in faultguard_data:
        return
    
    # Restore data
    important_data_1 = faultguard_data["important_data_1"]
    important_data_2 = faultguard_data["important_data_2"]
    
    # You might need to assign the class here by important_data_1.__class__ = ...
    print("important_data_1:", important_data_1)
    print("important_data_2:", important_data_2)
    
def main():
    faultguard.start(launch, rescue, args=("Hello", "World"))

if __name__ == "__main__":
    main()
```

## Credit

This project was initially developed for a hardware project at the University of Münster.
