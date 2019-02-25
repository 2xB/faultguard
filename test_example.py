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
    assert np.all(important_data_1 == [6, 7, 5])
    assert important_data_2 == "Hello World01234567"
    
def test_main():
    faultguard.start(launch, rescue, args=("Hello", "World"))
