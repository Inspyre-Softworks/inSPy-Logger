# CHANGELOG (Release Scope: v2.1a13 ~> v2.1a14)
#### Version 2.1 Alpha Build 14 (PyPi Release)
----

## API Changes

### Additions:
* **PROJECT_ROOT/inspy_logger/manifest.py**:
  * *New Class*: Manifest (Addressing issue #29)
    * **Functions**:
      * *add(log_name: str)*: Add an entry to the active Manifest instance.
      * *check(log_name: str)*: Check to see if the passed 'log_name' is found in the active Manifest instance's 'contents' attribute.
    * **Attributes**:
      * **contents**: The contents of the manifest. If you're accessing this via the API it might be worth noting that due to this class's utilization of the 'Box' package you can access keys in dot-signature format.


### Removals

None documented.


----


### Other Changes

* **PROJECT_ROOT/inspy_logger/__init__.py**:
  * Moved some code related to the manifest.
  * Changed 

