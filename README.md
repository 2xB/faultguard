# Faultguard

[![Build Status](https://travis-ci.com/2xB/faultguard.svg?branch=master)](https://travis-ci.com/2xB/faultguard)
[![GitHub license](https://img.shields.io/github/license/2xB/faultguard.svg)](https://github.com/2xB/faultguard)
[![pypi version](https://img.shields.io/pypi/v/faultguard.svg)](https://pypi.org/project/faultguard/)

Preventing data loss of your Python3 application. Keeps important data both duplicated in memory and on disk.

## Overview

Usually, after a crash through e.g. a segmentation fault or a power outage, data of running applications is lost. In environments where this is problematic – e.g. when users should not loose their work or important data is collected –, `faultguard` prevents data loss in two ways:

 1. `faultguard` keeps the selected data automatically backed up in a second process. This way, if your Python application crashes - even with a segmentation fault caused e.g. by an external library -, in most cases the backup process is still running and immediately provides its data to a rescue handling function that you can define. This even allows you to e.g. provide users with a custom graphical dialog informing about the crash and providing options for the recovered data.
 
 2. `faultguard` can save the selected data automatically in customizable time intervals to a file from which it can be recovered on the next application launch.

An example using all features of `faultguard` can be found in `example.py`.

To secure an application data using `faultguard`, you define a `launch` function that `faultguard` provides with a custom data dictionary. This dictionary, although working like a usual dictionary and accepting all content that can be serialized using `pickle`, is automatically backed up as described above. If the guarded application crashes, the backup process launches a crash handler in form of a `rescue` function also defined by you and provides it with the backed up dictionary. Additionally, if you provide `faultguard` with a time interval and a path for autosaves, it stores the data on disk and you can call the `recover` method to recover the file content and call your `rescue` function.

The `faultguard` interface is very simple - you just provide it with a `launch` and a `rescue` function and everything else works automatically. If you use autosaving, on application launch you should additionally test if a backup file exists, which would show that `faultguard` did previously not exit properly. If a backup file exists, you should let `faultguard` recover it and then delete it to make place for a new one.

On the technical side, the in-memory backup is realized through Python modules `pickle`, `multiprocessing` and `collections`, which are used to serialize and deserialize various types of data and provide the dictionary-like data type that is available in both the guarded application and the rescue handler process. The autosave functionality uses the Python module `lzma` for efficient compression of autosave files and `os` for file handling.
The Python module `signal` is used to ensure signals like keyboard interrupts are handled correctly and received by the guarded process.

Feel encouraged to look into the source code and to contribute through (well documented :D ) pull requests!

Faultguard is tested on Linux and Windows.

## Installation

This module is available via `pip install faultguard` or can be installed manually via `setup.py`, e.g. downloading the source code and running `python setup.py install`.

## Disclaimer

If a crash is observed frequently or reproducibly, it should be diagnosed – e.g. with `faulthandler` (another Python module) and `gdb`. If you somehow manage to generate a segmentation fault in the `faultguard` data dictionary, and therefore destroy the guard process, the rescue will of course not work. Preventing faults from happening in the first place is always the most important, so don't rely solely on this module, just use it as an additional safety net!

## Credit

This project was initially developed for a hardware project at the University of Münster.
