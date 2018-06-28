import predator_prey_model
from assimulo.solvers import CVode
from assimulo.problem import Explicit_Problem
import numpy as np


def rhs_fun(t, y, p):
	"""ode rhs fun for predator prey model using imported fortran code"""
	flux = predator_prey_model.all_flux(y, p)
	rhs = predator_prey_model.ode(flux)

	return rhs


def py_rhs_fun(t, y, p):
	alpha = p[0]
	beta = p[1]
	delta = p[2]
	gamma = p[3]

	flux = np.array([alpha*y[0], beta*y[0]*y[1], delta*y[0]*y[1], gamma*y[1]])
	rhs = np.array([flux[0]-flux[1], flux[2]-flux[3]])

	return rhs


if __name__=='__main__':    
	p = np.array([.5, .02, .4, .004])
	ode_function = lambda t, x : rhs_fun(t, x, p)

	# define explicit assimulo problem
	prob = Explicit_Problem(ode_function, y0=np.array([10, .0001]))

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

	print time_course
	print y_result