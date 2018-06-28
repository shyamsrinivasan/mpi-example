from assimulo.solvers import CVode
from assimulo.problem import Explicit_Problem


def solve_ode(rhsfun, y0, system_par):
	ode_function = lambda t, x : rhsfun(t, x, system_par)

	# define explicit assimulo problem
	prob = Explicit_Problem(ode_function, y0=y0)

	# create solver instance
	solver = CVode(prob)

	solver.iter = 'Newton'
	solver.discr = 'Adams'
	solver.atol = 1e-10
	solver.rtol = 1e-10
	solver.display_progress = True
	solver.verbosity = 10

	# simulate system
	time_course, y_result = solver.simulate(10, 200)
	return time_course, y_result