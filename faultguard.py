from multiprocessing import Process, Manager
import pickle
import collections

def start(launch, rescue, args = None):
    """
    Start application through faultguard.
    
    Launch and rescue have access to the same dictionary. Each entry in this dictionary is stored as serialized data using the python internal 'pickle' method. The "launch" method runs in a seperate process so a fault in that process should not affect the data stored in the dictionary.

    :param launch: The applications main method. Accepts faultguard data dictionary as first and args (if not None) as second parameter.
    :param rescue: The method to call on a fault. Accepts faultguard data dictionary as first and args (if not None) as second parameter.
    :param args: Data passed to launch and rescue methods.
    :returns: The applications exit code.
    """

    class FaultguardDict(collections.MutableMapping):
        """
        Dictionary-like object.

        Stores data in the faultguard process. Every data is automatically serialized and deserialized using pickle.
        If the application process(es) experience a fault, the data in this object should be preserved.
        """
        def __init__(self, managed_dict):
            self.store = managed_dict

        def __getitem__(self, key):
            return pickle.loads(self.store[key])

        def __setitem__(self, key, value):
            self.store[key] = pickle.dumps(value)

        def __delitem__(self, key):
            del self.store[key]

        def __iter__(self):
            return iter(self.store)

        def __len__(self):
            return len(self.store)
    
    manager = Manager()
    managed_dict = manager.dict()
    
    def wrapped_launch(args):
        faultguard_data = FaultguardDict(managed_dict)
        if args is None:
            launch(faultguard_data)
        else:
            launch(faultguard_data, args)

    p = Process(target=wrapped_launch, args=(args,))
    
    p.start()
    p.join()
    
    if p.exitcode != 0:
        faultguard_data = FaultguardDict(managed_dict)
        if args is None:
            rescue(faultguard_data, p.exitcode)
        else:
            rescue(faultguard_data, p.exitcode, args)
        
    return p.exitcode
