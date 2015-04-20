# Drivers for tomograph

### Git structure
  - tango_ds - TANGO device servers for X-Ray source, X-Ray shutter, motor and 2D detector
  - docs - documentation
  - test - unit tests for client side
  
### Run server
    
  ```shell
    tango_ds/run.sh
  ```
  
### Stop server

  **Warning: stop script just kills all processes containing `python` substring in their name**
  ```shell
    tango_ds/stop.sh
  ```
  
### Run tests

  ```shell
    cd test
    py.test
  ```
  
### Documentation

  Documentation is available at (rbtm.readthedocs.org)[http://rbtm.readthedocs.org/en/latest/client.html]
