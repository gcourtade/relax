from copy import deepcopy
from math import pi
from re import match

from data import data

from jw_mf import *
from djw_mf import *

from ri_dipole_csa_comps import *

from ri_prime import *
from dri_prime import *

from ri import *
from dri import *

from chi2 import calc_chi2

class mf:
	def __init__(self, relax, equation=None, param_types=None, init_params=None, relax_data=None, errors=None, bond_length=None, csa=None, diff_type=None, diff_params=None, scaling=None, print_flag=0):
		"""The model-free minimisation class.

		This class should be initialised before every calculation.

		Arguments
		~~~~~~~~~

		relax:		The program base class self.relax
		equation:	The model-free equation string which should be either 'mf_orig' or 'mf_ext'.
		param_types:	An array of the parameter types used in minimisation.
		relax_data:	An array containing the experimental relaxation values.
		errors:		An array containing the experimental errors.
		bond_length:	The fixed bond length in meters.
		csa:		The fixed CSA value.
		diff_type:	The diffusion tensor string which should be either 'iso', 'axial', or 'aniso'.
		diff_params:	An array with the diffusion parameters.
		scaling:	An array with the factors by which to scale the parameter vector.
		print_flag:	A flag specifying how much should be printed to screen.


		"""

		# Arguments.
		self.relax = relax
		self.equation = equation
		self.param_types = param_types
		self.params = init_params
		self.scaling = scaling
		self.print_flag = print_flag

		# Initialise the data.
		self.init_data()
		self.data.params = init_params
		self.data.relax_data = relax_data
		self.data.errors = errors
		self.data.bond_length = bond_length
		self.data.csa = csa
		self.data.diff_type = diff_type
		self.data.diff_params = diff_params

		# Calculate the five frequencies per field strength which cause R1, R2, and NOE relaxation.
		self.calc_frq_list()

		# Calculate the fixed components of the dipolar and CSA constants.
		calc_fixed_csa(self.data)
		calc_fixed_dip(self.data)

		# Setup the equations.
		if not self.setup_equations():
			print "The model-free equations could not be setup."


	def calc_frq_list(self):
		"Calculate the five frequencies per field strength which cause R1, R2, and NOE relaxation."

		self.data.frq_list = zeros((self.relax.data.num_frq, 5), Float64)
		for i in range(self.relax.data.num_frq):
			frqH = 2.0 * pi * self.relax.data.frq[i]
			frqX = frqH * (self.relax.data.gx / self.relax.data.gh)
			self.data.frq_list[i, 1] = frqX
			self.data.frq_list[i, 2] = frqH - frqX
			self.data.frq_list[i, 3] = frqH
			self.data.frq_list[i, 4] = frqH + frqX

		self.data.frq_sqrd_list = self.data.frq_list ** 2


	def func(self, params, print_flag=0):
		"""The function for calculating the model-free chi-squared value.

		The chi-sqared equation
		~~~~~~~~~~~~~~~~~~~~~~~
		        _n_
		        \    (Ri - Ri()) ** 2
		Chi2  =  >   ----------------
		        /__    sigma_i ** 2
		        i=1

		where:
			Ri are the values of the measured relaxation data set.
			Ri() are the values of the back calculated relaxation data set.
			sigma_i are the values of the error set.

		"""

		# Arguments
		self.data.params = params
		self.print_flag = print_flag

		# Store the parameter vector in self.data.func_test
		self.data.func_test = params

		# Calculate the spectral density values.
		self.calc_jw_comps(self.data)
		create_jw_struct(self.data, self.calc_jw)

		# Calculate the R1, R2, and sigma_noe values.
		calc_ri_prime(self.data, self.ri_prime_funcs)

		# Calculate the R1, R2, and NOE values.
		self.data.ri = self.data.ri_prime
		calc_ri(self.data, self.ri_funcs)

		# Calculate the chi-squared value.
		self.data.chi2 = calc_chi2(self.data.relax_data, self.data.ri, self.data.errors)

		return self.data.chi2


	def dfunc(self, params, print_flag=0):
		"""The function for calculating the model-free chi-squared gradient vector.
		"""

		# Arguments
		self.data.params = params
		self.print_flag = print_flag

		# Calculate the spectral density values.
		create_djw_struct(self.data, self.calc_djw)

		# Calculate the R1, R2, and sigma_noe values.
		calc_dri_prime(self.data, self.dri_prime_funcs)

		# Calculate the R1, R2, and NOE values.
		self.data.dri = deepcopy(self.data.dri_prime)
		calc_dri(self.data, self.dri_funcs)

		# Calculate the chi-squared value.
		self.data.dchi2 = calc_dchi2(self.data.relax_data, self.data.dri, self.data.errors)

		return self.data.dchi2


	def d2func(self, params, print_flag=0):
		"asdf"


	def init_data(self):
		"Function for initialisation of the data."

		# Initialise the data class used to store data.
		self.data = data()

		# Place some data structures from self.relax.data into the data class
		self.data.gh = self.relax.data.gh
		self.data.gx = self.relax.data.gx
		self.data.g_ratio = self.relax.data.g_ratio
		self.data.h_bar = self.relax.data.h_bar
		self.data.mu0 = self.relax.data.mu0
		self.data.num_ri = self.relax.data.num_ri
		self.data.num_frq = self.relax.data.num_frq
		self.data.frq = self.relax.data.frq
		self.data.remap_table = self.relax.data.remap_table
		self.data.noe_r1_table = self.relax.data.noe_r1_table
		self.data.ri_labels = self.relax.data.ri_labels

		# Initialise the spectral density values, gradients, and hessians.
		self.data.jw = zeros((self.relax.data.num_frq, 5), Float64)
		self.data.djw = zeros((self.relax.data.num_frq, 5, len(self.params)), Float64)

		# Initialise the components of the transformed relaxation equations.
		self.data.dip_comps = zeros((self.relax.data.num_ri), Float64)
		self.data.dip_jw_comps = zeros((self.relax.data.num_ri), Float64)
		self.data.csa_comps = zeros((self.relax.data.num_ri), Float64)
		self.data.csa_jw_comps = zeros((self.relax.data.num_ri), Float64)
		self.data.rex_comps = zeros((self.relax.data.num_ri), Float64)

		self.data.dip_comps_prime = zeros((len(self.params), self.relax.data.num_ri), Float64)
		self.data.dip_jw_comps_prime = zeros((len(self.params), self.relax.data.num_ri), Float64)
		self.data.csa_comps_prime = zeros((len(self.params), self.relax.data.num_ri), Float64)
		self.data.csa_jw_comps_prime = zeros((len(self.params), self.relax.data.num_ri), Float64)
		self.data.rex_comps_prime = zeros((len(self.params), self.relax.data.num_ri), Float64)

		# Initialise the transformed relaxation values, gradients, and hessians.
		self.data.ri_prime = zeros((self.relax.data.num_ri), Float64)
		self.data.dri_prime = zeros((len(self.params), self.relax.data.num_ri), Float64)


	def lm_dri(self):
		"Return the function used for Levenberg-Marquardt minimisation."

		return self.data.dri


	def setup_equations(self):
		"Setup the equations used to calculate the chi-squared statistic."

		self.calc_djw = []
		for i in range(len(self.params)):
			self.calc_djw.append(None)

		# The original model-free equations.
		if match('mf_orig', self.equation):
			# Find the indecies of the parameters in self.param_types
			self.data.s2_index, self.data.te_index, self.data.rex_index, self.data.r_index, self.data.csa_index = None, None, None, None, None
			for i in range(len(self.param_types)):
				if match('S2', self.param_types[i]):
					self.data.s2_index = i
				elif match('te', self.param_types[i]):
					self.data.te_index = i
				elif match('Rex', self.param_types[i]):
					self.data.rex_index = i
				elif match('Bond length', self.param_types[i]):
					self.data.r_index = i
				elif match('CSA', self.param_types[i]):
					self.data.csa_index = i
				else:
					return 0

			# Setup the equations for the calculation of spectral density values.
			if self.data.s2_index != None and self.data.te_index != None:
				self.calc_jw = calc_iso_s2_te_jw
				self.calc_jw_comps = calc_iso_s2_te_jw_comps
				self.calc_djw[self.data.s2_index] = calc_iso_S2_te_djw_dS2
				self.calc_djw[self.data.te_index] = calc_iso_S2_te_djw_dte
			elif self.data.s2_index != None:
				self.calc_jw = calc_iso_s2_jw
				self.calc_jw_comps = calc_iso_s2_jw_comps
				self.calc_djw[self.data.s2_index] = calc_iso_S2_te_djw_dS2
			elif self.data.te_index != None:
				print "Invalid model, you cannot have te as a parameter without S2 existing as well."
				return 0
			else:
				print "Invalid combination of parameters for the original model-free equation."
				return 0

		# The extended model-free equations.
		elif match('mf_ext', self.equation):
			# Find the indecies of the parameters in self.param_types
			self.data.s2f_index, self.data.tf_index, self.data.s2s_index, self.data.ts_index, self.data.rex_index, self.data.r_index, self.data.csa_index,  = None, None, None, None, None, None, None
			for i in range(len(self.param_types)):
				if match('S2f', self.param_types[i]):
					self.data.s2f_index = i
				elif match('tf', self.param_types[i]):
					self.data.tf_index = i
				elif match('S2s', self.param_types[i]):
					self.data.s2s_index = i
				elif match('ts', self.param_types[i]):
					self.data.ts_index = i
				elif match('Rex', self.param_types[i]):
					self.data.rex_index = i
				elif match('Bond length', self.param_types[i]):
					self.data.r_index = i
				elif match('CSA', self.param_types[i]):
					self.data.csa_index = i
				else: return 0

			# Setup the equations for the calculation of spectral density values.
			if self.data.s2f_index != None and self.data.tf_index != None and self.data.s2s_index != None and self.data.ts_index != None:
				self.calc_jw = calc_iso_s2f_tf_s2s_ts_jw
				self.calc_jw_comps = calc_iso_s2f_tf_s2s_ts_jw_comps
				self.calc_djw[self.data.s2f_index] = calc_iso_S2f_S2s_ts_djw_dS2f
				self.calc_djw[self.data.tf_index] = calc_iso_S2f_S2s_ts_djw_dtf
				self.calc_djw[self.data.s2s_index] = calc_iso_S2f_S2s_ts_djw_dS2s
				self.calc_djw[self.data.ts_index] = calc_iso_S2f_S2s_ts_djw_dts
			elif self.data.s2f_index != None and self.data.tf_index == None and self.data.s2s_index != None and self.data.ts_index != None:
				self.calc_jw = calc_iso_s2f_s2s_ts_jw
				self.calc_jw_comps = calc_iso_s2f_s2s_ts_jw_comps
				self.calc_djw[self.data.s2f_index] = calc_iso_S2f_S2s_ts_djw_dS2f
				self.calc_djw[self.data.s2s_index] = calc_iso_S2f_S2s_ts_djw_dS2s
				self.calc_djw[self.data.ts_index] = calc_iso_S2f_S2s_ts_djw_dts
			else:
				print "Invalid combination of parameters for the extended model-free equation."
				return 0

		else:
			return 0


		# The transformed relaxation equations.
		self.ri_funcs = []
		self.ri_prime_funcs = []

		# Both the bond length and CSA are fixed.
		if self.data.r_index == None and self.data.csa_index == None:
			calc_dip_const(self.data)
			calc_csa_const(self.data)
			for i in range(self.relax.data.num_ri):
				# The R1 equations.
				if self.relax.data.ri_labels[i]  == 'R1':
					self.ri_funcs.append(None)
					self.ri_prime_funcs.append(calc_r1_prime)

				# The R2 equations.
				elif self.relax.data.ri_labels[i] == 'R2':
					self.ri_funcs.append(None)
					if self.data.rex_index == None:
						self.ri_prime_funcs.append(calc_r2_prime)
					else:
						self.ri_prime_funcs.append(calc_r2_rex_prime)

				# The NOE equations.
				elif self.relax.data.ri_labels[i] == 'NOE':
					self.ri_funcs.append(calc_noe)
					self.ri_prime_funcs.append(calc_sigma_noe)

		# The bond length is part of the parameter vector.
		elif self.data.r_index != None and self.data.csa_index == None:
			calc_csa_const(self.data)
			for i in range(self.relax.data.num_ri):
				# The R1 equations.
				if self.relax.data.ri_labels[i]  == 'R1':
					self.ri_funcs.append(None)
					self.ri_prime_funcs.append(calc_r1_prime_r)

				# The R2 equations.
				elif self.relax.data.ri_labels[i] == 'R2':
					self.ri_funcs.append(None)
					if self.data.rex_index == None:
						self.ri_prime_funcs.append(calc_r2_prime_r)
					else:
						self.ri_prime_funcs.append(calc_r2_rex_prime_r)

				# The NOE equations.
				elif self.relax.data.ri_labels[i] == 'NOE':
					self.ri_funcs.append(calc_noe)
					self.ri_prime_funcs.append(calc_sigma_noe_r)

		# The CSA is part of the parameter vector.
		elif self.data.r_index == None and self.data.csa_index != None:
			calc_dip_const(self.data)
			for i in range(self.relax.data.num_ri):
				# The R1 equations.
				if self.relax.data.ri_labels[i]  == 'R1':
					self.ri_funcs.append(None)
					self.ri_prime_funcs.append(calc_r1_prime_csa)

				# The R2 equations.
				elif self.relax.data.ri_labels[i] == 'R2':
					self.ri_funcs.append(None)
					if self.data.rex_index == None:
						self.ri_prime_funcs.append(calc_r2_prime_csa)
					else:
						self.ri_prime_funcs.append(calc_r2_rex_prime_csa)

				# The NOE equations.
				elif self.relax.data.ri_labels[i] == 'NOE':
					self.ri_funcs.append(calc_noe)
					self.ri_prime_funcs.append(calc_sigma_noe)

		# Both the bond length and CSA are part of the parameter vector.
		elif self.data.r_index != None and self.data.csa_index != None:
			for i in range(self.relax.data.num_ri):
				# The R1 equations.
				if self.relax.data.ri_labels[i]  == 'R1':
					self.ri_funcs.append(None)
					self.ri_prime_funcs.append(calc_r1_prime_r_csa)

				# The R2 equations.
				elif self.relax.data.ri_labels[i] == 'R2':
					self.ri_funcs.append(None)
					if self.data.rex_index == None:
						self.ri_prime_funcs.append(calc_r2_prime_r_csa)
					else:
						self.ri_prime_funcs.append(calc_r2_rex_prime_r_csa)

				# The NOE equations.
				elif self.relax.data.ri_labels[i] == 'NOE':
					self.ri_funcs.append(calc_noe)
					self.ri_prime_funcs.append(calc_sigma_noe_r)

		# Invalid combination of parameters.
		else:
			print "Invalid combination of parameters for the model-free equations."
			return 0

		return 1
