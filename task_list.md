# Task list

 * Revise setup.py/requirements.txt/Dockerfile to include database_connection dependency
 * Add worker that sends data to Honeycomb
 * Add worker that sends data to Celery (thence to Honeycomb)
 * Combine workers (switch destination with command line option)?
 * Move details of data fields, etc. to shared constants
 * Record timestamps of individual ranges?
 * Record anchor IDs of ranges?
 * Fix dropouts?
 * Change strategy for distinguishing tags from other BLE devices?
