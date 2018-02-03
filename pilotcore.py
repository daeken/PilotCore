import krpc, math, time

POLLFREQ = 0.1

def to_property(stream):
	return property(lambda c: stream())

def pass_property(obj, name):
	getter = property(getattr(obj, name))
	setter = getter.setter(lambda _, value: setattr(obj, name, value))
	return setter

class PilotCore(object):
	def __init__(self):
		self.conn = krpc.connect(name='DAP')
		self.conn.prop_stream = lambda *args: to_property(self.conn.add_stream(*args))
		self.conn.prop_as_stream = lambda *args: to_property(self.conn.add_stream(getattr, *args))
		self.vessel = self.conn.space_center.active_vessel
		self.orbit = self.vessel.orbit
		self.flight = self.vessel.flight(self.vessel.orbit.body.reference_frame)
		self.autopilot = self.vessel.auto_pilot
		self._autopilot_engaged = False
		self.control = self.vessel.control

		self.autostage = False
		self.autostage_delay = 0

		PilotCore.stage = self.conn.prop_as_stream(self.control, 'current_stage')
		PilotCore.speed = self.conn.prop_as_stream(self.flight, 'speed')
		PilotCore.mean_altitude = self.conn.prop_as_stream(self.flight, 'mean_altitude')

		PilotCore.sas = pass_property(self.control, 'sas')
		PilotCore.throttle = pass_property(self.control, 'throttle')

		PilotCore.target_pitch = pass_property(self.autopilot, 'target_pitch')
		PilotCore.target_heading = pass_property(self.autopilot, 'target_heading')
		PilotCore.target_roll = pass_property(self.autopilot, 'target_roll')

		PilotCore.apoapsis = self.conn.prop_as_stream(self.orbit, 'apoapsis_altitude')
		PilotCore.periapsis = self.conn.prop_as_stream(self.orbit, 'periapsis_altitude')

		self.numstages = self.stage + 1
		self.stage_fuel_offsets = [0] * self.numstages

	def all_parts(self, root=None):
		root = self.vessel.parts.root if root is None else root
		yield root
		for child in root.children:
			for elem in self.all_parts(child):
				yield elem

	def exclude_part_resources(self, *names):
		for part in self.all_parts():
			if part.title in names:
				self.stage_fuel_offsets[part.stage] -= part.resources.amount('SolidFuel') + part.resources.amount('LiquidFuel')

	def do_stages(self, count=1):
		for i in xrange(count):
			self.control.activate_next_stage()
	do_stage = do_stages

	@property
	def autopilot_engaged(self):
		return self._autopilot_engaged
	@autopilot_engaged.setter
	def autopilot_engaged(self, value):
		if value == self._autopilot_engaged:
			return
		self._autopilot_engaged = value
		if value:
			self.autopilot.engage()
		else:
			self.autopilot.disengage()

	@property
	def point_sas(self):
		pass # XXX
	@point_sas.setter
	def point_sas(self, value):
		self.control.sas_mode = getattr(self.conn.space_center.SASMode, value)

	@property
	def fuel_in_stage(self):
		if self.stage == self.numstages:
			return 0
		res = self.vessel.resources_in_decouple_stage(stage=self.stage - 1, cumulative=False)
		amt = res.amount('LiquidFuel') + res.amount('SolidFuel') + self.stage_fuel_offsets[self.stage - 1]
		return amt if amt > 0 else 0

	def run_until(self, cond):
		while not cond():
			if self.stage != 0 and self.autostage and self.fuel_in_stage == 0:
				print 'No fuel [left] in this stage'
				time.sleep(self.autostage_delay)
				self.do_stage()
				continue

			time.sleep(POLLFREQ)

	def wait_until(self, cond):
		while not cond():
			time.sleep(POLLFREQ)
