# Task list

* Make environment name a required argument for Honeycomb worker
* Add option of specifying environment ID rather than environment name
* Separate Honeycomb worker from main tray sensor repo?
* Revise setup.py/requirements.txt/Dockerfile to include new dependencies:
    - database_connection
    - database_connection_honeycomb
    - honeycomb
    - gqlpycgen
* Add worker that sends data to Celery (thence to Honeycomb)
* Add worker to assign tray sensors to environment?
* Add worker to configure tray sensors?
* Combine workers (switch destination with command line option)?
* Move details of data fields, etc. to shared constants
* Record timestamps of individual ranges?
* Record anchor IDs of ranges?
* Fix dropouts?
* Change strategy for distinguishing tags from other BLE devices?
