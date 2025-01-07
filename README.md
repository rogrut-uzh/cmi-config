# CMI Config

This repository includes information about the CMI configuration of every CMI mandant. The data is saved in the file `static\cmi-config.xml`. 

For accessing the data, this repo also includes a REST API that works with Python 3 and is accessible on http://localhost:5001/api/data.

See comments in `cmi-config-rest-api.py` for more details.

## Windows Service "cmi-config-api"

Created with nssm ([The Non-Sucking Service Manager](https://nssm.cc/)).

  - `nssm install cmi-config-api`
  - `nssm edit cmi-config-api`
    - Path: `python.exe`
    - Startup Directory: `D:\gitlab\cmi-config`
    - Arguments: `D:\gitlab\cmi-config\cmi-config-rest-api.py`
  - Logon with Local System account, Startup Automatic.