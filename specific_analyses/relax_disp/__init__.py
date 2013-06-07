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

# Package docstring.
"""The relaxation dispersion analysis."""

# The available modules.
__all__ = [
    'cpmgfit',
    'disp_data',
    'parameters',
    'variables'
]

# Python module imports.
from copy import deepcopy
from minfx.generic import generic_minimise
from minfx.grid import grid
from numpy import array, average, dot, float64, identity, log, ones, zeros
from numpy.linalg import inv
from random import gauss
from re import match, search
import sys
from types import MethodType

# relax module imports.
from dep_check import C_module_exp_fn
from lib.dispersion.equations import calc_two_point_r2eff, calc_two_point_r2eff_err
from lib.errors import RelaxError, RelaxFuncSetupError, RelaxLenError, RelaxNoModelError, RelaxNoSequenceError, RelaxNoSpectraError
from lib.io import get_file_path, open_write_file
from lib.list import count_unique_elements, unique_elements
from lib.mathematics import round_to_next_order
from lib.software.grace import write_xy_data, write_xy_header
from lib.statistics import std
from lib.text.sectioning import subsection
from pipe_control import pipes, sequence
from pipe_control.mol_res_spin import exists_mol_res_spin_data, return_spin, spin_loop
from pipe_control.result_files import add_result_file
from specific_analyses.api_base import API_base
from specific_analyses.api_common import API_common
from specific_analyses.relax_disp.disp_data import average_intensity, find_intensity_keys, loop_cluster, loop_frq, loop_frq_point, loop_frq_point_key, loop_frq_point_time, loop_point, loop_time, relax_time, return_cpmg_frqs, return_index_from_disp_point, return_index_from_frq, return_key_from_disp_point_index, return_param_key_from_data, return_r2eff_arrays, return_spin_lock_nu1, spin_ids_to_containers
from specific_analyses.relax_disp.parameters import assemble_param_vector, assemble_scaling_matrix, disassemble_param_vector, linear_constraints, param_index_to_param_info, param_num
from specific_analyses.relax_disp.variables import CPMG_EXP, FIXED_TIME_EXP, MODEL_LIST_FULL, MODEL_LM63, MODEL_CR72, MODEL_M61, MODEL_NOREX, MODEL_R2EFF, R1RHO_EXP, VAR_TIME_EXP
from target_functions.relax_disp import Dispersion
from user_functions.data import Uf_tables; uf_tables = Uf_tables()
from user_functions.objects import Desc_container

# C modules.
if C_module_exp_fn:
    from target_functions.relax_fit import setup, func, dfunc, d2func, back_calc_I


