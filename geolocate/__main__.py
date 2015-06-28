"""
 Geolocate launcher.

 Programmed by: Dante Signal31

 email: dante.signal31@gmail.com
"""
import geolocate.classes.system as system

system.verify_python_version(3, 0)

from geolocate.glocate import main

main()
