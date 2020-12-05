v2.1 - Classy Cleric
=====================

API Changes
-----------

* LogDevice has been nested into InspyLogger
    - LogDevice.add_child added, moving InSPy-Logger even close to being an all-encompassing logging solution
    - LogDevice.manifest keeps a list of dictionaries for each child-logger you create
    - LogDevice.root_name keeps track of your root logger's name
    - LogDevice.start can be called to start the root logger

* Added ability to check PyPi for updates

* Fixed bug that caused any program using inspy-logger while offline would experience a fatal exception [issue #21](https://github.com/Inspyre-Softworks/inSPy-Logger/issues/21)
