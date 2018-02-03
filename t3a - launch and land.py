import time
from pilotcore import *

pilot = PilotCore()
pilot.sas = True
pilot.throttle = 1
pilot.autostage = True

print 'Launching'
pilot.run_until(lambda: pilot.stage == 1)

print 'Waiting for parachute deploy point'
pilot.wait_until(lambda: pilot.mean_altitude < 500)

print 'Deploying parachutes'
pilot.do_stage()
