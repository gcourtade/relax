###############################################################################
#                                                                             #
# Copyright (C) 2004-2013 Edward d'Auvergne                                   #
# Copyright (C) 2009 Sebastien Morin                                          #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Functions relating to the parameters of the relaxation dispersion models."""

# Python module imports.
from numpy import array, float64, identity, zeros
from re import search

# relax module imports.
from lib.errors import RelaxError
from lib.mathematics import round_to_next_order
from specific_analyses.relax_disp.disp_data import loop_exp_curve
from specific_analyses.relax_disp.variables import MODEL_R2EFF, VAR_TIME_EXP


def assemble_param_vector(spins=None, key=None, sim_index=None):
    """Assemble the dispersion relaxation dispersion curve fitting parameter vector.

    @keyword spins:         The list of spin data containers for the block.
    @type spins:            list of SpinContainer instances
    @keyword key:           The key for the R2eff and I0 parameters.
    @type key:              str or None
    @keyword sim_index:     The optional MC simulation index.
    @type sim_index:        int
    @return:                An array of the parameter values of the dispersion relaxation model.
    @rtype:                 numpy float array
    """

    # Initialise.
    param_vector = []

    # The R2eff model parameters.
    if cdp.model == MODEL_R2EFF:
        for spin_index in range(len(spins)):
            # Alias the spin.
            spin = spins[spin_index]

            # A specific exponential curve.
            if key:
                # Loop over the model parameters.
                for i in range(len(spin.params)):
                    # Effective transversal relaxation rate.
                    if spin.params[i] == 'r2eff':
                        if sim_index != None:
                            param_vector.append(spin.r2eff_sim[sim_index][key])
                        elif spin.r2eff == None or key not in spin.r2eff:
                            param_vector.append(0.0)
                        else:
                            param_vector.append(spin.r2eff[key])

                    # Initial intensity.
                    elif spin.params[i] == 'i0':
                        if sim_index != None:
                            param_vector.append(spin.i0_sim[sim_index][key])
                        elif spin.i0 == None or key not in spin.i0:
                            param_vector.append(0.0)
                        else:
                            param_vector.append(spin.i0[key])


            # Loop over each exponential curve.
            else:
                for exp_i, key in loop_exp_curve():
                    # Loop over the model parameters.
                    for i in range(len(spin.params)):
                        # Effective transversal relaxation rate.
                        if spin.params[i] == 'r2eff':
                            if sim_index != None:
                                param_vector.append(spin.r2eff_sim[sim_index][key])
                            elif spin.r2eff == None or key not in spin.r2eff:
                                param_vector.append(0.0)
                            else:
                                param_vector.append(spin.r2eff[key])

                        # Initial intensity.
                        elif spin.params[i] == 'i0':
                            if sim_index != None:
                                param_vector.append(spin.i0_sim[sim_index][key])
                            elif spin.i0 == None or key not in spin.i0:
                                param_vector.append(0.0)
                            else:
                                param_vector.append(spin.i0[key])

    # All other model parameters.
    else:
        # Only use the values from the first spin of the cluster.
        spin = spins[0]
        for i in range(len(spin.params)):
            # Transversal relaxation rate.
            if spin.params[i] == 'r2':
                if sim_index != None:
                    param_vector.append(spin.r2_sim[sim_index])
                elif spin.r2 == None:
                    param_vector.append(0.0)
                else:
                    param_vector.append(spin.r2)

            # Chemical exchange contribution to 'R2'.
            if spin.params[i] == 'rex':
                if sim_index != None:
                    param_vector.append(spin.rex_sim[sim_index])
                elif spin.rex == None:
                    param_vector.append(0.0)
                else:
                    param_vector.append(spin.rex)

            # Exchange rate.
            elif spin.params[i] == 'kex':
                if sim_index != None:
                    param_vector.append(spin.kex_sim[sim_index])
                elif spin.kex == None:
                    param_vector.append(0.0)
                else:
                    param_vector.append(spin.kex)

            # Transversal relaxation rate for state A.
            if spin.params[i] == 'r2a':
                if sim_index != None:
                    param_vector.append(spin.r2a_sim[sim_index])
                elif spin.r2a == None:
                    param_vector.append(0.0)
                else:
                    param_vector.append(spin.r2a)

            # Exchange rate from state A to state B.
            if spin.params[i] == 'ka':
                if sim_index != None:
                    param_vector.append(spin.ka_sim[sim_index])
                elif spin.ka == None:
                    param_vector.append(0.0)
                else:
                    param_vector.append(spin.ka)

            # Chemical shift difference between states A and B.
            if spin.params[i] == 'dw':
                if sim_index != None:
                    param_vector.append(spin.dw_sim[sim_index])
                elif spin.dw == None:
                    param_vector.append(0.0)
                else:
                    param_vector.append(spin.dw)

    # Return a numpy array.
    return array(param_vector, float64)


