from Numeric import sqrt

def cubic(a, b, fa, fb, ga, gb):
	"""Cubic interpolation using f(a), f(b), g(a), and g(b).

	Equations
	~~~~~~~~~

	f(a) = a'a**3 + b'a**2 + c'a + d'
	f(b) = a'b**3 + b'b**2 + c'b + d'
	g(a) = 3a'a**2 + 2b'a + c'
	g(b) = 3a'b**2 + 2b'b + c'


	Solution
	~~~~~~~~

	       -2f(a) + 2f(b) + ag(a) - bg(a) + ag(b) - bg(b)
	a'  =  ----------------------------------------------
	                        (a - b)**3


	       -a**2g(a) - 2a**2g(b) + 3af(b) - 3af(b) - abg(a) + abg(b) + 3bf(a) - 3bf(b) + 2b**2g(a) + b**2g(b)
	b'  =  --------------------------------------------------------------------------------------------------
	                                                (a - b)**3


	       a**3g(b) + 2a**2bg(a) + a**2bg(b) - 6abf(a) + 6abf(b) - ab**2g(a) - 2ab**2g(b) - b**3g(a)
	c'  =  -----------------------------------------------------------------------------------------
	                                            (a - b)**3


	       a**3f(b) - a**3bg(b) - 3a**2bf(b) - a**2b**2g(a) + a**2b**2g(b) + 3ab**2f(a) + ab**3g(a) - b**3f(a)
	d'  =  ---------------------------------------------------------------------------------------------------
	                                                (a - b)**3


	Interpolation
	~~~~~~~~~~~~~

	The extrema are the roots of the quadratic equation:

		3a'*alpha**2 + 2b'*alpha + c' = 0

	The root for which the equation (6a'*alpha + 2b') is positive is the minimum.

	"""


	# Calculate the cooefficients.
	temp = (a-b)**3

	#a_prime = (-2.0*fa + 2.0*fb + a*ga - b*ga + a*gb - b*gb) / temp
	#b_prime = (-a**2*ga - 2.0*a**2*gb + 3.0*a*fa - 3.0*a*fb - a*b*ga + a*b*gb + 3.0*b*fa - 3.0*b*fb + 2.0*b**2*ga + b**2*gb) / temp
	#c_prime = (a**3*gb + 2.0*a**2*b*ga + a**2*b*gb - 6.0*a*b*fa + 6.0*a*b*fb - a*b**2*ga - 2.0*a*b**2*gb - b**3*ga) / temp
	a_prime = (2.0*(fb - fa) + (a - b)*(ga + gb))
	b_prime = (3.0*(a + b)*(fa - fb) + (2.0*b**2 - a**2 - a*b)*ga - (2.0*a**2 - a*b - b**2)*gb)
	c_prime = (6.0*a*b*(fb -fa) + b*(2.0*a**2 - a*b - b**2)*ga - a*(2.0*b**2 - a*b - a**2)*gb)

	# Find the extrema.
	temp2 = sqrt(b_prime**2 - 3.0*a_prime*c_prime)

	alpha = (-b_prime + temp2) / (3.0*a_prime)

	# Find the minimum.
	if (6.0*a_prime*alpha + 2.0*b_prime) * temp > 0.0:
		return alpha
	else:
		return -(b_prime + temp2) / (3.0*a_prime)


def quadratic_fafbga(a, b, fa, fb, ga):
	"""Quadratic interpolation using f(a), f(b), and g(a).

	The extremum of the quadratic is given by:

		       2af(a) + b**2g(a) - a(2f(b) + ag(a))
		aq  =  ------------------------------------
		           2(f(a) - f(b) + (b - a)g(a))
	"""

	top = 2.0*a*fa + b**2*ga - a*(2.0*fb + a*ga)
	bottom = 2.0*(fa - fb + (b - a)*ga)
	if bottom == 0.0:
		return 1e99
	else:
		return top / bottom


def quadratic_gagb(a, b, ga, gb):
	"""Quadratic interpolation using g(a) and g(b).

	The extremum of the quadratic is given by:

		       bg(a) - ag(b)
		aq  =  -------------
		        g(a) - g(b)
	"""

	temp = ga - gb
	if temp == 0.0:
		return 1e99
	else:
		return (b*ga - a*gb)/(ga - gb)
