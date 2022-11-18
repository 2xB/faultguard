from multiprocessing import Process
import multiprocessing
import faultguard
import numpy as np
import time
import sys
import os

def launch(faultguard_data, args):
    """
    Demo software main method
    
    :param faultguard_data: Faultguard data dictionary
    :param args: Data passed from faultguard.start.
    """
    print("Launching demo")
    print(multiprocessing.current_process())
    
    # Some important data
    important_data_1 = np.array([1,2,3])
    important_data_2 = args[0] + " " + args[1]
    
    # Some dummy important data manipulation
    for i in range(1):
        important_data_1[i%3] = i
        important_data_2 += str(i)
        print("important_data_1:", important_data_1)
        print("important_data_2:", important_data_2)
        
        # Sending important data to faultguard process
        faultguard_data["important_data_1"] = important_data_1
        faultguard_data["important_data_2"] = important_data_2
        time.sleep(4)

def rescue(faultguard_data, exit_code, args):
    raise RuntimeError("Rescue handler was triggered unexpectedly...")

def run_test():
    # Run test with long autosave interval to be independent on startup times
    faultguard.start(launch, rescue, args=("Hello", "World"), autosave_interval=1, autosave_file="test.tmp.xz")

def recover(faultguard_data):
    important_data_1 = faultguard_data["important_data_1"]
    important_data_2 = faultguard_data["important_data_2"]
    
    # You might need to assign the class here by important_data_1.__class__ = ...
    print("important_data_1:", important_data_1)
    print("important_data_2:", important_data_2)
    assert np.all(important_data_1 == [0, 2, 3])
    assert important_data_2 == "Hello World0"

def test_main():
    # Prepare test environment
    if os.path.isfile("test.tmp.xz"):
        os.remove("test.tmp.xz")
    
    p = Process(target=run_test)
    
    # Run process
    p.start()
    p.join(2)
    os.rename("test.tmp.xz", "test.tmp.xz.backup")
    p.join()
    
    os.rename("test.tmp.xz.backup", "test.tmp.xz")
    assert faultguard.recover(recover, "test.tmp.xz") == 0

    os.rename("test.tmp.xz", "test.tmp.xz.tmp")
    with open("test.tmp.xz", "w") as f:
        f.write("Test")
    assert faultguard.recover(recover, "test.tmp.xz") == 1
