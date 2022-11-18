from multiprocessing import Process, Manager
import pickle
from collections.abc import MutableMapping
import signal

class FaultguardDict(MutableMapping):
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
    
def wrapped_launch(launch, managed_dict, signal_handlers, args):
    # Attach signal handlers
    for sig in signal_handlers:
        signal.signal(sig, signal_handlers[sig])

    faultguard_data = FaultguardDict(managed_dict)
    if args is None:
        launch(faultguard_data)
    else:
        launch(faultguard_data, args)

def recover(rescue, autosave_file=None):
    """
    Load the given faultguard data dictionary from an autosave file and pass it to a rescue function.
    
    :param rescue: The method to call with the recovered faultguard data dictionary.
    :param autosave_file: The file to recover the data from.
    :returns: Whether the main (0) or the backup file (1) was used for recovery
    """
    # Compression library
    import lzma
    import os

    success = True
    try:
        with lzma.open(autosave_file, "r") as f:
            faultguard_data = FaultguardDict(pickle.load(f))
    except Exception as e:
        print("The following issue occured during recovery:", e)
        success = False
    
    if success:
        rescue(faultguard_data)
        return 0
    
    if not os.path.isfile(autosave_file + ".tmp"):
        raise RuntimeError("Recovery unsuccessful.")
    
    print("Switching to try recovery of backup file")

    with lzma.open(autosave_file + ".tmp", "r") as f:
        faultguard_data = FaultguardDict(pickle.load(f))
        
    rescue(faultguard_data)
    return 1

def start(launch, rescue, args=None, autosave_interval=None, autosave_file=None):
    """
    Start application through faultguard.
    
    Launch and rescue have access to the same dictionary. Each entry in this dictionary is stored as serialized data using the python internal 'pickle' method. The "launch" method runs in a seperate process so a fault in that process should not affect the data stored in the dictionary.

    If the autosave parameters are set, the dictionary is compressed and saved in the specified time interval to the specified path. Throws an error if the autosave file already exists. After successful exit of the monitored application, the autosave file is deleted.

    :param launch: The applications main method. Accepts faultguard data dictionary as first and args (if not None) as second parameter.
    :param rescue: The method to call on a fault. Accepts faultguard data dictionary as first and args (if not None) as second parameter.
    :param args: Data passed to launch and rescue methods.
    :param autosave_interval: Time in seconds between each autosave of the `faultguard` dictionary.
    :param autosave_file: Path to file to use for autosaves.
    :returns: The applications exit code.
    """
    
    # Ensure valid parameters
    if autosave_interval is not None or autosave_file is not None:
        if autosave_interval is None or autosave_file is None:
            raise TypeError("Only one of the arguments 'autosave_interval' and 'autosave_file' is defined")
        
        import os
        
        if os.path.isfile(autosave_file):
            raise RuntimeError("The given autosave file already exists")
        
        with open(autosave_file, "w") as f:
            if not f.writable():
                raise RuntimeError("The given autosave file is not writable")
        
        if os.path.isfile(autosave_file + ".tmp"):
            os.remove(autosave_file + ".tmp")
    
    # Detach signal handlers from faultguard process
    # Ensures faultguard does not interfere with signals like SIGINT
    orig_handlers = {}
    for sig in signal.Signals:
        if   str(sig) == "Signals.CTRL_C_EVENT" \
          or str(sig) == "Signals.CTRL_BREAK_EVENT" \
          or str(sig) == "Signals.SIGKILL" \
          or str(sig) == "Signals.SIGSTOP" \
          or str(sig) == "Signals.SIGCHLD":
            continue
        orig_handlers[sig] = signal.signal(sig, signal.SIG_IGN)
    
    # Setup process
    manager = Manager()
    managed_dict = manager.dict()

    p = Process(target=wrapped_launch, args=(launch, managed_dict, orig_handlers, args,))
    
    # Run process
    p.start()
    
    if autosave_interval is None:
        p.join()
    else:
        # Compression library
        import lzma
        
        while p.is_alive():
            # Wait for next autosave
            p.join(autosave_interval)
            
            # Autosave
            if os.path.isfile(autosave_file + ".tmp"):
                os.remove(autosave_file + ".tmp")
            os.rename(autosave_file, autosave_file + ".tmp")
            
            with lzma.open(autosave_file, "w") as f:
                pickle.dump(dict(managed_dict), f)
    
    # Close Manager process
    # If this is not done and the faultguard process is terminated, the Manager process
    # would keep running.
    if p.exitcode != 0:
        faultguard_data = FaultguardDict(dict(managed_dict))
    manager.shutdown()
    
    # Re-attach signal handlers
    for sig in orig_handlers:
        signal.signal(sig, orig_handlers[sig])
    
    if p.exitcode != 0:
        if args is None:
            rescue(faultguard_data, p.exitcode)
        else:
            rescue(faultguard_data, p.exitcode, args)
    
    if autosave_interval is not None and os.path.isfile(autosave_file):
        # Remove autosave file
        os.remove(autosave_file)
        if os.path.isfile(autosave_file + ".tmp"):
            os.remove(autosave_file + ".tmp")

    return p.exitcode
