###############################################################################
#                                                                             #
# Copyright (C) 2003 Edward d'Auvergne                                        #
#                                                                             #
# This file is part of the program relax.                                     #
#                                                                             #
# Relax is free software; you can redistribute it and/or modify               #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation; either version 2 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# Relax is distributed in the hope that it will be useful,                    #
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
from math import pi
from Numeric import Float64, array, matrixmultiply, ones, transpose, zeros
from re import match
from string import replace
import sys

from functions.mf import Mf
from minimise.generic import generic_minimise


class Model_free:
    def __init__(self, relax):
        """Class containing functions specific to model-free analysis."""

        self.relax = relax


    def assemble_param_vector(self, run, data):
        """Function for assembling various pieces of data into a Numeric parameter array."""

        # Initialise.
        param_vector = zeros(len(data.params[run]), Float64)

        # Loop over the parameters.
        for i in range(len(data.params[run])):
            # S2.
            if data.params[run][i] == 'S2' and data.s2[run] != None:
                param_vector[i] = data.s2[run]

            # S2f.
            if data.params[run][i] == 'S2f' and data.s2f[run] != None:
                param_vector[i] = data.s2f[run]

            # S2s.
            if data.params[run][i] == 'S2s' and data.s2s[run] != None:
                param_vector[i] = data.s2s[run]

            # te.
            if data.params[run][i] == 'te' and data.te[run] != None:
                param_vector[i] = data.te[run]

            # tf.
            if data.params[run][i] == 'tf' and data.tf[run] != None:
                param_vector[i] = data.tf[run]

            # ts.
            if data.params[run][i] == 'ts' and data.ts[run] != None:
                param_vector[i] = data.ts[run]

            # Rex.
            if data.params[run][i] == 'Rex' and data.rex[run] != None:
                param_vector[i] = data.rex[run]

            # r.
            if data.params[run][i] == 'r' and data.r[run] != None:
                param_vector[i] = data.r[run]

            # CSA.
            if data.params[run][i] == 'CSA' and data.csa[run] != None:
                param_vector[i] = data.csa[run]

        return param_vector


    def assemble_scaling_matrix(self, run, data, index):
        """Function for creating the scaling matrix."""

        # Initialise.
        scaling_matrix = zeros((len(data.params[run]), len(data.params[run])), Float64)

        # Loop over the parameters.
        for i in range(len(data.params[run])):
            # tm.
            if data.params[run][i] == 'tm':
                scaling_matrix[i, i] = 1e-12

            # te, tf, and ts.
            elif match('t', data.params[run][i]):
                scaling_matrix[i, i] = 1e-12

            # Rex.
            elif data.params[run][i] == 'Rex':
                scaling_matrix[i, i] = 1.0 / (2.0 * pi * self.relax.data.res[index].frq[run][0]) ** 2

            # Bond length.
            elif data.params[run][i] == 'r':
                scaling_matrix[i, i] = 1e-10

            # CSA.
            elif data.params[run][i] == 'CSA':
                scaling_matrix[i, i] = 1e-4

            # No scaling.
            else:
                scaling_matrix[i, i] = 1.0

        return scaling_matrix


    def calculate(self, run=None, i=None, params=None, scaling_matrix=None):
        """Calculation of the model-free chi-squared value."""

        # Set up the relaxation data and errors and the function options.
        relax_data = array(self.relax.data.res[i].relax_data[run], Float64)
        relax_error = array(self.relax.data.res[i].relax_error[run], Float64)
        self.function_ops = ()

        # Initialise the functions used in the minimisation.
        self.mf = Mf(self.relax, run=run, i=i, equation=self.relax.data.res[i].equations[run], param_types=self.relax.data.res[i].params[run], init_params=params, relax_data=relax_data, errors=relax_error, bond_length=self.relax.data.res[i].r[run], csa=self.relax.data.res[i].csa[run], diff_type=self.relax.data.diff_type[run], diff_params=self.relax.data.diff_params[run], scaling_matrix=scaling_matrix)

        # Chi-squared calculation.
        self.relax.data.res[i].chi2[run] = self.mf.func(params, 0)


    def create(self, run=None, model=None, equation=None, params=None, scaling=1):
        """Function to create a model-free model."""

        # Test if sequence data is loaded.
        if not len(self.relax.data.res):
            raise RelaxSequenceError

        # Check the validity of the model-free equation type.
        valid_types = ['mf_orig', 'mf_ext', 'mf_ext2']
        if not equation in valid_types:
            raise RelaxError, "The model-free equation type argument " + `equation` + " is invalid and should be one of " + `valid_types` + "."

        # Check the validity of the parameter array.
        s2, te, s2f, tf, s2s, ts, rex, csa, r = 0, 0, 0, 0, 0, 0, 0, 0, 0
        for i in range(len(params)):
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
                for j in range(len(params)):
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
                for j in range(len(params)):
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
                for j in range(len(params)):
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
                for j in range(len(params)):
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

        # Add the run to the runs list.
        if not run in self.relax.data.runs:
            self.relax.data.runs.append(run)

        # Set up the model.
        self.model_setup(run, model, equation, params, scaling)


    def data_init(self, name):
        """Function for returning an initial data structure corresponding to 'name'."""

        # Empty arrays.
        list_data = [ 'models',
                      'params' ]
        if name in list_data:
            return []

        # None.
        none_data = [ 'equations',
                      'scaling',
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


    def data_names(self):
        """Function for returning a list of names of data structures associated with model-free.

        Description
        ~~~~~~~~~~~

        The names are as follows:

        model: The model-free model name.

        equations:  The model-free equation type.

        params:  An array of the model-free parameter names associated with the model.

        scaling:  The scaling flag.

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

        names = [ 'models',
                  'equations',
                  'params',
                  'scaling',
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

        return names


    def model_setup(self, run, model, equation, params, scaling_flag):
        """Function for updating various data structures depending on the model selected."""

        # Loop over the sequence.
        for i in range(len(self.relax.data.res)):
            # Skip unselected residues.
            if not self.relax.data.res[i].select:
                continue

            # Initialise the data structures (if needed).
            self.initialise_mf_data(self.relax.data.res[i], run)

            # Model-free models, equations, and parameter types.
            self.relax.data.res[i].models[run] = model
            self.relax.data.res[i].equations[run] = equation
            self.relax.data.res[i].params[run] = params

            # Diagonal scaling.
            self.relax.data.res[i].scaling[run] = scaling_flag


    def fixed_setup(self, params=None, min_options=None):
        """The fixed parameter value setup function."""

        for i in range(len(params)):
            # {S2, S2f, S2s}.
            if match('S2', params[i]):
                min_options[i] = 0.5

            # {te, tf, ts}.
            elif match('t', params[i]):
                if params[i] == 'tf':
                    min_options[i] = 10.0 * 1e-12
                elif params[i] == 'ts':
                    min_options[i] = 1000.0 * 1e-12
                else:
                    min_options[i] = 100.0 * 1e-12

            # Rex.
            if params[i] == 'Rex':
                min_options[i] = 0.0

            # Bond length.
            if params[i] == 'r':
                min_options[i] = 1.02 * 1e-10

            # CSA.
            if params[i] == 'CSA':
                min_options[i] = -170 * 1e-6

        return min_options


    def grid_setup(self, run=None, params=None, index=None, inc_vector=None):
        """The grid search setup function."""

        # Initialise.
        min_options = []

        for i in range(len(params)):
            # {S2, S2f, S2s}.
            if match('S2', params[i]):
                min_options.append([inc_vector[i], 0.0, 1.0])

            # {te, tf, ts}.
            elif match('t', params[i]):
                min_options.append([inc_vector[i], 0.0, 10000.0 * 1e-12])

            # Rex.
            elif params[i] == 'Rex':
                min_options.append([inc_vector[i], 0.0, 10.0 / (2.0 * pi * self.relax.data.res[index].frq[run][0])**2])

            # Bond length.
            elif params[i] == 'r':
                min_options.append([inc_vector[i], 1.0 * 1e-10, 1.05 * 1e-10])

            # CSA.
            elif params[i] == 'CSA':
                min_options.append([inc_vector[i], -120 * 1e-6, -200 * 1e-6])

        return min_options


    def initialise_mf_data(self, data, run):
        """Function for the initialisation of model-free data structures.

        Only data structures which do not exist are created.
        """

        # Get the data names.
        data_names = self.data_names()

        # Loop over the names.
        for name in data_names:
            # If the name is not in 'data', add it.
            if not hasattr(data, name):
                setattr(data, name, {})

            # Get the data.
            object = getattr(data, name)

            # Get the initial data structure.
            value = self.data_init(name)

            # If the data structure does not have the key 'run', add it.
            if not object.has_key(run):
                object[run] = value


    def linear_constraints(self, run=None, data=None, index=None):
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
        n = len(data.params[run])
        zero_array = zeros(n, Float64)
        j = 0

        # The original model-free equations.
        for i in range(n):
            # Order parameters {S2, S2f, S2s}.
            if match('S2', data.params[run][i]):
                # 0 <= S2 <= 1.
                A.append(zero_array * 0.0)
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                A[j+1][i] = -1.0
                b.append(0.0)
                b.append(-1.0)
                j = j + 2

                # S2 <= S2f and S2 <= S2s.
                if data.params[run][i] == 'S2':
                    for k in range(n):
                        if data.params[run][k] == 'S2f' or data.params[run][k] == 'S2s':
                            A.append(zero_array * 0.0)
                            A[j][i] = -1.0
                            A[j][k] = 1.0
                            b.append(0.0)
                            j = j + 1

            # Correlation times {tm, te, tf, ts}.
            elif match('t', data.params[run][i]):
                # te >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0)
                j = j + 1

                # tf <= ts.
                if data.params[run][i] == 'ts':
                    for k in range(n):
                        if data.params[run][k] == 'tf':
                            A.append(zero_array * 0.0)
                            A[j][i] = 1.0
                            A[j][k] = -1.0
                            b.append(0.0)
                            j = j + 1

            # Rex.
            elif data.params[run][i] == 'Rex':
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0)
                j = j + 1

            # Bond length.
            elif match('r', data.params[run][i]):
                # 0.9e-10 <= r <= 2e-10.
                A.append(zero_array * 0.0)
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                A[j+1][i] = -1.0
                b.append(0.9e-10)
                b.append(-2e-10)
                j = j + 2

            # CSA.
            elif match('CSA', data.params[run][i]):
                # -300e-6 <= CSA <= 0.
                A.append(zero_array * 0.0)
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                A[j+1][i] = -1.0
                b.append(-300e-6)
                b.append(0.0)
                j = j + 2

        # Convert to Numeric data structures.
        A = array(A, Float64)
        b = array(b, Float64)

        return A, b


    def macro_create(self, run=None, model=None, equation=None, params=None, scaling=1):
        """Macro to create a model-free model.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The run to assign the values to.

        model:  The name of the model-free model.

        equation:  The model-free equation.

        params:  The parameters of the model.

        scaling:  The diagonal scaling flag.


        Description
        ~~~~~~~~~~~

        Model-free equation.

        'mf_orig' selects the original model-free equations with parameters {S2, te}.
        'mf_ext' selects the extended model-free equations with parameters {S2f, tf, S2, ts}.
        'mf_ext2' selects the extended model-free equations with parameters {S2f, tf, S2s, ts}.


        Model-free parameters.

        The following parameters are accepted for the original model-free equation:
            S2:     The square of the generalised order parameter.
            te:     The effective correlation time.
        The following parameters are accepted for the extended model-free equation:
            S2f:    The square of the generalised order parameter of the faster motion.
            tf:     The effective correlation time of the faster motion.
            S2:     The square of the generalised order parameter S2 = S2f*S2s.
            ts:     The effective correlation time of the slower motion.
        The following parameters are accepted for the extended 2 model-free equation:
            S2f:    The square of the generalised order parameter of the faster motion.
            tf:     The effective correlation time of the faster motion.
            S2s:    The square of the generalised order parameter of the slower motion.
            ts:     The effective correlation time of the slower motion.
        The following parameters are accepted for all equations:
            Rex:    The chemical exchange relaxation.
            r:      The average bond length <r>.
            CSA:    The chemical shift anisotropy.


        Diagonal scaling.

        This is the scaling of parameter values with the intent of having the same order of
        magnitude for all parameters values.  For example, if S2 = 0.5, te = 200 ps, and
        Rex = 15 1/s at 600 MHz, the unscaled parameter vector would be [0.5, 2.0e-10, 1.055e-18]
        (Rex is divided by (2*pi*600,000,000)**2 to make it field strength independent).  The
        scaling vector for this model is [1.0, 1e-10, 1/(2*pi*6*1e8)**2].  By dividing the unscaled
        parameter vector by the scaling vector the scaled parameter vector is [0.5, 2.0, 15.0].  To
        revert to the original unscaled parameter vector, the scaled parameter vector and scaling
        vector are multiplied.  The reason for diagonal scaling is that certain minimisation
        techniques fail when the model is not properly scaled.


        Examples
        ~~~~~~~~

        The following commands will create the model-free model 'm1' which is based on the original
        model-free equation and contains the single parameter 'S2'.

        relax> model.create_mf('m1', 'm1', 'mf_orig', ['S2'])
        relax> model.create_mf(run='m1', model='m1', params=['S2'], equation='mf_orig')


        The following commands will create the model-free model 'large_model' which is based on the
        extended model-free equation and contains the seven parameters 'S2f', 'tf', 'S2', 'ts',
        'Rex', 'CSA', 'r'.

        relax> model.create_mf('test', 'large_model', 'mf_ext', ['S2f', 'tf', 'S2', 'ts', 'Rex',
                               'CSA', 'r'])
        relax> model.create_mf(run='test', model='large_model', params=['S2f', 'tf', 'S2', 'ts',
                               'Rex', 'CSA', 'r'], equation='mf_ext')
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = sys.macro_prompt + "model.create_mf("
            text = text + "run=" + `run`
            text = text + ", model=" + `model`
            text = text + ", equation=" + `equation`
            text = text + ", params=" + `params`
            text = text + ", scaling=" + `scaling` + ")"
            print text

        # Run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Model argument.
        if type(model) != str:
            raise RelaxStrError, ('model', model)

        # Equation.
        if equation == None:
            raise RelaxNoneError, 'model-free equation'
        elif type(equation) != str:
            raise RelaxStrError, ('model-free equation', equation)

        # Parameter types.
        if params == None:
            raise RelaxNoneError, 'parameter types'
        elif type(params) != list:
            raise RelaxListError, ('parameter types', params)
        for i in range(len(params)):
            if type(params[i]) != str:
                raise RelaxListStrError, ('parameter types', params)

        # Scaling.
        if type(scaling) != int or (scaling != 0 and scaling != 1):
            raise RelaxBinError, ('scaling', scaling)

        # Execute the functional code.
        self.create(run=run, model=model, equation=equation, params=params, scaling=scaling)


    def macro_select(self, run=None, model=None, scaling=1):
        """Macro for the selection of a preset model-free model.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The run to assign the values to.

        model:  The name of the preset model.

        scaling:  The diagonal scaling flag.


        Description
        ~~~~~~~~~~~

        The preset model-free models are:
            'm0'    => []
            'm1'    => [S2]
            'm2'    => [S2, te]
            'm3'    => [S2, Rex]
            'm4'    => [S2, te, Rex]
            'm5'    => [S2f, S2, ts]
            'm6'    => [S2f, tf, S2, ts]
            'm7'    => [S2f, S2, ts, Rex]
            'm8'    => [S2f, tf, S2, ts, Rex]
            'm9'    => [Rex]

            'm10'   => [CSA]
            'm11'   => [CSA, S2]
            'm12'   => [CSA, S2, te]
            'm13'   => [CSA, S2, Rex]
            'm14'   => [CSA, S2, te, Rex]
            'm15'   => [CSA, S2f, S2, ts]
            'm16'   => [CSA, S2f, tf, S2, ts]
            'm17'   => [CSA, S2f, S2, ts, Rex]
            'm18'   => [CSA, S2f, tf, S2, ts, Rex]
            'm19'   => [CSA, Rex]

            'm20'   => [r]
            'm21'   => [r, S2]
            'm22'   => [r, S2, te]
            'm23'   => [r, S2, Rex]
            'm24'   => [r, S2, te, Rex]
            'm25'   => [r, S2f, S2, ts]
            'm26'   => [r, S2f, tf, S2, ts]
            'm27'   => [r, S2f, S2, ts, Rex]
            'm28'   => [r, S2f, tf, S2, ts, Rex]
            'm29'   => [r, CSA, Rex]

            'm30'   => [r, CSA]
            'm31'   => [r, CSA, S2]
            'm32'   => [r, CSA, S2, te]
            'm33'   => [r, CSA, S2, Rex]
            'm34'   => [r, CSA, S2, te, Rex]
            'm35'   => [r, CSA, S2f, S2, ts]
            'm36'   => [r, CSA, S2f, tf, S2, ts]
            'm37'   => [r, CSA, S2f, S2, ts, Rex]
            'm38'   => [r, CSA, S2f, tf, S2, ts, Rex]
            'm39'   => [r, CSA, Rex]

        Warning:  The models in the thirties range fail when using standard R1, R2, and NOE
        relaxation data.  This is due to the extreme flexibly of these models where a change in the
        parameter 'r' is compensated by a corresponding change in the parameter 'CSA' and
        vice versa.


        Additional preset model-free models, which are simply extensions of the above models with
        the addition of a local tm parameter are:
            'tm0'   => [tm]
            'tm1'   => [tm, S2]
            'tm2'   => [tm, S2, te]
            'tm3'   => [tm, S2, Rex]
            'tm4'   => [tm, S2, te, Rex]
            'tm5'   => [tm, S2f, S2, ts]
            'tm6'   => [tm, S2f, tf, S2, ts]
            'tm7'   => [tm, S2f, S2, ts, Rex]
            'tm8'   => [tm, S2f, tf, S2, ts, Rex]
            'tm9'   => [tm, Rex]

            'tm10'  => [tm, CSA]
            'tm11'  => [tm, CSA, S2]
            'tm12'  => [tm, CSA, S2, te]
            'tm13'  => [tm, CSA, S2, Rex]
            'tm14'  => [tm, CSA, S2, te, Rex]
            'tm15'  => [tm, CSA, S2f, S2, ts]
            'tm16'  => [tm, CSA, S2f, tf, S2, ts]
            'tm17'  => [tm, CSA, S2f, S2, ts, Rex]
            'tm18'  => [tm, CSA, S2f, tf, S2, ts, Rex]
            'tm19'  => [tm, CSA, Rex]

            'tm20'  => [tm, r]
            'tm21'  => [tm, r, S2]
            'tm22'  => [tm, r, S2, te]
            'tm23'  => [tm, r, S2, Rex]
            'tm24'  => [tm, r, S2, te, Rex]
            'tm25'  => [tm, r, S2f, S2, ts]
            'tm26'  => [tm, r, S2f, tf, S2, ts]
            'tm27'  => [tm, r, S2f, S2, ts, Rex]
            'tm28'  => [tm, r, S2f, tf, S2, ts, Rex]
            'tm29'  => [tm, r, CSA, Rex]

            'tm30'  => [tm, r, CSA]
            'tm31'  => [tm, r, CSA, S2]
            'tm32'  => [tm, r, CSA, S2, te]
            'tm33'  => [tm, r, CSA, S2, Rex]
            'tm34'  => [tm, r, CSA, S2, te, Rex]
            'tm35'  => [tm, r, CSA, S2f, S2, ts]
            'tm36'  => [tm, r, CSA, S2f, tf, S2, ts]
            'tm37'  => [tm, r, CSA, S2f, S2, ts, Rex]
            'tm38'  => [tm, r, CSA, S2f, tf, S2, ts, Rex]
            'tm39'  => [tm, r, CSA, Rex]



        Diagonal scaling.

        This is the scaling of parameter values with the intent of having the same order of
        magnitude for all parameters values.  For example, if S2 = 0.5, te = 200 ps, and
        Rex = 15 1/s at 600 MHz, the unscaled parameter vector would be [0.5, 2.0e-10, 1.055e-18]
        (Rex is divided by (2*pi*600,000,000)**2 to make it field strength independent).  The
        scaling vector for this model is [1.0, 1e-10, 1/(2*pi*6*1e8)**2].  By dividing the unscaled
        parameter vector by the scaling vector the scaled parameter vector is [0.5, 2.0, 15.0].  To
        revert to the original unscaled parameter vector, the scaled parameter vector and scaling
        vector are multiplied.  The reason for diagonal scaling is that certain minimisation
        techniques fail when the model is not properly scaled.


        Examples
        ~~~~~~~~

        To pick model 'm1' for all selected residues and assign it to the run 'mixed', type:

        relax> model.select_mf('mixed', 'm1')
        relax> model.select_mf(run='mixed', model='m1', scaling=1)
        """

        # Macro intro text.
        if self.relax.interpreter.intro:
            text = sys.macro_prompt + "model.select_mf("
            text = text + "run=" + `run`
            text = text + ", model=" + `model`
            text = text + ", scaling=" + `scaling` + ")"
            print text

        # Run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Model argument.
        elif type(model) != str:
            raise RelaxStrError, ('model', model)

        # Scaling.
        if type(scaling) != int or (scaling != 0 and scaling != 1):
            raise RelaxBinError, ('scaling', scaling)

        # Execute the functional code.
        self.select(run=run, model=model, scaling=scaling)


    def minimise(self, run=None, i=None, init_params=None, scaling_matrix=None, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=0, print_flag=0):
        """Model-free minimisation."""

        # Linear constraints.
        if constraints:
            A, b = self.linear_constraints(run, self.relax.data.res[i], i)

        if print_flag >= 1:
            if print_flag >= 2:
                print "\n\n"
            string = "Fitting to residue: " + `self.relax.data.res[i].num` + " " + self.relax.data.res[i].name
            print string
            string2 = ""
            for j in range(len(string)):
                string2 = string2 + "~"
            print string2

        # Initialise the iteration counter and function, gradient, and Hessian call counters.
        self.iter_count = 0
        self.f_count = 0
        self.g_count = 0
        self.h_count = 0

        # Set up the relaxation data and errors and the function options.
        relax_data = array(self.relax.data.res[i].relax_data[run], Float64)
        relax_error = array(self.relax.data.res[i].relax_error[run], Float64)
        self.function_ops = ()

        # Initialise the functions used in the minimisation.
        self.mf = Mf(self.relax, run=run, i=i, equation=self.relax.data.res[i].equations[run], param_types=self.relax.data.res[i].params[run], init_params=init_params, relax_data=relax_data, errors=relax_error, bond_length=self.relax.data.res[i].r[run], csa=self.relax.data.res[i].csa[run], diff_type=self.relax.data.diff_type[run], diff_params=self.relax.data.diff_params[run], scaling_matrix=scaling_matrix)

        # Levenberg-Marquardt minimisation.
        if constraints and not match('^[Gg]rid', min_algor):
            algor = min_options[0]
        else:
            algor = min_algor
        if match('[Ll][Mm]$', algor) or match('[Ll]evenburg-[Mm]arquardt$', algor):
            min_options = min_options + (self.mf.lm_dri, relax_error)


        # Minimisation.
        if constraints:
            results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, args=self.function_ops, x0=init_params, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, A=A, b=b, full_output=1, print_flag=print_flag)
        else:
            results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, args=self.function_ops, x0=init_params, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, full_output=1, print_flag=print_flag)
        if results == None:
            return
        self.params, self.func, iter, fc, gc, hc, self.warning = results
        self.iter_count = self.iter_count + iter
        self.f_count = self.f_count + fc
        self.g_count = self.g_count + gc
        self.h_count = self.h_count + hc

        # Scaling.
        if self.relax.data.res[i].scaling[run]:
            self.params = matrixmultiply(scaling_matrix, self.params)

        # Types.
        types = self.relax.data.res[i].params[run]

        # Loop over the minimised parameters.
        for j in range(len(self.params)):
            # S2.
            if types[j] == 'S2':
                self.relax.data.res[i].s2[run] = self.params[j]

            # S2f.
            elif types[j] == 'S2f':
                # S2f.
                self.relax.data.res[i].s2f[run] = self.params[j]

                # Other order parameters.
                for k in range(len(types)):
                    # S2 = S2f.S2s
                    if types[k] == 'S2s':
                        self.relax.data.res[i].s2[run] = self.params[j] * self.params[k]

                    # S2s = S2/S2f
                    elif types[k] == 'S2':
                        self.relax.data.res[i].s2s[run] = self.params[k] / self.params[j]

            # S2s.
            elif types[j] == 'S2s':
                self.relax.data.res[i].s2s[run] = self.params[j]

            # te.
            elif types[j] == 'te':
                self.relax.data.res[i].te[run] = self.params[j]

            # tf.
            elif types[j] == 'tf':
                self.relax.data.res[i].tf[run] = self.params[j]

            # ts.
            elif types[j] == 'ts':
                self.relax.data.res[i].ts[run] = self.params[j]

            # Rex.
            elif types[j] == 'Rex':
                self.relax.data.res[i].rex[run] = self.params[j]

            # Bond length.
            elif types[j] == 'r':
                self.relax.data.res[i].r[run] = self.params[j]

            # CSA.
            elif types[j] == 'CSA':
                self.relax.data.res[i].csa[run] = self.params[j]

        # Chi-squared statistic.
        self.relax.data.res[i].chi2[run] = self.func

        # Iterations.
        self.relax.data.res[i].iter[run] = self.iter_count

        # Function evaluations.
        self.relax.data.res[i].f_count[run] = self.f_count

        # Gradient evaluations.
        self.relax.data.res[i].g_count[run] = self.g_count

        # Hessian evaluations.
        self.relax.data.res[i].h_count[run] = self.h_count

        # Warning.
        self.relax.data.res[i].warning[run] = self.warning


    def map_bounds(self, index, params):
        """The function for creating bounds for the mapping function."""

        # Bounds array.
        bounds = zeros((len(params), 2), Float64)

        for i in range(len(params)):
            # {S2, S2f, S2s}.
            if match('S2', params[i]):
                bounds[i] = [0, 1]

            # {te, tf, ts}.
            elif match('t', params[i]):
                bounds[i] = [0, 1e-8]

            # Rex.
            elif params[i] == 'Rex':
                bounds[i] = [0, 30.0 / (2.0 * pi * self.relax.data.res[index].frq[run][0])**2]

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
        axis_incs = 5.0
        loc_inc = inc / axis_incs

        # Increment over the model parameters.
        for i in range(n):
            # {S2, S2f, S2s}.
            if match('S2', params[swap[i]]):
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
                labels = labels + "\"Rex (" + self.relax.data.res[index].frq_labels[run][0] + " MHz)\""

                # Tick values.
                vals = bounds[swap[i], 0] * (2.0 * pi * self.relax.data.res[index].frq[run][0])**2
                val_inc = (bounds[swap[i], 1] - bounds[swap[i], 0]) / axis_incs * (2.0 * pi * self.relax.data.res[index].frq[run][0])**2

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
            for j in range(axis_incs + 1):
                string = string + " " + `val`
                val = val + loc_inc
            string = string + " }"
            tick_locations.append(string)

            # Tick values.
            string = "{"
            for j in range(axis_incs + 1):
                if self.relax.data.res[index].scaling.has_key(run):
                    string = string + "\"" + "%.2f" % (vals * self.relax.data.res[index].scaling[run][swap[i]]) + "\" "
                else:
                    string = string + "\"" + "%.2f" % vals + "\" "
                vals = vals + val_inc
            string = string + "}"
            tick_values.append(string)

        return labels, tick_locations, tick_values


    def read_results(self, file_data, run):
        """Function for printing the core of the results file."""

        # Remove the header.
        file_data = file_data[1:]

        # Loop over the file data.
        for i in range(len(file_data)):
            # Residue number and name.
            try:
                num = int(file_data[i][0])
            except ValueError:
                print "Warning, the residue number " + file_data[i][0] + " is not an integer."
                continue
            name = file_data[i][1]

            # Find the residue index.
            index = None
            for j in range(len(self.relax.data.res)):
                if self.relax.data.res[j].num == num and self.relax.data.res[j].name == name:
                    index = j
                    break
            if index == None:
                print "Warning, residue " + `num` + " " + name + " cannot be found in the sequence."
                continue

            # Test if relaxation data has been loaded.
            if not hasattr(self.relax.data.res[index], 'relax_data'):
                print "Relaxation data has not been loaded.  This is required for the frequency data for Rex values."
                break

            # Model details.
            model = file_data[i][2]
            equation = file_data[i][3]

            # Paramters.
            params = eval(file_data[i][4])
            if type(params) != list:
                print "Warning, the parameters " + file_data[i][4] + " is not an array."
                continue

            # S2.
            try:
                s2 = float(file_data[i][5])
            except ValueError:
                s2 = None

            # S2f.
            try:
                s2f = float(file_data[i][6])
            except ValueError:
                s2f = None

            # S2s.
            try:
                s2s = float(file_data[i][7])
            except ValueError:
                s2s = None

            # tm.
            try:
                tm = float(file_data[i][8])
                tm = tm * 1e-12
            except ValueError:
                tm = None

            # tf.
            try:
                tf = float(file_data[i][9])
                tf = tf * 1e-12
            except ValueError:
                tf = None

            # te and ts.
            try:
                te = float(file_data[i][10])
                te = te * 1e-12
            except ValueError:
                te = None
            if "te" in params:
                ts = None
            else:
                ts = te
                te = None

            # Rex.
            try:
                rex = float(file_data[i][11])
                rex = rex / (2.0 * pi * self.relax.data.res[i].frq[run][0])**2
            except ValueError:
                rex = None

            # Bond length.
            try:
                r = float(file_data[i][12])
                r = r * 1e-10
            except ValueError:
                r = None

            # CSA.
            try:
                csa = float(file_data[i][13])
                csa = csa * 1e-6
            except ValueError:
                csa = None

            # Chi-squared.
            try:
                chi2 = float(file_data[i][14])
            except ValueError:
                chi2 = None

            # Number of iterations.
            try:
                iter = int(file_data[i][15])
            except ValueError:
                iter = None

            # Function count.
            try:
                f_count = int(file_data[i][16])
            except ValueError:
                f_count = None

            # Gradient count.
            try:
                g_count = int(file_data[i][17])
            except ValueError:
                g_count = None

            # Hessian count.
            try:
                h_count = int(file_data[i][18])
            except ValueError:
                h_count = None

            # Warning.
            if len(file_data[i]) > 19:
                warning = file_data[19]
                for j in range(20, len(file_data[i])):
                    warning = warning + " " + file_data[i][j]
            else:
                warning = None

            # Initialise the data structures (if needed).
            self.initialise_mf_data(self.relax.data.res[index], run)

            # Place the data into 'self.relax.data'.
            self.relax.data.res[index].models[run] = model
            self.relax.data.res[index].equations[run] = equation
            self.relax.data.res[index].params[run] = params
            self.relax.data.res[index].s2[run] = s2
            self.relax.data.res[index].s2f[run] = s2f
            self.relax.data.res[index].s2s[run] = s2s
            self.relax.data.res[index].tm[run] = tm
            self.relax.data.res[index].tf[run] = tf
            self.relax.data.res[index].te[run] = te
            self.relax.data.res[index].ts[run] = ts
            self.relax.data.res[index].rex[run] = rex
            self.relax.data.res[index].r[run] = r
            self.relax.data.res[index].csa[run] = csa
            self.relax.data.res[index].chi2[run] = chi2
            self.relax.data.res[index].iter[run] = iter
            self.relax.data.res[index].f_count[run] = f_count
            self.relax.data.res[index].g_count[run] = g_count
            self.relax.data.res[index].h_count[run] = h_count
            self.relax.data.res[index].warning[run] = warning


    def select(self, run=None, model=None, scaling=1):
        """Function for the selection of a preset model-free model."""

        # Test if sequence data is loaded.
        if not len(self.relax.data.res):
            raise RelaxSequenceError


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

        # Add the run to the runs list.
        if not run in self.relax.data.runs:
            self.relax.data.runs.append(run)

        # Set up the model.
        self.model_setup(run, model, equation, params, scaling)


    def write_header(self, file, run):
        """Function for printing the header of the results file."""

        # Residue number and name.
        file.write("%-5s" % "Num")
        file.write("%-6s" % "Name")

        # Model details.
        file.write("%-6s" % "Model")
        file.write("%-10s" % "Equation")
        file.write("%-36s" % "Params")

        # Parameters.
        file.write("%-26s" % "S2")
        file.write("%-26s" % "S2f")
        file.write("%-26s" % "S2s")
        file.write("%-26s" % "tm_(ps)")
        file.write("%-26s" % "tf_(ps)")
        file.write("%-26s" % "te_or_ts_(ps)")
        file.write("%-26s" % ("Rex_(" + self.relax.data.res[0].frq_labels[run][0] + "_MHz)"))
        file.write("%-26s" % "Bond_length_(A)")
        file.write("%-26s" % "CSA_(ppm)")

        # Minimisation results.
        file.write("%-26s" % "Chi-squared")
        file.write("%-9s" % "Iter")
        file.write("%-9s" % "f")
        file.write("%-9s" % "g")
        file.write("%-9s" % "h")
        file.write("Warning")

        # End of line.
        file.write("\n")


    def write_results(self, file, run):
        """Function for printing the core of the results file."""

        # Loop over the sequence.
        for i in range(len(self.relax.data.res)):
            # Skip unselected residues.
            if not self.relax.data.res[i].select:
                continue

            # Initialise.
            types = self.relax.data.res[i].params[run]

            # Residue number and name.
            file.write("%-5s" % self.relax.data.res[i].num)
            file.write("%-6s" % self.relax.data.res[i].name)

            # Model details.
            file.write("%-6s" % self.relax.data.res[i].models[run])
            file.write("%-10s" % self.relax.data.res[i].equations[run])
            file.write("%-36s" % replace(`types`, ' ', ''))

            # S2.
            if self.relax.data.res[i].s2[run] == None:
                file.write("%-26s" % "N/A")
            else:
                file.write("%-26s" % `self.relax.data.res[i].s2[run]`)

            # S2f.
            if self.relax.data.res[i].s2f[run] == None:
                file.write("%-26s" % "N/A")
            else:
                file.write("%-26s" % `self.relax.data.res[i].s2f[run]`)

            # S2s.
            if self.relax.data.res[i].s2s[run] == None:
                file.write("%-26s" % "N/A")
            else:
                file.write("%-26s" % `self.relax.data.res[i].s2s[run]`)

            # tm.
            if hasattr(self.relax.data.res[i], 'tm') and self.relax.data.res[i].tm.has_key(run) and self.relax.data.res[i].tm[run] != None:
                file.write("%-26s" % `self.relax.data.res[i].tm[run] / 1e-12`)
            else:
                file.write("%-26s" % `self.relax.data.diff_params[run][0] / 1e-12`)

            # tf.
            if self.relax.data.res[i].tf[run] == None:
                file.write("%-26s" % "N/A")
            else:
                file.write("%-26s" % `self.relax.data.res[i].tf[run] / 1e-12`)

            # te or ts.
            if self.relax.data.res[i].te[run] == None and self.relax.data.res[i].ts[run] == None:
                file.write("%-26s" % "N/A")
            elif self.relax.data.res[i].te[run] != None:
                file.write("%-26s" % `self.relax.data.res[i].te[run] / 1e-12`)
            else:
                file.write("%-26s" % `self.relax.data.res[i].ts[run] / 1e-12`)

            # Rex.
            if self.relax.data.res[i].rex[run] == None:
                file.write("%-26s" % "N/A")
            else:
                file.write("%-26s" % `self.relax.data.res[i].rex[run] * (2.0 * pi * self.relax.data.res[i].frq[run][0])**2`)

            # Bond length.
            if self.relax.data.res[i].r[run] == None:
                file.write("%-26s" % "N/A")
            else:
                file.write("%-26s" % `self.relax.data.res[i].r[run] / 1e-10`)

            # CSA.
            if self.relax.data.res[i].csa[run] == None:
                file.write("%-26s" % "N/A")
            else:
                file.write("%-26s" % `self.relax.data.res[i].csa[run] / 1e-6`)

            # Chi-squared.
            file.write("%-26s" % `self.relax.data.res[i].chi2[run]`)

            # Iterations
            file.write("%-9i" % self.relax.data.res[i].iter[run])

            # Function count.
            file.write("%-9i" % self.relax.data.res[i].f_count[run])

            # Gradient count.
            file.write("%-9i" % self.relax.data.res[i].g_count[run])

            # Hessian count.
            file.write("%-9i" % self.relax.data.res[i].h_count[run])

            # Warning
            if self.relax.data.res[i].warning[run] != None:
                file.write(self.relax.data.res[i].warning[run])

            # End of line.
            file.write("\n")
