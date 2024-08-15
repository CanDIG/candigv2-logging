# candigv2-logging
Common CanDIGv2 logging methods.


## To use this library:

Add the following to your requirements.txt:

```
candigv2-logging@git+https://github.com/CanDIG/candigv2-logging.git@develop
```

Then add `import candigv2.logging` to your code.


## To log in a module:

In the initial startup of your module's python code, e.g. `server.py` or similar, add:

```
import candigv2_logging.logging

candigv2_logging.logging.initialize()
```

Afterwards, instantiate a candigv2.logging.CanDIGLogger instance and use that to log:

```
from candigv2_logging.logging import CanDIGLogger


logger = CanDIGLogger(__file__)

...
    logger.log_message("INFO", f"whatever you want to log", request)
...
```