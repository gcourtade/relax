###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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

from copy import deepcopy
from LinearAlgebra import inverse
from math import pi
from Numeric import Float64, array, identity, matrixmultiply, ones, transpose, zeros
from re import match, search
from string import replace
import sys

from base_class import Common_functions
from maths_fns.mf import Mf
from minimise.generic import generic_minimise


class Model_free(Common_functions):
    def __init__(self, relax):
        """Class containing functions specific to model-free analysis."""

        self.relax = relax


    def are_mf_params_set(self, index=None):
        """Function for testing if the model-free parameter values are set."""

        # Alias the data structure.
        data = self.relax.data.res[self.run][index]

        # Loop over the model-free parameters.
        for j in xrange(len(data.params)):
            # tm.
            if data.params[j] == 'tm' and data.tm == None:
                return data.params[j]

            # S2.
            elif data.params[j] == 'S2' and data.s2 == None:
                return data.params[j]

            # S2f.
            elif data.params[j] == 'S2f' and data.s2f == None:
                return data.params[j]

            # S2s.
            elif data.params[j] == 'S2s' and data.s2s == None:
                return data.params[j]

            # te.
            elif data.params[j] == 'te' and data.te == None:
                return data.params[j]

            # tf.
            elif data.params[j] == 'tf' and data.tf == None:
                return data.params[j]

            # ts.
            elif data.params[j] == 'ts' and data.ts == None:
                return data.params[j]

            # Rex.
            elif data.params[j] == 'Rex' and data.rex == None:
                return data.params[j]

            # r.
            elif data.params[j] == 'r' and data.r == None:
                return data.params[j]

            # CSA.
            elif data.params[j] == 'CSA' and data.csa == None:
                return data.params[j]


    def assemble_param_names(self, index=None):
        """Function for assembling various pieces of data into a Numeric parameter array."""

        # Initialise.
        self.param_names = []

        # Diffusion tensor parameters.
        if self.param_set == 'diff' or self.param_set == 'all':
            # Isotropic diffusion.
            if self.relax.data.diff[self.run].type == 'iso':
                self.param_names.append('tm')

            # Axially symmetric diffusion.
            elif self.relax.data.diff[self.run].type == 'axial':
                self.param_names.append('tm')
                self.param_names.append('Da')
                self.param_names.append('theta')
                self.param_names.append('phi')

            # Anisotropic diffusion.
            elif self.relax.data.diff[self.run].type == 'aniso':
                self.param_names.append('tm')
                self.param_names.append('Da')
                self.param_names.append('Dr')
                self.param_names.append('alpha')
                self.param_names.append('beta')
                self.param_names.append('gamma')

        # Model-free parameters (residue specific parameters).
        if self.param_set != 'diff':
            for i in xrange(len(self.relax.data.res[self.run])):
                # Only add parameters for a single residue if index has a value.
                if index != None and i != index:
                    continue

                # Skip unselected residues.
                if not self.relax.data.res[self.run][i].select:
                    continue

                # Loop over the model-free parameters and add the names.
                for j in xrange(len(self.relax.data.res[self.run][i].params)):
                    self.param_names.append(self.relax.data.res[self.run][i].params[j])


    def assemble_param_vector(self, index=None, sim_index=None, param_set=None):
        """Function for assembling various pieces of data into a Numeric parameter array."""

        # Initialise.
        param_vector = []
        if param_set == None:
            param_set = self.param_set

        # Monte Carlo diffusion tensor parameters.
        if sim_index != None and (param_set == 'diff' or param_set == 'all'):
            # Isotropic diffusion.
            if self.relax.data.diff[self.run].type == 'iso':
                param_vector.append(self.relax.data.diff[self.run].tm_sim[sim_index])

            # Axially symmetric diffusion.
            elif self.relax.data.diff[self.run].type == 'axial':
                param_vector.append(self.relax.data.diff[self.run].tm_sim[sim_index])
                param_vector.append(self.relax.data.diff[self.run].Da_sim[sim_index])
                param_vector.append(self.relax.data.diff[self.run].theta_sim[sim_index])
                param_vector.append(self.relax.data.diff[self.run].phi_sim[sim_index])

            # Anisotropic diffusion.
            elif self.relax.data.diff[self.run].type == 'aniso':
                param_vector.append(self.relax.data.diff[self.run].tm_sim[sim_index])
                param_vector.append(self.relax.data.diff[self.run].Da_sim[sim_index])
                param_vector.append(self.relax.data.diff[self.run].Dr_sim[sim_index])
                param_vector.append(self.relax.data.diff[self.run].alpha_sim[sim_index])
                param_vector.append(self.relax.data.diff[self.run].beta_sim[sim_index])
                param_vector.append(self.relax.data.diff[self.run].gamma_sim[sim_index])

        # Diffusion tensor parameters.
        elif param_set == 'diff' or param_set == 'all':
            # Isotropic diffusion.
            if self.relax.data.diff[self.run].type == 'iso':
                param_vector.append(self.relax.data.diff[self.run].tm)

            # Axially symmetric diffusion.
            elif self.relax.data.diff[self.run].type == 'axial':
                param_vector.append(self.relax.data.diff[self.run].tm)
                param_vector.append(self.relax.data.diff[self.run].Da)
                param_vector.append(self.relax.data.diff[self.run].theta)
                param_vector.append(self.relax.data.diff[self.run].phi)

            # Anisotropic diffusion.
            elif self.relax.data.diff[self.run].type == 'aniso':
                param_vector.append(self.relax.data.diff[self.run].tm)
                param_vector.append(self.relax.data.diff[self.run].Da)
                param_vector.append(self.relax.data.diff[self.run].Dr)
                param_vector.append(self.relax.data.diff[self.run].alpha)
                param_vector.append(self.relax.data.diff[self.run].beta)
                param_vector.append(self.relax.data.diff[self.run].gamma)

        # Model-free parameters (residue specific parameters).
        if param_set != 'diff':
            for i in xrange(len(self.relax.data.res[self.run])):
                # Skip unselected residues.
                if not self.relax.data.res[self.run][i].select:
                    continue

                # Only add parameters for a single residue if index has a value.
                if index != None and i != index:
                    continue

                # Loop over the model-free parameters.
                for j in xrange(len(self.relax.data.res[self.run][i].params)):
                    # tm.
                    if self.relax.data.res[self.run][i].params[j] == 'tm':
                        if self.relax.data.res[self.run][i].tm == None:
                            param_vector.append(0.0)
                        elif sim_index != None:
                            param_vector.append(self.relax.data.res[self.run][i].tm_sim[sim_index])
                        else:
                            param_vector.append(self.relax.data.res[self.run][i].tm)

                    # S2.
                    elif self.relax.data.res[self.run][i].params[j] == 'S2':
                        if self.relax.data.res[self.run][i].s2 == None:
                            param_vector.append(0.0)
                        elif sim_index != None:
                            param_vector.append(self.relax.data.res[self.run][i].s2_sim[sim_index])
                        else:
                            param_vector.append(self.relax.data.res[self.run][i].s2)

                    # S2f.
                    elif self.relax.data.res[self.run][i].params[j] == 'S2f':
                        if self.relax.data.res[self.run][i].s2f == None:
                            param_vector.append(0.0)
                        elif sim_index != None:
                            param_vector.append(self.relax.data.res[self.run][i].s2f_sim[sim_index])
                        else:
                            param_vector.append(self.relax.data.res[self.run][i].s2f)

                    # S2s.
                    elif self.relax.data.res[self.run][i].params[j] == 'S2s':
                        if self.relax.data.res[self.run][i].s2s == None:
                            param_vector.append(0.0)
                        elif sim_index != None:
                            param_vector.append(self.relax.data.res[self.run][i].s2s_sim[sim_index])
                        else:
                            param_vector.append(self.relax.data.res[self.run][i].s2s)

                    # te.
                    elif self.relax.data.res[self.run][i].params[j] == 'te':
                        if self.relax.data.res[self.run][i].te == None:
                            param_vector.append(0.0)
                        elif sim_index != None:
                            param_vector.append(self.relax.data.res[self.run][i].te_sim[sim_index])
                        else:
                            param_vector.append(self.relax.data.res[self.run][i].te)

                    # tf.
                    elif self.relax.data.res[self.run][i].params[j] == 'tf':
                        if self.relax.data.res[self.run][i].tf == None:
                            param_vector.append(0.0)
                        elif sim_index != None:
                            param_vector.append(self.relax.data.res[self.run][i].tf_sim[sim_index])
                        else:
                            param_vector.append(self.relax.data.res[self.run][i].tf)

                    # ts.
                    elif self.relax.data.res[self.run][i].params[j] == 'ts':
                        if self.relax.data.res[self.run][i].ts == None:
                            param_vector.append(0.0)
                        elif sim_index != None:
                            param_vector.append(self.relax.data.res[self.run][i].ts_sim[sim_index])
                        else:
                            param_vector.append(self.relax.data.res[self.run][i].ts)

                    # Rex.
                    elif self.relax.data.res[self.run][i].params[j] == 'Rex':
                        if self.relax.data.res[self.run][i].rex == None:
                            param_vector.append(0.0)
                        elif sim_index != None:
                            param_vector.append(self.relax.data.res[self.run][i].rex_sim[sim_index])
                        else:
                            param_vector.append(self.relax.data.res[self.run][i].rex)

                    # r.
                    elif self.relax.data.res[self.run][i].params[j] == 'r':
                        if self.relax.data.res[self.run][i].r == None:
                            param_vector.append(0.0)
                        elif sim_index != None:
                            param_vector.append(self.relax.data.res[self.run][i].r_sim[sim_index])
                        else:
                            param_vector.append(self.relax.data.res[self.run][i].r)

                    # CSA.
                    elif self.relax.data.res[self.run][i].params[j] == 'CSA':
                        if self.relax.data.res[self.run][i].csa == None:
                            param_vector.append(0.0)
                        elif sim_index != None:
                            param_vector.append(self.relax.data.res[self.run][i].csa_sim[sim_index])
                        else:
                            param_vector.append(self.relax.data.res[self.run][i].csa)

                    # Unknown parameter.
                    else:
                        raise RelaxError, "Unknown parameter."

        # Return a Numeric array.
        return array(param_vector, Float64)


    def assemble_scaling_matrix(self, index=None, scaling=1):
        """Function for creating the scaling matrix."""

        # Initialise.
        self.scaling_matrix = identity(len(self.param_vector), Float64)
        i = 0

        # No diagonal scaling.
        if not scaling:
            return

        # Diffusion tensor parameters.
        if self.param_set == 'diff' or self.param_set == 'all':
            # Isotropic diffusion.
            if self.relax.data.diff[self.run].type == 'iso':
                # tm.
                self.scaling_matrix[i, i] = 1e-9

                # Increment i.
                i = i + 1

            # Axially symmetric diffusion.
            elif self.relax.data.diff[self.run].type == 'axial':
                # tm, Da, theta, phi
                self.scaling_matrix[i, i] = 1e-9
                self.scaling_matrix[i+1, i+1] = 1e9
                self.scaling_matrix[i+2, i+2] = 1.0
                self.scaling_matrix[i+3, i+3] = 1.0

                # Increment i.
                i = i + 4

            # Anisotropic diffusion.
            elif self.relax.data.diff[self.run].type == 'aniso':
                # tm, Da, Dr, alpha, beta, gamma.
                self.scaling_matrix[i, i] = 1e-9
                self.scaling_matrix[i+1, i+1] = 1e9
                self.scaling_matrix[i+2, i+2] = 1e9
                self.scaling_matrix[i+3, i+3] = 1.0
                self.scaling_matrix[i+4, i+4] = 1.0
                self.scaling_matrix[i+5, i+5] = 1.0

                # Increment i.
                i = i + 6

        # Model-free parameters.
        if self.param_set != 'diff':
            # Loop over all residues.
            for j in xrange(len(self.relax.data.res[self.run])):
                # Skip unselected residues.
                if not self.relax.data.res[self.run][j].select:
                    continue

                # Only add parameters for a single residue if index has a value.
                if index != None and j != index:
                    continue

                # Loop over the model-free parameters.
                for k in xrange(len(self.relax.data.res[self.run][j].params)):
                    # tm.
                    if self.relax.data.res[self.run][j].params[k] == 'tm':
                        self.scaling_matrix[i, i] = 1e-9

                    # te, tf, and ts.
                    elif match('t', self.relax.data.res[self.run][j].params[k]):
                        self.scaling_matrix[i, i] = 1e-9

                    # Rex.
                    elif self.relax.data.res[self.run][j].params[k] == 'Rex':
                        self.scaling_matrix[i, i] = 1.0 / (2.0 * pi * self.relax.data.res[self.run][j].frq[0]) ** 2

                    # Bond length.
                    elif self.relax.data.res[self.run][j].params[k] == 'r':
                        self.scaling_matrix[i, i] = 1e-10

                    # CSA.
                    elif self.relax.data.res[self.run][j].params[k] == 'CSA':
                        self.scaling_matrix[i, i] = 1e-4

                    # Increment i.
                    i = i + 1


    def back_calc(self, run=None, index=None, ri_label=None, frq_label=None, frq=None):
        """Back-calculation of relaxation data from the model-free parameter values."""

        # Run argument.
        self.run = run

        # Get the relaxation value from the minimise function.
        value = self.minimise(run=self.run, min_algor='back_calc', min_options=(index, ri_label, frq_label, frq))

        # Return the relaxation value.
        return value


    def calculate(self, run=None, res_num=None, print_flag=1, sim_index=None):
        """Calculation of the model-free chi-squared value."""

        # Run argument.
        self.run = run

        # Go to the minimise function.
        self.minimise(run=self.run, min_algor='calc', min_options=res_num, sim_index=sim_index)


    def copy(self, run1=None, run2=None):
        """Function for copying all model-free data from run1 to run2."""

        # Test if run1 exists.
        if not run1 in self.relax.data.run_names:
            raise RelaxNoRunError, run1

        # Test if run2 exists.
        if not run2 in self.relax.data.run_names:
            raise RelaxNoRunError, run2

        # Test if the run type is set to 'mf'.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(self.run)]
        if function_type != 'mf':
            raise RelaxFuncSetupError, self.relax.specific_setup.get_string(function_type)

        # Test if the sequence data for run1 is loaded.
        if not self.relax.data.res.has_key(run1):
            raise RelaxNoSequenceError, run1

        # Test if the sequence data for run2 is loaded.
        if not self.relax.data.res.has_key(run2):
            raise RelaxNoSequenceError, run2

        # Get all data structure names.
        names = self.data_names()

        # Test if run2 contains any model-free data.
        for i in xrange(len(self.relax.data.res[run2])):
            # Remap the data structure 'self.relax.data.res[run2][i]'.
            data = self.relax.data.res[run2][i]

            # Loop through the data structure names.
            for name in names:
                # Raise an error if data exists.
                if hasattr(data, name):
                    raise RelaxMfError, run2

        # Copy the data.
        for i in xrange(len(self.relax.data.res[run1])):
            # Remap the data structure 'self.relax.data.res[run1][i]'.
            data1 = self.relax.data.res[run1][i]
            data2 = self.relax.data.res[run2][i]

            # Loop through the data structure names.
            for name in names:
                # Skip the data structure if it does not exist.
                if not hasattr(data1, name):
                    continue

                # Copy the data structure.
                setattr(data2, name, deepcopy(getattr(data1, name)))


    def create_mc_data(self, run, i):
        """Function for creating the Monte Carlo Ri data."""

        # Arguments
        self.run = run

        # Initialise the data data structure.
        data = []

        # Test if the model is set.
        if not hasattr(self.relax.data.res[self.run][i], 'model') or not self.relax.data.res[self.run][i].model:
            raise RelaxNoMfModelError, self.run

        # Loop over the relaxation data.
        for j in xrange(len(self.relax.data.res[run][i].relax_data)):
            # Back calculate the value.
            value = self.back_calc(run=run, index=i, ri_label=self.relax.data.res[run][i].ri_labels[j], frq_label=self.relax.data.res[run][i].frq_labels[self.relax.data.res[run][i].remap_table[j]], frq=self.relax.data.res[run][i].frq[self.relax.data.res[run][i].remap_table[j]])

            # Append the value.
            data.append(value)

        # Return the data.
        return data


    def create_model(self, run=None, model=None, equation=None, params=None, res_num=None):
        """Function to create a model-free model."""

        # Run argument.
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the run type is set to 'mf'.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(self.run)]
        if function_type != 'mf':
            raise RelaxFuncSetupError, self.relax.specific_setup.get_string(function_type)

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Check the validity of the model-free equation type.
        valid_types = ['mf_orig', 'mf_ext', 'mf_ext2']
        if not equation in valid_types:
            raise RelaxError, "The model-free equation type argument " + `equation` + " is invalid and should be one of " + `valid_types` + "."

        # Check the validity of the parameter array.
        s2, te, s2f, tf, s2s, ts, rex, csa, r = 0, 0, 0, 0, 0, 0, 0, 0, 0
        for i in xrange(len(params)):
            # Invalid parameter flag.
            invalid_param = 0

            # S2.
            if params[i] == 'S2':
                # Does the array contain more than one instance of S2.
                if s2:
                    invalid_param = 1
                s2 = 1

                # Does the array contain S2s.
                s2s_flag = 0
                for j in xrange(len(params)):
                    if params[j] == 'S2s':
                        s2s_flag = 1
                if s2s_flag:
                    invalid_param = 1

            # te.
            elif params[i] == 'te':
                # Does the array contain more than one instance of te and has the extended model-free formula been selected.
                if equation == 'mf_ext' or te:
                    invalid_param = 1
                te = 1

                # Does the array contain the parameter S2.
                s2_flag = 0
                for j in xrange(len(params)):
                    if params[j] == 'S2':
                        s2_flag = 1
                if not s2_flag:
                    invalid_param = 1

            # S2f.
            elif params[i] == 'S2f':
                # Does the array contain more than one instance of S2f and has the original model-free formula been selected.
                if equation == 'mf_orig' or s2f:
                    invalid_param = 1
                s2f = 1

            # S2s.
            elif params[i] == 'S2s':
                # Does the array contain more than one instance of S2s and has the original model-free formula been selected.
                if equation == 'mf_orig' or s2s:
                    invalid_param = 1
                s2s = 1

            # tf.
            elif params[i] == 'tf':
                # Does the array contain more than one instance of tf and has the original model-free formula been selected.
                if equation == 'mf_orig' or tf:
                    invalid_param = 1
                tf = 1

                # Does the array contain the parameter S2f.
                s2f_flag = 0
                for j in xrange(len(params)):
                    if params[j] == 'S2f':
                        s2f_flag = 1
                if not s2f_flag:
                    invalid_param = 1

            # ts.
            elif params[i] == 'ts':
                # Does the array contain more than one instance of ts and has the original model-free formula been selected.
                if equation == 'mf_orig' or ts:
                    invalid_param = 1
                ts = 1

                # Does the array contain the parameter S2 or S2s.
                flag = 0
                for j in xrange(len(params)):
                    if params[j] == 'S2' or params[j] == 'S2f':
                        flag = 1
                if not flag:
                    invalid_param = 1

            # Rex.
            elif params[i] == 'Rex':
                if rex:
                    invalid_param = 1
                rex = 1

            # Bond length.
            elif params[i] == 'r':
                if r:
                    invalid_param = 1
                r = 1

            # CSA.
            elif params[i] == 'CSA':
                if csa:
                    invalid_param = 1
                csa = 1

            # Unknown parameter.
            else:
                raise RelaxError, "The parameter " + params[i] + " is not supported."

            # The invalid parameter flag is set.
            if invalid_param:
                raise RelaxError, "The parameter array " + `params` + " contains an invalid combination of parameters."

        # Set up the model.
        self.model_setup(run, model, equation, params, res_num)


    def data_init(self, name):
        """Function for returning an initial data structure corresponding to 'name'."""

        # Empty arrays.
        list_data = [ 'params' ]
        if name in list_data:
            return []

        # None.
        none_data = [ 'equation',
                      'model',
                      's2',
                      's2f',
                      's2s',
                      'tm',
                      'te',
                      'tf',
                      'ts',
                      'rex',
                      'r',
                      'csa',
                      'chi2',
                      'iter',
                      'f_count',
                      'g_count',
                      'h_count',
                      'warning' ]
        if name in none_data:
            return None


    def data_names(self, set='all'):
        """Function for returning a list of names of data structures.

        Description
        ~~~~~~~~~~~

        The names are as follows:

        model: The model-free model name.

        equation:  The model-free equation type.

        params:  An array of the model-free parameter names associated with the model.

        s2:  S2.

        s2f:  S2f.

        s2s:  S2s.

        tm:  tm.

        te:  te.

        tf:  tf.

        ts:  ts.

        rex:  Rex.

        r:  Bond length.

        csa:  CSA value.

        chi2:  Chi-squared value.

        iter:  Iterations.

        f_count:  Function count.

        g_count:  Gradient count.

        h_count:  Hessian count.

        warning:  Minimisation warning.
        """

        # Initialise.
        names = []

        # Generic.
        if set == 'all' or set == 'generic':
            names.append('model')
            names.append('equation')
            names.append('params')

        # Parameters.
        if set == 'all' or set == 'params':
            names.append('s2')
            names.append('s2f')
            names.append('s2s')
            names.append('tm')
            names.append('te')
            names.append('tf')
            names.append('ts')
            names.append('rex')
            names.append('r')
            names.append('csa')

        # Minimisation statistics.
        if set == 'all' or set == 'min':
            names.append('chi2')
            names.append('iter')
            names.append('f_count')
            names.append('g_count')
            names.append('h_count')
            names.append('warning')

        return names


    def default_value(self, param):
        """
        Model-free default values
        ~~~~~~~~~~~~~~~~~~~~~~~~~

        _______________________________________________________________________________________
        |                                       |              |                              |
        | Data type                             | Object name  | Value                        |
        |_______________________________________|______________|______________________________|
        |                                       |              |                              |
        | Bond length                           | r            | 1.02 * 1e-10                 |
        |_______________________________________|______________|______________________________|
        |                                       |              |                              |
        | CSA                                   | csa          | -170 * 1e-6                  |
        |_______________________________________|______________|______________________________|
        |                                       |              |                              |
        | Chemical exchange relaxation          | rex          | 0.0                          |
        |_______________________________________|______________|______________________________|
        |                                       |              |                              |
        | Order parameters S2, S2f, and S2s     | s2, s2f, s2s | 0.8                          |
        |_______________________________________|______________|______________________________|
        |                                       |              |                              |
        | Correlation time te                   | te           | 100 * 1e-12                  |
        |_______________________________________|______________|______________________________|
        |                                       |              |                              |
        | Correlation time tf                   | tf           | 10 * 1e-12                   |
        |_______________________________________|______________|______________________________|
        |                                       |              |                              |
        | Correlation time ts                   | ts           | 1000 * 1e-12                 |
        |_______________________________________|______________|______________________________|
        |                                       |              |                              |
        | Local tm                              | tm           | 10 * 1e-9                    |
        |_______________________________________|______________|______________________________|

        """

        # Bond length.
        if param == 'r':
            return 1.02 * 1e-10

        # CSA.
        if param == 'CSA':
            return -170 * 1e-6

        # Rex.
        if param == 'Rex':
            return 0.0

        # {S2, S2f, S2s}.
        if match('S2', param):
            return 0.8

        # {te, tf, ts}.
        elif match('t', param):
            if param == 'tf':
                return 10.0 * 1e-12
            elif param == 'ts':
                return 1000.0 * 1e-12
            elif param == 'tm':
                return 10.0 * 1e-9
            else:
                return 100.0 * 1e-12


    def delete(self, run):
        """Function for deleting all model-free data."""

        # Arguments.
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the run type is set to 'mf'.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(self.run)]
        if function_type != 'mf':
            raise RelaxFuncSetupError, self.relax.specific_setup.get_string(function_type)

        # Test if the sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Get all data structure names.
        names = self.data_names()

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Remap the data structure 'self.relax.data.res[self.run][i]'.
            data = self.relax.data.res[self.run][i]

            # Loop through the data structure names.
            for name in names:
                # Skip the data structure if it does not exist.
                if not hasattr(data, name):
                    continue

                # Delete the data.
                delattr(data, name)

        # Clean up the runs.
        self.relax.generic.delete.clean_runs()


    def determine_param_set_type(self):
        """Determine the type of parameter set."""

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Test if the params data structure exists for all residues.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Skip unselected residues.
            if not self.relax.data.res[self.run][i].select:
                continue

            # No params.
            if not hasattr(self.relax.data.res[self.run][i], 'params'):
                return None

        # If there is a local tm, fail if not all residues have a local tm parameter.
        local_tm = 0
        for i in xrange(len(self.relax.data.res[self.run])):
            # Skip unselected residues.
            if not self.relax.data.res[self.run][i].select:
                continue

            if local_tm == 0 and 'tm' in self.relax.data.res[self.run][i].params:
                local_tm = 1

            elif local_tm == 1 and not 'tm' in self.relax.data.res[self.run][i].params:
                raise RelaxError, "All residues must either have a local tm parameter or not."

        # Check if any model-free parameters are allowed to vary.
        mf_all_fixed = 1
        for i in xrange(len(self.relax.data.res[self.run])):
            # Skip unselected residues.
            if not self.relax.data.res[self.run][i].select:
                continue

            # Test the fixed flag.
            if not hasattr(self.relax.data.res[self.run][i], 'fixed'):
                mf_all_fixed = 0
                break
            if not self.relax.data.res[self.run][i].fixed:
                mf_all_fixed = 0
                break

        # Local tm.
        if local_tm:
            return 'local_tm'

        # Test if the diffusion tensor data is loaded.
        if not self.relax.data.diff.has_key(self.run):
            return None
            #raise RelaxNoTensorError, self.run

        # 'diff' parameter set.
        if mf_all_fixed:
            # All parameters fixed.
            if self.relax.data.diff[self.run].fixed:
                raise RelaxError, "All parameters are fixed."

            return 'diff'

        # 'mf' parameter set.
        if self.relax.data.diff[self.run].fixed:
            return 'mf'

        # 'all' parameter set.
        else:
            return 'all'


    def disassemble_param_vector(self, index=None, sim_index=None):
        """Function for disassembling the parameter vector."""

        # Initialise.
        param_index = 0

        # Monte Carlo diffusion tensor parameters.
        if sim_index != None and (self.param_set == 'diff' or self.param_set == 'all'):
            # Isotropic diffusion.
            if self.relax.data.diff[self.run].type == 'iso':
                self.relax.data.diff[self.run].tm_sim[sim_index] = self.param_vector[0]
                param_index = param_index + 1

            # Axially symmetric diffusion.
            elif self.relax.data.diff[self.run].type == 'axial':
                self.relax.data.diff[self.run].tm_sim[sim_index] = self.param_vector[0]
                self.relax.data.diff[self.run].Da_sim[sim_index] = self.param_vector[1]
                self.relax.data.diff[self.run].theta_sim[sim_index] = self.param_vector[2]
                self.relax.data.diff[self.run].phi_sim[sim_index] = self.param_vector[3]
                param_index = param_index + 4

            # Anisotropic diffusion.
            elif self.relax.data.diff[self.run].type == 'aniso':
                self.relax.data.diff[self.run].tm_sim[sim_index] = self.param_vector[0]
                self.relax.data.diff[self.run].Da_sim[sim_index] = self.param_vector[1]
                self.relax.data.diff[self.run].Dr_sim[sim_index] = self.param_vector[2]
                self.relax.data.diff[self.run].alpha_sim[sim_index] = self.param_vector[3]
                self.relax.data.diff[self.run].beta_sim[sim_index] = self.param_vector[4]
                self.relax.data.diff[self.run].gamma_sim[sim_index] = self.param_vector[5]
                param_index = param_index + 6

        # Diffusion tensor parameters.
        elif self.param_set == 'diff' or self.param_set == 'all':
            # Isotropic diffusion.
            if self.relax.data.diff[self.run].type == 'iso':
                self.relax.data.diff[self.run].tm = self.param_vector[0]
                param_index = param_index + 1

            # Axially symmetric diffusion.
            elif self.relax.data.diff[self.run].type == 'axial':
                self.relax.data.diff[self.run].tm = self.param_vector[0]
                self.relax.data.diff[self.run].Da = self.param_vector[1]
                self.relax.data.diff[self.run].theta = self.relax.generic.angles.wrap_angles(self.param_vector[2], 0.0, pi)
                self.relax.data.diff[self.run].phi = self.relax.generic.angles.wrap_angles(self.param_vector[3], 0.0, 2.0*pi)
                param_index = param_index + 4

            # Anisotropic diffusion.
            elif self.relax.data.diff[self.run].type == 'aniso':
                self.relax.data.diff[self.run].tm = self.param_vector[0]
                self.relax.data.diff[self.run].Da = self.param_vector[1]
                self.relax.data.diff[self.run].Dr = self.param_vector[2]
                self.relax.data.diff[self.run].alpha = self.relax.generic.angles.wrap_angles(self.param_vector[3], 0.0, 2.0*pi)
                self.relax.data.diff[self.run].beta = self.relax.generic.angles.wrap_angles(self.param_vector[4], 0.0, pi)
                self.relax.data.diff[self.run].gamma = self.relax.generic.angles.wrap_angles(self.param_vector[5], 0.0, 2.0*pi)
                param_index = param_index + 6

        # Model-free parameters.
        if self.param_set != 'diff':
            # Loop over all residues.
            for i in xrange(len(self.relax.data.res[self.run])):
                # Remap the residue data structure.
                res = self.relax.data.res[self.run][i]

                # Skip unselected residues.
                if not res.select:
                    continue

                # Only add parameters for a single residue if index has a value.
                if index != None and i != index:
                    continue

                # Loop over the model-free parameters.
                for j in xrange(len(res.params)):
                    # tm.
                    if res.params[j] == 'tm':
                        if sim_index == None:
                            res.tm = self.param_vector[param_index]
                        else:
                            res.tm_sim[sim_index] = self.param_vector[param_index]

                    # S2.
                    elif res.params[j] == 'S2':
                        if sim_index == None:
                            res.s2 = self.param_vector[param_index]
                        else:
                            res.s2_sim[sim_index] = self.param_vector[param_index]

                    # S2f.
                    elif res.params[j] == 'S2f':
                        if sim_index == None:
                            res.s2f = self.param_vector[param_index]
                        else:
                            res.s2f_sim[sim_index] = self.param_vector[param_index]

                    # S2s.
                    elif res.params[j] == 'S2s':
                        if sim_index == None:
                            res.s2s = self.param_vector[param_index]
                        else:
                            res.s2s_sim[sim_index] = self.param_vector[param_index]

                    # te.
                    elif res.params[j] == 'te':
                        if sim_index == None:
                            res.te = self.param_vector[param_index]
                        else:
                            res.te_sim[sim_index] = self.param_vector[param_index]

                    # tf.
                    elif res.params[j] == 'tf':
                        if sim_index == None:
                            res.tf = self.param_vector[param_index]
                        else:
                            res.tf_sim[sim_index] = self.param_vector[param_index]

                    # ts.
                    elif res.params[j] == 'ts':
                        if sim_index == None:
                            res.ts = self.param_vector[param_index]
                        else:
                            res.ts_sim[sim_index] = self.param_vector[param_index]

                    # Rex.
                    elif res.params[j] == 'Rex':
                        if sim_index == None:
                            res.rex = self.param_vector[param_index]
                        else:
                            res.rex_sim[sim_index] = self.param_vector[param_index]

                    # r.
                    elif res.params[j] == 'r':
                        if sim_index == None:
                            res.r = self.param_vector[param_index]
                        else:
                            res.r_sim[sim_index] = self.param_vector[param_index]

                    # CSA.
                    elif res.params[j] == 'CSA':
                        if sim_index == None:
                            res.csa = self.param_vector[param_index]
                        else:
                            res.csa_sim[sim_index] = self.param_vector[param_index]

                    # Unknown parameter.
                    else:
                        raise RelaxError, "Unknown parameter."

                    # Increment the parameter index.
                    param_index = param_index + 1

        # Calculate all order parameters after unpacking the vector.
        if self.param_set != 'diff':
            # Loop over all residues.
            for i in xrange(len(self.relax.data.res[self.run])):
                # Remap the residue data structure.
                res = self.relax.data.res[self.run][i]

                # Skip unselected residues.
                if not res.select:
                    continue

                # Only add parameters for a single residue if index has a value.
                if index != None and i != index:
                    continue

                # Normal values.
                if sim_index == None:
                    # S2.
                    if 'S2' not in res.params and 'S2f' in res.params and 'S2s' in res.params:
                        res.s2 = res.s2f * res.s2s

                    # S2f.
                    if 'S2f' not in res.params and 'S2' in res.params and 'S2s' in res.params:
                        if res.s2s == 0.0:
                            res.s2f = 1e99
                        else:
                            res.s2f = res.s2 / res.s2s

                    # S2s.
                    if 'S2s' not in res.params and 'S2' in res.params and 'S2f' in res.params:
                        if res.s2f == 0.0:
                            res.s2s = 1e99
                        else:
                            res.s2s = res.s2 / res.s2f

                # Simulation values.
                else:
                    # S2.
                    if 'S2' not in res.params and 'S2f' in res.params and 'S2s' in res.params:
                        res.s2_sim[sim_index] = res.s2f_sim[sim_index] * res.s2s_sim[sim_index]

                    # S2f.
                    if 'S2f' not in res.params and 'S2' in res.params and 'S2s' in res.params:
                        if res.s2s_sim[sim_index] == 0.0:
                            res.s2f_sim[sim_index] = 1e99
                        else:
                            res.s2f_sim[sim_index] = res.s2_sim[sim_index] / res.s2s_sim[sim_index]

                    # S2s.
                    if 'S2s' not in res.params and 'S2' in res.params and 'S2f' in res.params:
                        if res.s2f_sim[sim_index] == 0.0:
                            res.s2s_sim[sim_index] = 1e99
                        else:
                            res.s2s_sim[sim_index] = res.s2_sim[sim_index] / res.s2f_sim[sim_index]


    def duplicate_data(self, new_run=None, old_run=None, instance=None):
        """Function for duplicating data."""

        # Duplicate all non-residue specific data.
        for data_name in dir(self.relax.data):
            # Skip 'res'.
            if data_name == 'res':
                continue

            # Get the object.
            data = getattr(self.relax.data, data_name)

            # Skip the data if it is not a dictionary (or equivalent).
            if not hasattr(data, 'has_key'):
                continue

            # Skip the data if it doesn't contain the key 'old_run'.
            if not data.has_key(old_run):
                continue

            # If the dictionary already contains the key 'new_run', but the data is different, raise an error (skip PDB and diffusion data).
            if data_name != 'pdb' and data_name != 'diff' and data.has_key(new_run) and data[old_run] != data[new_run]:
                raise RelaxError, "The data between run " + `new_run` + " and run " + `old_run` + " is not consistent."

            # Skip the data if it contains the key 'new_run'.
            if data.has_key(new_run):
                continue

            # Duplicate the data.
            data[new_run] = deepcopy(data[old_run])

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Sequence specific data.
        if self.param_set == 'mf' or self.param_set == 'local_tm':
            # Create the sequence data if it does not exist.
            if not self.relax.data.res.has_key(new_run):
                # Add the new run to 'self.relax.data.res'.
                self.relax.data.res.add_list(new_run)

                # Fill the array 'self.relax.data.res[new_run]' with empty data containers and place sequence data into the array.
                for i in xrange(len(self.relax.data.res[old_run])):
                    # Append a data container.
                    self.relax.data.res[new_run].add_element()

                    # Insert the data.
                    self.relax.data.res[new_run][i].num = self.relax.data.res[old_run][i].num
                    self.relax.data.res[new_run][i].name = self.relax.data.res[old_run][i].name
                    self.relax.data.res[new_run][i].select = self.relax.data.res[old_run][i].select

            # Duplicate the residue specific data.
            self.relax.data.res[new_run][instance] = deepcopy(self.relax.data.res[old_run][instance])

        # Other data types.
        elif self.param_set == 'diff' or self.param_set == 'all':
            # Duplicate the residue specific data.
            self.relax.data.res[new_run] = deepcopy(self.relax.data.res[old_run])


    def eliminate(self, name, value, run, i, args):
        """
        Model-free model elimination rules
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        Local tm.

        The local tm, in some cases, may exceed the value expected for a global correlation time.
        Generally the tm value will be stuck at the upper limit defined for the parameter.  These
        models are eliminated using the rule:

            tm >= c

        The default value of c is 50 ns, although this can be overriden by supplying the value (in
        seconds) as the first element of the args tuple.


        Internal correlation times {te, tf, ts}.

        These parameters may experience the same problem as the local tm in that the model fails and
        the parameter value is stuck at the upper limit.  These parameters are constrained using the
        formula 'te, tf, ts <= 2.tm'.  These failed models are eliminated using the rule:

            te, tf, ts >= c.tm

        The default value of c is 1.5.  Because of round-off errors and the constraint algorithm,
        setting c to 2 will result in no models being eliminated as the minimised parameters will
        always be less than 2.tm.  The value can be changed by supplying the value as the second
        element of the tuple.


        Arguments.

        The 'args' argument must be a tuple of length 2, the element of which must be numbers.  For
        example to eliminate models which have a local tm value greater than 25 ns and models with
        internal correlation times greater than 1.5 times tm, set 'args' to (25 * 1e-9, 1.5).
        """

        # Default values.
        c1 = 50.0 * 1e-9
        c2 = 1.5

        # Depack the arguments.
        if args != None:
            c1, c2 = args

        # Get the tm value.
        if self.param_set == 'local_tm':
            tm = self.relax.data.res[run][i].tm
        else:
            tm = self.relax.data.diff[run].tm

        # Local tm.
        if name == 'tm' and value >= c1:
            return 1

        # Internal correlation times.
        if match('t[efs]', name) and value >= c2 * tm:
            return 1

        # Accept model.
        return 0


    def get_data_name(self, name):
        """
        Model-free data type string matching patterns
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        ____________________________________________________________________________________________
        |                        |              |                                                  |
        | Data type              | Object name  | Patterns                                         |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Bond length            | r            | '^r$' or '[Bb]ond[ -_][Ll]ength'                 |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | CSA                    | csa          | '^[Cc][Ss][Aa]$'                                 |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Chemical exchange      | rex          | '^[Rr]ex$' or '[Cc]emical[ -_][Ee]xchange'       |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Order parameter S2     | s2           | '^[Ss]2$'                                        |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Order parameter S2f    | s2f          | '^[Ss]2f$'                                       |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Order parameter S2s    | s2s          | '^[Ss]2s$'                                       |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Correlation time te    | te           | '^te$'                                           |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Correlation time tf    | tf           | '^tf$'                                           |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Correlation time ts    | ts           | '^ts$'                                           |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Local tm               | tm           | '^tm$'                                           |
        |________________________|______________|__________________________________________________|

        """

        # Bond length.
        if match('^r$', name) or match('[Bb]ond[ -_][Ll]ength', name):
            return 'r'

        # CSA.
        if match('^[Cc][Ss][Aa]$', name):
            return 'csa'

        # Rex
        if match('^[Rr]ex$', name) or match('[Cc]emical[ -_][Ee]xchange', name):
            return 'rex'

        # Order parameter S2.
        if match('^[Ss]2$', name):
            return 's2'

        # Order parameter S2f.
        if match('^[Ss]2f$', name):
            return 's2f'

        # Order parameter S2s.
        if match('^[Ss]2s$', name):
            return 's2s'

        # Correlation time te.
        if match('^te$', name):
            return 'te'

        # Correlation time tf.
        if match('^tf$', name):
            return 'tf'

        # Correlation time ts.
        if match('^ts$', name):
            return 'ts'

        # Local tm.
        if match('^tm$', name):
            return 'tm'


    def get_param_names(self, run, i):
        """Function for returning a vector of parameter names."""

        # Arguments
        self.run = run

        # Test if the model-free model has been setup.
        for j in xrange(len(self.relax.data.res[self.run])):
            # Skip unselected residues.
            if not self.relax.data.res[self.run][j].select:
                continue

            # Not setup.
            if not self.relax.data.res[self.run][j].model:
                raise RelaxNoMfModelError, self.run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Residue index.
        if self.param_set == 'mf' or self.param_set == 'local_tm':
            index = i
        else:
            index = None

        # Assemble the parameter names.
        self.assemble_param_names(index=index)

        # Return the parameter names.
        return self.param_names


    def get_param_values(self, run, i):
        """Function for returning a vector of parameter values."""

        # Arguments
        self.run = run

        # Test if the model-free model has been setup.
        for j in xrange(len(self.relax.data.res[self.run])):
            # Skip unselected residues.
            if not self.relax.data.res[self.run][j].select:
                continue

            # Not setup.
            if not self.relax.data.res[self.run][j].model:
                raise RelaxNoMfModelError, self.run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Residue index.
        if self.param_set == 'mf' or self.param_set == 'local_tm':
            index = i
        else:
            index = None

        # Assemble the parameter values.
        self.param_vector = self.assemble_param_vector(index=index)

        # Return the parameter names.
        return self.param_vector


    def grid_search(self, run, lower, upper, inc, constraints, print_flag, sim_index=None):
        """The grid search function."""

        # Arguments.
        self.lower = lower
        self.upper = upper
        self.inc = inc

        # Minimisation.
        self.minimise(run=run, min_algor='grid', constraints=constraints, print_flag=print_flag, sim_index=sim_index)


    def grid_search_setup(self, index=None):
        """The grid search setup function."""

        # The length of the parameter array.
        n = len(self.param_vector)

        # Make sure that the length of the parameter array is > 0.
        if n == 0:
            raise RelaxError, "Cannot run a grid search on a model with zero parameters."

        # Lower bounds.
        if self.lower != None:
            if len(self.lower) != n:
                raise RelaxLenError, ('lower bounds', n)

        # Upper bounds.
        if self.upper != None:
            if len(self.upper) != n:
                raise RelaxLenError, ('upper bounds', n)

        # Increment.
        if type(self.inc) == list:
            if len(self.inc) != n:
                raise RelaxLenError, ('increment', n)
            inc = self.inc
        elif type(self.inc) == int:
            temp = []
            for j in xrange(n):
                temp.append(self.inc)
            inc = temp

        # Minimisation options initialisation.
        min_options = []
        m = 0

        # Minimisation options for diffusion tensor parameters.
        if self.param_set == 'diff' or self.param_set == 'all':
            # Isotropic diffusion {tm}.
            if self.relax.data.diff[self.run].type == 'iso':
                min_options.append([inc[0], 1.0 * 1e-9, 20.0 * 1e-9])
                m = m + 1

            # Axially symmetric diffusion {tm, Da, theta, phi}.
            if self.relax.data.diff[self.run].type == 'axial':
                min_options.append([inc[0], 1.0 * 1e-9, 20.0 * 1e-9])
                if self.relax.data.diff[self.run].axial_type == 'prolate':
                    min_options.append([inc[1], 0.0, 10.0 * 1e8])
                elif self.relax.data.diff[self.run].axial_type == 'oblate':
                    min_options.append([inc[1], -10.0 * 1e8, 0.0])
                else:
                    min_options.append([inc[1], -10.0 * 1e8, 10.0 * 1e8])
                min_options.append([inc[2], 0.0, pi])
                min_options.append([inc[3], 0.0, 2 * pi])
                m = m + 4

            # Anisotropic diffusion {tm, Da, Dr, alpha, beta, gamma}.
            elif self.relax.data.diff[self.run].type == 'aniso':
                min_options.append([inc[0], 1.0 * 1e-9, 20.0 * 1e-9])
                min_options.append([inc[1], -10.0 * 1e8, 10.0 * 1e8])
                min_options.append([inc[2], -10.0 * 1e8, 10.0 * 1e8])
                min_options.append([inc[3], 0.0, 2 * pi])
                min_options.append([inc[4], 0.0, pi])
                min_options.append([inc[5], 0.0, 2 * pi])
                m = m + 6

        # Model-free parameters (residue specific parameters).
        if self.param_set != 'diff':
            for i in xrange(len(self.relax.data.res[self.run])):
                # Skip unselected residues.
                if not self.relax.data.res[self.run][i].select:
                    continue

                # Only add parameters for a single residue if index has a value.
                if index != None and i != index:
                    continue

                # Loop over the model-free parameters.
                for j in xrange(len(self.relax.data.res[self.run][i].params)):
                    # Local tm.
                    if self.relax.data.res[self.run][i].params[j] == 'tm':
                        min_options.append([inc[m], 1.0 * 1e-9, 20.0 * 1e-9])

                    # {S2, S2f, S2s}.
                    elif match('S2', self.relax.data.res[self.run][i].params[j]):
                        min_options.append([inc[m], 0.0, 1.0])

                    # {te, tf, ts}.
                    elif match('t', self.relax.data.res[self.run][i].params[j]):
                        min_options.append([inc[m], 0.0, 500.0 * 1e-12])

                    # Rex.
                    elif self.relax.data.res[self.run][i].params[j] == 'Rex':
                        min_options.append([inc[m], 0.0, 5.0 / (2.0 * pi * self.relax.data.res[self.run][i].frq[0])**2])

                    # Bond length.
                    elif self.relax.data.res[self.run][i].params[j] == 'r':
                        min_options.append([inc[m], 1.0 * 1e-10, 1.05 * 1e-10])

                    # CSA.
                    elif self.relax.data.res[self.run][i].params[j] == 'CSA':
                        min_options.append([inc[m], -120 * 1e-6, -200 * 1e-6])

                    # Unknown option.
                    else:
                        raise RelaxError, "Unknown model-free parameter."

                    # Increment m.
                    m = m + 1

        # Set the lower and upper bounds if these are supplied.
        if self.lower != None:
            for j in xrange(n):
                if self.lower[j] != None:
                    min_options[j][1] = self.lower[j]
        if self.upper != None:
            for j in xrange(n):
                if self.upper[j] != None:
                    min_options[j][2] = self.upper[j]

        # Test if the grid is too large.
        grid_size = 1
        for i in xrange(len(min_options)):
            grid_size = grid_size * min_options[i][0]
        if type(grid_size) == long:
            raise RelaxError, "A grid search of size " + `grid_size` + " is too large."

        # Diagonal scaling of minimisation options.
        for j in xrange(len(min_options)):
            min_options[j][1] = min_options[j][1] / self.scaling_matrix[j, j]
            min_options[j][2] = min_options[j][2] / self.scaling_matrix[j, j]

        return min_options


    def linear_constraints(self, index=None):
        """Function for setting up the model-free linear constraint matrices A and b.

        Standard notation
        ~~~~~~~~~~~~~~~~~

        The order parameter constraints are:

            0 <= S2 <= 1
            0 <= S2f <= 1
            0 <= S2s <= 1

        By substituting the formula S2 = S2f.S2s into the above inequalities, the additional two
        inequalities can be derived:

            S2 <= S2f
            S2 <= S2s

        Correlation time constraints are:

            te >= 0
            tf >= 0
            ts >= 0

            tf <= ts

            te, tf, ts <= 2 * tm

        Additional constraints used include:

            Rex >= 0
            0.9e-10 <= r <= 2e-10
            -300e-6 <= CSA <= 0


        Rearranged notation
        ~~~~~~~~~~~~~~~~~~~
        The above ineqality constraints can be rearranged into:

            S2 >= 0
            -S2 >= -1
            S2f >= 0
            -S2f >= -1
            S2s >= 0
            -S2s >= -1
            S2f - S2 >= 0
            S2s - S2 >= 0
            te >= 0
            tf >= 0
            ts >= 0
            ts - tf >= 0
            Rex >= 0
            r >= 0.9e-10
            -r >= -2e-10
            CSA >= -300e-6
            -CSA >= 0


        Matrix notation
        ~~~~~~~~~~~~~~~

        In the notation A.x >= b, where A is an matrix of coefficients, x is an array of parameter
        values, and b is a vector of scalars, these inequality constraints are:

            | 1  0  0  0  0  0  0  0  0 |                  |    0    |
            |                           |                  |         |
            |-1  0  0  0  0  0  0  0  0 |                  |   -1    |
            |                           |                  |         |
            | 0  1  0  0  0  0  0  0  0 |                  |    0    |
            |                           |                  |         |
            | 0 -1  0  0  0  0  0  0  0 |                  |   -1    |
            |                           |                  |         |
            | 0  0  1  0  0  0  0  0  0 |     | S2  |      |    0    |
            |                           |     |     |      |         |
            | 0  0 -1  0  0  0  0  0  0 |     | S2f |      |   -1    |
            |                           |     |     |      |         |
            |-1  1  0  0  0  0  0  0  0 |     | S2s |      |    0    |
            |                           |     |     |      |         |
            |-1  0  1  0  0  0  0  0  0 |     | te  |      |    0    |
            |                           |     |     |      |         |
            | 0  0  0  1  0  0  0  0  0 |  .  | tf  |  >=  |    0    |
            |                           |     |     |      |         |
            | 0  0  0  0  1  0  0  0  0 |     | ts  |      |    0    |
            |                           |     |     |      |         |
            | 0  0  0  0  0  1  0  0  0 |     | Rex |      |    0    |
            |                           |     |     |      |         |
            | 0  0  0  0 -1  1  0  0  0 |     |  r  |      |    0    |
            |                           |     |     |      |         |
            | 0  0  0  0  0  0  1  0  0 |     | CSA |      |    0    |
            |                           |                  |         |
            | 0  0  0  0  0  0  0  1  0 |                  | 0.9e-10 |
            |                           |                  |         |
            | 0  0  0  0  0  0  0 -1  0 |                  | -2e-10  |
            |                           |                  |         |
            | 0  0  0  0  0  0  0  0  1 |                  | -300e-6 |
            |                           |                  |         |
            | 0  0  0  0  0  0  0  0 -1 |                  |    0    |

        """

        # Initialisation (0..j..m).
        A = []
        b = []
        n = len(self.param_vector)
        zero_array = zeros(n, Float64)
        i = 0
        j = 0

        # Diffusion tensor parameters.
        if self.param_set != 'mf' and self.relax.data.diff.has_key(self.run):
            # Isotropic diffusion.
            if self.relax.data.diff[self.run].type == 'iso':
                # tm >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 1

            # Axially symmetric diffusion.
            elif self.relax.data.diff[self.run].type == 'axial':
                # tm >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 1

                # Prolate diffusion, Da >= 0.
                if self.relax.data.diff[self.run].axial_type == 'prolate':
                    A.append(zero_array * 0.0)
                    A[j][i] = 1.0
                    b.append(0.0 / self.scaling_matrix[i, i])
                    i = i + 1
                    j = j + 1

                # Oblate diffusion, Da <= 0.
                elif self.relax.data.diff[self.run].axial_type == 'oblate':
                    A.append(zero_array * 0.0)
                    A[j][i] = -1.0
                    b.append(0.0 / self.scaling_matrix[i, i])
                    i = i + 1
                    j = j + 1

                # Add two to i for the theta and phi parameters.
                i = i + 2

            # Anisotropic diffusion.
            elif self.relax.data.diff[self.run].type == 'aniso':
                # tm >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0 / self.scaling_matrix[i, i])
                i = i + 1
                j = j + 1

                # Add five to i for the Da, Dr, alpha, beta, and gamma parameters.
                i = i + 5

        # Model-free parameters.
        if self.param_set != 'diff':
            # Loop over all residues.
            for k in xrange(len(self.relax.data.res[self.run])):
                # Skip unselected residues.
                if not self.relax.data.res[self.run][k].select:
                    continue

                # Only add parameters for a single residue if index has a value.
                if index != None and k != index:
                    continue

                # Save current value of i.
                old_i = i

                # Loop over the model-free parameters.
                for l in xrange(len(self.relax.data.res[self.run][k].params)):
                    # Local tm (skip).
                    if self.relax.data.res[self.run][k].params[l] == 'tm':
                        continue

                    # Order parameters {S2, S2f, S2s}.
                    elif match('S2', self.relax.data.res[self.run][k].params[l]):
                        # 0 <= S2 <= 1.
                        A.append(zero_array * 0.0)
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        A[j+1][i] = -1.0
                        b.append(0.0 / self.scaling_matrix[i, i])
                        b.append(-1.0 / self.scaling_matrix[i, i])
                        j = j + 2

                        # S2 <= S2f and S2 <= S2s.
                        if self.relax.data.res[self.run][k].params[l] == 'S2':
                            for m in xrange(len(self.relax.data.res[self.run][k].params)):
                                if self.relax.data.res[self.run][k].params[m] == 'S2f' or self.relax.data.res[self.run][k].params[m] == 'S2s':
                                    A.append(zero_array * 0.0)
                                    A[j][i] = -1.0
                                    A[j][old_i+m] = 1.0
                                    b.append(0.0)
                                    j = j + 1

                    # Correlation times {te, tf, ts}.
                    elif match('t[efs]', self.relax.data.res[self.run][k].params[l]):
                        # te, tf, tm >= 0.
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        b.append(0.0 / self.scaling_matrix[i, i])
                        j = j + 1

                        # tf <= ts.
                        if self.relax.data.res[self.run][k].params[l] == 'ts':
                            for m in xrange(len(self.relax.data.res[self.run][k].params)):
                                if self.relax.data.res[self.run][k].params[m] == 'tf':
                                    A.append(zero_array * 0.0)
                                    A[j][i] = 1.0
                                    A[j][old_i+m] = -1.0
                                    b.append(0.0)
                                    j = j + 1

                        # te, tf, ts <= 2 * tm.  (tf not needed because tf <= ts).
                        if not self.relax.data.res[self.run][k].params[l] == 'tf':
                            if self.param_set == 'mf':
                                A.append(zero_array * 0.0)
                                A[j][i] = -1.0
                                b.append(-2.0 * self.relax.data.diff[self.run].tm / self.scaling_matrix[i, i])
                            else:
                                A.append(zero_array * 0.0)
                                A[j][0] = 2.0
                                A[j][i] = -1.0
                                b.append(0.0)

                            j = j + 1

                    # Rex.
                    elif self.relax.data.res[self.run][k].params[l] == 'Rex':
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        b.append(0.0 / self.scaling_matrix[i, i])
                        j = j + 1

                    # Bond length.
                    elif self.relax.data.res[self.run][k].params[l] == 'r':
                        # 0.9e-10 <= r <= 2e-10.
                        A.append(zero_array * 0.0)
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        A[j+1][i] = -1.0
                        b.append(0.9e-10 / self.scaling_matrix[i, i])
                        b.append(-2e-10 / self.scaling_matrix[i, i])
                        j = j + 2

                    # CSA.
                    elif self.relax.data.res[self.run][k].params[l] == 'CSA':
                        # -300e-6 <= CSA <= 0.
                        A.append(zero_array * 0.0)
                        A.append(zero_array * 0.0)
                        A[j][i] = 1.0
                        A[j+1][i] = -1.0
                        b.append(-300e-6 / self.scaling_matrix[i, i])
                        b.append(0.0 / self.scaling_matrix[i, i])
                        j = j + 2

                    # Increment i.
                    i = i + 1

        # Convert to Numeric data structures.
        A = array(A, Float64)
        b = array(b, Float64)

        return A, b


    def map_bounds(self, run, index):
        """The function for creating bounds for the mapping function."""

        # Arguments.
        self.run = run

        # Determine the parameter set type.
        #self.param_set = self.determine_param_set_type()

        # Parameter array.
        params = self.relax.data.res[run][index].params

        # Bounds array.
        bounds = zeros((len(params), 2), Float64)

        # Loop over the parameters.
        for i in xrange(len(params)):
            # {S2, S2f, S2s}.
            if match('S2', params[i]):
                bounds[i] = [0, 1]

            # {tm, te, tf, ts}.
            elif match('t', params[i]):
                bounds[i] = [0, 1e-8]

            # Rex.
            elif params[i] == 'Rex':
                bounds[i] = [0, 30.0 / (2.0 * pi * self.relax.data.res[run][index].frq[0])**2]

            # Bond length.
            elif params[i] == 'r':
                bounds[i] = [1.0 * 1e-10, 1.1 * 1e-10]

            # CSA.
            elif params[i] == 'CSA':
                bounds[i] = [-100 * 1e-6, -300 * 1e-6]

        return bounds


    def map_labels(self, run, index, params, bounds, swap, inc):
        """Function for creating labels, tick locations, and tick values for an OpenDX map."""

        # Initialise.
        labels = "{"
        tick_locations = []
        tick_values = []
        n = len(params)
        axis_incs = 5
        loc_inc = inc / axis_incs

        # Increment over the model parameters.
        for i in xrange(n):
            # Local tm.
            if params[swap[i]] == 'tm':
                # Labels.
                labels = labels + "\"" + params[swap[i]] + " (ns)\""

                # Tick values.
                vals = bounds[swap[i], 0] * 1e9
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * 1e9

            # {S2, S2f, S2s}.
            elif match('S2', params[swap[i]]):
                # Labels.
                labels = labels + "\"" + params[swap[i]] + "\""

                # Tick values.
                vals = bounds[swap[i], 0] * 1.0
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * 1.0

            # {te, tf, and ts}.
            elif match('t', params[swap[i]]):
                # Labels.
                labels = labels + "\"" + params[swap[i]] + " (ps)\""

                # Tick values.
                vals = bounds[swap[i], 0] * 1e12
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * 1e12

            # Rex.
            elif params[swap[i]] == 'Rex':
                # Labels.
                labels = labels + "\"Rex (" + self.relax.data.res[run][index].frq_labels[0] + " MHz)\""

                # Tick values.
                vals = bounds[swap[i], 0] * (2.0 * pi * self.relax.data.res[run][index].frq[0])**2
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * (2.0 * pi * self.relax.data.res[run][index].frq[0])**2

            # Bond length.
            elif params[swap[i]] == 'r':
                # Labels.
                labels = labels + "\"" + params[swap[i]] + " (A)\""

                # Tick values.
                vals = bounds[swap[i], 0] * 1e-10
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * 1e-10

            # CSA.
            elif params[swap[i]] == 'CSA':
                # Labels.
                labels = labels + "\"" + params[swap[i]] + " (ppm)\""

                # Tick values.
                vals = bounds[swap[i], 0] * 1e-6
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * 1e-6

            if i < n - 1:
                labels = labels + " "
            else:
                labels = labels + "}"

            # Tick locations.
            string = "{"
            val = 0.0
            for j in xrange(axis_incs + 1):
                string = string + " " + `val`
                val = val + loc_inc
            string = string + " }"
            tick_locations.append(string)

            # Tick values.
            string = "{"
            for j in xrange(axis_incs + 1):
                string = string + "\"" + "%.2f" % vals + "\" "
                vals = vals + val_inc
            string = string + "}"
            tick_values.append(string)

        return labels, tick_locations, tick_values


    def minimise(self, run=None, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=0, scaling=1, print_flag=0, sim_index=None):
        """Model-free minimisation.

        Three types of parameter sets exist for which minimisation is different.  These are:
            'mf' - Model-free parameters for single residues.
            'diff' - Diffusion tensor parameters.
            'all' - All model-free and all diffusion tensor parameters.

        """

        # Arguments.
        self.run = run
        self.print_flag = print_flag

        # Test if the model-free model has been setup.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Skip unselected residues.
            if not self.relax.data.res[self.run][i].select:
                continue

            # Not setup.
            if not self.relax.data.res[self.run][i].model:
                raise RelaxNoMfModelError, self.run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Parameter set for the back-calculate function.
        if min_algor == 'back_calc' and self.param_set != 'local_tm':
            self.param_set = 'mf'

        # Tests for the PDB file and unit vectors.
        if self.param_set != 'local_tm' and self.relax.data.diff[self.run].type != 'iso':
            # Test if the PDB file has been loaded.
            if not self.relax.data.pdb.has_key(self.run):
                raise RelaxPdbError, self.run

            # Test if unit vectors exist.
            for i in xrange(len(self.relax.data.res[self.run])):
                # Skip unselected residues.
                if not self.relax.data.res[self.run][i].select:
                    continue

                # Unit vector.
                if not hasattr(self.relax.data.res[self.run][i], 'xh_unit'):
                    raise RelaxNoVectorsError, self.run

        # Test if the nucleus type has been set.
        if not hasattr(self.relax.data, 'gx'):
            raise RelaxNucleusError

        # Test if the model-free parameter values are set for minimising diffusion tensor parameters by themselves.
        if self.param_set == 'diff':
            # Loop over the sequence.
            for i in xrange(len(self.relax.data.res[self.run])):
                unset_param = self.are_mf_params_set(i)
                if unset_param != None:
                    raise RelaxNoValueError, unset_param

        # Print out.
        if self.print_flag >= 1:
            if self.param_set == 'mf':
                print "Only the model-free parameters for single residues will be used."
            elif self.param_set == 'local_mf':
                print "Only a local tm value together with the model-free parameters for single residues will be used."
            elif self.param_set == 'diff':
                print "Only diffusion tensor parameters will be used."
            elif self.param_set == 'all':
                print "The diffusion tensor parameters together with the model-free parameters for all residues will be used."

        # Count the total number of residues and test if the CSA and bond length values have been set.
        num_res = 0
        for i in xrange(len(self.relax.data.res[self.run])):
            # Skip unselected residues.
            if not self.relax.data.res[self.run][i].select:
                continue

            # CSA value.
            if not hasattr(self.relax.data.res[self.run][i], 'csa') or self.relax.data.res[self.run][i].csa == None:
                raise RelaxNoValueError, "CSA"

            # Bond length value.
            if not hasattr(self.relax.data.res[self.run][i], 'r') or self.relax.data.res[self.run][i].r == None:
                raise RelaxNoValueError, "bond length"

            # Increment the number of residues.
            num_res = num_res + 1

        # Number of residues, minimisation instances, and data sets for each parameter set type.
        if self.param_set == 'mf' or self.param_set == 'local_tm':
            num_instances = len(self.relax.data.res[self.run])
            num_data_sets = 1
            num_res = 1
        elif self.param_set == 'diff' or self.param_set == 'all':
            num_instances = 1
            num_data_sets = len(self.relax.data.res[self.run])

        # Number of residues for the calculate function.
        if min_algor == 'calc' and min_options != None:
            num_res = 1

        # Number of residues, minimisation instances, and data sets for the back-calculate function.
        if min_algor == 'back_calc':
            num_instances = 1
            num_data_sets = 0
            num_res = 1

        # Loop over the minimisation instances.
        for i in xrange(num_instances):
            # Set the index to None.
            index = None

            # Individual residue stuff.
            if self.param_set == 'mf' or self.param_set == 'local_tm':
                # Skip unselected residues.
                if not self.relax.data.res[self.run][i].select:
                    continue

                # Single residue.
                if min_algor == 'calc' and min_options != None and min_options != self.relax.data.res[self.run][i].num:
                    continue

                # Set the index to i.
                index = i

            # Index for the back_calc function.
            if min_algor == 'back_calc':
                # Index for the back_calc function.
                index = min_options[0]

                # Create the initial parameter vector.
                self.param_vector = self.assemble_param_vector(index=index)

                # Diagonal scaling.
                self.scaling_matrix = None

            else:
                # Create the initial parameter vector.
                self.param_vector = self.assemble_param_vector(index=index, sim_index=sim_index)

                # Diagonal scaling.
                self.assemble_scaling_matrix(index=index, scaling=scaling)
                self.param_vector = matrixmultiply(inverse(self.scaling_matrix), self.param_vector)

            # Get the grid search minimisation options.
            if match('^[Gg]rid', min_algor):
                min_options = self.grid_search_setup(index=index)

            # Scaling of values for the set function.
            if match('^[Ss]et', min_algor):
                min_options = matrixmultiply(inverse(self.scaling_matrix), min_options)

            # Linear constraints.
            if constraints and min_algor != 'calc':
                A, b = self.linear_constraints(index=index)

            # Print out.
            if self.print_flag >= 1:
                # Individual residue stuff.
                if self.param_set == 'mf' or self.param_set == 'local_tm':
                    if self.print_flag >= 2:
                        print "\n\n"
                    string = "Fitting to residue: " + `self.relax.data.res[self.run][index].num` + " " + self.relax.data.res[self.run][index].name
                    print string
                    print len(string) * '~'

            # Initialise the iteration counter and function, gradient, and Hessian call counters.
            self.iter_count = 0
            self.f_count = 0
            self.g_count = 0
            self.h_count = 0

            # Initialise the data structures for the model-free function.
            relax_data = []
            relax_error = []
            equations = []
            param_types = []
            param_values = None
            r = []
            csa = []
            num_frq = []
            frq = []
            num_ri = []
            remap_table = []
            noe_r1_table = []
            ri_labels = []
            num_params = []
            xh_unit_vectors = []
            if self.param_set == 'local_tm':
                mf_params = []
            elif self.param_set == 'diff':
                param_values = []

            # Set up the data for the back_calc function.
            if min_algor == 'back_calc':
                # The data.
                relax_data = [0.0]
                relax_error = [0.000001]
                equations = [self.relax.data.res[self.run][index].equation]
                param_types = [self.relax.data.res[self.run][index].params]
                r = [self.relax.data.res[self.run][index].r]
                csa = [self.relax.data.res[self.run][index].csa]
                num_frq = [1]
                frq = [[min_options[3]]]
                num_ri = [1]
                remap_table = [[0]]
                noe_r1_table = [[None]]
                ri_labels = [[min_options[1]]]
                if self.param_set != 'local_tm' and self.relax.data.diff[self.run].type != 'iso':
                    xh_unit_vectors = [self.relax.data.res[self.run][index].xh_unit]
                else:
                    xh_unit_vectors = [None]

                # Count the number of model-free parameters for the residue index.
                num_params = [len(self.relax.data.res[self.run][index].params)]

            # Loop over the number of data sets.
            for j in xrange(num_data_sets):
                # Set the sequence index.
                if self.param_set == 'mf' or self.param_set == 'local_tm':
                    seq_index = i
                else:
                    seq_index = j

                # Skip unselected residues.
                if not self.relax.data.res[self.run][seq_index].select:
                    continue

                # Make sure that the errors are strictly positive numbers.
                for k in xrange(len(self.relax.data.res[self.run][seq_index].relax_error)):
                    if self.relax.data.res[self.run][seq_index].relax_error[k] == 0.0:
                        raise RelaxError, "Zero error for residue '" + `self.relax.data.res[self.run][seq_index].num` + " " + self.relax.data.res[self.run][seq_index].name + "', minimisation not possible."
                    elif self.relax.data.res[self.run][seq_index].relax_error[k] < 0.0:
                        raise RelaxError, "Negative error for residue '" + `self.relax.data.res[self.run][seq_index].num` + " " + self.relax.data.res[self.run][seq_index].name + "', minimisation not possible."

                # Repackage the data.
                if sim_index == None:
                    relax_data.append(self.relax.data.res[self.run][seq_index].relax_data)
                else:
                    relax_data.append(self.relax.data.res[self.run][seq_index].relax_sim_data[sim_index])
                relax_error.append(self.relax.data.res[self.run][seq_index].relax_error)
                equations.append(self.relax.data.res[self.run][seq_index].equation)
                param_types.append(self.relax.data.res[self.run][seq_index].params)
                num_frq.append(self.relax.data.res[self.run][seq_index].num_frq)
                frq.append(self.relax.data.res[self.run][seq_index].frq)
                num_ri.append(self.relax.data.res[self.run][seq_index].num_ri)
                remap_table.append(self.relax.data.res[self.run][seq_index].remap_table)
                noe_r1_table.append(self.relax.data.res[self.run][seq_index].noe_r1_table)
                ri_labels.append(self.relax.data.res[self.run][seq_index].ri_labels)
                if sim_index == None:
                    r.append(self.relax.data.res[self.run][seq_index].r)
                    csa.append(self.relax.data.res[self.run][seq_index].csa)
                else:
                    r.append(self.relax.data.res[self.run][seq_index].r_sim[sim_index])
                    csa.append(self.relax.data.res[self.run][seq_index].csa_sim[sim_index])

                # Model-free parameter values.
                if self.param_set == 'local_tm':
                    pass

                # Vectors.
                if self.param_set != 'local_tm' and self.relax.data.diff[self.run].type != 'iso':
                    xh_unit_vectors.append(self.relax.data.res[self.run][seq_index].xh_unit)
                else:
                    xh_unit_vectors.append(None)

                # Count the number of model-free parameters for the residue index.
                num_params.append(len(self.relax.data.res[self.run][seq_index].params))

                # Repackage the parameter values for minimising just the diffusion tensor parameters.
                if self.param_set == 'diff':
                    param_values.append(self.assemble_param_vector(param_set='mf'))

            # Convert to Numeric arrays.
            for k in xrange(len(relax_data)):
                relax_data[k] = array(relax_data[k], Float64)
                relax_error[k] = array(relax_error[k], Float64)

            # Diffusion tensor type.
            if self.param_set == 'local_tm':
                diff_type = 'iso'
            else:
                diff_type = self.relax.data.diff[self.run].type

            # Package the diffusion tensor parameters.
            diff_params = None
            if self.param_set == 'mf':
                # Alias.
                data = self.relax.data.diff[self.run]

                # Isotropic diffusion.
                if diff_type == 'iso':
                    diff_params = [data.tm]

                # Axially symmetric diffusion.
                elif diff_type == 'axial':
                    diff_params = [data.tm, data.Da, data.theta, data.phi]

                # Anisotropic diffusion.
                elif diff_type == 'aniso':
                    diff_params = [data.tm, data.Da, data.Dr, data.alpha, data.beta, data.gamma]


            # Initialise the function to minimise.
            ######################################

            self.mf = Mf(init_params=self.param_vector, param_set=self.param_set, diff_type=diff_type, diff_params=diff_params, scaling_matrix=self.scaling_matrix, num_res=num_res, equations=equations, param_types=param_types, param_values=param_values, relax_data=relax_data, errors=relax_error, bond_length=r, csa=csa, num_frq=num_frq, frq=frq, num_ri=num_ri, remap_table=remap_table, noe_r1_table=noe_r1_table, ri_labels=ri_labels, gx=self.relax.data.gx, gh=self.relax.data.gh, g_ratio=self.relax.data.g_ratio, h_bar=self.relax.data.h_bar, mu0=self.relax.data.mu0, num_params=num_params, vectors=xh_unit_vectors)


            # Setup the minimisation algorithm when constraints are present.
            ################################################################

            if constraints and not match('^[Gg]rid', min_algor) and min_algor != 'calc':
                algor = min_options[0]
            else:
                algor = min_algor


            # Levenberg-Marquardt minimisation.
            ###################################

            if match('[Ll][Mm]$', algor) or match('[Ll]evenburg-[Mm]arquardt$', algor):
                # Total number of ri.
                number_ri = 0
                for k in xrange(len(relax_error)):
                    number_ri = number_ri + len(relax_error[k])

                # Reconstruct the error data structure.
                lm_error = zeros(number_ri, Float64)
                index = 0
                for k in xrange(len(relax_error)):
                    lm_error[index:len(relax_error[k])] = relax_error[k]
                    index = index + len(relax_error[k])

                min_options = min_options + (self.mf.lm_dri, lm_error)


            # Chi-squared calculation.
            ##########################

            if min_algor == 'calc':
                # Chi-squared.
                try:
                    self.relax.data.res[self.run][i].chi2 = self.mf.func(self.param_vector)
                except OverflowError:
                    self.relax.data.res[self.run][i].chi2 = 1e200

                # Exit the function.
                return


            # Back-calculation.
            ###################

            if min_algor == 'back_calc':
                return self.mf.calc_ri()


            # Minimisation.
            ###############

            if constraints:
                results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, args=(), x0=self.param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, A=A, b=b, full_output=1, print_flag=print_flag)
            else:
                results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, args=(), x0=self.param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, full_output=1, print_flag=print_flag)
            if results == None:
                return
            self.param_vector, self.func, iter, fc, gc, hc, self.warning = results
            self.iter_count = self.iter_count + iter
            self.f_count = self.f_count + fc
            self.g_count = self.g_count + gc
            self.h_count = self.h_count + hc

            # Scaling.
            if scaling:
                self.param_vector = matrixmultiply(self.scaling_matrix, self.param_vector)

            # Disassemble the parameter vector.
            self.disassemble_param_vector(index=index, sim_index=sim_index)

            # Monte Carlo minimisation statistics.
            if sim_index != None:
                # Sequence specific minimisation statistics.
                if self.param_set == 'mf' or self.param_set == 'local_tm':
                    # Chi-squared statistic.
                    self.relax.data.res[self.run][i].chi2_sim[sim_index] = self.func

                    # Iterations.
                    self.relax.data.res[self.run][i].iter_sim[sim_index] = self.iter_count

                    # Function evaluations.
                    self.relax.data.res[self.run][i].f_count_sim[sim_index] = self.f_count

                    # Gradient evaluations.
                    self.relax.data.res[self.run][i].g_count_sim[sim_index] = self.g_count

                    # Hessian evaluations.
                    self.relax.data.res[self.run][i].h_count_sim[sim_index] = self.h_count

                    # Warning.
                    self.relax.data.res[self.run][i].warning_sim[sim_index] = self.warning

                # Global minimisation statistics.
                elif self.param_set == 'diff' or self.param_set == 'all':
                    # Chi-squared statistic.
                    self.relax.data.chi2_sim[self.run][sim_index] = self.func

                    # Iterations.
                    self.relax.data.iter_sim[self.run][sim_index] = self.iter_count

                    # Function evaluations.
                    self.relax.data.f_count_sim[self.run][sim_index] = self.f_count

                    # Gradient evaluations.
                    self.relax.data.g_count_sim[self.run][sim_index] = self.g_count

                    # Hessian evaluations.
                    self.relax.data.h_count_sim[self.run][sim_index] = self.h_count

                    # Warning.
                    self.relax.data.warning_sim[self.run][sim_index] = self.warning

            # Normal statistics.
            else:
                # Sequence specific minimisation statistics.
                if self.param_set == 'mf' or self.param_set == 'local_tm':
                    # Chi-squared statistic.
                    self.relax.data.res[self.run][i].chi2 = self.func

                    # Iterations.
                    self.relax.data.res[self.run][i].iter = self.iter_count

                    # Function evaluations.
                    self.relax.data.res[self.run][i].f_count = self.f_count

                    # Gradient evaluations.
                    self.relax.data.res[self.run][i].g_count = self.g_count

                    # Hessian evaluations.
                    self.relax.data.res[self.run][i].h_count = self.h_count

                    # Warning.
                    self.relax.data.res[self.run][i].warning = self.warning

                # Global minimisation statistics.
                elif self.param_set == 'diff' or self.param_set == 'all':
                    # Chi-squared statistic.
                    self.relax.data.chi2[self.run] = self.func

                    # Iterations.
                    self.relax.data.iter[self.run] = self.iter_count

                    # Function evaluations.
                    self.relax.data.f_count[self.run] = self.f_count

                    # Gradient evaluations.
                    self.relax.data.g_count[self.run] = self.g_count

                    # Hessian evaluations.
                    self.relax.data.h_count[self.run] = self.h_count

                    # Warning.
                    self.relax.data.warning[self.run] = self.warning


    def model_setup(self, run=None, model=None, equation=None, params=None, res_num=None):
        """Function for updating various data structures depending on the model selected."""

        # Test that no diffusion tensor exists for the run if tm is a parameter in the model.
        for param in params:
            if param == 'tm' and self.relax.data.diff.has_key(run):
                raise RelaxTensorError, run

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[run])):
            # Skip unselected residues.
            if not self.relax.data.res[run][i].select:
                continue

            # If res_num is set, then skip all other residues.
            if res_num != None and res_num != self.relax.data.res[run][i].num:
                continue

            # Initialise the data structures (if needed).
            self.initialise_data(self.relax.data.res[run][i], run)

            # Model-free model, equation, and parameter types.
            self.relax.data.res[run][i].model = model
            self.relax.data.res[run][i].equation = equation
            self.relax.data.res[run][i].params = params


    def model_statistics(self, run=None, instance=None):
        """Function for returning k, n, and chi2.

        k - number of parameters.
        n - number of data points.
        chi2 - the chi-squared value.
        """

        # Arguments.
        self.run = run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Missing data sets.
        if not hasattr(self.relax.data.res[self.run][instance], 'relax_data'):
            return None, None, None

        # Sequence specific data.
        if self.param_set == 'mf' or self.param_set == 'local_tm':
            # Create the parameter vector.
            self.param_vector = self.assemble_param_vector(index=instance)

            # Count the number of data points.
            n = len(self.relax.data.res[self.run][instance].relax_data)

            # The chi2 value.
            chi2 = self.relax.data.res[self.run][instance].chi2

        # Other data.
        elif self.param_set == 'diff' or self.param_set == 'all':
            # Create the parameter vector.
            self.param_vector = self.assemble_param_vector()

            # Loop over the sequence.
            n = 0
            for i in xrange(len(self.relax.data.res[self.run])):
                # Skip unselected residues.
                if not self.relax.data.res[self.run][i].select:
                    continue

                # Count the number of data points.
                n = n + len(self.relax.data.res[self.run][i].relax_data)

            # The chi2 value.
            chi2 = self.relax.data.chi2[self.run]

        # Count the number of parameters.
        k = len(self.param_vector)

        # Return the data.
        return k, n, chi2


    def num_instances(self, run=None):
        """Function for returning the number of instances."""

        # Arguments.
        self.run = run

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Test if the diffusion tensor data is loaded.
        if not self.relax.data.diff.has_key(self.run):
            raise RelaxNoTensorError, self.run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Sequence specific data.
        if self.param_set == 'mf' or self.param_set == 'local_tm':
            return len(self.relax.data.res[self.run])

        # Other data.
        elif self.param_set == 'diff' or self.param_set == 'all':
            return 1


    def read_columnar_results(self, run, file_name, file_data):
        """Function for printing the core of the results file."""

        # Arguments.
        self.run = run

        # Get the parameter object names.
        param_names = self.data_names(set='params')

        # Get the minimisation statistic object names.
        min_names = self.data_names(set='min')

        # Extract and remove the header.
        header = file_data[0]
        file_data = file_data[1:]

        # Sort the column numbers.
        col = {}
        for i in xrange(len(header)):
            if header[i] == 'Num':
                col['num'] = i
            elif header[i] == 'Name':
                col['name'] = i
            elif header[i] == 'Selected':
                col['select'] = i
            elif header[i] == 'Data_set':
                col['data_set'] = i
            elif header[i] == 'Nucleus':
                col['nucleus'] = i
            elif header[i] == 'Model':
                col['model'] = i
            elif header[i] == 'Equation':
                col['eqi'] = i
            elif header[i] == 'Params':
                col['params'] = i
            elif header[i] == 'Param_set':
                col['param_set'] = i
            elif header[i] == 'S2':
                col['s2'] = i
            elif header[i] == 'S2f':
                col['s2f'] = i
            elif header[i] == 'S2s':
                col['s2s'] = i
            elif header[i] == 'Local_tm_(ns)':
                col['local_tm'] = i
            elif header[i] == 'tf_(ps)':
                col['tf'] = i
            elif header[i] == 'te_or_ts_(ps)':
                col['te'] = i
            elif header[i] == 'Rex_(1st_field)':
                col['rex'] = i
            elif header[i] == 'Bond_length_(A)':
                col['r'] = i
            elif header[i] == 'CSA_(ppm)':
                col['csa'] = i
            elif header[i] == 'Chi-squared':
                col['chi2'] = i
            elif header[i] == 'Iter':
                col['iter'] = i
            elif header[i] == 'f_count':
                col['f_count'] = i
            elif header[i] == 'g_count':
                col['g_count'] = i
            elif header[i] == 'h_count':
                col['h_count'] = i
            elif header[i] == 'Warning':
                col['warn'] = i

            # Diffusion tensor.
            elif header[i] == 'Diff_type':
                col['diff_type'] = i
            elif header[i] == 'tm_(s)':
                col['tm'] = i
            elif header[i] == 'Da':
                col['da'] = i
            elif header[i] == 'theta_(deg)':
                col['theta'] = i
            elif header[i] == 'phi_(deg)':
                col['phi'] = i
            elif header[i] == 'Da':
                col['da'] = i
            elif header[i] == 'Dr':
                col['dr'] = i
            elif header[i] == 'alpha_(deg)':
                col['alpha'] = i
            elif header[i] == 'beta_(deg)':
                col['beta'] = i
            elif header[i] == 'gamma_(deg)':
                col['gamma'] = i

            # PDB and XH vector.
            elif header[i] == 'PDB':
                col['pdb'] = i
            elif header[i] == 'PDB_model':
                col['pdb_model'] = i
            elif header[i] == 'XH_vector':
                col['xh_vect'] = i

            # Relaxation data.
            elif header[i] == 'Ri_labels':
                col['ri_labels'] = i
            elif header[i] == 'Remap_table':
                col['remap_table'] = i
            elif header[i] == 'Frq_labels':
                col['frq_labels'] = i
            elif header[i] == 'Frequencies':
                col['frq'] = i

        # Test the file.
        if len(col) < 2:
            raise RelaxInvalidFileError, file_name


        # Sequence.
        ###########

        # Generate the sequence.
        for i in xrange(len(file_data)):
            # Skip all lines where the data_set column is not 'value'.
            if file_data[i][col['data_set']] != 'value':
                continue

            # Residue number and name.
            try:
                res_num = int(file_data[i][col['num']])
            except ValueError:
                raise RelaxError, "The residue number " + file_data[i][col['num']] + " is not an integer."
            res_name = file_data[i][col['name']]

            # Add the residue.
            self.relax.generic.sequence.add(self.run, res_num, res_name, select=int(file_data[i][col['select']]))


        # Nucleus.
        ##########

        # Set the nucleus type.
        for i in xrange(len(file_data)):
            if int(file_data[i][col['select']]):
                self.relax.generic.nuclei.set_values(file_data[i][col['nucleus']])
                break


        # Parameter set.
        ################

        # Initialise.
        self.param_set = None

        # The parameter set.
        for i in xrange(len(file_data)):
            if self.param_set == None:
                self.param_set = file_data[i][col['param_set']]

            # Test if diff_type is the same for all residues.
            if self.param_set != file_data[i][col['param_set']]:
                raise RelaxError, "The parameter set is not the same for all residues."


        # Simulations.
        ##############

        # Determine the number of simulations.
        sims = []
        for i in xrange(len(file_data)):
            # The data set.
            data_set = file_data[i][col['data_set']]

            # Add the data set to 'sims' if it is a simulation and if it isn't already in the array.
            if search('sim', data_set) and data_set not in sims:
                sims.append(data_set)

        # Set up the simulations.
        if len(sims):
            self.relax.generic.monte_carlo.setup(self.run, len(sims))


        # Diffusion tensor.
        ###################

        # Get the diffusion tensor.
        diff_type = None
        diff_params = []
        for i in xrange(len(file_data)):
            # Skip all lines where the data_set column is not 'value'.
            if file_data[i][col['data_set']] != 'value':
                continue

            # The diffusion tensor type.
            if not diff_type:
                diff_type = file_data[i][col['diff_type']]

            # Test if diff_type is the same for all residues.
            if diff_type != file_data[i][col['diff_type']]:
                raise RelaxError, "The diffusion tensor is not of the same type for all residues."

            # Temporary diffusion tensor parameters.
            temp_diff_params = []

            # No tensor.
            if diff_type == 'None':
                diff_type = None

            # Isotropic.
            if diff_type == 'iso':
                try:
                    temp_diff_params.append(float(file_data[i][col['tm']]))
                except ValueError:
                    raise RelaxError, "The diffusion tensor parameters are not numbers."

            # Axial symmetery.
            if diff_type == 'axial' or diff_type == 'oblate' or diff_type == 'prolate':
                try:
                    temp_diff_params.append(float(file_data[i][col['tm']]))
                    temp_diff_params.append(float(file_data[i][col['da']]))
                    temp_diff_params.append(float(file_data[i][col['theta']]))
                    temp_diff_params.append(float(file_data[i][col['phi']]))
                except ValueError:
                    raise RelaxError, "The diffusion tensor parameters are not numbers."

            # Anisotropic.
            if diff_type == 'aniso':
                try:
                    temp_diff_params.append(float(file_data[i][col['tm']]))
                    temp_diff_params.append(float(file_data[i][col['da']]))
                    temp_diff_params.append(float(file_data[i][col['dr']]))
                    temp_diff_params.append(float(file_data[i][col['alpha']]))
                    temp_diff_params.append(float(file_data[i][col['beta']]))
                    temp_diff_params.append(float(file_data[i][col['gamma']]))
                except ValueError:
                    raise RelaxError, "The diffusion tensor parameters are not numbers."

            # Diffusion tensor.
            if len(diff_params) == 0:
                diff_params = deepcopy(temp_diff_params)

            # Test if the diffusion tensor parameter are the same for all residues.
            if diff_params != temp_diff_params:
                raise RelaxError, "The diffusion tensor is not the same for all residues."

        # Set the diffusion tensor.
        axial_type = None
        if diff_type == 'oblate' or diff_type == 'prolate':
            axial_type = diff_type
        if diff_type == 'iso':
            diff_params = diff_params[0]
        if diff_type:
            self.relax.generic.diffusion_tensor.set(run=self.run, params=diff_params, axial_type=axial_type)


        # PDB and XH vector.
        ####################

        # Test if the relaxation data is consistent.
        pdb = None
        pdb_model = None
        for i in xrange(len(file_data)):
            # File name.
            if not pdb:
                pdb = file_data[i][col['pdb']]
                pdb_model = eval(file_data[i][col['pdb_model']])

            # Test the file name.
            if pdb != file_data[i][col['pdb']]:
                raise RelaxError, "The PDB file name is not consistent for all residues."

            # Test the model number.
            if pdb_model != eval(file_data[i][col['pdb_model']]):
                raise RelaxError, "The PDB model number is not consistent for all residues."

        # Load the PDB.
        if not pdb == 'None':
            self.relax.generic.pdb.pdb(run=self.run, file=pdb, model=pdb_model)

        # XH vectors.
        for i in xrange(len(file_data)):
            # Skip all lines where the data_set column is not 'value'.
            if file_data[i][col['data_set']] != 'value':
                continue

            # Residue number.
            try:
                res_num = int(file_data[i][col['num']])
            except ValueError:
                raise RelaxError, "The residue number " + file_data[i][col['num']] + " is not an integer."
            res_name = file_data[i][col['name']]

            # Find the residue index.
            index = None
            for j in xrange(len(self.relax.data.res[self.run])):
                if self.relax.data.res[self.run][j].num == res_num and self.relax.data.res[self.run][j].name == res_name:
                    index = j
                    break
            if index == None:
                raise RelaxError, "Residue " + `res_num` + " " + res_name + " cannot be found in the sequence."

            # The vector.
            xh_vect = eval(file_data[i][col['xh_vect']])
            if xh_vect:
                try:
                    xh_vect = array(xh_vect, Float64)
                except:
                    raise RelaxError, "The XH vector " + file_data[i][col['xh_vect']] + " is invalid."

            # Set the vector.
            if xh_vect:
                self.relax.generic.vectors.set(run=self.run, res=index, xh_vect=xh_vect)


        # Relaxation data.
        ##################

        # Test if the relaxation data is consistent.
        ri_labels = None
        for i in xrange(len(file_data)):
            # Relaxation data structures.
            if not ri_labels:
                ri_labels = eval(file_data[i][col['ri_labels']])
                remap_table = eval(file_data[i][col['remap_table']])
                frq_labels = eval(file_data[i][col['frq_labels']])
                frq = eval(file_data[i][col['frq']])

            # Test the data.
            if ri_labels != eval(file_data[i][col['ri_labels']]) or remap_table != eval(file_data[i][col['remap_table']]) or frq_labels != eval(file_data[i][col['frq_labels']]) or frq != eval(file_data[i][col['frq']]):
                raise RelaxError, "The relaxation data is not consistent for all residues."

        # Relaxation data exists.
        if ri_labels and remap_table and frq_labels and frq:
            # Loop over the relaxation data sets.
            for j in xrange(len(ri_labels)):
                # Data and error column.
                data_col = col['frq'] + j + 1
                error_col = col['frq'] + len(ri_labels) + j + 1

                # Reconstruct a data array.
                data_array = []
                for i in xrange(len(file_data)):
                    # Skip all lines where the data_set column is not 'value'.
                    if file_data[i][col['data_set']] != 'value':
                        continue

                    # Skip when data_col is None.
                    if eval(file_data[i][data_col]) == None:
                        continue

                    # Append an array containing the residue number and name and the data and error values.
                    data_array.append([file_data[i][col['num']], file_data[i][col['name']], file_data[i][data_col], file_data[i][error_col]])

                # Read the relaxation data.
                self.relax.specific.relax_data.read(run=self.run, ri_label=ri_labels[j], frq_label=frq_labels[remap_table[j]], frq=frq[remap_table[j]], file_data=data_array)

            # Simulation data.
            if len(sims):
                for i in xrange(len(file_data)):
                    # Skip all lines where the data_set column is not 'value'.
                    if file_data[i][col['data_set']] != 'value':
                        continue

                    # Residue number and name.
                    try:
                        res_num = int(file_data[i][col['num']])
                    except ValueError:
                        raise RelaxError, "The residue number " + file_data[i][col['num']] + " is not an integer."
                    res_name = file_data[i][col['name']]

                    # Find the residue index.
                    res_index = None
                    for j in xrange(len(self.relax.data.res[self.run])):
                        if self.relax.data.res[self.run][j].num == res_num and self.relax.data.res[self.run][j].name == res_name:
                            res_index = j
                            break
                    if res_index == None:
                        raise RelaxError, "Residue " + `res_num` + " " + res_name + " cannot be found in the sequence."

                    # Initialise the simulation data.
                    sim_data = []

                    # Loop over the simulations.
                    for j in xrange(len(sims)):
                        # Append an empty array to sim_data.
                        sim_data.append([])

                        # Sim label.
                        sim_label = 'sim_' + `j`

                        # Find the line of the data file corresponding to the residue number and name and the sim label.
                        for k in xrange(len(file_data)):
                            if int(file_data[k][col['num']]) == res_num and file_data[k][col['name']] == res_name and file_data[k][col['data_set']] == sim_label:
                                # Loop over the relaxation data sets.
                                for l in xrange(len(ri_labels)):
                                    # Data column.
                                    data_col = col['frq'] + l + 1

                                    # Skip when data_col is None.
                                    if eval(file_data[k][data_col]) == None:
                                        continue

                                    # Add the data to sim_data.
                                    try:
                                        sim_data[j].append(eval(file_data[k][data_col]))
                                    except ValueError:
                                        raise RelaxError, "The relaxation data " + `file_data[k][data_col]` + " is not a floating point number."

                    # Pack the simulation data.
                    self.sim_pack_data(self.run, res_index, sim_data)


        # Model-free data.
        ##################

        # Loop over the file data.
        for i in xrange(len(file_data)):
            # The data set.
            data_set = file_data[i][col['data_set']]

            # Residue number and name.
            try:
                res_num = int(file_data[i][col['num']])
            except ValueError:
                raise RelaxError, "The residue number " + file_data[i][col['num']] + " is not an integer."
            res_name = file_data[i][col['name']]

            # Find the residue index.
            index = None
            for j in xrange(len(self.relax.data.res[self.run])):
                if self.relax.data.res[self.run][j].num == res_num and self.relax.data.res[self.run][j].name == res_name:
                    index = j
                    break
            if index == None:
                raise RelaxError, "Residue " + `res_num` + " " + res_name + " cannot be found in the sequence."

            # Reassign data structure.
            res = self.relax.data.res[self.run][index]

            # Skip unselected residues.
            if not res.select:
                continue

            # Set up the model-free models.
            if data_set == 'value':
                model = file_data[i][col['model']]
                equation = file_data[i][col['eqi']]
                params = eval(file_data[i][col['params']])
                if model and equation and params:
                    self.model_setup(self.run, model=model, equation=equation, params=params, res_num=res_num)

            # Values.
            if data_set == 'value':
                # S2.
                try:
                    res.s2 = float(file_data[i][col['s2']])
                except ValueError:
                    res.s2 = None

                # S2f.
                try:
                    res.s2f = float(file_data[i][col['s2f']])
                except ValueError:
                    res.s2f = None

                # S2s.
                try:
                    res.s2s = float(file_data[i][col['s2s']])
                except ValueError:
                    res.s2s = None

                # Local tm.
                try:
                    res.tm = float(file_data[i][col['local_tm']]) * 1e-9
                except ValueError:
                    res.tm = None

                # tf.
                try:
                    res.tf = float(file_data[i][col['tf']]) * 1e-12
                except ValueError:
                    res.tf = None

                # te and ts.
                try:
                    te = float(file_data[i][col['te']]) * 1e-12
                except ValueError:
                    te = None
                if not hasattr(res, 'params'):
                    res.te = None
                    res.ts = None
                elif "te" in res.params:
                    res.te = te
                    res.ts = None
                else:
                    res.te = None
                    res.ts = te

                # Rex.
                try:
                    res.rex = float(file_data[i][col['rex']]) / (2.0 * pi * res.frq[0])**2
                except:
                    res.rex = None

                # Bond length.
                try:
                    res.r = float(file_data[i][col['r']]) * 1e-10
                except ValueError:
                    res.r = None

                # CSA.
                try:
                    res.csa = float(file_data[i][col['csa']]) * 1e-6
                except ValueError:
                    res.csa = None

                # Minimisation details (global minimisation results).
                if self.param_set == 'diff' or self.param_set == 'all':
                    self.relax.data.chi2[self.run] = eval(file_data[i][col['chi2']])
                    self.relax.data.iter[self.run] = eval(file_data[i][col['iter']])
                    self.relax.data.f_count[self.run] = eval(file_data[i][col['f_count']])
                    self.relax.data.g_count[self.run] = eval(file_data[i][col['g_count']])
                    self.relax.data.h_count[self.run] = eval(file_data[i][col['h_count']])
                    self.relax.data.warning[self.run] = eval(replace(file_data[i][col['warn']], '_', ' '))

                # Minimisation details (individual residue results).
                else:
                    res.chi2 = eval(file_data[i][col['chi2']])
                    res.iter = eval(file_data[i][col['iter']])
                    res.f_count = eval(file_data[i][col['f_count']])
                    res.g_count = eval(file_data[i][col['g_count']])
                    res.h_count = eval(file_data[i][col['h_count']])
                    res.warning = eval(replace(file_data[i][col['warn']], '_', ' '))

            # Errors.
            if data_set == 'error':
                # S2.
                try:
                    res.s2_err = float(file_data[i][col['s2']])
                except ValueError:
                    res.s2_err = None

                # S2f.
                try:
                    res.s2f_err = float(file_data[i][col['s2f']])
                except ValueError:
                    res.s2f_err = None

                # S2s.
                try:
                    res.s2s_err = float(file_data[i][col['s2s']])
                except ValueError:
                    res.s2s_err = None

                # Local tm.
                try:
                    res.tm_err = float(file_data[i][col['local_tm']]) * 1e-9
                except ValueError:
                    res.tm_err = None

                # tf.
                try:
                    res.tf_err = float(file_data[i][col['tf']]) * 1e-12
                except ValueError:
                    res.tf_err = None

                # te and ts.
                try:
                    te_err = float(file_data[i][col['te']]) * 1e-12
                except ValueError:
                    te_err = None
                if "te" in res.params:
                    res.te_err = te_err
                    res.ts_err = None
                else:
                    res.te_err = None
                    res.ts_err = te_err

                # Rex.
                try:
                    res.rex_err = float(file_data[i][col['rex']]) / (2.0 * pi * res.frq[0])**2
                except:
                    res.rex_err = None

                # Bond length.
                try:
                    res.r_err = float(file_data[i][col['r']]) * 1e-10
                except ValueError:
                    res.r_err = None

                # CSA.
                try:
                    res.csa_err = float(file_data[i][col['csa']]) * 1e-6
                except ValueError:
                    res.csa_err = None


            # Construct the simulation data structures.
            if data_set == 'sim_0':
                # Loop over all the parameter names.
                for object_name in param_names:
                    # Name for the simulation object.
                    sim_object_name = object_name + '_sim'

                    # Create the simulation object.
                    setattr(res, sim_object_name, [])

                # Loop over all the minimisation object names.
                for object_name in min_names:
                    # Name for the simulation object.
                    sim_object_name = object_name + '_sim'

                    # Create the simulation object.
                    if self.param_set == 'diff' or self.param_set == 'all':
                        setattr(self.relax.data, sim_object_name, {})
                        object = getattr(self.relax.data, sim_object_name)
                        object[self.run] = []
                    else:
                        setattr(res, sim_object_name, [])

            # Simulations.
            if search('sim', data_set):
                # S2.
                try:
                    res.s2_sim.append(float(file_data[i][col['s2']]))
                except ValueError:
                    res.s2_sim.append(None)

                # S2f.
                try:
                    res.s2f_sim.append(float(file_data[i][col['s2f']]))
                except ValueError:
                    res.s2f_sim.append(None)

                # S2s.
                try:
                    res.s2s_sim.append(float(file_data[i][col['s2s']]))
                except ValueError:
                    res.s2s_sim.append(None)

                # Local tm.
                try:
                    res.tm_sim.append(float(file_data[i][col['local_tm']]) * 1e-9)
                except ValueError:
                    res.tm_sim.append(None)

                # tf.
                try:
                    res.tf_sim.append(float(file_data[i][col['tf']]) * 1e-12)
                except ValueError:
                    res.tf_sim.append(None)

                # te and ts.
                try:
                    te = float(file_data[i][col['te']]) * 1e-12
                except ValueError:
                    te = None
                if "te" in res.params:
                    res.te_sim.append(te)
                    res.ts_sim.append(None)
                else:
                    res.te_sim.append(None)
                    res.ts_sim.append(te)

                # Rex.
                try:
                    res.rex_sim.append(float(file_data[i][col['rex']]) / (2.0 * pi * res.frq[0])**2)
                except:
                    res.rex_sim.append(None)

                # Bond length.
                try:
                    res.r_sim.append(float(file_data[i][col['r']]) * 1e-10)
                except ValueError:
                    res.r_sim.append(None)

                # CSA.
                try:
                    res.csa_sim.append(float(file_data[i][col['csa']]) * 1e-6)
                except ValueError:
                    res.csa_sim.append(None)

                # Minimisation details (global minimisation results).
                if self.param_set == 'diff' or self.param_set == 'all':
                    self.relax.data.chi2_sim[self.run].append(eval(file_data[i][col['chi2']]))
                    self.relax.data.iter_sim[self.run].append(eval(file_data[i][col['iter']]))
                    self.relax.data.f_count_sim[self.run].append(eval(file_data[i][col['f_count']]))
                    self.relax.data.g_count_sim[self.run].append(eval(file_data[i][col['g_count']]))
                    self.relax.data.h_count_sim[self.run].append(eval(file_data[i][col['h_count']]))
                    self.relax.data.warning_sim[self.run].append(eval(replace(file_data[i][col['warn']], '_', ' ')))

                # Minimisation details (individual residue results).
                else:
                    res.chi2_sim.append(eval(file_data[i][col['chi2']]))
                    res.iter_sim.append(eval(file_data[i][col['iter']]))
                    res.f_count_sim.append(eval(file_data[i][col['f_count']]))
                    res.g_count_sim.append(eval(file_data[i][col['g_count']]))
                    res.h_count_sim.append(eval(file_data[i][col['h_count']]))
                    res.warning_sim.append(eval(replace(file_data[i][col['warn']], '_', ' ')))


    def return_value(self, run, i, data_type):
        """Function for returning the value and error corresponding to 'data_type'."""

        # Arguments.
        self.run = run

        # Get the object.
        object_name = self.get_data_name(data_type)
        if not object_name:
            raise RelaxError, "The model-free data type " + `data_type` + " does not exist."
        object_error = object_name + "_err"

        # Get the value.
        if hasattr(self.relax.data.res[self.run][i], object_name):
            value = getattr(self.relax.data.res[self.run][i], object_name)
        else:
            value = None

        # Get the error.
        if hasattr(self.relax.data.res[self.run][i], object_error):
            error = getattr(self.relax.data.res[self.run][i], object_error)
        else:
            error = None

        # Return the data.
        return value, error


    def select_model(self, run=None, model=None, res_num=None):
        """Function for the selection of a preset model-free model."""

        # Run argument.
        self.run = run

        # Test if the run exists.
        if not self.run in self.relax.data.run_names:
            raise RelaxNoRunError, self.run

        # Test if the run type is set to 'mf'.
        function_type = self.relax.data.run_types[self.relax.data.run_names.index(self.run)]
        if function_type != 'mf':
            raise RelaxFuncSetupError, self.relax.specific_setup.get_string(function_type)

        # Test if sequence data is loaded.
        if not self.relax.data.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run


        # Preset models.
        ################

        # Block 1.
        if model == 'm0':
            equation = 'mf_orig'
            params = []
        elif model == 'm1':
            equation = 'mf_orig'
            params = ['S2']
        elif model == 'm2':
            equation = 'mf_orig'
            params = ['S2', 'te']
        elif model == 'm3':
            equation = 'mf_orig'
            params = ['S2', 'Rex']
        elif model == 'm4':
            equation = 'mf_orig'
            params = ['S2', 'te', 'Rex']
        elif model == 'm5':
            equation = 'mf_ext'
            params = ['S2f', 'S2', 'ts']
        elif model == 'm6':
            equation = 'mf_ext'
            params = ['S2f', 'tf', 'S2', 'ts']
        elif model == 'm7':
            equation = 'mf_ext'
            params = ['S2f', 'S2', 'ts', 'Rex']
        elif model == 'm8':
            equation = 'mf_ext'
            params = ['S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'm9':
            equation = 'mf_orig'
            params = ['Rex']

        # Block 2.
        elif model == 'm10':
            equation = 'mf_orig'
            params = ['CSA']
        elif model == 'm11':
            equation = 'mf_orig'
            params = ['CSA', 'S2']
        elif model == 'm12':
            equation = 'mf_orig'
            params = ['CSA', 'S2', 'te']
        elif model == 'm13':
            equation = 'mf_orig'
            params = ['CSA', 'S2', 'Rex']
        elif model == 'm14':
            equation = 'mf_orig'
            params = ['CSA', 'S2', 'te', 'Rex']
        elif model == 'm15':
            equation = 'mf_ext'
            params = ['CSA', 'S2f', 'S2', 'ts']
        elif model == 'm16':
            equation = 'mf_ext'
            params = ['CSA', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'm17':
            equation = 'mf_ext'
            params = ['CSA', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'm18':
            equation = 'mf_ext'
            params = ['CSA', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'm19':
            equation = 'mf_orig'
            params = ['CSA', 'Rex']

        # Block 3.
        elif model == 'm20':
            equation = 'mf_orig'
            params = ['r']
        elif model == 'm21':
            equation = 'mf_orig'
            params = ['r', 'S2']
        elif model == 'm22':
            equation = 'mf_orig'
            params = ['r', 'S2', 'te']
        elif model == 'm23':
            equation = 'mf_orig'
            params = ['r', 'S2', 'Rex']
        elif model == 'm24':
            equation = 'mf_orig'
            params = ['r', 'S2', 'te', 'Rex']
        elif model == 'm25':
            equation = 'mf_ext'
            params = ['r', 'S2f', 'S2', 'ts']
        elif model == 'm26':
            equation = 'mf_ext'
            params = ['r', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'm27':
            equation = 'mf_ext'
            params = ['r', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'm28':
            equation = 'mf_ext'
            params = ['r', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'm29':
            equation = 'mf_orig'
            params = ['r', 'Rex']

        # Block 4.
        elif model == 'm30':
            equation = 'mf_orig'
            params = ['r', 'CSA']
        elif model == 'm31':
            equation = 'mf_orig'
            params = ['r', 'CSA', 'S2']
        elif model == 'm32':
            equation = 'mf_orig'
            params = ['r', 'CSA', 'S2', 'te']
        elif model == 'm33':
            equation = 'mf_orig'
            params = ['r', 'CSA', 'S2', 'Rex']
        elif model == 'm34':
            equation = 'mf_orig'
            params = ['r', 'CSA', 'S2', 'te', 'Rex']
        elif model == 'm35':
            equation = 'mf_ext'
            params = ['r', 'CSA', 'S2f', 'S2', 'ts']
        elif model == 'm36':
            equation = 'mf_ext'
            params = ['r', 'CSA', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'm37':
            equation = 'mf_ext'
            params = ['r', 'CSA', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'm38':
            equation = 'mf_ext'
            params = ['r', 'CSA', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'm39':
            equation = 'mf_orig'
            params = ['r', 'CSA', 'Rex']


        # Preset models with local correlation time.
        ############################################

        # Block 1.
        elif model == 'tm0':
            equation = 'mf_orig'
            params = ['tm']
        elif model == 'tm1':
            equation = 'mf_orig'
            params = ['tm', 'S2']
        elif model == 'tm2':
            equation = 'mf_orig'
            params = ['tm', 'S2', 'te']
        elif model == 'tm3':
            equation = 'mf_orig'
            params = ['tm', 'S2', 'Rex']
        elif model == 'tm4':
            equation = 'mf_orig'
            params = ['tm', 'S2', 'te', 'Rex']
        elif model == 'tm5':
            equation = 'mf_ext'
            params = ['tm', 'S2f', 'S2', 'ts']
        elif model == 'tm6':
            equation = 'mf_ext'
            params = ['tm', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'tm7':
            equation = 'mf_ext'
            params = ['tm', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'tm8':
            equation = 'mf_ext'
            params = ['tm', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'tm9':
            equation = 'mf_orig'
            params = ['tm', 'Rex']

        # Block 2.
        elif model == 'tm10':
            equation = 'mf_orig'
            params = ['tm', 'CSA']
        elif model == 'tm11':
            equation = 'mf_orig'
            params = ['tm', 'CSA', 'S2']
        elif model == 'tm12':
            equation = 'mf_orig'
            params = ['tm', 'CSA', 'S2', 'te']
        elif model == 'tm13':
            equation = 'mf_orig'
            params = ['tm', 'CSA', 'S2', 'Rex']
        elif model == 'tm14':
            equation = 'mf_orig'
            params = ['tm', 'CSA', 'S2', 'te', 'Rex']
        elif model == 'tm15':
            equation = 'mf_ext'
            params = ['tm', 'CSA', 'S2f', 'S2', 'ts']
        elif model == 'tm16':
            equation = 'mf_ext'
            params = ['tm', 'CSA', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'tm17':
            equation = 'mf_ext'
            params = ['tm', 'CSA', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'tm18':
            equation = 'mf_ext'
            params = ['tm', 'CSA', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'tm19':
            equation = 'mf_orig'
            params = ['tm', 'CSA', 'Rex']

        # Block 3.
        elif model == 'tm20':
            equation = 'mf_orig'
            params = ['tm', 'r']
        elif model == 'tm21':
            equation = 'mf_orig'
            params = ['tm', 'r', 'S2']
        elif model == 'tm22':
            equation = 'mf_orig'
            params = ['tm', 'r', 'S2', 'te']
        elif model == 'tm23':
            equation = 'mf_orig'
            params = ['tm', 'r', 'S2', 'Rex']
        elif model == 'tm24':
            equation = 'mf_orig'
            params = ['tm', 'r', 'S2', 'te', 'Rex']
        elif model == 'tm25':
            equation = 'mf_ext'
            params = ['tm', 'r', 'S2f', 'S2', 'ts']
        elif model == 'tm26':
            equation = 'mf_ext'
            params = ['tm', 'r', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'tm27':
            equation = 'mf_ext'
            params = ['tm', 'r', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'tm28':
            equation = 'mf_ext'
            params = ['tm', 'r', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'tm29':
            equation = 'mf_orig'
            params = ['tm', 'r', 'Rex']

        # Block 4.
        elif model == 'tm30':
            equation = 'mf_orig'
            params = ['tm', 'r', 'CSA']
        elif model == 'tm31':
            equation = 'mf_orig'
            params = ['tm', 'r', 'CSA', 'S2']
        elif model == 'tm32':
            equation = 'mf_orig'
            params = ['tm', 'r', 'CSA', 'S2', 'te']
        elif model == 'tm33':
            equation = 'mf_orig'
            params = ['tm', 'r', 'CSA', 'S2', 'Rex']
        elif model == 'tm34':
            equation = 'mf_orig'
            params = ['tm', 'r', 'CSA', 'S2', 'te', 'Rex']
        elif model == 'tm35':
            equation = 'mf_ext'
            params = ['tm', 'r', 'CSA', 'S2f', 'S2', 'ts']
        elif model == 'tm36':
            equation = 'mf_ext'
            params = ['tm', 'r', 'CSA', 'S2f', 'tf', 'S2', 'ts']
        elif model == 'tm37':
            equation = 'mf_ext'
            params = ['tm', 'r', 'CSA', 'S2f', 'S2', 'ts', 'Rex']
        elif model == 'tm38':
            equation = 'mf_ext'
            params = ['tm', 'r', 'CSA', 'S2f', 'tf', 'S2', 'ts', 'Rex']
        elif model == 'tm39':
            equation = 'mf_orig'
            params = ['tm', 'r', 'CSA', 'Rex']

        # Invalid models.
        else:
            raise RelaxError, "The model '" + model + "' is invalid."

        # Set up the model.
        self.model_setup(self.run, model, equation, params, res_num)


    def set(self, run=None, value=None, error=None, data_type=None, index=None):
        """
        Model-free set details
        ~~~~~~~~~~~~~~~~~~~~~~

        Setting a parameter value may have no effect depending on which model-free model is chosen,
        for example if S2f values and S2s values are set but the run corresponds to model-free model
        'm4' then, because these data values are not parameters of the model, they will have no
        effect.

        Note that the Rex values are scaled quadratically with field strength and should be supplied
        as a field strength independent value.  Use the following formula to get the correct value:

            value = Rex / (2.0 * pi * frequency) ** 2

        where:
            Rex is the chemical exchange value for the current frequency.
            pi is in the namespace of relax, ie just type 'pi'.
            frequency is the proton frequency corresponding to the data.
        """

        # Arguments.
        self.run = run

        # Setting the model parameters prior to minimisation.
        #####################################################

        if data_type == None:
            # The values are supplied by the user:
            if value:
                # Test if the length of the value array is equal to the length of the model-free parameter array.
                if len(value) != len(self.relax.data.res[self.run][index].params):
                    raise RelaxError, "The length of " + `len(value)` + " of the value array must be equal to the length of the model-free parameter array, " + `self.relax.data.res[self.run][index].params` + ", for residue " + `self.relax.data.res[self.run][index].num` + " " + self.relax.data.res[self.run][index].name + "."

            # Default values.
            else:
                # Set 'value' to an empty array.
                value = []

                # Loop over the model-free parameters.
                for i in xrange(len(self.relax.data.res[self.run][index].params)):
                    value.append(self.default_value(self.relax.data.res[self.run][index].params[i]))

            # Loop over the model-free parameters.
            for i in xrange(len(self.relax.data.res[self.run][index].params)):
                # Get the object.
                object_name = self.get_data_name(self.relax.data.res[self.run][index].params[i])
                if not object_name:
                    raise RelaxError, "The model-free data type " + `self.relax.data.res[self.run][index].params[i]` + " does not exist."

                # Initialise all data if it doesn't exist.
                if not hasattr(self.relax.data.res[self.run][index], object_name):
                    self.initialise_data(self.relax.data.res[self.run][index], self.run)

                # Set the value.
                setattr(self.relax.data.res[self.run][index], object_name, float(value[i]))


        # Individual data type.
        #######################

        else:
            # Get the object.
            object_name = self.get_data_name(data_type)
            if not object_name:
                raise RelaxError, "The model-free data type " + `data_type` + " does not exist."

            # Initialise all data if it doesn't exist.
            if not hasattr(self.relax.data.res[self.run][index], object_name):
                self.initialise_data(self.relax.data.res[self.run][index], self.run)

            # Default value.
            if value == None:
                value = self.default_value(object_name)

            # Set the value.
            setattr(self.relax.data.res[self.run][index], object_name, float(value))

            # Set the error.
            if error != None:
                setattr(self.relax.data.res[self.run][index], object_name+'_error', float(error))


    def set_error(self, run, instance, index, error):
        """Function for setting parameter errors."""

        # Arguments.
        self.run = run

        # Increment counter for the parameter set 'all'.
        inc = 0

        # Get the parameter object names.
        param_names = self.data_names(set='params')


        # Diffusion tensor parameter errors.
        ####################################

        if self.param_set == 'diff' or self.param_set == 'all':
            # Isotropic diffusion.
            if self.relax.data.diff[self.run].type == 'iso':
                # Return the parameter array.
                if index == 0:
                    self.relax.data.diff[self.run].tm_err = error

                # Increment.
                inc = inc + 1

            # Axially symmetric diffusion.
            elif self.relax.data.diff[self.run].type == 'axial':
                # Return the parameter array.
                if index == 0:
                    self.relax.data.diff[self.run].tm_err = error
                elif index == 1:
                    self.relax.data.diff[self.run].Da_err = error
                elif index == 2:
                    self.relax.data.diff[self.run].theta_err = error
                elif index == 3:
                    self.relax.data.diff[self.run].phi_err = error

                # Increment.
                inc = inc + 4

            # Anisotropic diffusion.
            elif self.relax.data.diff[self.run].type == 'aniso':
                # Return the parameter array.
                if index == 0:
                    self.relax.data.diff[self.run].tm_err = error
                elif index == 1:
                    self.relax.data.diff[self.run].Da_err = error
                elif index == 2:
                    self.relax.data.diff[self.run].Dr_err = error
                elif index == 3:
                    self.relax.data.diff[self.run].alpha_err = error
                elif index == 4:
                    self.relax.data.diff[self.run].beta_err = error
                elif index == 5:
                    self.relax.data.diff[self.run].gamma_err = error

                # Increment.
                inc = inc + 6


        # Model-free parameter errors for the parameter set 'all'.
        ##########################################################

        if self.param_set == 'all':
            # Loop over the sequence.
            for i in xrange(len(self.relax.data.res[self.run])):
                # Skip unselected residues.
                if not self.relax.data.res[self.run][i].select:
                    continue

                # Loop over the residue specific parameters.
                for param in param_names:
                    # Return the parameter array.
                    if index == inc:
                        setattr(self.relax.data.res[self.run][i], param + "_err", error)

                    # Increment.
                    inc = inc + 1


        # Model-free parameters for the parameter sets 'mf' and 'local_tm'.
        ###################################################################

        if self.param_set == 'mf' or self.param_set == 'local_tm':
            # Skip unselected residues.
            if not self.relax.data.res[self.run][instance].select:
                return

            # Loop over the residue specific parameters.
            for param in param_names:
                # Return the parameter array.
                if index == inc:
                    setattr(self.relax.data.res[self.run][instance], param + "_err", error)

                # Increment.
                inc = inc + 1


    def sim_init_values(self, run):
        """Function for initialising Monte Carlo parameter values."""

        # Arguments.
        self.run = run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Get the parameter object names.
        param_names = self.data_names(set='params')

        # Get the minimisation statistic object names.
        min_names = self.data_names(set='min')

        # List of diffusion tensor parameters.
        if self.param_set == 'diff' or self.param_set == 'all':
            # Isotropic diffusion.
            if self.relax.data.diff[self.run].type == 'iso':
                diff_params = ['tm']

            # Axially symmetric diffusion.
            elif self.relax.data.diff[self.run].type == 'axial':
                diff_params = ['tm', 'Da', 'theta', 'phi']

            # Anisotropic diffusion.
            elif self.relax.data.diff[self.run].type == 'aniso':
                diff_params = ['tm', 'Da', 'Dr', 'alpha', 'beta', 'gamma']


        # Test if Monte Carlo parameter values have already been set.
        #############################################################

        # Diffusion tensor parameters and non residue specific minimisation statistics.
        if self.param_set == 'diff' or self.param_set == 'all':
            # Loop over the parameters.
            for object_name in diff_params:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Test if the simulation object already exists.
                if hasattr(self.relax.data.diff[self.run], sim_object_name):
                    raise RelaxError, "Monte Carlo parameter values have already been set."

            # Loop over the minimisation stats objects.
            for object_name in min_names:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Test if the simulation object already exists.
                if hasattr(self.relax.data, sim_object_name):
                    raise RelaxError, "Monte Carlo parameter values have already been set."

        # Residue specific parameters.
        if self.param_set != 'diff':
            for i in xrange(len(self.relax.data.res[self.run])):
                # Skip unselected residues.
                if not self.relax.data.res[self.run][i].select:
                    continue

                # Loop over all the parameter names.
                for object_name in param_names:
                    # Name for the simulation object.
                    sim_object_name = object_name + '_sim'

                    # Test if the simulation object already exists.
                    if hasattr(self.relax.data.res[self.run][i], sim_object_name):
                        raise RelaxError, "Monte Carlo parameter values have already been set."


        # Set the Monte Carlo parameter values.
        #######################################

        # Diffusion tensor parameters and non residue specific minimisation statistics.
        if self.param_set == 'diff' or self.param_set == 'all':
            # Loop over the parameters.
            for object_name in diff_params:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Create the simulation object.
                setattr(self.relax.data.diff[self.run], sim_object_name, [])

                # Get the simulation object.
                sim_object = getattr(self.relax.data.diff[self.run], sim_object_name)

                # Loop over the simulations.
                for j in xrange(self.relax.data.sim_number[self.run]):
                    # Copy and append the data.
                    sim_object.append(deepcopy(getattr(self.relax.data.diff[self.run], object_name)))

            # Loop over the minimisation stats objects.
            for object_name in min_names:
                # Name for the simulation object.
                sim_object_name = object_name + '_sim'

                # Create the simulation object.
                setattr(self.relax.data, sim_object_name, {})

                # Get the simulation object.
                sim_object = getattr(self.relax.data, sim_object_name)

                # Add the run.
                sim_object[self.run] = []

                # Loop over the simulations.
                for j in xrange(self.relax.data.sim_number[self.run]):
                    # Get the object.
                    object = getattr(self.relax.data, object_name)

                    # Copy and append the data.
                    sim_object[self.run].append(deepcopy(object[self.run]))

        # Residue specific parameters.
        if self.param_set != 'diff':
            for i in xrange(len(self.relax.data.res[self.run])):
                # Skip unselected residues.
                if not self.relax.data.res[self.run][i].select:
                    continue

                # Loop over all the data names.
                for object_name in param_names:
                    # Name for the simulation object.
                    sim_object_name = object_name + '_sim'

                    # Create the simulation object.
                    setattr(self.relax.data.res[self.run][i], sim_object_name, [])

                    # Get the simulation object.
                    sim_object = getattr(self.relax.data.res[self.run][i], sim_object_name)

                    # Loop over the simulations.
                    for j in xrange(self.relax.data.sim_number[self.run]):
                        # Copy and append the data.
                        sim_object.append(deepcopy(getattr(self.relax.data.res[self.run][i], object_name)))

                # Loop over all the minimisation object names.
                if self.param_set != 'all':
                    for object_name in min_names:
                        # Name for the simulation object.
                        sim_object_name = object_name + '_sim'

                        # Create the simulation object.
                        setattr(self.relax.data.res[self.run][i], sim_object_name, [])

                        # Get the simulation object.
                        sim_object = getattr(self.relax.data.res[self.run][i], sim_object_name)

                        # Loop over the simulations.
                        for j in xrange(self.relax.data.sim_number[self.run]):
                            # Copy and append the data.
                            sim_object.append(deepcopy(getattr(self.relax.data.res[self.run][i], object_name)))


    def sim_return_chi2(self, run, instance):
        """Function for returning the array of simulation chi-squared values."""

        # Arguments.
        self.run = run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Single instance.
        if self.param_set == 'all' or self.param_set == 'diff':
            return self.relax.data.chi2_sim[self.run]

        # Multiple instances.
        else:
            return self.relax.data.res[self.run][instance].chi2_sim


    def sim_return_param(self, run, instance, index):
        """Function for returning the array of simulation parameter values."""

        # Arguments.
        self.run = run

        # Increment counter for the parameter set 'all'.
        inc = 0

        # Get the parameter object names.
        param_names = self.data_names(set='params')


        # Diffusion tensor parameters.
        ##############################

        if self.param_set == 'diff' or self.param_set == 'all':
            # Isotropic diffusion.
            if self.relax.data.diff[self.run].type == 'iso':
                # Return the parameter array.
                if index == 0:
                    return self.relax.data.diff[self.run].tm_sim

                # Increment.
                inc = inc + 1

            # Axially symmetric diffusion.
            elif self.relax.data.diff[self.run].type == 'axial':
                # Return the parameter array.
                if index == 0:
                    return self.relax.data.diff[self.run].tm_sim
                elif index == 1:
                    return self.relax.data.diff[self.run].Da_sim
                elif index == 2:
                    return self.relax.data.diff[self.run].theta_sim
                elif index == 3:
                    return self.relax.data.diff[self.run].phi_sim

                # Increment.
                inc = inc + 4

            # Anisotropic diffusion.
            elif self.relax.data.diff[self.run].type == 'aniso':
                # Return the parameter array.
                if index == 0:
                    return self.relax.data.diff[self.run].tm_sim
                elif index == 1:
                    return self.relax.data.diff[self.run].Da_sim
                elif index == 2:
                    return self.relax.data.diff[self.run].Dr_sim
                elif index == 3:
                    return self.relax.data.diff[self.run].alpha_sim
                elif index == 4:
                    return self.relax.data.diff[self.run].beta_sim
                elif index == 5:
                    return self.relax.data.diff[self.run].gamma_sim

                # Increment.
                inc = inc + 6


        # Model-free parameters for the parameter set 'all'.
        ####################################################

        if self.param_set == 'all':
            # Loop over the sequence.
            for i in xrange(len(self.relax.data.res[self.run])):
                # Skip unselected residues.
                if not self.relax.data.res[self.run][i].select:
                    continue

                # Loop over the residue specific parameters.
                for param in param_names:
                    # Return the parameter array.
                    if index == inc:
                        return getattr(self.relax.data.res[self.run][i], param + "_sim")

                    # Increment.
                    inc = inc + 1


        # Model-free parameters for the parameter sets 'mf' and 'local_tm'.
        ###################################################################

        if self.param_set == 'mf' or self.param_set == 'local_tm':
            # Skip unselected residues.
            if not self.relax.data.res[self.run][instance].select:
                return

            # Loop over the residue specific parameters.
            for param in param_names:
                # Return the parameter array.
                if index == inc:
                    return getattr(self.relax.data.res[self.run][instance], param + "_sim")

                # Increment.
                inc = inc + 1


    def skip_function(self, run=None, instance=None):
        """Function for skiping certain data."""

        # Arguments.
        self.run = run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Sequence specific data.
        if self.param_set == 'mf' or self.param_set == 'local_tm':
            if not self.relax.data.res[self.run][instance].select:
                return 1
            else:
                return 0

        # Other data types.
        elif self.param_set == 'diff' or self.param_set == 'all':
            return 0


    def unselect(self, run, i):
        """Function for unselecting models."""

        # Arguments.
        self.run = run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()

        # Single residue.
        if self.param_set == 'mf' or self.param_set == 'local_tm':
            self.relax.data.res[self.run][i].select = 0

        # All residues.
        else:
            self.relax.data.select[self.run] = 0


    def write_columnar_line(self, file=None, num=None, name=None, select=None, data_set=None, nucleus=None, model=None, equation=None, params=None, param_set=None, s2=None, s2f=None, s2s=None, local_tm=None, tf=None, te=None, rex=None, r=None, csa=None, chi2=None, i=None, f=None, g=None, h=None, warn=None, diff_type=None, diff_params=None, pdb=None, pdb_model=None, xh_vect=None, ri_labels=None, remap_table=None, frq_labels=None, frq=None, ri=None, ri_error=None):
        """Function for printing a single line of the columnar formatted results."""

        # Residue number and name.
        file.write("%-4s %-5s " % (num, name))

        # Selected flag and data set.
        file.write("%-9s %-9s " % (select, data_set))
        if not select:
            file.write("\n")
            return

        # Nucleus.
        file.write("%-7s " % nucleus)

        # Model details.
        file.write("%-5s %-9s %-35s " % (model, equation, params))

        # Parameter set.
        file.write("%-10s " % param_set)

        # Parameters.
        file.write("%-25s " % s2)
        file.write("%-25s " % s2f)
        file.write("%-25s " % s2s)
        file.write("%-25s " % local_tm)
        file.write("%-25s " % tf)
        file.write("%-25s " % te)
        file.write("%-25s " % rex)
        file.write("%-25s " % r)
        file.write("%-25s " % csa)

        # Minimisation results.
        file.write("%-25s %-8s %-8s %-8s %-8s %-45s " % (chi2, i, f, g, h, warn))

        # Diffusion parameters.
        file.write("%-10s " % diff_type)
        if diff_params:
            for i in xrange(len(diff_params)):
                file.write("%-25s " % diff_params[i])

        # PDB.
        file.write("%-40s " % pdb)
        file.write("%-10s " % pdb_model)

        # XH vector.
        file.write("%-70s " % xh_vect)

        # Relaxation data setup.
        if ri_labels:
            file.write("%-40s " % ri_labels)
            file.write("%-25s " % remap_table)
            file.write("%-25s " % frq_labels)
            file.write("%-30s " % frq)

        # Relaxation data.
        if ri:
            for i in xrange(len(ri)):
                if ri[i] == None:
                    file.write("%-25s " % 'None')
                else:
                    file.write("%-25s " % ri[i])

        # Relaxation errors.
        if ri_error:
            for i in xrange(len(ri_error)):
                if ri_error[i] == None:
                    file.write("%-25s " % 'None')
                else:
                    file.write("%-25s " % ri_error[i])

        # End of the line.
        file.write("\n")


    def write_columnar_results(self, file, run):
        """Function for printing the results into a file."""

        # Arguments.
        self.run = run

        # Determine the parameter set type.
        self.param_set = self.determine_param_set_type()


        # Header.
        #########

        # Diffusion parameters.
        diff_params = None
        if self.param_set != 'local_tm' and hasattr(self.relax.data, 'diff') and self.relax.data.diff.has_key(self.run):
            # Isotropic.
            if self.relax.data.diff[self.run].type == 'iso':
                diff_params = ['tm_(s)']

            # Axially symmetric.
            elif self.relax.data.diff[self.run].type == 'axial':
                diff_params = ['tm_(s)', 'Da_(1/s)', 'theta_(deg)', 'phi_(deg)']

            # Anisotropic.
            elif self.relax.data.diff[self.run].type == 'aniso':
                diff_params = ['tm_(s)', 'Da_(1/s)', 'Dr_(1/s)', 'alpha_(deg)', 'beta_(deg)', 'gamma_(deg)']

        # Relaxation data and errors.
        ri = []
        ri_error = []
        if hasattr(self.relax.data, 'num_ri'):
            for i in xrange(self.relax.data.num_ri[self.run]):
                ri.append('Ri_(' + self.relax.data.ri_labels[self.run][i] + "_" + self.relax.data.frq_labels[self.run][self.relax.data.remap_table[self.run][i]] + ")")
                ri_error.append('Ri_error_(' + self.relax.data.ri_labels[self.run][i] + "_" + self.relax.data.frq_labels[self.run][self.relax.data.remap_table[self.run][i]] + ")")

        # Write the header line.
        self.write_columnar_line(file=file, num='Num', name='Name', select='Selected', data_set='Data_set', nucleus='Nucleus', model='Model', equation='Equation', params='Params', param_set='Param_set', s2='S2', s2f='S2f', s2s='S2s', local_tm='Local_tm_(ns)', tf='tf_(ps)', te='te_or_ts_(ps)', rex='Rex_(1st_field)', r='Bond_length_(A)', csa='CSA_(ppm)', chi2='Chi-squared', i='Iter', f='f_count', g='g_count', h='h_count', warn='Warning', diff_type='Diff_type', diff_params=diff_params, pdb='PDB', pdb_model='PDB_model', xh_vect='XH_vector', ri_labels='Ri_labels', remap_table='Remap_table', frq_labels='Frq_labels', frq='Frequencies', ri=ri, ri_error=ri_error)


        # Values.
        #########

        # Nucleus.
        nucleus = self.relax.generic.nuclei.find_nucleus()

        # Diffusion parameters.
        diff_type = None
        diff_params = None
        if self.param_set != 'local_tm' and hasattr(self.relax.data, 'diff') and self.relax.data.diff.has_key(self.run):
            # Isotropic.
            if self.relax.data.diff[self.run].type == 'iso':
                diff_type = 'iso'
                diff_params = [`self.relax.data.diff[self.run].tm`]

            # Axially symmetric.
            elif self.relax.data.diff[self.run].type == 'axial':
                diff_type = self.relax.data.diff[self.run].axial_type
                if diff_type == None:
                    diff_type = 'axial'
                diff_params = [`self.relax.data.diff[self.run].tm`, `self.relax.data.diff[self.run].Da`, `self.relax.data.diff[self.run].theta * 360 / (2.0 * pi)`, `self.relax.data.diff[self.run].phi * 360 / (2.0 * pi)`]

            # Anisotropic.
            elif self.relax.data.diff[self.run].type == 'aniso':
                diff_type = 'aniso'
                diff_params = [`self.relax.data.diff[self.run].tm`, `self.relax.data.diff[self.run].Da`, `self.relax.data.diff[self.run].Dr`, `self.relax.data.diff[self.run].alpha * 360 / (2.0 * pi)`, `self.relax.data.diff[self.run].beta * 360 / (2.0 * pi)`, `self.relax.data.diff[self.run].gamma * 360 / (2.0 * pi)`]

        # PDB.
        pdb = None
        pdb_model = None
        if hasattr(self.relax.data, 'pdb') and self.relax.data.pdb.has_key(self.run):
            pdb = self.relax.data.pdb[self.run].filename
            pdb_model = self.relax.data.pdb[self.run].user_model

        # Relaxation data setup.
        try:
            ri_labels = replace(`self.relax.data.ri_labels[self.run]`, ' ', '')
            remap_table = replace(`self.relax.data.remap_table[self.run]`, ' ', '')
            frq_labels = replace(`self.relax.data.frq_labels[self.run]`, ' ', '')
            frq = replace(`self.relax.data.frq[self.run]`, ' ', '')
        except AttributeError:
            ri_labels = `None`
            remap_table = `None`
            frq_labels = `None`
            frq = `None`

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Reassign data structure.
            res = self.relax.data.res[self.run][i]

            # Unselected residues.
            if not res.select:
                self.write_columnar_line(file=file, num=res.num, name=res.name, select=0, data_set='value')
                continue

            # Model details.
            model = None
            if hasattr(res, 'model'):
                model = res.model

            equation = None
            if hasattr(res, 'equation'):
                equation = res.equation

            params = None
            if hasattr(res, 'params'):
                params = replace(`res.params`, ' ', '')

            # S2.
            s2 = None
            if hasattr(res, 's2'):
                s2 = res.s2

            # S2f.
            s2f = None
            if hasattr(res, 's2f'):
                s2f = res.s2f

            # S2s.
            s2s = None
            if hasattr(res, 's2s'):
                s2s = res.s2s

            # tm.
            local_tm = None
            if hasattr(res, 'tm') and res.tm != None:
                local_tm = res.tm / 1e-9

            # tf.
            tf = None
            if hasattr(res, 'tf') and res.tf != None:
                tf = res.tf / 1e-12

            # te or ts.
            te = None
            if hasattr(res, 'te') and res.te != None:
                te = res.te / 1e-12
            elif hasattr(res, 'ts') and res.ts != None:
                te = res.ts / 1e-12

            # Rex.
            rex = None
            if hasattr(res, 'rex') and res.rex != None:
                rex = res.rex * (2.0 * pi * res.frq[0])**2

            # Bond length.
            r = None
            if hasattr(res, 'r') and res.r != None:
                r = res.r / 1e-10

            # CSA.
            csa = None
            if hasattr(res, 'csa') and res.csa != None:
                csa = res.csa / 1e-6

            # Minimisation details.
            try:
                # Global minimisation results.
                if self.param_set == 'diff' or self.param_set == 'all':
                    chi2 = self.relax.data.chi2[self.run]
                    iter = self.relax.data.iter[self.run]
                    f = self.relax.data.f_count[self.run]
                    g = self.relax.data.g_count[self.run]
                    h = self.relax.data.h_count[self.run]
                    if type(self.relax.data.warning[self.run]) == str:
                        warn = replace(self.relax.data.warning[self.run], ' ', '_')
                    else:
                        warn = self.relax.data.warning[self.run]

                # Individual residue results.
                else:
                    chi2 = res.chi2
                    iter = res.iter
                    f = res.f_count
                    g = res.g_count
                    h = res.h_count
                    if type(res.warning) == str:
                        warn = replace(res.warning, ' ', '_')
                    else:
                        warn = res.warning

            # No minimisation details.
            except:
                chi2 = None
                iter = None
                f = None
                g = None
                h = None
                warn = None

            # XH vector.
            xh_vect = None
            if hasattr(res, 'xh_vect'):
                xh_vect = replace(`res.xh_vect.tolist()`, ' ', '')

            # Relaxation data and errors.
            ri = []
            ri_error = []
            if hasattr(self.relax.data, 'num_ri'):
                for i in xrange(self.relax.data.num_ri[self.run]):
                    # Find the residue specific data corresponding to i.
                    index = None
                    for j in xrange(res.num_ri):
                        if res.ri_labels[j] == self.relax.data.ri_labels[self.run][i] and res.frq_labels[res.remap_table[j]] == self.relax.data.frq_labels[self.run][self.relax.data.remap_table[self.run][i]]:
                            index = j

                    # Data exists for this data type.
                    try:
                        ri.append(`res.relax_data[index]`)
                        ri_error.append(`res.relax_error[index]`)
                    except:
                        ri.append(None)
                        ri_error.append(None)

            # Write the line.
            self.write_columnar_line(file=file, num=res.num, name=res.name, select=res.select, data_set='value', nucleus=nucleus, model=model, equation=equation, params=params, param_set=self.param_set, s2=`s2`, s2f=`s2f`, s2s=`s2s`, local_tm=`local_tm`, tf=`tf`, te=`te`, rex=`rex`, r=`r`, csa=`csa`, chi2=chi2, i=iter, f=f, g=g, h=h, warn=warn, diff_type=diff_type, diff_params=diff_params, pdb=pdb, pdb_model=pdb_model, xh_vect=xh_vect, ri_labels=ri_labels, remap_table=remap_table, frq_labels=frq_labels, frq=frq, ri=ri, ri_error=ri_error)


        # Errors.
        #########

        # Skip this section and the next if no simulations have been setup.
        if not hasattr(self.relax.data, 'sim_state'):
            return
        elif self.relax.data.sim_state[self.run] == 0:
            return

        # Diffusion parameters.
        diff_params = None
        if self.param_set != 'local_tm' and hasattr(self.relax.data, 'diff') and self.relax.data.diff.has_key(self.run):
            # Diffusion parameter errors.
            if self.param_set == 'diff' or self.param_set == 'all':
                # Isotropic.
                if self.relax.data.diff[self.run].type == 'iso':
                    diff_params = [`self.relax.data.diff[self.run].tm_err`]

                # Axially symmetric.
                elif self.relax.data.diff[self.run].type == 'axial':
                    diff_params = [`self.relax.data.diff[self.run].tm_err`, `self.relax.data.diff[self.run].Da_err`, `self.relax.data.diff[self.run].theta_err`, `self.relax.data.diff[self.run].phi_err`]

                # Anisotropic.
                elif self.relax.data.diff[self.run].type == 'aniso':
                    diff_params = [`self.relax.data.diff[self.run].tm_err`, `self.relax.data.diff[self.run].Da_err`, `self.relax.data.diff[self.run].Dr_err`, `self.relax.data.diff[self.run].alpha_err`, `self.relax.data.diff[self.run].beta_err`, `self.relax.data.diff[self.run].gamma_err`]

            # No errors.
            else:
                # Isotropic.
                if self.relax.data.diff[self.run].type == 'iso':
                    diff_params = [None]

                # Axially symmetric.
                elif self.relax.data.diff[self.run].type == 'axial':
                    diff_params = [None, None, None, None]

                # Anisotropic.
                elif self.relax.data.diff[self.run].type == 'aniso':
                    diff_params = [None, None, None, None, None, None]

        # Loop over the sequence.
        for i in xrange(len(self.relax.data.res[self.run])):
            # Reassign data structure.
            res = self.relax.data.res[self.run][i]

            # Unselected residues.
            if not res.select:
                self.write_columnar_line(file=file, num=res.num, name=res.name, select=0, data_set='error')
                continue

            # S2.
            s2 = None
            if hasattr(res, 's2_err'):
                s2 = res.s2_err

            # S2f.
            s2f = None
            if hasattr(res, 's2f_err'):
                s2f = res.s2f_err

            # S2s.
            s2s = None
            if hasattr(res, 's2s_err'):
                s2s = res.s2s_err

            # tm.
            local_tm = None
            if hasattr(res, 'tm_err') and res.tm_err != None:
                local_tm = res.tm_err / 1e-9

            # tf.
            tf = None
            if hasattr(res, 'tf_err') and res.tf_err != None:
                tf = res.tf_err / 1e-12

            # te or ts.
            te = None
            if hasattr(res, 'te_err') and res.te_err != None:
                te = res.te_err / 1e-12
            elif hasattr(res, 'ts_err') and res.ts_err != None:
                te = res.ts_err / 1e-12

            # Rex.
            rex = None
            if hasattr(res, 'rex_err') and res.rex_err != None:
                rex = res.rex_err * (2.0 * pi * res.frq[0])**2

            # Bond length.
            r = None
            if hasattr(res, 'r_err') and res.r_err != None:
                r = res.r_err / 1e-10

            # CSA.
            csa = None
            if hasattr(res, 'csa_err') and res.csa_err != None:
                csa = res.csa_err / 1e-6

            # Relaxation data and errors.
            ri = []
            ri_error = []
            for i in xrange(self.relax.data.num_ri[self.run]):
                ri.append(None)
                ri_error.append(None)

            # Write the line.
            self.write_columnar_line(file=file, num=res.num, name=res.name, select=res.select, data_set='error', nucleus=nucleus, model=res.model, equation=res.equation, params=params, param_set=self.param_set, s2=`s2`, s2f=`s2f`, s2s=`s2s`, local_tm=`local_tm`, tf=`tf`, te=`te`, rex=`rex`, r=`r`, csa=`csa`, diff_type=diff_type, diff_params=diff_params, pdb=pdb, pdb_model=pdb_model, xh_vect=xh_vect, ri_labels=ri_labels, remap_table=remap_table, frq_labels=frq_labels, frq=frq, ri=ri, ri_error=ri_error)


        # Simulation values.
        ####################

        # Loop over the simulations.
        for i in xrange(self.relax.data.sim_number[self.run]):
            # Diffusion parameters.
            diff_params = None
            if self.param_set != 'local_tm' and hasattr(self.relax.data, 'diff') and self.relax.data.diff.has_key(self.run):
                # Diffusion parameter simulation values.
                if self.param_set == 'diff' or self.param_set == 'all':
                    # Isotropic.
                    if self.relax.data.diff[self.run].type == 'iso':
                        diff_params = [`self.relax.data.diff[self.run].tm_sim[i]`]

                    # Axially symmetric.
                    elif self.relax.data.diff[self.run].type == 'axial':
                        diff_params = [`self.relax.data.diff[self.run].tm_sim[i]`, `self.relax.data.diff[self.run].Da_sim[i]`, `self.relax.data.diff[self.run].theta_sim[i]`, `self.relax.data.diff[self.run].phi_sim[i]`]

                    # Anisotropic.
                    elif self.relax.data.diff[self.run].type == 'aniso':
                        diff_params = [`self.relax.data.diff[self.run].tm_sim[i]`, `self.relax.data.diff[self.run].Da_sim[i]`, `self.relax.data.diff[self.run].Dr_sim[i]`, `self.relax.data.diff[self.run].alpha_sim[i]`, `self.relax.data.diff[self.run].beta_sim[i]`, `self.relax.data.diff[self.run].gamma_sim[i]`]

                # No simulation values.
                else:
                    # Isotropic.
                    if self.relax.data.diff[self.run].type == 'iso':
                        diff_params = [None]

                    # Axially symmetric.
                    elif self.relax.data.diff[self.run].type == 'axial':
                        diff_params = [None, None, None, None]

                    # Anisotropic.
                    elif self.relax.data.diff[self.run].type == 'aniso':
                        diff_params = [None, None, None, None, None, None]

            # Loop over the sequence.
            for j in xrange(len(self.relax.data.res[self.run])):
                # Reassign data structure.
                res = self.relax.data.res[self.run][j]

                # Unselected residues.
                if not res.select:
                    self.write_columnar_line(file=file, num=res.num, name=res.name, select=0, data_set='sim_'+`i`)
                    continue

                # S2.
                s2 = None
                if hasattr(res, 's2_sim'):
                    s2 = res.s2_sim[i]

                # S2f.
                s2f = None
                if hasattr(res, 's2f_sim'):
                    s2f = res.s2f_sim[i]

                # S2s.
                s2s = None
                if hasattr(res, 's2s_sim'):
                    s2s = res.s2s_sim[i]

                # tm.
                local_tm = None
                if hasattr(res, 'tm_sim') and res.tm_sim[i] != None:
                    local_tm = res.tm_sim[i] / 1e-9

                # tf.
                tf = None
                if hasattr(res, 'tf_sim') and res.tf_sim[i] != None:
                    tf = res.tf_sim[i] / 1e-12

                # te or ts.
                te = None
                if hasattr(res, 'te_sim') and res.te_sim[i] != None:
                    te = res.te_sim[i] / 1e-12
                elif hasattr(res, 'ts_sim') and res.ts_sim[i] != None:
                    te = res.ts_sim[i] / 1e-12

                # Rex.
                rex = None
                if hasattr(res, 'rex_sim') and res.rex_sim[i] != None:
                    rex = res.rex_sim[i] * (2.0 * pi * res.frq[0])**2

                # Bond length.
                r = None
                if hasattr(res, 'r_sim') and res.r_sim[i] != None:
                    r = res.r_sim[i] / 1e-10

                # CSA.
                csa = None
                if hasattr(res, 'csa_sim') and res.csa_sim[i] != None:
                    csa = res.csa_sim[i] / 1e-6

                # Minimisation details.
                try:
                    # Global minimisation results.
                    if self.param_set == 'diff' or self.param_set == 'all':
                        chi2 = self.relax.data.chi2_sim[self.run][i]
                        iter = self.relax.data.iter_sim[self.run][i]
                        f = self.relax.data.f_count_sim[self.run][i]
                        g = self.relax.data.g_count_sim[self.run][i]
                        h = self.relax.data.h_count_sim[self.run][i]
                        if type(self.relax.data.warning_sim[self.run][i]) == str:
                            warn = replace(self.relax.data.warning_sim[self.run][i], ' ', '_')
                        else:
                            warn = self.relax.data.warning_sim[self.run][i]

                    # Individual residue results.
                    else:
                        chi2 = res.chi2_sim[i]
                        iter = res.iter_sim[i]
                        f = res.f_count_sim[i]
                        g = res.g_count_sim[i]
                        h = res.h_count_sim[i]
                        if type(res.warning_sim[i]) == str:
                            warn = replace(res.warning_sim[i], ' ', '_')
                        else:
                            warn = res.warning_sim[i]

                # No minimisation details.
                except AttributeError:
                    chi2 = None
                    iter = None
                    f = None
                    g = None
                    h = None
                    warn = None

                # Relaxation data and errors.
                ri = []
                ri_error = []
                for k in xrange(self.relax.data.num_ri[self.run]):
                    # Find the residue specific data corresponding to k.
                    index = None
                    for l in xrange(res.num_ri):
                        if res.ri_labels[l] == self.relax.data.ri_labels[self.run][k] and res.frq_labels[res.remap_table[l]] == self.relax.data.frq_labels[self.run][self.relax.data.remap_table[self.run][k]]:
                            index = l

                    # Data exists for this data type.
                    try:
                        ri.append(`res.relax_sim_data[i][index]`)
                        ri_error.append(`res.relax_error[index]`)
                    except:
                        ri.append(None)
                        ri_error.append(None)

                # Write the line.
                self.write_columnar_line(file=file, num=res.num, name=res.name, select=res.select, data_set='sim_'+`i`, nucleus=nucleus, model=res.model, equation=res.equation, params=params, param_set=self.param_set, s2=`s2`, s2f=`s2f`, s2s=`s2s`, local_tm=`local_tm`, tf=`tf`, te=`te`, rex=`rex`, r=`r`, csa=`csa`, chi2=`chi2`, i=iter, f=f, g=g, h=h, warn=warn, diff_type=diff_type, diff_params=diff_params, pdb=pdb, pdb_model=pdb_model, xh_vect=xh_vect, ri_labels=ri_labels, remap_table=remap_table, frq_labels=frq_labels, frq=frq, ri=ri, ri_error=ri_error)
