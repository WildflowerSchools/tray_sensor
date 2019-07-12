# Task list

 * Add worker to assign tray sensors to environment?
 * Add worker to configure tray sensors?
 * Make environment name a required argument for Honeycomb worker
 * Revise setup.py/requirements.txt/Dockerfile to include new dependencies:
  - database_connection
  - database_connection_honeycomb
  - honeycomb
  - gqlpycgen
 * Revise setup.py/requirements.txt/Dockerfile to include database_connection_honeycomb dependency
 * Add worker that sends data to Honeycomb
 * Add worker that sends data to Celery (thence to Honeycomb)
 * Combine workers (switch destination with command line option)?
 * Remove all of the old measurement database code
 * Move details of data fields, etc. to shared constants
 * Record timestamps of individual ranges?
 * Record anchor IDs of ranges?
 * Fix dropouts?
 * Change strategy for distinguishing tags from other BLE devices?
