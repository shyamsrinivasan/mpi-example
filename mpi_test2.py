import numpy as np
from mpi4py import MPI


comm = MPI.COMM_WORLD
rank = comm.Get_rank()

randNum = np.zeros(1)
diffNum = np.random.random_sample(1)

if rank == 1:
	randNum = np.random.random_sample(1)
	print('Process', rank, 'drew number', randNum[0])
	comm.Isend(randNum, dest=0)
	# overlapping operation
	diffNum /= 3.14
	print('diffNum=', diffNum[0])
	req = comm.Irecv(randNum, source=0)
	req.Wait()
	print('Process', rank, 'received the number', randNum[0])

if rank == 0:
	print('Process', rank, 'before receiving has the number', randNum[0])
	req = comm.Irecv(randNum, source=1)
	req.Wait()
	# comm.Recv(randNum, source=MPI.ANY_SOURCE)
	print('Process', rank, 'received the number', randNum[0])
	randNum *= 2
	comm.Isend(randNum, dest=1)