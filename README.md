# Faultguard

[![Build Status](https://travis-ci.com/2xB/faultguard.svg?branch=master)](https://travis-ci.com/2xB/faultguard)
[![GitHub license](https://img.shields.io/github/license/2xB/faultguard.svg)](https://github.com/2xB/faultguard)
[![pypi version](https://img.shields.io/pypi/v/faultguard.svg)](https://pypi.org/project/faultguard/)

Preventing data loss of your Python3 application. Keeps important data both duplicated in memory and on disk.

## Overview

Usually, after a crash through e.g. a segmentation fault or a power outage, data of running applications is lost. In environments where this is problematic – e.g. when users should not loose their work or important data is collected –, `faultguard` prevents data loss in two ways:

 1. `faultguard` keeps the selected data automatically backed up in a second process. This way, if your Python application crashes - even with a segmentation fault caused e.g. by an external library -, in most cases the backup process is still running and immediately provides its data to a rescue handling function that you can define. This even allows you to e.g. provide users with a custom graphical dialog informing about the crash and providing options for the recovered data.
 
 2. `faultguard` can save the selected data automatically in customizable time intervals to a file from which it can be recovered on the next application launch.

### Example

An example using all features of `faultguard` can be found in `example.py`.

### Usage

To secure an application data using `faultguard`, you define a `launch` function that receives a custom data dictionary from `faultguard`. This dictionary, although working like a usual dictionary and accepting all content that can be serialized using `pickle`, is automatically backed up as described above. If the guarded application crashes, the backup process launches a crash handler in form of a `rescue` function also defined by you and provides it with the backed up dictionary. Additionally, if you provide `faultguard` with a time interval and a path for autosaves, it stores the data on disk and you can call the `recover` method to recover the file content and call your `rescue` function. `faultguard` will raise a `RuntimeError` when trying to write to an existing autosave file or reading the autosave file of a running process.

The `faultguard` interface is very simple - you just provide it with a `launch` and a `rescue` function and everything else works automatically. If you use autosaving, on application launch you should additionally check for backup files and use `is_active` to see if the process corresponding to an autosave file is still active. If not, that would show that `faultguard` did previously not exit properly, so you can then let `faultguard` `recover` the file.

### Technical description

On the technical side, the in-memory backup is realized through Python modules `pickle`, `multiprocessing` and `collections`, which are used to serialize and deserialize various types of data and provide the dictionary-like data type that is available in both the guarded application and the rescue handler process.
The Python module `signal` is used to ensure signals like keyboard interrupts are handled correctly and received by the guarded process.
The autosave functionality uses the Python module `lzma` for efficient compression of autosave files, `os` for file handling and `time` for measuring the time since a process corresponding to a backup file was last active.

Feel encouraged to look into the source code and to contribute through (well documented :D ) pull requests!

Faultguard is tested on Linux and Windows.

## Installation

This module is available via `pip install faultguard` or can be installed manually via `setup.py`, e.g. downloading the source code and running `pip install .` inside the downloaded folder.

## Disclaimer

If a crash is observed frequently or reproducibly, it should be diagnosed – e.g. with `faulthandler` (another Python module) and `gdb`. If you somehow manage to generate a segmentation fault in the `faultguard` data dictionary, and therefore destroy the guard process, the rescue will of course not work. Preventing faults from happening in the first place is always the most important, so don't rely solely on this module, just use it as an additional safety net!

## Credit

This project was initially developed for a hardware project at the University of Münster.