def assemble_scaling_matrix(spins=None, key=None, scaling=True):
    """Create and return the scaling matrix.

    @keyword spins:         The list of spin data containers for the block.
    @type spins:            list of SpinContainer instances
    @keyword key:           The key for the R2eff and I0 parameters.
    @type key:              str or None
    @keyword scaling:       A flag which if False will cause the identity matrix to be returned.
    @type scaling:          bool
    @return:                The diagonal and square scaling matrix.
    @rtype:                 numpy diagonal matrix
    """

    # Initialise.
    scaling_matrix = identity(param_num(spins=spins), float64)
    i = 0
    param_index = 0

    # No diagonal scaling.
    if not scaling:
        return scaling_matrix

    # The R2eff model.
    if cdp.model == MODEL_R2EFF:
        for spin_index in range(len(spins)):
            # Alias the spin.
            spin = spins[spin_index]

            # A specific exponential curve.
            if key:
                # Effective transversal relaxation rate scaling.
                scaling_matrix[param_index, param_index] = 10
                param_index += 1

                # Initial intensity scaling.
                scaling_matrix[param_index, param_index] = round_to_next_order(max(spin.intensities.values()))
                param_index += 1

            # Loop over each exponential curve.
            else:
                for exp_i, key in loop_exp_curve():
                    # Effective transversal relaxation rate scaling.
                    scaling_matrix[param_index, param_index] = 10
                    param_index += 1

                    # Initial intensity scaling.
                    scaling_matrix[param_index, param_index] = round_to_next_order(max(spin.intensities.values()))
                    param_index += 1

    # All other models.
    else:
        # Only use the parameters of the first spin of the cluster.
        spin = spins[0]
        for i in range(len(spin.params)):
            # Transversal relaxation rate scaling.
            if spin.params[i] == 'r2':
                scaling_matrix[param_index, param_index] = 10

            # Chemical exchange contribution to 'R2' scaling.
            elif spin.params[i] == 'rex':
                scaling_matrix[param_index, param_index] = 10

            # Exchange rate scaling.
            elif spin.params[i] == 'kex':
                scaling_matrix[param_index, param_index] = 10000

            # Transversal relaxation rate for state A scaling
            elif spin.params[i] == 'r2a':
                scaling_matrix[param_index, param_index] = 10

            # Exchange rate from state A to state B scaling.
            elif spin.params[i] == 'ka':
                scaling_matrix[param_index, param_index] = 10000

            # Chemical shift difference between states A and B scaling.
            elif spin.params[i] == 'dw':
                scaling_matrix[param_index, param_index] = 1000

            # Increment the parameter index.
            param_index += 1

    # Return the scaling matrix.
    return scaling_matrix


