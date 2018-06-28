import numpy as np
from math import acos, cos
from mpi4py import MPI


comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()


# compute integral process with parallel collective process
def integral(a_i, h, n):
	# compute inner sum
	integ = 0.0
	for j in range(n):
		a_ij = a_i + (j + 0.5) * h
		integ += cos(a_ij) * h
	return integ


if __name__ == '__main__':
	pi = 3.14159265359	
	a = 0.0
	b = pi/2.0
	dest = 0
	my_int = np.zeros(1)
	integral_sum = np.zeros(1)

	if rank == 0:
		n = np.full(1, 500, dtype=int)
	else:
		n = np.zeros(1, dtype=int)

	# broadcast n to all processes
	print('Process ', rank, ' before n = ', n[0])
	comm.Bcast(n, root=0)
	print('Process ', rank, ' after n = ', n[0])

	# compute partition
	h = (b - a)/(n * size) # calculate h after n is received
	a_i = a + rank * n * h
	my_int[0] = integral(a_i, h, n[0])

	# send partition back to root process, and compute sum across all processes
	print('Process ', rank, ' has the partial integral ', my_int[0])
	comm.Reduce(my_int, integral_sum, MPI.SUM, dest)

	if rank == 0:
		# print sum only in process 0
		print('The integral sum = ', integral_sum[0])
	