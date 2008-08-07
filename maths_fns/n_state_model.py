###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# relax is distributed in the hope that it will be useful,                    #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with relax; if not, write to the Free Software                        #
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA   #
#                                                                             #
###############################################################################

# Python module imports.
from copy import deepcopy
from numpy import array, dot, float64, ones, transpose, zeros

# relax module imports.
from alignment_tensor import dAi_dAxx, dAi_dAyy, dAi_dAxy, dAi_dAxz, dAi_dAyz, to_tensor
from chi2 import chi2, dchi2_element, d2chi2_element
from float import isNaN
from pcs import ave_pcs_tensor, ave_pcs_tensor_dDij_dAmn, pcs_tensor
from rdc import ave_rdc_tensor, ave_rdc_tensor_dDij_dAmn, rdc_tensor
from rotation_matrix import R_euler_zyz


class N_state_opt:
    """Class containing the target function of the optimisation of the N-state model."""

    def __init__(self, model=None, N=None, init_params=None, full_tensors=None, red_data=None, red_errors=None, full_in_ref_frame=None, pcs=None, pcs_errors=None, rdcs=None, rdc_errors=None, xh_vect=None, dip_const=None, scaling_matrix=None):
        """Set up the class instance for optimisation.

        All constant data required for the N-state model are initialised here.


        @keyword model:         The N-state model type.  This can be one of '2-domain', 'population'
                                or 'fixed'.
        @type model:            str
        @keyword N:             The number of states.
        @type N:                int
        @keyword init_params:   The initial parameter values.  Optimisation must start at some
                                point!
        @type init_params:      numpy float64 array
        @keyword full_tensors:  A list of the full alignment tensors in matrix form.
        @type full_tensors:     list of 3x3 numpy matricies
        @keyword red_data:      An array of the {Sxx, Syy, Sxy, Sxz, Syz} values for all reduced
                                tensors.  The format is [Sxx1, Syy1, Sxy1, Sxz1, Syz1, Sxx2, Syy2,
                                Sxy2, Sxz2, Syz2, ..., Sxxn, Syyn, Sxyn, Sxzn, Syzn]
        @type red_data:         numpy float64 array
        @keyword red_errors:    An array of the {Sxx, Syy, Sxy, Sxz, Syz} errors for all reduced
                                tensors.  The array format is the same as for red_data.
        @type red_errors:       numpy float64 array
        @keyword pcs:           The PCS lists.  The first index must correspond to the different
                                alignment media i and the second index to the spin systems j.
        @type pcs:              numpy matrix
        @keyword pcs_errors:    The PCS error lists.  The dimensions of this argument are the same
                                as for 'pcs'.
        @type pcs_errors:       numpy matrix
        @keyword rdcs:          The RDC lists.  The first index must correspond to the different
                                alignment media i and the second index to the spin systems j.
        @type rdcs:             numpy matrix
        @keyword rdc_errors:    The RDC error lists.  The dimensions of this argument are the same
                                as for 'rdcs'.
        @type rdc_errors:       numpy matrix
        @keyword xh_vect:       The unit XH vector lists.  The first index must correspond to the
                                spin systems and the second index to each structure (its size being
                                equal to the number of states).
        @type xh_vect:          numpy matrix
        @keyword dip_const:     The dipolar constants for each XH vector.  The indices correspond to
                                the spin systems j.
        @scaling_matrix:        The square and diagonal scaling matrix.
        @scaling_matrix:        numpy rank-2 array
        """

        # Store the data inside the class instance namespace.
        self.N = N
        self.params = 1.0 * init_params    # Force a copy of the data to be stored.
        self.deltaij = pcs
        self.Dij = rdcs
        self.mu = xh_vect
        self.dip_const = dip_const
        self.total_num_params = len(init_params)

        # Initialise the function value, gradient, and Hessian.
        self.chi2 = 0.0
        self.dchi2 = zeros((self.total_num_params), float64)
        self.d2chi2 = zeros((self.total_num_params, self.total_num_params), float64)

        # Scaling initialisation.
        self.scaling_matrix = scaling_matrix
        if self.scaling_matrix != None:
            self.scaling_flag = True
        else:
            self.scaling_flag = False

        # The 2-domain N-state model.
        if model == '2-domain':
            # Some checks.
            if red_data == None and not len(red_data):
                raise RelaxError, "The red_data argument " + `red_data` + " must be supplied."
            if red_errors == None and not len(red_errors):
                raise RelaxError, "The red_errors argument " + `red_errors` + " must be supplied."
            if full_in_ref_frame == None and not len(full_in_ref_frame):
                raise RelaxError, "The full_in_ref_frame argument " + `full_in_ref_frame` + " must be supplied."

            # Tensor set up.
            self.full_tensors = array(full_tensors, float64)
            self.num_tensors = len(self.full_tensors)
            self.red_data = red_data
            self.red_errors = red_errors
            self.full_in_ref_frame = full_in_ref_frame

            # Initialise some empty numpy objects for storage of:
            # R:  the transient rotation matricies.
            # RT:  the transposes of the rotation matricies.
            # red_bc:  the back-calculated reduced alignment tensors.
            # red_bc_vector:  the back-calculated reduced alignment tensors in vector form {Sxx, Syy, Sxy, Sxz, Syz}.
            self.R = zeros((self.N,3,3), float64)
            self.RT = zeros((self.N,3,3), float64)
            self.red_bc = zeros((self.num_tensors,3,3), float64)
            self.red_bc_vector = zeros(self.num_tensors*5, float64)

            # Set the target function.
            self.func = self.func_2domain

        # The flexible population N-state model.
        elif model == 'population':
            # Some checks.
            if xh_vect == None and not len(xh_vect):
                raise RelaxError, "The xh_vect argument " + `xh_vect` + " must be supplied."

            # The total number of spins.
            if rdcs != None:
                self.num_spins = len(rdcs[0])
            else:
                self.num_spins = len(pcs[0])

            # The total number of alignments.
            if rdcs != None:
                self.num_align = len(rdcs)
            else:
                self.num_align = len(pcs)
            self.num_align_params = self.num_align * 5

            # PCS errors.
            if pcs_errors == None:
                # Missing errors.
                self.pcs_sigma_ij = ones((self.num_align, self.num_spins), float64)
            else:
                self.pcs_sigma_ij = pcs_errors

            # RDC errors.
            if rdc_errors == None:
                # Missing errors.
                self.rdc_sigma_ij = ones((self.num_align, self.num_spins), float64)
            else:
                self.rdc_sigma_ij = rdc_errors

            # Alignment tensor function and gradient matrices.
            self.A = zeros((self.num_align, 3, 3), float64)
            self.dA = zeros((5, 3, 3), float64)

            # The alignment tensor gradients don't change, so pre-calculate them.
            dAi_dAxx(self.dA[0])
            dAi_dAyy(self.dA[1])
            dAi_dAxy(self.dA[2])
            dAi_dAxz(self.dA[3])
            dAi_dAyz(self.dA[4])

            # Missing data matrices.
            self.missing_Dij = zeros((self.num_align, self.num_spins), float64)
            for i in xrange(self.num_align):
                for j in xrange(self.num_spins):
                    if isNaN(self.Dij[i, j]):
                        self.missing_Dij[i, j] = 1
            self.missing_deltaij = zeros((self.num_align, self.num_spins), float64)
            for i in xrange(self.num_align):
                for j in xrange(self.num_spins):
                    if isNaN(self.deltaij[i, j]):
                        self.missing_deltaij[i, j] = 1


            # PCS function, gradient, and Hessian matrices.
            self.detaij_theta = zeros((self.num_align, self.num_spins), float64)
            self.ddetaij_theta = zeros((self.total_num_params, self.num_align, self.num_spins), float64)
            self.d2detaij_theta = zeros((self.total_num_params, self.total_num_params, self.num_align, self.num_spins), float64)

            # RDC function, gradient, and Hessian matrices.
            self.Dij_theta = zeros((self.num_align, self.num_spins), float64)
            self.dDij_theta = zeros((self.total_num_params, self.num_align, self.num_spins), float64)
            self.d2Dij_theta = zeros((self.total_num_params, self.total_num_params, self.num_align, self.num_spins), float64)

            # Set the target function, gradient, and Hessian.
            self.func = self.func_population
            self.dfunc = self.dfunc_population
            self.d2func = self.d2func_population


    def func_2domain(self, params):
        """The target function for optimisation of the 2-domain N-state model.

        This function should be passed to the optimisation algorithm.  It accepts, as an array, a
        vector of parameter values and, using these, returns the single chi-squared value
        corresponding to that coordinate in the parameter space.  If no tensor errors are supplied,
        then the SSE (the sum of squares error) value is returned instead.  The chi-squared is
        simply the SSE normalised to unit variance (the SSE divided by the error squared).

        @param params:  The vector of parameter values.
        @type params:   list of float
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Reset the back-calculated the reduced tensor structure.
        self.red_bc = self.red_bc * 0.0

        # Loop over the N states.
        for c in xrange(self.N):
            # The rotation matrix.
            R_euler_zyz(self.R[c], params[self.N-1+3*c], params[self.N-1+3*c+1], params[self.N-1+3*c+2])

            # Its transpose.
            self.RT[c] = transpose(self.R[c])

            # The probability of state c.
            if c < self.N-1:
                pc = params[c]

            # The probability of state N (1 minus the pc of all other states).
            else:
                pc = 1.0
                for c2 in xrange(self.N-1):
                    pc = pc - params[c2]

            # Back-calculate the reduced tensors for sum element c and add these to red_bc.
            for i in xrange(self.num_tensors):
                # Normal RT.X.R rotation.
                if self.full_in_ref_frame[i]:
                    self.red_bc[i] = self.red_bc[i]  +  pc * dot(self.RT[c], dot(self.full_tensors[i], self.R[c]))

                # Inverse R.X.RT rotation.
                else:
                    self.red_bc[i] = self.red_bc[i]  +  pc * dot(self.R[c], dot(self.full_tensors[i], self.RT[c]))

        # 5D vectorise the back-calculated tensors (create red_bc_vector from red_bc).
        for i in xrange(self.num_tensors):
            self.red_bc_vector[5*i]   = self.red_bc[i,0,0]    # Sxx.
            self.red_bc_vector[5*i+1] = self.red_bc[i,1,1]    # Syy.
            self.red_bc_vector[5*i+2] = self.red_bc[i,0,1]    # Sxy.
            self.red_bc_vector[5*i+3] = self.red_bc[i,0,2]    # Sxz.
            self.red_bc_vector[5*i+4] = self.red_bc[i,1,2]    # Syz.

        # Return the chi-squared value.
        return chi2(self.red_data, self.red_bc_vector, self.red_errors)


    def func_population(self, params):
        """The target function for optimisation of the flexible population N-state model.

        Description
        ===========

        This function should be passed to the optimisation algorithm.  It accepts, as an array, a
        vector of parameter values and, using these, returns the single chi-squared value
        corresponding to that coordinate in the parameter space.  If no RDC errors are supplied,
        then the SSE (the sum of squares error) value is returned instead.  The chi-squared is
        simply the SSE normalised to unit variance (the SSE divided by the error squared).


        Indices
        =======

        For this calculation, five indices are looped over and used in the various data structures.
        These include:
            - i, the index over alignments,
            - j, the index over spin systems,
            - c, the index over the N-states (or over the structures),
            - n, the index over the first dimension of the alignment tensor n = {x, y, z},
            - m, the index over the second dimension of the alignment tensor m = {x, y, z}.


        Equations
        =========

        To calculate the function value, a chain of equations are used.  This includes the
        chi-squared equation and the RDC equation.


        The chi-squared equation
        ------------------------

        The equations are::

                         ___
                         \    (Dij - Dij(theta)) ** 2
         chi^2(theta)  =  >   ----------------------- ,
                         /__       sigma_ij ** 2
                          ij

                         ___
                         \    (delta_ij - delta_ij(theta)) ** 2
         chi^2(theta)  =  >   --------------------------------- ,
                         /__             sigma_ij ** 2
                          ij

        where:
            - theta is the parameter vector,
            - Dij are the measured RDCs for alignment i, spin j,
            - Dij(theta) are the back calculated RDCs for alignment i, spin j,
            - delta_ij are the measured PCSs for alignment i, spin j,
            - delta_ij(theta) are the back calculated PCSs for alignment i, spin j,
            - sigma_ij are the RDC or PCS errors.

        Both chi-squared values sum.


        The RDC equation
        ----------------

        The RDC equation is::

                           _N_
                           \              T
         Dij(theta)  =  dj  >   pc . mu_jc . Ai . mu_jc,
                           /__
                           c=1

        where:
            - dj is the dipolar constant for spin j,
            - N is the total number of states or structures,
            - pc is the weight or probability associated with state c,
            - mu_jc is the unit vector corresponding to spin j and state c,
            - Ai is the alignment tensor.

        The dipolar constant is henceforth defined as::

            dj = 3 / (2pi) d',

        where the factor of 2pi is to convert from units of rad.s^-1 to Hertz, the factor of 3 is
        associated with the alignment tensor and the pure dipolar constant in SI units is::

                   mu0 gI.gS.h_bar
            d' = - --- ----------- ,
                   4pi    r**3

        where:
            - mu0 is the permeability of free space,
            - gI and gS are the gyromagnetic ratios of the I and S spins,
            - h_bar is Dirac's constant which is equal to Planck's constant divided by 2pi,
            - r is the distance between the two spins.


        The PCS equation
        ----------------

        The PCS equation is::

                               _N_
                               \                   T
            delta_ij(theta)  =  >  pc . djc . mu_jc . Ai . mu_jc,
                               /__
                               c=1

        where:
            - djc is the PCS constant for spin j and state c,
            - N is the total number of states or structures,
            - pc is the weight or probability associated with state c,
            - mu_jc is the unit vector corresponding to spin j and state c,
            - Ai is the alignment tensor.

        The PCS constant is defined as::

                 mu0 15kT   1
            dj = --- ----- ---- ,
                 4pi Bo**2 r**3

        where:
            - mu0 is the permeability of free space,
            - k is Boltzmann's constant,
            - T is the absolute temperature,
            - Bo is the magnetic field strength,
            - r is the distance between the paramagnetic centre (electron spin) and the nuclear spin.


        Stored data structures
        ======================

        There are a number of data structures calculated by this function and stored for subsequent
        use in the gradient and Hessian functions.  This include the back calculated RDCs and the
        alignment tensors.

        Dij(theta)
        ----------

        The back calculated RDCs.  This is a rank-2 tensor with indices {i, j}.

        delta_ij(theta)
        ---------------

        The back calculated PCS.  This is a rank-2 tensor with indices {i, j}.

        Ai
        --

        The alignment tensors.  This is a rank-3 tensor with indices {i, n, m}.


        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 array
        @return:        The chi-squared or SSE value.
        @rtype:         float
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Initial chi-squared (or SSE) value.
        chi2_sum = 0.0

        # Unpack the probabilities (located at the end of the parameter array).
        self.probs = params[-(self.N-1):]

        # Loop over each alignment.
        for i in xrange(self.num_align):
            # Create tensor i from the parameters.
            to_tensor(self.A[i], params[5*i:5*i + 5])

            # Loop over the spin systems j.
            for j in xrange(self.num_spins):
                # The back calculated RDC.
                if self.rdc_flag:
                    # Calculate the average RDC.
                    self.Dij_theta[i, j] = ave_rdc_tensor(self.dip_const[j], self.mu[j], self.N, self.A[i], weights=self.probs)

                    # Replace missing data with the back calculated value (to give a zero chi-squared for the missing element).
                    if self.missing_Dij[i, j]:
                        self.Dij[i, j] = self.Dij_theta[i, j]

                # The back calculated PCS.
                if self.pcs_flag:
                    # Calculate the average PCS.
                    self.deltaij_theta[i, j] = ave_pcs_tensor(self.pcs_const[j], self.mu[j], self.N, self.A[i], weights=self.probs)

                    # Replace missing data with the back calculated value (to give a zero chi-squared for the missing element).
                    if self.missing_deltaij[i, j]:
                        self.deltaij[i, j] = self.deltaij_theta[i, j]

            # Calculate and sum the single alignment chi-squared value (for the RDC).
            if self.rdc_flag:
                chi2_sum = chi2_sum + chi2(self.Dij[i], self.Dij_theta[i], self.rdc_sigma_ij[i])

            # Calculate and sum the single alignment chi-squared value (for the PCS).
            if self.pcs_flag:
                chi2_sum = chi2_sum + chi2(self.deltaij[i], self.deltaij_theta[i], self.pcs_sigma_ij[i])

        # Return the chi-squared value.
        return chi2_sum


    def dfunc_population(self, params):
        """The gradient function for optimisation of the flexible population N-state model.

        Description
        ===========

        This function should be passed to the optimisation algorithm.  It accepts, as an array, a
        vector of parameter values and, using these, returns the chi-squared gradient corresponding
        to that coordinate in the parameter space.  If no RDC errors are supplied, then the SSE (the
        sum of squares error) gradient is returned instead.  The chi-squared gradient is simply the
        SSE gradient normalised to unit variance (the SSE divided by the error squared).


        Indices
        =======

        For this calculation, six indices are looped over and used in the various data structures.
        These include:
            - k, the index over all parameters,
            - i, the index over alignments,
            - j, the index over spin systems,
            - c, the index over the N-states (or over the structures),
            - m, the index over the first dimension of the alignment tensor m = {x, y, z}.
            - n, the index over the second dimension of the alignment tensor n = {x, y, z},


        Equations
        =========

        To calculate the chi-squared gradient, a chain of equations are used.  This includes the
        chi-squared gradient, the RDC gradient and the alignment tensor gradient.


        The chi-squared gradient
        ------------------------

        The equation is::
                              ___
         dchi^2(theta)        \   / Dij - Dij(theta)     dDij(theta) \ 
         -------------  =  -2  >  | ----------------  .  ----------- |
            dthetak           /__ \   sigma_ij**2         dthetak    /
                              ij

        where:
            - theta is the parameter vector,
            - Dij are the measured RDCs or PCSs,
            - Dij(theta) are the back calculated RDCs or PCSs,
            - sigma_ij are the RDC or PCS errors,
            - dDij(theta)/dthetak is the RDC or PCS gradient for parameter k.


        The RDC gradient
        ----------------

        This gradient is different for the various parameter types.

        pc partial derivative
        ~~~~~~~~~~~~~~~~~~~~~

        The population parameter partial derivative is::

         dDij(theta)               T
         -----------  =  dj . mu_jc . Ai . mu_jc,
             dpc

        where:
            - dj is the dipolar constant for spin j,
            - mu_jc is the unit vector corresponding to spin j and state c,
            - Ai is the alignment tensor.

        Amn partial derivative
        ~~~~~~~~~~~~~~~~~~~~~~

        The alignment tensor element partial derivative is::

                            _N_
         dDij(theta)        \              T   dAi
         -----------  =  dj  >   pc . mu_jc . ---- . mu_jc,
            dAmn            /__               dAmn
                            c=1

        where:
            - dj is the dipolar constant for spin j,
            - pc is the weight or probability associated with state c,
            - mu_jc is the unit vector corresponding to spin j and state c,
            - dAi/dAmn is the partial derivative of the alignment tensor with respect to element
            Amn.


        The PCS gradient
        ----------------

        This gradient is also different for the various parameter types.

        pc partial derivative
        ~~~~~~~~~~~~~~~~~~~~~

        The population parameter partial derivative is::

         ddeltaij(theta)                T
         ---------------  =  djc . mu_jc . Ai . mu_jc,
              dpc

        where:
            - djc is the pseudocontact shift constant for spin j and state c,
            - mu_jc is the unit vector corresponding to spin j and state c,
            - Ai is the alignment tensor.

        Amn partial derivative
        ~~~~~~~~~~~~~~~~~~~~~~

        The alignment tensor element partial derivative is::

                            _N_
        ddelta_ij(theta)    \                   T   dAi
        ----------------  =  >  pc . djc . mu_jc . ---- . mu_jc,
              dAmn          /__                    dAmn
                            c=1

        where:
            - djc is the pseudocontact shift constant for spin j and state c,
            - pc is the weight or probability associated with state c,
            - mu_jc is the unit vector corresponding to spin j and state c,
            - dAi/dAmn is the partial derivative of the alignment tensor with respect to element
            Amn.


        The alignment tensor gradient
        -----------------------------

        The five unique elements of the tensor {Axx, Ayy, Axy, Axz, Ayz} give five different partial
        derivatives.  These are::

          dAi   | 1  0  0 |
         ---- = | 0  0  0 |,
         dAxx   | 0  0 -1 |

          dAi   | 0  0  0 |
         ---- = | 0  1  0 |,
         dAyy   | 0  0 -1 |

          dAi   | 0  1  0 |
         ---- = | 1  0  0 |,
         dAxy   | 0  0  0 |

          dAi   | 0  0  1 |
         ---- = | 0  0  0 |,
         dAxz   | 1  0  0 |

          dAi   | 0  0  0 |
         ---- = | 0  0  1 |.
         dAyz   | 0  1  0 |

        As these are invariant, they can be pre-calculated.


        Stored data structures
        ======================

        There are a number of data structures calculated by this function and stored for subsequent
        use in the Hessian function.  This include the back calculated RDC and PCS gradients and the
        alignment tensor gradients.

        dDij(theta)/dthetak
        -------------------

        The back calculated RDC gradient.  This is a rank-3 tensor with indices {k, i, j}.

        ddeltaij(theta)/dthetak
        -------------------

        The back calculated PCS gradient.  This is a rank-3 tensor with indices {k, i, j}.

        dAi/dAmn
        --------

        The alignment tensor gradients.  This is a rank-3 tensor with indices {5, n, m}.


        @param params:  The vector of parameter values.  This is unused as it is assumed that
                        func_population() was called first.
        @type params:   numpy rank-1 array
        @return:        The chi-squared or SSE gradient.
        @rtype:         numpy rank-1 array
        """

        # Scaling.
        if self.scaling_flag:
            params = dot(params, self.scaling_matrix)

        # Initial chi-squared (or SSE) gradient.
        self.dchi2 = self.dchi2 * 0.0

        # Loop over each alignment.
        for i in xrange(self.num_align):
            # Construct the Amn partial derivative components.
            for j in xrange(self.num_spins):
                # RDC.
                if self.rdc_flag:
                    self.dDij_theta[i*5, i, j] =   ave_rdc_tensor_dDij_dAmn(self.dip_const[j], self.mu[j], self.N, self.dA[0], weights=self.probs)
                    self.dDij_theta[i*5+1, i, j] = ave_rdc_tensor_dDij_dAmn(self.dip_const[j], self.mu[j], self.N, self.dA[1], weights=self.probs)
                    self.dDij_theta[i*5+2, i, j] = ave_rdc_tensor_dDij_dAmn(self.dip_const[j], self.mu[j], self.N, self.dA[2], weights=self.probs)
                    self.dDij_theta[i*5+3, i, j] = ave_rdc_tensor_dDij_dAmn(self.dip_const[j], self.mu[j], self.N, self.dA[3], weights=self.probs)
                    self.dDij_theta[i*5+4, i, j] = ave_rdc_tensor_dDij_dAmn(self.dip_const[j], self.mu[j], self.N, self.dA[4], weights=self.probs)

                # PCS.
                if self.pcs_flag:
                    self.ddeltaij_theta[i*5, i, j] =   ave_pcs_tensor_ddeltaij_dAmn(self.dip_const[j], self.mu[j], self.N, self.dA[0], weights=self.probs)
                    self.ddeltaij_theta[i*5+1, i, j] = ave_pcs_tensor_ddeltaij_dAmn(self.dip_const[j], self.mu[j], self.N, self.dA[1], weights=self.probs)
                    self.ddeltaij_theta[i*5+2, i, j] = ave_pcs_tensor_ddeltaij_dAmn(self.dip_const[j], self.mu[j], self.N, self.dA[2], weights=self.probs)
                    self.ddeltaij_theta[i*5+3, i, j] = ave_pcs_tensor_ddeltaij_dAmn(self.dip_const[j], self.mu[j], self.N, self.dA[3], weights=self.probs)
                    self.ddeltaij_theta[i*5+4, i, j] = ave_pcs_tensor_ddeltaij_dAmn(self.dip_const[j], self.mu[j], self.N, self.dA[4], weights=self.probs)

            # Construct the pc partial derivative gradient components, looping over each state.
            for c in xrange(self.N - 1):
                # Index in the parameter array.
                param_index = self.num_align_params + c

                # Loop over the spins.
                for j in xrange(self.num_spins):
                    # Calculate the RDC for state c (this is the pc partial derivative).
                    if self.rdc_flag:
                        self.dDij_theta[param_index, i, j] = rdc_tensor(self.dip_const[j], self.mu[j, c], self.A[i])

                    # Calculate the PCS for state c (this is the pc partial derivative).
                    if self.pcs_flag:
                        self.ddeltaij_theta[param_index, i, j] = pcs_tensor(self.dip_const[j], self.mu[j, c], self.A[i])

            # Construct the chi-squared gradient element for parameter k, alignment i.
            for k in xrange(self.total_num_params):
                # RDC part of the chi-squared gradient.
                if self.rdc_flag:
                    self.dchi2[k] = self.dchi2[k] + dchi2_element(self.Dij[i], self.Dij_theta[i], self.dDij_theta[k, i], self.rdc_sigma_ij[i])

                # PCS part of the chi-squared gradient.
                if self.pcs_flag:
                    self.dchi2[k] = self.dchi2[k] + dchi2_element(self.deltaij[i], self.deltaij_theta[i], self.ddeltaij_theta[k, i], self.pcs_sigma_ij[i])

        # Diagonal scaling.
        if self.scaling_flag:
            self.dchi2 = dot(self.dchi2, self.scaling_matrix)

        # The gradient.
        return self.dchi2


    def d2func_population(self, params):
        """The Hessian function for optimisation of the flexible population N-state model.

        This function should be passed to the optimisation algorithm.  It accepts, as an array, a
        vector of parameter values and, using these, returns the chi-squared Hessian corresponding
        to that coordinate in the parameter space.  If no RDC errors are supplied, then the SSE (the
        sum of squares error) Hessian is returned instead.  The chi-squared Hessian is simply the
        SSE Hessian normalised to unit variance (the SSE divided by the error squared).

        @param params:  The vector of parameter values.
        @type params:   numpy rank-1 array
        @return:        The chi-squared or SSE Hessian.
        @rtype:         numpy rank-2 array
        """
