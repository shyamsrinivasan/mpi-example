from math import acos, cos


# compute integral process serially and compare with parallel performance
def integral(a_i, h, n):
	# compute inner sum
	integ = 0.0
	for j in range(n):
		a_ij = a_i + (j + 0.5) * h
		integ += cos(a_ij) * h
	return integ


if __name__ == '__main__':
	pi = 3.14159265359
	p = 4
	n = 500
	a = 0.0
	b = pi/2.0
	h = (b - a)/(n * p)

	integral_sum = 0.0

	# compute outer sum
	for i in range(p):
		a_i = a + i * n * h
		integral_sum += integral(a_i, h, n)

	print('The integral = ', integral_sum)