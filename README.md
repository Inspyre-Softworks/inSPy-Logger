# inSPy-Logger

![GitHub Workflow Status](https://img.shields.io/github/workflow/status/Inspyre-Softworks/inSPy-Logger/CI?label=CI&logo=github&logoColor=9cf&style=for-the-badge)
![Codacy grade](https://img.shields.io/codacy/grade/7171eec682c549a88dee0da9cc9b92b3?logo=codacy&logoColor=9cf&style=for-the-badge)
![GitHub release (latest by date including pre-releases)](https://img.shields.io/github/v/release/Inspyre-Softworks/inSPy-Logger?color=9cf&include_prereleases&label=Pre-Release&logo=pypi&logoColor=9cf&style=for-the-badge)
![PyPI](https://img.shields.io/pypi/v/inspy-logger?color=9cf&label=Latest&logo=pypi&logoColor=9cf&style=for-the-badge)
![GitHub issues](https://img.shields.io/github/issues/Inspyre-Softworks/inSPy-Logger?color=9cf&logo=github&logoColor=9cf&style=for-the-badge)
![PyPI - Format](https://img.shields.io/pypi/format/inSPy-Logger?logo=PyPi&style=for-the-badge)

## Installation

### Prerequisites:

**Platform/Env**:

* **Python**: ^3.6.3
* **PIP**: (_If you want to install via PIP, that is_)

**inSPy-Logger Runtime Dependencies**:
I am providing this list of dependencies for transparency and for instances where one would not be able to install
inSPy-Logger via PyPi's package manager. It is **highly** recommended you
use `python3 -m pip install inspy_logger==<ver>` to install inSPy-Logger 2.0+

* [colorlog](https://pypi.org/project/colorlog) (^4.2.1)
* [setuptools-autover](https://pypi.org/project/setuptools-autover) = (^1.0.2)
* [luddite](https://pypi.org/project/luddite) = (^1.0.1)
* [packaging](https://pypi.org/project/packaging) = (^20.4)

### Installation via Pip on Python 3.6.3+ (recommended method):

- `$> python3 -m pip install inspy_logger==<version>`

#### Test out InspyLogger:

```python3

import inspy_logger

# Initialize the main IL class. This structure will help
# manage/keep track of a child loggers and the root logger
il = inspy_logger.InspyLogger()


# Initialize the LogDevice class which will be a more direct
# way to manipulate and take advantage of it's manifest
#
# Information on the two parameters:
#     1) A string that will be the name of our root logger device
#     2) A string that matches ones of the following:
#         - debug
#         - info
#         - warning
#         - error
il_device = il.LogDevice("TestApp", "debug")

```

> Note:
>    It's important to take note that the logger device isn't started yet [INSERT LINK TO MORE INFO]

So, we have our device, let's start it. We'll be basic in this readme. You can look in the examples/ directory.

```python3

r_log = il_device.start()

# Now we'll 
def do_a_thing():

# Set up a log device object. The first parameter is the root loggers name, and the second is the debug level
log_device = inspy_logger.InspyLogger('LogName', 'debug')

# Start a running log from that device
log = log_device.start()

# Output our own logger lines:
log.debug('This is a debug log entry')
log.info('This is an info log entry')
log.warning('This is a warning log entry!')
log.error('This is an error log entry!')
log.exception('This is an exception log entry!')

```

If you run the code above you'll get output similar to this:

![output1](https://github.com/Inspyre-Softworks/inSPy-Logger/blob/v2.0-alpha.6/examples/v2.0/output_screenies/v2.0.0a.6_screenie1.png)

v2.0+ repository for inSPy-Logger