def disassemble_param_vector(param_vector=None, key=None, spins=None, sim_index=None):
    """Disassemble the parameter vector.

    @keyword param_vector:  The parameter vector.
    @type param_vector:     numpy array
    @keyword key:           The key for the R2eff and I0 parameters.
    @type key:              str or None
    @keyword spins:         The list of spin data containers for the block.
    @type spins:            list of SpinContainer instances
    @keyword sim_index:     The optional MC simulation index.
    @type sim_index:        int
    """

    # Initialise.
    param_index = 0

    # The R2eff model.
    if cdp.model == MODEL_R2EFF:
        for spin_index in range(len(spins)):
            # Alias the spin.
            spin = spins[spin_index]

            # A specific exponential curve.
            if key:
                param_index += 2

                # Loop over the model parameters.
                for i in range(len(spin.params)):
                    # Effective transversal relaxation rate.
                    if spin.params[i] == 'r2eff':
                        if sim_index != None:
                            spin.r2eff_sim[sim_index][key] = param_vector[0]
                        else:
                            spin.r2eff[key] = param_vector[0]

                    # Initial intensity.
                    elif spin.params[i] == 'i0':
                        if sim_index != None:
                            spin.i0_sim[sim_index][key] = param_vector[1]
                        else:
                            spin.i0[key] = param_vector[1]

            # Loop over each exponential curve.
            else:
                for exp_index, key in loop_exp_curve():
                    index = spin_index * 2 * cdp.dispersion_points + exp_index * cdp.dispersion_points
                    param_index += 2

                    # Loop over the model parameters.
                    for i in range(len(spin.params)):
                        # Effective transversal relaxation rate.
                        if spin.params[i] == 'r2eff':
                            if sim_index != None:
                                spin.r2eff_sim[sim_index][key] = param_vector[index]
                            else:
                                spin.r2eff[key] = param_vector[index]

                        # Initial intensity.
                        elif spin.params[i] == 'i0':
                            if sim_index != None:
                                spin.i0_sim[sim_index][key] = param_vector[index+1]
                            else:
                                spin.i0[key] = param_vector[index+1]

    # All other models.
    else:
        # Set the values for all spins.
        for spin_index in range(len(spins)):
            # Alias the spin.
            spin = spins[spin_index]

            # Reset the parameter index.
            param_index = 0

            # Loop over each parameter.
            for i in range(len(spin.params)):
                # Transversal relaxation rate.
                if spin.params[i] == 'r2':
                    if sim_index != None:
                        spin.r2_sim[sim_index] = param_vector[param_index]
                    else:
                        spin.r2 = param_vector[param_index]

                # Chemical exchange contribution to 'R2'.
                if spin.params[i] == 'rex':
                    if sim_index != None:
                        spin.rex_sim[sim_index] = param_vector[param_index]
                    else:
                        spin.rex = param_vector[param_index]

                # Exchange rate.
                elif spin.params[i] == 'kex':
                    if sim_index != None:
                        spin.kex_sim[sim_index] = param_vector[param_index]
                    else:
                        spin.kex = param_vector[param_index]

                # Transversal relaxation rate for state A.
                if spin.params[i] == 'r2a':
                    if sim_index != None:
                        spin.r2a_sim[sim_index] = param_vector[param_index]
                    else:
                        spin.r2a = param_vector[param_index]

                # Exchange rate from state A to state B.
                if spin.params[i] == 'ka':
                    if sim_index != None:
                        spin.ka_sim[sim_index] = param_vector[param_index]
                    else:
                        spin.ka = param_vector[param_index]

                # Chemical shift difference between states A and B.
                if spin.params[i] == 'dw':
                    if sim_index != None:
                        spin.dw_sim[sim_index] = param_vector[param_index]
                    else:
                        spin.dw = param_vector[param_index]

                # Increment the parameter index.
                param_index = param_index + 1