class Relax_disp(API_base, API_common):
    """Class containing functions for relaxation dispersion curve fitting."""

    def __init__(self):
        """Initialise the class by placing API_common methods into the API."""

        # Execute the base class __init__ method.
        super(Relax_disp, self).__init__()

        # Place methods into the API.
        self.data_init = self._data_init_spin
        self.model_type = self._model_type_local
        self.return_conversion_factor = self._return_no_conversion_factor
        self.return_value = self._return_value_general
        self.set_param_values = self._set_param_values_spin
        self.sim_init_values = self._sim_init_values_spin

        # Set up the spin parameters.
        self.PARAMS.add('intensities', scope='spin', py_type=dict, grace_string='\\qPeak intensities\\Q')
        self.PARAMS.add('relax_times', scope='spin', py_type=dict, grace_string='\\qRelaxation time period (s)\\Q')
        self.PARAMS.add('cpmg_frqs', scope='spin', py_type=dict, grace_string='\\qCPMG pulse train frequency (Hz)\\Q')
        self.PARAMS.add('spin_lock_nu1', scope='spin', py_type=dict, grace_string='\\qSpin-lock field strength (Hz)\\Q')
        self.PARAMS.add('r2eff', scope='spin', default=15.0, desc='The effective transversal relaxation rate', set='params', py_type=dict, grace_string='\\qR\\s2,eff\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.PARAMS.add('i0', scope='spin', default=10000.0, desc='The initial intensity', py_type=dict, set='params', grace_string='\\qI\\s0\\Q', err=True, sim=True)
        self.PARAMS.add('r2', scope='spin', default=15.0, desc='The transversal relaxation rate', set='params', py_type=list, grace_string='\\qR\\s2\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.PARAMS.add('pA', scope='spin', default=0.5, desc='The population for state A', set='params', py_type=float, grace_string='\\qp\\sA\\N\\Q', err=True, sim=True)
        self.PARAMS.add('pB', scope='spin', default=0.5, desc='The population for state B', set='params', py_type=float, grace_string='\\qp\\sB\\N\\Q', err=True, sim=True)
        self.PARAMS.add('phi_ex', scope='spin', default=5.0, desc='The phi_ex = pA.pB.dw**2 value (ppm^2)', set='params', py_type=float, grace_string='\\xF\\B\\sex\\N = \\q p\\sA\\N.p\\sB\\N.\\xDw\\B\\S2\\N\\Q  (ppm\\S2\\N)', err=True, sim=True)
        self.PARAMS.add('dw', scope='spin', default=0.0, desc='The chemical shift difference between states A and B (in ppm)', set='params', py_type=float, grace_string='\\q\\xDw\f{}\\Q (ppm)', err=True, sim=True)
        self.PARAMS.add('kex', scope='spin', default=10000.0, desc='The exchange rate', set='params', py_type=float, grace_string='\\qk\\sex\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.PARAMS.add('r2a', scope='spin', default=15.0, desc='The transversal relaxation rate for state A', set='params', py_type=float, grace_string='\\qR\\s2,A\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.PARAMS.add('ka', scope='spin', default=10000.0, desc='The exchange rate from state A to state B', set='params', py_type=float, grace_string='\\qk\\sA\\N\\Q (rad.s\\S-1\\N)', err=True, sim=True)
        self.PARAMS.add('params', scope='spin', desc='The model parameters', py_type=list)

        # Add the minimisation data.
        self.PARAMS.add_min_data(min_stats_global=False, min_stats_spin=True)


    def _back_calc_r2eff(self, spin=None, spin_id=None):
        """Back-calculation of R2eff/R1rho values for the given spin.

        @keyword spin:      The specific spin data container.
        @type spin:         SpinContainer instance
        @keyword spin_id:   The spin ID string for the spin container.
        @type spin_id:      str
        @return:            The back-calculated R2eff/R1rho value for the given spin.
        @rtype:             numpy rank-1 float array
        """

        # Create the initial parameter vector.
        param_vector = assemble_param_vector(spins=[spin])

        # Create a scaling matrix.
        scaling_matrix = assemble_scaling_matrix(spins=[spin], scaling=False)

        # Number of spectrometer fields.
        fields = [None]
        field_count = 1
        if hasattr(cdp, 'spectrometer_frq_count'):
            fields = cdp.spectrometer_frq_list
            field_count = cdp.spectrometer_frq_count

        # Initialise the data structures for the target function.
        values, errors, missing, frqs = return_r2eff_arrays(spins=[spin], spin_ids=[spin_id], fields=fields, field_count=field_count)

        # Initialise the relaxation dispersion fit functions.
        model = Dispersion(model=cdp.model, num_params=param_num(spins=[spin]), num_spins=1, num_frq=field_count, num_disp_points=cdp.dispersion_points, values=values, errors=errors, missing=missing, frqs=frqs, cpmg_frqs=return_cpmg_frqs(ref_flag=False), spin_lock_nu1=return_spin_lock_nu1(ref_flag=False), scaling_matrix=scaling_matrix)

        # Make a single function call.  This will cause back calculation and the data will be stored in the class instance.
        model.func(param_vector)

        # Convert to a dictionary matching the R2eff data structure.
        results = {}
        for frq, point in loop_frq_point():
            # The indices.
            frq_index = return_index_from_frq(frq)
            point_index = return_index_from_disp_point(point)

            # The parameter key.
            param_key = return_param_key_from_data(frq=frq, point=point)

            # Skip missing data.
            if missing[0, frq_index, point_index]:
                continue

            # Store the result.
            results[param_key] = model.back_calc[0, frq_index, point_index]

        # Return the back calculated R2eff values.
        return results


    def _back_calc_peak_intensities(self, spin=None, frq=None, point=None):
        """Back-calculation of peak intensity for the given relaxation time.

        @keyword spin:  The specific spin data container.
        @type spin:     SpinContainer instance
        @keyword frq:   The spectrometer frequency.
        @type frq:      float
        @keyword point: The dispersion point data (either the spin-lock field strength in Hz or the nu_CPMG frequency in Hz).
        @type point:    float
        @return:        The back-calculated peak intensities for the given exponential curve.
        @rtype:         numpy rank-1 float array
        """

        # Check.
        if cdp.exp_type in FIXED_TIME_EXP:
            raise RelaxError("Back-calculation is not allowed for the fixed time experiment types.")

        # The key.
        param_key = return_param_key_from_data(frq=frq, point=point)

        # Create the initial parameter vector.
        param_vector = assemble_param_vector(spins=[spin], key=param_key)

        # Create a scaling matrix.
        scaling_matrix = assemble_scaling_matrix(spins=[spin], key=param_key, scaling=False)

        # The peak intensities and times.
        values = []
        errors = []
        times = []
        for time in cdp.relax_time_list:
            # The data.
            values.append(average_intensity(spin=spin, frq=frq, point=point, time=time))
            errors.append(average_intensity(spin=spin, frq=frq, point=point, time=time, error=True))
            times.append(time)

        # The scaling matrix in a diagonalised list form.
        scaling_list = []
        for i in range(len(scaling_matrix)):
            scaling_list.append(scaling_matrix[i, i])

        # Initialise the relaxation fit functions.
        setup(num_params=len(param_vector), num_times=len(times), values=values, sd=errors, relax_times=times, scaling_matrix=scaling_list)

        # Make a single function call.  This will cause back calculation and the data will be stored in the C module.
        func(param_vector)

        # Get the data back.
        results = back_calc_I()

        # Return the correct peak height.
        return results


    def _cluster(self, cluster_id=None, spin_id=None):
        """Define spin clustering.

        @keyword cluster_id:    The cluster ID string.
        @type cluster_id:       str
        @keyword spin_id:       The spin ID string for the spin or group of spins to add to the cluster.
        @type spin_id:          str
        """

        # Initialise.
        if not hasattr(cdp, 'clustering'):
            # Create the dictionary.
            cdp.clustering = {}
            cdp.clustering['free spins'] = []

            # Add all spin IDs to the cluster.
            for spin, id in spin_loop(return_id=True):
                cdp.clustering['free spins'].append(id)

        # Add the key.
        if cluster_id not in cdp.clustering:
            cdp.clustering[cluster_id] = []

        # Loop over the spins to add to the cluster.
        for spin, id in spin_loop(selection=spin_id, return_id=True):
            # First remove the ID from all clusters.
            for key in cdp.clustering.keys():
                if id in cdp.clustering[key]:
                    cdp.clustering[key].pop(cdp.clustering[key].index(id))

            # Then add the ID to the cluster.
            cdp.clustering[cluster_id].append(id)

        # Clean up - delete any empty clusters (except the free spins).
        clean = []
        for key in cdp.clustering.keys():
            if key == 'free spins':
                continue
            if cdp.clustering[key] == []:
                clean.append(key)
        for key in clean:
            cdp.clustering.pop(key)


    def _cluster_ids(self):
        """Return the current list of cluster ID strings.

        @return:    The list of cluster IDs.
        @rtype:     list of str
        """

        # Initialise.
        ids = ['free spins']

        # Add the defined IDs.
        if hasattr(cdp, 'cluster'):
            for key in list(cdp.cluster.keys()):
                if key not in ids:
                    ids.append(key)

        # Return the IDs.
        return ids


    def _exp_type(self, exp_type='cpmg fixed'):
        """Select the relaxation dispersion experiment type performed.

        @keyword exp: The relaxation dispersion experiment type.  Can be one of 'cpmg fixed', 'cpmg exponential', 'r1rho fixed' or 'r1rho exponential'.
        @type exp:    str
        """

        # Test if the current pipe exists.
        pipes.test()

        # Printouts.
        if exp_type == 'cpmg fixed':
            print("The fixed relaxation time period CPMG-type experiments.")
        elif exp_type == 'cpmg exponential':
            print("The CPMG-type experiments consisting of full exponential curves for each dispersion point.")
        elif exp_type == 'r1rho fixed':
            print("The fixed relaxation time period R1rho-type experiments.")
        elif exp_type == 'r1rho exponential':
            print("The R1rho-type experiments consisting of full exponential curves for each dispersion point.")
        else:
            raise RelaxError("The relaxation dispersion experiment '%s' is invalid." % exp_type)

        # Sanity check.
        if exp_type not in FIXED_TIME_EXP and exp_type not in VAR_TIME_EXP:
            raise RelaxError("The experiment type '%s' is neither a fixed relaxation time period or variable relaxation time period experiment." % exp_type)

        # Store the value.
        cdp.exp_type = exp_type


    def _grid_search_setup(self, spins=None, param_vector=None, lower=None, upper=None, inc=None, scaling_matrix=None):
        """The grid search setup function.

        @keyword spins:             The list of spin data containers for the block.
        @type spins:                list of SpinContainer instances
        @keyword param_vector:      The parameter vector.
        @type param_vector:         numpy array
        @keyword lower:             The lower bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type lower:                array of numbers
        @keyword upper:             The upper bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type upper:                array of numbers
        @keyword inc:               The increments for each dimension of the space for the grid search.  The number of elements in the array must equal to the number of parameters in the model.  This argument is only used when doing a grid search.
        @type inc:                  array of int
        @keyword scaling_matrix:    The scaling matrix.
        @type scaling_matrix:       numpy diagonal matrix
        @return:                    A tuple of the grid size and the minimisation options.  For the minimisation options, the first dimension corresponds to the model parameter.  The second dimension is a list of the number of increments, the lower bound, and upper bound.
        @rtype:                     (int, list of lists [int, float, float])
        """

        # The length of the parameter array.
        n = len(param_vector)

        # Make sure that the length of the parameter array is > 0.
        if n == 0:
            raise RelaxError("Cannot run a grid search on a model with zero parameters.")

        # Lower bounds.
        if lower != None and len(lower) != n:
            raise RelaxLenError('lower bounds', n)

        # Upper bounds.
        if upper != None and len(upper) != n:
            raise RelaxLenError('upper bounds', n)

        # Increment.
        if isinstance(inc, list) and len(inc) != n:
            raise RelaxLenError('increment', n)
        elif isinstance(inc, int):
            inc = [inc]*n

        # Set up the default bounds.
        if not lower:
            # Init.
            lower = []
            upper = []

            # The R2eff model.
            if cdp.model == MODEL_R2EFF:
                for spin_index in range(len(spins)):
                    # Alias the spin.
                    spin = spins[spin_index]

                    # Loop over each spectrometer frequency and dispersion point.
                    for frq, point in loop_frq_point():
                        # Loop over the parameters.
                        for i in range(len(spin.params)):
                            # R2eff relaxation rate (from 1 to 40 s^-1).
                            if spin.params[i] == 'r2eff':
                                lower.append(1.0)
                                upper.append(40.0)

                            # Intensity.
                            elif spin.params[i] == 'i0':
                                lower.append(0.0001)
                                upper.append(max(spin.intensities.values()))

            # All other models.
            else:
                # Only use the parameters of the first spin of the cluster.
                spin = spins[0]
                for i in range(len(spin.params)):
                    # R2 relaxation rates (from 1 to 40 s^-1).
                    if spin.params[i] in ['r2', 'r2a']:
                        lower.append(1.0)
                        upper.append(40.0)

                    # The population of state A.
                    elif spin.params[i] == 'pA':
                        lower.append(0.5)
                        upper.append(1.0)

                    # The pA.pB.dw**2 parameter.
                    elif spin.params[i] == 'phi_ex':
                        lower.append(0.0)
                        upper.append(10.0)

                    # Chemical shift difference between states A and B.
                    elif spin.params[i] == 'dw':
                        lower.append(0.0)
                        upper.append(10.0)

                    # Exchange rates.
                    elif spin.params[i] in ['kex', 'ka']:
                        lower.append(1.0)
                        upper.append(100000.0)

        # The full grid size.
        grid_size = 1
        for i in range(n):
            grid_size *= inc[i]

        # Diagonal scaling of minimisation options.
        lower_new = []
        upper_new = []
        for i in range(n):
            lower_new.append(lower[i] / scaling_matrix[i, i])
            upper_new.append(upper[i] / scaling_matrix[i, i])

        # Return the data structures.
        return grid_size, inc, lower_new, upper_new


    def _minimise_r2eff(self, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=False, scaling=True, verbosity=0, sim_index=None, lower=None, upper=None, inc=None):
        """Optimise the R2eff model by fitting the 2-parameter exponential curves.

        This mimics the R1 and R2 relax_fit analysis.


        @keyword min_algor:         The minimisation algorithm to use.
        @type min_algor:            str
        @keyword min_options:       An array of options to be used by the minimisation algorithm.
        @type min_options:          array of str
        @keyword func_tol:          The function tolerance which, when reached, terminates optimisation.  Setting this to None turns of the check.
        @type func_tol:             None or float
        @keyword grad_tol:          The gradient tolerance which, when reached, terminates optimisation.  Setting this to None turns of the check.
        @type grad_tol:             None or float
        @keyword max_iterations:    The maximum number of iterations for the algorithm.
        @type max_iterations:       int
        @keyword constraints:       If True, constraints are used during optimisation.
        @type constraints:          bool
        @keyword scaling:           If True, diagonal scaling is enabled during optimisation to allow the problem to be better conditioned.
        @type scaling:              bool
        @keyword verbosity:         The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:            int
        @keyword sim_index:         The index of the simulation to optimise.  This should be None if normal optimisation is desired.
        @type sim_index:            None or int
        @keyword lower:             The lower bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type lower:                array of numbers
        @keyword upper:             The upper bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type upper:                array of numbers
        @keyword inc:               The increments for each dimension of the space for the grid search. The number of elements in the array must equal to the number of parameters in the model.  This argument is only used when doing a grid search.
        @type inc:                  array of int
        """

        # Loop over the spins.
        for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
            # Skip spins which have no data.
            if not hasattr(spin, 'intensities'):
                continue

            # Loop over each spectrometer frequency and dispersion point.
            for frq, point in loop_frq_point():
                # The parameter key.
                param_key = return_param_key_from_data(frq=frq, point=point)

                # The initial parameter vector.
                param_vector = assemble_param_vector(spins=[spin], key=param_key, sim_index=sim_index)

                # Diagonal scaling.
                scaling_matrix = assemble_scaling_matrix(spins=[spin], key=param_key, scaling=scaling)
                if len(scaling_matrix):
                    param_vector = dot(inv(scaling_matrix), param_vector)

                # Get the grid search minimisation options.
                lower_new, upper_new = None, None
                if match('^[Gg]rid', min_algor):
                    grid_size, inc_new, lower_new, upper_new = self._grid_search_setup(spins=[spin], param_vector=param_vector, lower=lower, upper=upper, inc=inc, scaling_matrix=scaling_matrix)

                # Linear constraints.
                A, b = None, None
                if constraints:
                    A, b = linear_constraints(spins=[spin], scaling_matrix=scaling_matrix)

                # Print out.
                if verbosity >= 1:
                    # Individual spin section.
                    top = 2
                    if verbosity >= 2:
                        top += 2
                    text = "Fitting to spin %s, frequency %s and dispersion point %s" % (spin_id, frq, point)
                    subsection(file=sys.stdout, text=text, prespace=top)

                    # Grid search printout.
                    if match('^[Gg]rid', min_algor):
                        print("Unconstrained grid search size: %s (constraints may decrease this size).\n" % grid_size)

                # The peak intensities, errors and times.
                values = []
                errors = []
                times = []
                for time in cdp.relax_time_list:
                    values.append(average_intensity(spin=spin, frq=frq, point=point, time=time, sim_index=sim_index))
                    errors.append(average_intensity(spin=spin, frq=frq, point=point, time=time, error=True))
                    times.append(time)

                # The scaling matrix in a diagonalised list form.
                scaling_list = []
                for i in range(len(scaling_matrix)):
                    scaling_list.append(scaling_matrix[i, i])

                # Initialise the function to minimise.
                setup(num_params=len(param_vector), num_times=len(times), values=values, sd=errors, relax_times=times, scaling_matrix=scaling_list)

                # Grid search.
                if search('^[Gg]rid', min_algor):
                    results = grid(func=func, args=(), num_incs=inc_new, lower=lower_new, upper=upper_new, A=A, b=b, verbosity=verbosity)

                    # Unpack the results.
                    param_vector, chi2, iter_count, warning = results
                    f_count = iter_count
                    g_count = 0.0
                    h_count = 0.0

                # Minimisation.
                else:
                    results = generic_minimise(func=func, dfunc=dfunc, d2func=d2func, args=(), x0=param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, A=A, b=b, full_output=True, print_flag=verbosity)

                    # Unpack the results.
                    if results == None:
                        return
                    param_vector, chi2, iter_count, f_count, g_count, h_count, warning = results

                # Scaling.
                if scaling:
                    param_vector = dot(scaling_matrix, param_vector)

                # Disassemble the parameter vector.
                disassemble_param_vector(param_vector=param_vector, spins=[spin], key=param_key, sim_index=sim_index)

                # Monte Carlo minimisation statistics.
                if sim_index != None:
                    # Chi-squared statistic.
                    spin.chi2_sim[sim_index] = chi2

                    # Iterations.
                    spin.iter_sim[sim_index] = iter_count

                    # Function evaluations.
                    spin.f_count_sim[sim_index] = f_count

                    # Gradient evaluations.
                    spin.g_count_sim[sim_index] = g_count

                    # Hessian evaluations.
                    spin.h_count_sim[sim_index] = h_count

                    # Warning.
                    spin.warning_sim[sim_index] = warning

                # Normal statistics.
                else:
                    # Chi-squared statistic.
                    spin.chi2 = chi2

                    # Iterations.
                    spin.iter = iter_count

                    # Function evaluations.
                    spin.f_count = f_count

                    # Gradient evaluations.
                    spin.g_count = g_count

                    # Hessian evaluations.
                    spin.h_count = h_count

                    # Warning.
                    spin.warning = warning


    def _model_setup(self, model, params):
        """Update various model specific data structures.

        @param model:   The relaxation dispersion curve type.
        @type model:    str
        @param params:  A list consisting of the model parameters.
        @type params:   list of str
        """

        # Set the model.
        cdp.model = model

        # Loop over the sequence.
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # The model and parameter names.
            spin.model = model
            spin.params = params

            # Initialise the data structures (if needed).
            self.data_init(spin)


    def _plot_disp_curves(self, dir=None, force=None):
        """Custom 2D Grace plotting function for the dispersion curves.

        One file will be created per spin system.


        @keyword dir:           The optional directory to place the file into.
        @type dir:              str
        @param force:           Boolean argument which if True causes the files to be overwritten if it already exists.
        @type force:            bool
        """

        # Test if the current pipe exists.
        pipes.test()

        # Test if the sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Loop over each spin.
        for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
            # Open the file for writing.
            file_name = "disp_%s.agr" % spin_id
            file_path = get_file_path(file_name, dir)
            file = open_write_file(file_name, dir, force)

            # Initialise some data structures.
            data = []
            set_labels = []
            axis_max = [0, 0]
            x_err_flag = False
            y_err_flag = False

            # Loop over the spectrometer frequencies.
            graph_index = 0
            err = False
            for frq in loop_frq():
                # Add a new set for the data at each frequency.
                data.append([])

                # Add a new label.
                if cdp.exp_type in CPMG_EXP:
                    label = "R\\s2eff\\N"
                else:
                    label = "R\\s1\\xr\\B\\N"
                if frq != None:
                    label += " (%.6f MHz)" % (frq / 1e6)
                set_labels.append(label)

                # Loop over the dispersion points.
                for disp_point in loop_point():
                    # The data key.
                    key = return_param_key_from_data(frq=frq, point=disp_point)

                    # No data present.
                    if key not in spin.r2eff:
                        continue

                    # Add the data.
                    data[-1].append([disp_point, spin.r2eff[key]])

                    # Extend the Grace world.
                    if disp_point > axis_max[0]:
                        axis_max[0] = disp_point
                    if spin.r2eff[key] > axis_max[1]:
                        axis_max[1] = spin.r2eff[key]

                    # Add the error.
                    if hasattr(spin, 'r2eff_err') and key in spin.r2eff_err:
                        err = True
                        data[-1][-1].append(spin.r2eff_err[key])

            # Add the back-calculated data.
            for frq in loop_frq():
                # Add a new set for the data at each frequency.
                data.append([])

                # Add a new label.
                if cdp.exp_type in CPMG_EXP:
                    label = "Back-calculated R\\s2eff\\N"
                else:
                    label = "Back-calculated R\\s1\\xr\\B\\N"
                if frq != None:
                    label += " (%.6f MHz)" % (frq / 1e6)
                set_labels.append(label)

                # Loop over the dispersion points.
                for disp_point in loop_point():
                    # The data key.
                    key = return_param_key_from_data(frq=frq, point=disp_point)

                    # No data present.
                    if not hasattr(spin, 'r2eff_bc') or key not in spin.r2eff_bc:
                        continue

                    # Add the data.
                    data[-1].append([disp_point, spin.r2eff_bc[key]])

                    # Handle the errors.
                    if err:
                        data[-1][-1].append(None)

            # Add the residuals for statistical comparison.
            for frq in loop_frq():
                # Add a new set for the data at each frequency.
                data.append([])

                # Add a new label.
                label = "Residuals"
                if frq != None:
                    label += " (%.6f MHz)" % (frq / 1e6)
                set_labels.append(label)

                # Loop over the dispersion points.
                for disp_point in loop_point():
                    # The data key.
                    key = return_param_key_from_data(frq=frq, point=disp_point)

                    # No data present.
                    if key not in spin.r2eff or not hasattr(spin, 'r2eff_bc') or key not in spin.r2eff_bc:
                        continue

                    # Add the data.
                    data[-1].append([disp_point, spin.r2eff[key] - spin.r2eff_bc[key]])

                    # Handle the errors.
                    if err:
                        err = True
                        data[-1][-1].append(spin.r2eff_err[key])

            # The axis labels.
            if cdp.exp_type == 'CPMG':
                axis_labels = ['\\qCPMG pulse train frequency (Hz)\\Q', '\\qR\\s2,eff\\N\\Q (rad.s\\S-1\\N)']
            else:
                axis_labels = ['\\qSpin-lock field strength (Hz)\\Q', '\\qR\\s1\\xr\\B\\N\\Q (rad.s\\S-1\\N)']

            # Write the header.
            title = "Relaxation dispersion plot"
            write_xy_header(file=file, title=title, sets=len(data), set_names=set_labels, axis_labels=axis_labels, axis_max=axis_max)

            # Write the data.
            graph_type = 'xy'
            if err:
                graph_type = 'xydy'
            write_xy_data([data], file=file, graph_type=graph_type)

            # Close the file.
            file.close()

            # Add the file to the results file list.
            add_result_file(type='grace', label='Grace', file=file_path)


    def _plot_exp_curves(self, file=None, dir=None, force=None, norm=None):
        """Custom 2D Grace plotting function for the exponential curves.

        @keyword file:          The name of the Grace file to create.
        @type file:             str
        @keyword dir:           The optional directory to place the file into.
        @type dir:              str
        @param force:           Boolean argument which if True causes the file to be overwritten if it already exists.
        @type force:            bool
        @keyword norm:          The normalisation flag which if set to True will cause all graphs to be normalised to a starting value of 1.
        @type norm:             bool
        """

        # Test if the current pipe exists.
        pipes.test()

        # Test if the sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Open the file for writing.
        file_path = get_file_path(file, dir)
        file = open_write_file(file, dir, force)

        # Initialise some data structures.
        data = []
        set_labels = []
        x_err_flag = False
        y_err_flag = False

        # Loop over the spectrometer frequencies.
        graph_index = 0
        err = False
        for frq in loop_frq():
            # Loop over the dispersion points.
            for disp_point in loop_point():
                # Create a new graph.
                data.append([])

                # Loop over each spin.
                for spin, id in spin_loop(return_id=True, skip_desel=True):
                    # No data present.
                    if not hasattr(spin, 'intensities'):
                        continue

                    # Append a new set structure and set the name to the spin ID.
                    data[graph_index].append([])
                    if graph_index == 0:
                        set_labels.append("Spin %s" % id)

                    # Loop over the relaxation time periods.
                    for time in cdp.relax_time_list:
                        # The key.
                        keys = find_intensity_keys(frq=frq, point=disp_point, time=time)

                        # Loop over each key.
                        for key in keys:
                            # No key present.
                            if key not in spin.intensities:
                                continue

                            # Add the data.
                            if hasattr(spin, 'intensity_err'):
                                data[graph_index][-1].append([time, spin.intensities[key], spin.intensity_err[key]])
                                err = True
                            else:
                                data[graph_index][-1].append([time, spin.intensities[key]])

                # Increment the frq index.
                graph_index += 1

        # The axis labels.
        axis_labels = ['Relaxation time period (s)', 'Peak intensities']

        # Write the header.
        write_xy_header(sets=len(data[0]), file=file, set_names=set_labels, axis_labels=axis_labels, norm=norm)

        # Write the data.
        graph_type = 'xy'
        if err:
            graph_type = 'xydy'
        write_xy_data(data, file=file, graph_type=graph_type, norm=norm)

        # Close the file.
        file.close()

        # Add the file to the results file list.
        add_result_file(type='grace', label='Grace', file=file_path)


    def _select_model(self, model=MODEL_R2EFF):
        """Set up the model for the relaxation dispersion analysis.

        @keyword model: The relaxation dispersion analysis type.  This can be one of 'R2eff', 'No Rex', 'LM63', 'CR72', 'M61'.
        @type model:    str
        """

        # Test if the current pipe exists.
        pipes.test()

        # Test if the pipe type is set to 'relax_disp'.
        function_type = cdp.pipe_type
        if function_type != 'relax_disp':
            raise RelaxFuncSetupError(specific_setup.get_string(function_type))

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Test if the experiment type is set.
        if not hasattr(cdp, 'exp_type'):
            raise RelaxError("The relaxation dispersion experiment type has not been set.")

        # Test for the C-modules.
        if model == MODEL_R2EFF and cdp.exp_type in VAR_TIME_EXP and not C_module_exp_fn:
            raise RelaxError("The exponential curve-fitting C module cannot be found.")

        # R2eff/R1rho model.
        if model == MODEL_R2EFF:
            print("R2eff/R1rho value and error determination.")
            params = ['r2eff', 'i0']

        # The model for no chemical exchange relaxation.
        elif model == MODEL_NOREX:
            print("The model for no chemical exchange relaxation.")
            params = []
            for frq in loop_frq():
                params.append('r2')

        # LM63 model.
        elif model == MODEL_LM63:
            print("The Luz and Meiboom (1963) 2-site fast exchange model.")
            params = []
            for frq in loop_frq():
                params.append('r2')
            params += ['phi_ex', 'kex']

        # CR72 model.
        elif model == MODEL_CR72:
            print("The Carver and Richards (1972) 2-site model for all time scales.")
            params = []
            for frq in loop_frq():
                params.append('r2')
            params += ['pA', 'dw', 'kex']

        # M61 model.
        elif model == MODEL_M61:
            print("The Meiboom (1961) 2-site fast exchange model for R1rho-type experiments.")
            params = []
            for frq in loop_frq():
                params.append('r2')
            params += ['phi_ex', 'kex']

        # Invalid model.
        else:
            raise RelaxError("The model '%s' must be one of %s." % (model, MODEL_LIST_FULL))

        # Set up the model.
        self._model_setup(model, params)


    def base_data_loop(self):
        """Custom generator method for looping over the base data.

        For the R2eff model, the base data is the peak intensity data defining a single exponential curve.  For all other models, the base data is the R2eff/R1rho values for individual spins.


        @return:    For the R2eff model, a tuple of the spin container and the exponential curve identifying key (the CPMG frequency or R1rho spin-lock field strength).  For all other models, the spin container and ID from the spin loop.
        @rtype:     (tuple of SpinContainer instance and float) or (SpinContainer instance and str)
        """

        # The R2eff model data (the base data is peak intensities).
        if cdp.model == MODEL_R2EFF:
            # Loop over the sequence.
            for spin in spin_loop():
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Skip spins with no peak intensity data.
                if not hasattr(spin, 'intensities'):
                    continue

                # Loop over each spectrometer frequency and dispersion point.
                for frq, point in loop_frq_point():
                    yield spin, frq, point

        # All other models (the base data is the R2eff/R1rho values).
        else:
            # Loop over the sequence.
            for spin, spin_id in spin_loop(return_id=True):
                # Skip deselected spins.
                if not spin.select:
                    continue

                # Skip spins with no R2eff/R1rho values.
                if not hasattr(spin, 'r2eff'):
                    continue

                # Yield the spin container and ID.
                yield spin, spin_id


    def calculate(self, spin_id=None, verbosity=1, sim_index=None):
        """Calculate the R2eff values for fixed relaxation time period data.

        @keyword spin_id:   The spin identification string.
        @type spin_id:      None or str
        @keyword verbosity: The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:    int
        @keyword sim_index: The MC simulation index (unused).
        @type sim_index:    None
        """

        # Test if the current pipe exists.
        pipes.test()

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Test if the model has been set.
        if not hasattr(cdp, 'exp_type'):
            raise RelaxError("The relaxation dispersion experiment type has not been specified.")

        # Test if the model has been set.
        if not hasattr(cdp, 'model'):
            raise RelaxError("The relaxation dispersion model has not been specified.")

        # Test if the curve count exists.
        if not hasattr(cdp, 'dispersion_points'):
            if cdp.exp_type == 'cpmg':
                raise RelaxError("The CPMG frequencies have not been set up.")
            elif cdp.exp_type == 'r1rho':
                raise RelaxError("The spin-lock field strengths have not been set up.")

        # Only allow the fixed relaxation time period data types.
        if cdp.exp_type not in FIXED_TIME_EXP:
            raise RelaxError("The experiment '%s' is not of the fixed relaxation time period data type, the R2eff/R1rho values cannot be directly calculated." % cdp.exp_type)

        # Printouts.
        print("Calculating the R2eff/R1rho values for fixed relaxation time period data.")

        # Loop over the spins.
        for spin, spin_id in spin_loop(return_id=True, skip_desel=True):
            # Spin ID printout.
            print("Spin '%s'." % spin_id)

            # Skip spins which have no data.
            if not hasattr(spin, 'intensities'):
                continue

            # Initialise the data structures.
            if not hasattr(spin, 'r2eff'):
                spin.r2eff = {}
            if not hasattr(spin, 'r2eff_err'):
                spin.r2eff_err = {}

            # Loop over all the data.
            for frq, point, time in loop_frq_point_time():
                # The three keys.
                ref_keys = find_intensity_keys(frq=frq, point=None, time=time)
                int_keys = find_intensity_keys(frq=frq, point=point, time=time)
                param_key = return_param_key_from_data(frq=frq, point=point)

                # Check for missing data.
                missing = False
                for i in range(len(ref_keys)):
                    if ref_keys[i] not in spin.intensities:
                        missing = True
                for i in range(len(int_keys)):
                    if int_keys[i] not in spin.intensities:
                        missing = True
                if missing:
                    continue

                # Average the reference intensity data and errors.
                ref_intensity = average_intensity(spin=spin, frq=frq, point=None, time=time)
                ref_intensity_err = average_intensity(spin=spin, frq=frq, point=None, time=time, error=True)

                # Average the intensity data and errors.
                intensity = average_intensity(spin=spin, frq=frq, point=point, time=time)
                intensity_err = average_intensity(spin=spin, frq=frq, point=point, time=time, error=True)

                # Calculate the R2eff value.
                spin.r2eff[param_key] = calc_two_point_r2eff(relax_time=time, I_ref=ref_intensity, I=intensity)

                # Calculate the R2eff error.
                spin.r2eff_err[param_key] = calc_two_point_r2eff_err(relax_time=time, I_ref=ref_intensity, I=intensity, I_ref_err=ref_intensity_err, I_err=intensity_err)


    def constraint_algorithm(self):
        """Return the 'Log barrier' optimisation constraint algorithm.

        @return:    The 'Log barrier' constraint algorithm.
        @rtype:     str
        """

        # The log barrier algorithm, as required by minfx.
        return 'Log barrier'


    def create_mc_data(self, data_id):
        """Create the Monte Carlo peak intensity data.

        @param data_id: The tuple of the spin container and the exponential curve identifying key, as yielded by the base_data_loop() generator method.
        @type data_id:  SpinContainer instance and float
        @return:        The Monte Carlo simulation data.
        @rtype:         list of floats
        """

        # The R2eff model (with peak intensity base data).
        if cdp.model == MODEL_R2EFF:
            # Unpack the data.
            spin, frq, point = data_id

            # Back calculate the peak intensities.
            values = self._back_calc_peak_intensities(spin=spin, frq=frq, point=point)

        # All other models (with R2eff/R1rho base data).
        else:
            # Unpack the data.
            spin, spin_id = data_id

            # Back calculate the R2eff/R1rho data.
            values = self._back_calc_r2eff(spin=spin, spin_id=spin_id)

        # Return the MC data.
        return values


    def duplicate_data(self, pipe_from=None, pipe_to=None, model_info=None, global_stats=False, verbose=True):
        """Duplicate the data specific to a single model.

        @keyword pipe_from:     The data pipe to copy the data from.
        @type pipe_from:        str
        @keyword pipe_to:       The data pipe to copy the data to.
        @type pipe_to:          str
        @keyword model_info:    The model index from model_info().
        @type model_info:       int
        @keyword global_stats:  The global statistics flag.
        @type global_stats:     bool
        @keyword verbose:       A flag which if True will cause info to be printed out.
        @type verbose:          bool
        """

        # First create the pipe_to data pipe, if it doesn't exist, but don't switch to it.
        if not pipes.has_pipe(pipe_to):
            pipes.create(pipe_to, pipe_type='relax_disp', switch=False)

        # Get the data pipes.
        dp_from = pipes.get_pipe(pipe_from)
        dp_to = pipes.get_pipe(pipe_to)

        # Duplicate all non-sequence specific data.
        for data_name in dir(dp_from):
            # Skip the container objects.
            if data_name in ['mol', 'interatomic', 'structure', 'exp_info']:
                continue

            # Skip special objects.
            if search('^_', data_name) or data_name in list(dp_from.__class__.__dict__.keys()):
                continue

            # Get the original object.
            data_from = getattr(dp_from, data_name)

            # The data already exists.
            if hasattr(dp_to, data_name):
                # Get the object in the target pipe.
                data_to = getattr(dp_to, data_name)

                # The data must match!
                if data_from != data_to:
                    raise RelaxError("The object " + repr(data_name) + " is not consistent between the pipes " + repr(pipe_from) + " and " + repr(pipe_to) + ".")

                # Skip the data.
                continue

            # Duplicate the data.
            setattr(dp_to, data_name, deepcopy(data_from))

        # No sequence data, so skip the rest.
        if dp_from.mol.is_empty():
            return

        # Duplicate the sequence data if it doesn't exist.
        if dp_to.mol.is_empty():
            sequence.copy(pipe_from=pipe_from, pipe_to=pipe_to, preserve_select=True, verbose=verbose)

        # Loop over the cluster.
        for id in model_info:
            # The original spin container.
            spin = return_spin(id, pipe=pipe_from)

            # Duplicate the spin specific data.
            for name in dir(spin):
                # Skip special objects.
                if search('^__', name):
                    continue

                # Get the object.
                obj = getattr(spin, name)

                # Skip methods.
                if isinstance(obj, MethodType):
                    continue

                # Duplicate the object.
                new_obj = deepcopy(getattr(spin, name))
                setattr(dp_to.mol[spin._mol_index].res[spin._res_index].spin[spin._spin_index], name, new_obj)


    def grid_search(self, lower=None, upper=None, inc=None, constraints=True, verbosity=1, sim_index=None):
        """The relaxation dispersion curve fitting grid search function.

        @keyword lower:         The lower bounds of the grid search which must be equal to the number of parameters in the model.
        @type lower:            array of numbers
        @keyword upper:         The upper bounds of the grid search which must be equal to the number of parameters in the model.
        @type upper:            array of numbers
        @keyword inc:           The increments for each dimension of the space for the grid search. The number of elements in the array must equal to the number of parameters in the model.
        @type inc:              array of int
        @keyword constraints:   If True, constraints are applied during the grid search (eliminating parts of the grid).  If False, no constraints are used.
        @type constraints:      bool
        @keyword verbosity:     A flag specifying the amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:        int
        @keyword sim_index:     The index of the simulation to apply the grid search to.  If None, the normal model is optimised.
        @type sim_index:        int
        """

        # Minimisation.
        self.minimise(min_algor='grid', lower=lower, upper=upper, inc=inc, constraints=constraints, verbosity=verbosity, sim_index=sim_index)


    def minimise(self, min_algor=None, min_options=None, func_tol=None, grad_tol=None, max_iterations=None, constraints=False, scaling=True, verbosity=0, sim_index=None, lower=None, upper=None, inc=None):
        """Relaxation dispersion curve fitting function.

        @keyword min_algor:         The minimisation algorithm to use.
        @type min_algor:            str
        @keyword min_options:       An array of options to be used by the minimisation algorithm.
        @type min_options:          array of str
        @keyword func_tol:          The function tolerance which, when reached, terminates optimisation.  Setting this to None turns of the check.
        @type func_tol:             None or float
        @keyword grad_tol:          The gradient tolerance which, when reached, terminates optimisation.  Setting this to None turns of the check.
        @type grad_tol:             None or float
        @keyword max_iterations:    The maximum number of iterations for the algorithm.
        @type max_iterations:       int
        @keyword constraints:       If True, constraints are used during optimisation.
        @type constraints:          bool
        @keyword scaling:           If True, diagonal scaling is enabled during optimisation to allow the problem to be better conditioned.
        @type scaling:              bool
        @keyword verbosity:         The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:            int
        @keyword sim_index:         The index of the simulation to optimise.  This should be None if normal optimisation is desired.
        @type sim_index:            None or int
        @keyword lower:             The lower bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type lower:                array of numbers
        @keyword upper:             The upper bounds of the grid search which must be equal to the number of parameters in the model.  This optional argument is only used when doing a grid search.
        @type upper:                array of numbers
        @keyword inc:               The increments for each dimension of the space for the grid search. The number of elements in the array must equal to the number of parameters in the model.  This argument is only used when doing a grid search.
        @type inc:                  array of int
        """

        # Test if sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Test if the model has been set.
        if not hasattr(cdp, 'exp_type'):
            raise RelaxError("The relaxation dispersion experiment type has not been specified.")

        # Test if the model has been set.
        if not hasattr(cdp, 'model'):
            raise RelaxError("The relaxation dispersion model has not been specified.")

        # Test if the curve count exists.
        if not hasattr(cdp, 'dispersion_points'):
            if cdp.exp_type == 'cpmg':
                raise RelaxError("The CPMG frequencies have not been set up.")
            elif cdp.exp_type == 'r1rho':
                raise RelaxError("The spin-lock field strengths have not been set up.")

        # Test if the spectrometer frequencies have been set.
        if cdp.model in [MODEL_LM63, MODEL_CR72, MODEL_M61] and not hasattr(cdp, 'spectrometer_frq'):
            raise RelaxError("The spectrometer frequency information has not been specified.")

        # Initialise some empty data pipe structures so that the target function set up does not fail.
        if not hasattr(cdp, 'cpmg_frqs_list'):
            cdp.cpmg_frqs_list = []
        if not hasattr(cdp, 'spin_lock_nu1_list'):
            cdp.spin_lock_nu1_list = []

        # Special exponential curve-fitting for the 'R2eff' model.
        if cdp.model == MODEL_R2EFF:
            # Sanity checks.
            if cdp.exp_type in FIXED_TIME_EXP:
                raise RelaxError("The R2eff model with the fixed time period CPMG experiment cannot be optimised.")

            # Optimisation.
            self._minimise_r2eff(min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, max_iterations=max_iterations, constraints=constraints, scaling=scaling, verbosity=verbosity, sim_index=sim_index, lower=lower, upper=upper, inc=inc)

            # Exit the method.
            return

        # The number of time points for the exponential curves (if present).
        num_time_pts = 1
        if hasattr(cdp, 'num_time_pts'):
            num_time_pts = cdp.num_time_pts

        # Number of spectrometer fields.
        fields = [None]
        field_count = 1
        if hasattr(cdp, 'spectrometer_frq'):
            fields = cdp.spectrometer_frq_list
            field_count = cdp.spectrometer_frq_count

        # Loop over the spin blocks.
        for spin_ids in self.model_loop():
            # The spin containers.
            spins = spin_ids_to_containers(spin_ids)

            # The R2eff/R1rho data.
            values, errors, missing, frqs = return_r2eff_arrays(spins=spins, spin_ids=spin_ids, fields=fields, field_count=field_count)

            # Create the initial parameter vector.
            param_vector = assemble_param_vector(spins=spins)

            # Diagonal scaling.
            scaling_matrix = assemble_scaling_matrix(spins=spins, scaling=scaling)
            if len(scaling_matrix):
                param_vector = dot(inv(scaling_matrix), param_vector)

            # Get the grid search minimisation options.
            lower_new, upper_new = None, None
            if match('^[Gg]rid', min_algor):
                grid_size, inc_new, lower_new, upper_new = self._grid_search_setup(spins=spins, param_vector=param_vector, lower=lower, upper=upper, inc=inc, scaling_matrix=scaling_matrix)

            # Linear constraints.
            A, b = None, None
            if constraints:
                A, b = linear_constraints(spins=spins, scaling_matrix=scaling_matrix)

            # Print out.
            if verbosity >= 1:
                # Individual spin block section.
                top = 2
                if verbosity >= 2:
                    top += 2
                subsection(file=sys.stdout, text="Fitting to the spin block %s"%spin_ids, prespace=top)

                # Grid search printout.
                if match('^[Gg]rid', min_algor):
                    print("Unconstrained grid search size: %s (constraints may decrease this size).\n" % grid_size)

            # Initialise the function to minimise.
            model = Dispersion(model=cdp.model, num_params=param_num(spins=spins), num_spins=len(spins), num_frq=field_count, num_disp_points=cdp.dispersion_points, values=values, errors=errors, missing=missing, frqs=frqs, cpmg_frqs=return_cpmg_frqs(ref_flag=False), spin_lock_nu1=return_spin_lock_nu1(ref_flag=False), scaling_matrix=scaling_matrix)

            # Grid search.
            if search('^[Gg]rid', min_algor):
                results = grid(func=model.func, args=(), num_incs=inc_new, lower=lower_new, upper=upper_new, A=A, b=b, verbosity=verbosity)

                # Unpack the results.
                param_vector, chi2, iter_count, warning = results
                f_count = iter_count
                g_count = 0.0
                h_count = 0.0

            # Minimisation.
            else:
                results = generic_minimise(func=model.func, args=(), x0=param_vector, min_algor=min_algor, min_options=min_options, func_tol=func_tol, grad_tol=grad_tol, maxiter=max_iterations, A=A, b=b, full_output=True, print_flag=verbosity)

                # Unpack the results.
                if results == None:
                    return
                param_vector, chi2, iter_count, f_count, g_count, h_count, warning = results

            # Scaling.
            if scaling:
                param_vector = dot(scaling_matrix, param_vector)

            # Disassemble the parameter vector.
            disassemble_param_vector(param_vector=param_vector, spins=spins, sim_index=sim_index)

            # Monte Carlo minimisation statistics.
            if sim_index != None:
                for spin in spins:
                    # Chi-squared statistic.
                    spin.chi2_sim[sim_index] = chi2

                    # Iterations.
                    spin.iter_sim[sim_index] = iter_count

                    # Function evaluations.
                    spin.f_count_sim[sim_index] = f_count

                    # Gradient evaluations.
                    spin.g_count_sim[sim_index] = g_count

                    # Hessian evaluations.
                    spin.h_count_sim[sim_index] = h_count

                    # Warning.
                    spin.warning_sim[sim_index] = warning

            # Normal statistics.
            else:
                for spin in spins:
                    # Chi-squared statistic.
                    spin.chi2 = chi2

                    # Iterations.
                    spin.iter = iter_count

                    # Function evaluations.
                    spin.f_count = f_count

                    # Gradient evaluations.
                    spin.g_count = g_count

                    # Hessian evaluations.
                    spin.h_count = h_count

                    # Warning.
                    spin.warning = warning

            # Store the back-calculated values.
            if sim_index == None:
                for spin_index in range(len(spins)):
                    # Alias the spin.
                    spin = spins[spin_index]

                    # No data.
                    if not hasattr(spin, 'r2eff'):
                        continue

                    # Initialise.
                    if not hasattr(spin, 'r2eff_bc'):
                        spin.r2eff_bc = {}

                    # Loop over the R2eff data.
                    for frq, point in loop_frq_point():
                        # The indices.
                        disp_pt_index = return_index_from_disp_point(point)
                        frq_index = return_index_from_frq(frq)

                        # Missing data.
                        if missing[spin_index, frq_index, disp_pt_index]:
                            continue

                        # The R2eff key.
                        key = return_param_key_from_data(frq=frq, point=point)

                        # Store the back-calculated data.
                        spin.r2eff_bc[key] = model.back_calc[spin_index, frq_index, disp_pt_index]


    def model_desc(self, model_info):
        """Return a description of the model.

        @param model_info:  The model index from model_info().
        @type model_info:   int
        @return:            The model description.
        @rtype:             str
        """

        # The model loop is over the spin clusters, so return a description of the cluster.
        return "The spin cluster %s." % model_info


    def model_loop(self):
        """Loop over the spin groupings for one model applied to multiple spins.

        @return:    The list of spins per block will be yielded, as well as the list of spin IDs.
        @rtype:     tuple of list of SpinContainer instances and list of spin IDs
        """

        # The cluster loop.
        for spin_ids in loop_cluster():
            yield spin_ids


    def model_statistics(self, model_info=None, spin_id=None, global_stats=None):
        """Return the k, n, and chi2 model statistics.

        k - number of parameters.
        n - number of data points.
        chi2 - the chi-squared value.


        @keyword model_info:    The model index from model_info().
        @type model_info:       None or int
        @keyword spin_id:       The spin identification string.  This is ignored in the N-state model.
        @type spin_id:          None or str
        @keyword global_stats:  A parameter which determines if global or local statistics are returned.  For the N-state model, this argument is ignored.
        @type global_stats:     None or bool
        @return:                The optimisation statistics, in tuple format, of the number of parameters (k), the number of data points (n), and the chi-squared value (chi2).
        @rtype:                 tuple of (int, int, float)
        """

        # Unpack the data.
        spin_ids = model_info
        spins = spin_ids_to_containers(spin_ids)

        # Take the number of parameters from the first spin.
        k = len(spins[0].params)

        # The number of points and chi-squared is the sum from all spins.
        n = 0
        chi2 = 0.0
        for spin in spins:
            n += len(spin.r2eff)
            chi2 += spin.chi2

        # Return the values.
        return k, n, chi2


    def overfit_deselect(self, data_check=True, verbose=True):
        """Deselect spins which have insufficient data to support minimisation.

        @keyword data_check:    A flag to signal if the presence of base data is to be checked for.
        @type data_check:       bool
        @keyword verbose:       A flag which if True will allow printouts.
        @type verbose:          bool
        """

        # Test the sequence data exists.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Loop over spin data.
        for spin in spin_loop():
            # Check if data exists.
            if not hasattr(spin, 'intensities'):
                spin.select = False
                continue

            # Require 3 or more data points.
            if len(spin.intensities) < 3:
                spin.select = False
                continue


    def return_data(self, data_id=None):
        """Return the peak intensity data structure.

        @param data_id: The spin ID string, as yielded by the base_data_loop() generator method.
        @type data_id:  str
        @return:        The peak intensity data structure.
        @rtype:         list of float
        """

        # Get the spin container.
        spin = return_spin(spin_id)

        # Return the data.
        return spin.intensities


    return_data_name_doc =  Desc_container("Relaxation dispersion curve fitting data type string matching patterns")
    _table = uf_tables.add_table(label="table: dispersion curve-fit data type patterns", caption="Relaxation dispersion curve fitting data type string matching patterns.")
    _table.add_headings(["Data type", "Object name"])
    _table.add_row(["Transversal relaxation rate (rad/s)", "'r2'"])
    _table.add_row(["Transversal relaxation rate for state A (rad/s)", "'r2a'"])
    _table.add_row(["Population of state A", "'pA'"])
    _table.add_row(["Population of state B", "'pB'"])
    _table.add_row(["The pA.pB.dw**2 parameter (ppm^2)", "'phi_ex'"])
    _table.add_row(["Chemical shift difference between states A and B (ppm)", "'dw'"])
    _table.add_row(["Exchange rate (rad/s)", "'kex'"])
    _table.add_row(["Exchange rate from state A to state B (rad/s)", "'ka'"])
    _table.add_row(["Peak intensities (series)", "'intensities'"])
    _table.add_row(["CPMG pulse train frequency (series, Hz)", "'cpmg_frqs'"])
    return_data_name_doc.add_table(_table.label)


    def return_error(self, data_id=None):
        """Return the standard deviation data structure.

        @param data_id: The tuple of the spin container and the exponential curve identifying key, as yielded by the base_data_loop() generator method.
        @type data_id:  SpinContainer instance and float
        @return:        The standard deviation data structure.
        @rtype:         list of float
        """

        # The R2eff model.
        if cdp.model == MODEL_R2EFF:
            # Unpack the data.
            spin, frq, point = data_id

            # Generate the data structure to return.
            errors = []
            for time in cdp.relax_time_list:
                errors.append(average_intensity(spin=spin, frq=frq, point=point, time=time, error=True))

        # All other models.
        else:
            # Unpack the data.
            spin, spin_id = data_id

            # The errors.
            return spin.r2eff_err

        # Return the error list.
        return errors


    set_doc = Desc_container("Relaxation dispersion curve fitting set details")
    set_doc.add_paragraph("Only three parameters can be set for either the slow- or the fast-exchange regime. For the slow-exchange regime, these parameters include the transversal relaxation rate for state A (R2A), the exchange rate from state A to state (kA) and the chemical shift difference between states A and B (dw). For the fast-exchange regime, these include the transversal relaxation rate (R2), the chemical exchange contribution to R2 (Rex) and the exchange rate (kex). Setting parameters for a non selected model has no effect.")


    def set_error(self, model_info, index, error):
        """Set the parameter errors.

        @param model_info:  The spin container originating from model_loop().
        @type model_info:   unknown
        @param index:       The index of the parameter to set the errors for.
        @type index:        int
        @param error:       The error value.
        @type error:        float
        """

        # Unpack the data.
        spin_ids = model_info
        spins = spin_ids_to_containers(spin_ids)

        # Convert the parameter index.
        param_name, spin_index = param_index_to_param_info(index=index, spins=spins, names=self.data_names(set='params'))

        # The parameter error name.
        err_name = param_name + "_err"

        # The exponential curve parameters.
        if param_name in ['r2eff', 'i0']:
            # Initialise if needed.
            if not hasattr(spins[spin_index], err_name):
                setattr(spins[spin_index], err_name, {})

            # Set the value.
            setattr(spins[spin_index], err_name, error)

        # All other parameters.
        else:
            for spin in spins:
                setattr(spin, err_name, error)


    def set_selected_sim(self, model_info, select_sim):
        """Set the simulation selection flag.

        @param model_info:  The list of spins and spin IDs per cluster originating from model_loop().
        @type model_info:   tuple of list of SpinContainer instances and list of spin IDs
        @param select_sim:  The selection flag for the simulations.
        @type select_sim:   bool
        """

        # Unpack the data.
        spin_ids = model_info
        spins = spin_ids_to_containers(spin_ids)

        # Loop over the spins, storing the structure for each spin.
        for spin in spins:
            spin.select_sim = deepcopy(select_sim)


    def sim_pack_data(self, data_id, sim_data):
        """Pack the Monte Carlo simulation data.

        @param data_id:     The tuple of the spin container and the exponential curve identifying key, as yielded by the base_data_loop() generator method.
        @type data_id:      SpinContainer instance and float
        @param sim_data:    The Monte Carlo simulation data.
        @type sim_data:     list of float
        """

        # The R2eff model (with peak intensity base data).
        if cdp.model == MODEL_R2EFF:
            # Unpack the data.
            spin, frq, point = data_id

            # Initialise the data structure if needed.
            if not hasattr(spin, 'intensity_sim'):
                spin.intensity_sim = {}

            # Loop over each time point.
            time_index = 0
            for time in loop_time():
                # Get the intensity keys.
                int_keys = find_intensity_keys(frq=frq, point=point, time=time)

                # Loop over the intensity keys.
                for int_key in int_keys:
                    # Test if the simulation data point already exists.
                    if int_key in spin.intensity_sim:
                        raise RelaxError("Monte Carlo simulation data for the key '%s' already exists." % int_key)

                    # Initialise the list.
                    spin.intensity_sim[int_key] = []

                    # Loop over the simulations, appending the corresponding data.
                    for i in range(cdp.sim_number):
                        spin.intensity_sim[int_key].append(sim_data[i][time_index])

                # Increment the time index.
                time_index += 1

        # All other models (with R2eff/R1rho base data).
        else:
            # Unpack the data.
            spin, spin_id = data_id

            # Pack the data.
            spin.r2eff_sim = sim_data


    def sim_return_param(self, model_info, index):
        """Return the array of simulation parameter values.

        @param model_info:  The model information originating from model_loop().
        @type model_info:   unknown
        @param index:       The index of the parameter to return the array of values for.
        @type index:        int
        @return:            The array of simulation parameter values.
        @rtype:             list of float
        """

        # Unpack the data.
        spin_ids = model_info
        spins = spin_ids_to_containers(spin_ids)

        # The number of parameters.
        total_param_num = param_num(spins=spins)

        # No more parameters.
        if index >= total_param_num:
            return

        # Convert the parameter index.
        param_name, spin_index = param_index_to_param_info(index=index, spins=spins, names=self.data_names(set='params'))

        # The exponential curve parameters.
        sim_data = []
        if param_name == 'r2eff':
            for i in range(cdp.sim_number):
                sim_data.append(spins[spin_index].r2eff_sim[i])
        elif param_name == 'i0':
            for i in range(cdp.sim_number):
                sim_data.append(spins[spin_index].i0_sim[i])

        # All other parameters.
        else:
            sim_data = getattr(spins[0], param_name + "_sim")

        # Set the sim data to None if empty.
        if sim_data == []:
            sim_data = None

        # Return the object.
        return sim_data


    def sim_return_selected(self, model_info):
        """Return the array of selected simulation flags.

        @param model_info:  The list of spins and spin IDs per cluster originating from model_loop().
        @type model_info:   tuple of list of SpinContainer instances and list of spin IDs
        @return:            The array of selected simulation flags.
        @rtype:             list of int
        """

        # Unpack the data.
        spin_ids = model_info
        spins = spin_ids_to_containers(spin_ids)

        # Return the array from the first spin, as this array will be identical for all spins in the cluster.
        return spins[0].select_sim
