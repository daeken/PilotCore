import time
from pilotcore import *

pilot = PilotCore()
pilot.exclude_part_resources('Sepratron I')
pilot.sas = True
pilot.throttle = 1
pilot.autostage = True

print 'Launching'
pilot.run_until(lambda: pilot.mean_altitude > 1000)

pilot.target_heading = 90
pilot.target_roll = 90
pilot.target_pitch = 45
pilot.autopilot_engaged = True
print 'Executing pitchover phase 1'
pilot.run_until(lambda: pilot.mean_altitude > 15000)

pilot.target_pitch = 20
print 'Executing pitchover phase 2'
pilot.run_until(lambda: pilot.apoapsis > 100000)
pilot.autopilot_engaged = False

pilot.sas = True
pilot.throttle = 0
print 'Waiting for orbital insertion burn'
pilot.wait_until(lambda: pilot.mean_altitude >= 99900)

prev_ap = pilot.apoapsis

pilot.throttle = 1
pilot.target_pitch = 0
pilot.autopilot_engaged = True
print 'Performing orbital insertion burn'
pilot.run_until(lambda: pilot.periapsis > prev_ap)
pilot.autopilot_engaged = False
pilot.throttle = 0
pilot.sas = True

print 'Done'