def linear_constraints(spins=None, scaling_matrix=None):
    """Set up the relaxation dispersion curve fitting linear constraint matrices A and b.

    Standard notation
    =================

    The different constraints are::

        R2 >= 0
        Rex >= 0
        kex >= 0

        R2A >= 0
        kA >= 0
        dw >= 0


    Matrix notation
    ===============

    In the notation A.x >= b, where A is a matrix of coefficients, x is an array of parameter values, and b is a vector of scalars, these inequality constraints are::

        | 1  0  0 |     |  R2  |      |    0    |
        |         |     |      |      |         |
        | 1  0  0 |  .  |  Rex |      |    0    |
        |         |     |      |      |         |
        | 1  0  0 |     |  kex |      |    0    |
        |         |     |      |  >=  |         |
        | 1  0  0 |     |  R2A |      |    0    |
        |         |     |      |      |         |
        | 1  0  0 |     |  kA  |      |    0    |
        |         |     |      |      |         |
        | 1  0  0 |     |  dw  |      |    0    |


    @keyword spins:             The list of spin data containers for the block.
    @type spins:                list of SpinContainer instances
    @keyword scaling_matrix:    The diagonal, square scaling matrix.
    @type scaling_matrix:       numpy diagonal matrix
    """

    # Initialisation (0..j..m).
    A = []
    b = []
    n = param_num(spins=spins)
    zero_array = zeros(n, float64)
    i = 0
    j = 0

    # The R2eff model (no need for constraints).
    if cdp.model == MODEL_R2EFF:
        return None, None

    # All other models.
    else:
        # Only use the parameters of the first spin of the cluster.
        spin = spins[0]
        for k in range(len(spin.params)):
            # The transversal relaxation rate >= 0.
            if spin.params[k] == 'r2':
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0)
                j += 1

            # Relaxation rates and Rex.
            elif search('^r', spin.params[k]):
                # Rex, R2A >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0)
                j += 1

            # Exchange rates.
            elif search('^k', spin.params[k]):
                # kex, kA >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0)
                j += 1

            # Chemical exchange difference.
            elif spin.params[k] == 'dw':
                # dw >= 0.
                A.append(zero_array * 0.0)
                A[j][i] = 1.0
                b.append(0.0)
                j += 1

            # Increment i.
            i += 1

    # Convert to numpy data structures.
    A = array(A, float64)
    b = array(b, float64)

    # Return the matrices.
    return A, b


def param_index_to_param_info(index=None, spins=None, names=None):
    """Convert the given parameter array index to parameter identifying information.
    
    The parameter index will be converted to the parameter name, the relevant spin index in the cluster, and relevant exponential curve key.

    @keyword index: The index of the parameter array.
    @type index:    int
    @keyword spins: The list of spin data containers for the block.
    @type spins:    list of SpinContainer instances
    @keyword names: The list of all parameter names for the given spin block.
    @type names:    list of str
    @return:        The parameter name and spin cluster index
    @rtype:         str, int
    """

    # Initialise.
    param_name = None
    spin_index = 0

    # The R2eff model.
    if cdp.model == MODEL_R2EFF:
        # The number of spin specific parameters (R2eff and I0 per spin).
        num = len(spins) * 2

        # The exponential curve parameters.
        if index < num:
            # Even indices are R2eff, odd are I0.
            if index % 2:
                param_name = 'i0'
            else:
                param_name = 'r2eff'

            # The spin index.
            spin_index = int(index / 2)

    # All other parameters.
    else:
        param_name = names[index-num+2]

    # Return the data.
    return param_name, spin_index


def param_num(spins=None):
    """Determine the number of parameters in the model.

    @keyword spins:         The list of spin data containers for the block.
    @type spins:            list of SpinContainer instances
    @return:                The number of model parameters.
    @rtype:                 int
    """

    # The R2eff model.
    if cdp.model == MODEL_R2EFF:
        # Exponential curves (with clustering).
        if cdp.exp_type in VAR_TIME_EXP:
            return 2 * len(spins)

        # Fixed time period experiments (with clustering).
        else:
            return 1 * len(spins)

    # The number of parameters for the cluster.
    num = len(spins[0].params)

    # Check the spin cluster.
    for spin in spins:
        if len(spin.params) != num:
            raise RelaxError("The number of parameters for each spin in the cluster are not the same.")

    # Return the number.
    return num
