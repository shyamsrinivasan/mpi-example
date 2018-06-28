from predator_prey import rhs_fun
from solve_ode import solve_ode
import numpy as np
import mpi4py as MPI


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


p = np.array([.5, .02, .4, .004])
yinitial = [np.array([10, .0001]), np.array([2, .0001]), 
			np.array([3, 0.0001]), np.array([0.0001, 10])]

t, yout = solve_ode(rhs_fun, y0=yinitial, system_par=p)

print('time course :\n', t, '\n', 'ode solution :\n', yout)
