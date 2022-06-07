# Faultguard

[![Build Status](https://travis-ci.com/2xB/faultguard.svg?branch=master)](https://travis-ci.com/2xB/faultguard)
[![GitHub license](https://img.shields.io/github/license/2xB/faultguard.svg)](https://github.com/2xB/faultguard)
[![pypi version](https://img.shields.io/pypi/v/faultguard.svg)](https://pypi.org/project/faultguard/)

Let users save important data after a crash of your Python3 application.

## Introduction

If a process experiences e.g. a segmentation fault, it cannot execute further operations to recover. Also, memory of a process is considered inconsistent after a segmentation fault. However, as soon as a project depends on third party libraries, the appearence of such faults is out of hand.

This module provides an approach to implement a crash rescue handler that can access important data even after segmentation faults: While the guarded application runs (see `launch` function in the example below), it has access to a special Python dictionary (`faultguard_data` in example) in which it stores a copy of important user data. Data stored in this dictionary remains accessible when the guarded application abruptly terminates, at which point a rescue handler can access the dictionary and rescue data from there (`rescue` function in example).

Starting the application with a given rescue handler is just one line of code when using `faultguard`, shown in the `main` function in the example below.

On the technical side, this is realized through Python modules `pickle`, `multiprocessing` and `collections`, which are used to serialize and deserialize various types of data and provide the dictionary-like data type that is available in both the guarded application and the rescue handler process.
The Python module 'signal' is used to ensure signals like keyboard interrupts are handled correctly and received by the guarded process.

This module is really simple, although its functionality is very reuseable. Feel encouraged to look into the source code and to contribute through (well documented :D ) pull requests!

## Installation

This module is available through pip or can be installed manually via setup.py.

## Disclamer

If a crash is observed frequently or reproducibly, it should be diagnosed – e.g. with `faulthandler` (another Python module) and `gdb`. If you somehow manage to generate a segmentation fault in the `faultguard` data dictionary, and therefore destroy the guard process, the rescue will of course not work. Preventing faults from happening in the first place is always the most important, so don't rely solely on this module, just use it as an additional safety net!

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
