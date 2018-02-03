import time
from pilotcore import *

pilot = PilotCore()
pilot.sas = True
pilot.point_sas = 'retrograde'
pilot.throttle = 1
pilot.autostage = True

print 'Performing deorbit burn'
pilot.run_until(lambda: pilot.periapsis < 20000)

pilot.throttle = 0
pilot.autostage = False

print 'Waiting to ditch engines'
pilot.wait_until(lambda: pilot.mean_altitude < 40000)

while pilot.stage > 1:
	time.sleep(1)
	pilot.do_stage()

print 'Waiting for parachute deployment'
pilot.wait_until(lambda: pilot.mean_altitude < 2500)

print 'Deploying parachutes'
pilot.do_stage()

print 'Done'
