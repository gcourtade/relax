###############################################################################
#                                                                             #
# Copyright (C) 2011-2012 Edward d'Auvergne                                   #
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
"""The full frame order analysis."""


# Python module imports.
from math import pi
from numpy import float64, zeros
from os import F_OK, access, getcwd, sep
from random import gauss, uniform
import sys
from time import localtime

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns.angles import wrap_angles
from generic_fns.pipes import cdp_name, get_pipe
from maths_fns.coord_transform import spherical_to_cartesian
from prompt.interpreter import Interpreter
from relax_errors import RelaxError
from status import Status; status = Status()


class Frame_order_analysis:
    def __init__(self, data_pipe_full=None, data_pipe_subset=None, pipe_bundle=None, results_dir=None, grid_inc=11, grid_inc_rigid=21, min_algor='simplex', num_int_pts_grid=50, num_int_pts_subset=[20, 100], func_tol_subset=[1e-2, 1e-2], num_int_pts_full=[100, 1000, 200000], func_tol_full=[1e-2, 1e-3, 1e-4], mc_sim_num=500):
        """Perform the full frame order analysis.

        @param data_pipe_full:      The name of the data pipe containing all of the RDC and PCS data.
        @type data_pipe_full:       str
        @param data_pipe_subset:    The name of the data pipe containing all of the RDC data but only a small subset of ~5 PCS points.
        @type data_pipe_subset:     str
        @keyword pipe_bundle:       The data pipe bundle to associate all spawned data pipes with.
        @type pipe_bundle:          str
        @keyword results_dir:       The directory where files are saved in.
        @type results_dir:          str
        @keyword grid_inc:          The number of grid increments to use in the grid search of certain models.
        @type grid_inc:             int
        @keyword grid_inc_rigid:    The number of grid increments to use in the grid search of the initial rigid model.
        @type grid_inc_rigid:       int
        @keyword min_algor:         The minimisation algorithm (in most cases this should not be changed).
        @type min_algor:            str
        @keyword mc_sim_num:        The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        @type mc_sim_num:           int
        """

        # Execution lock.
        status.exec_lock.acquire(pipe_bundle, mode='auto-analysis')

        # Store the args.
        self.data_pipe_full = data_pipe_full
        self.data_pipe_subset = data_pipe_subset
        self.pipe_bundle = pipe_bundle
        self.grid_inc = grid_inc
        self.grid_inc_rigid = grid_inc_rigid
        self.min_algor = min_algor
        self.num_int_pts_grid = num_int_pts_grid
        self.num_int_pts_subset = num_int_pts_subset
        self.func_tol_subset = func_tol_subset
        self.num_int_pts_full = num_int_pts_full
        self.func_tol_full = func_tol_full
        self.mc_sim_num = mc_sim_num

        # A dictionary of the data pipe names.
        self.models = {}
        self.pipes = []

        # Project directory (i.e. directory containing the model-free model results and the newly generated files)
        if results_dir:
            self.results_dir = results_dir + sep
        else:
            self.results_dir = getcwd() + sep

        # Data checks.
        self.check_vars()

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, quit=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)

        # Execute the full protocol.
        try:
            # The nested model optimisation protocol.
            self.optimise()

            # Model selection.
            self.interpreter.model_selection(method='AIC', modsel_pipe='final', pipes=self.pipes)

            # Monte Carlo simulations.
            self.interpreter.monte_carlo.setup(number=self.mc_sim_num)
            self.interpreter.monte_carlo.create_data()
            self.interpreter.monte_carlo.initial_values()
            self.interpreter.minimise(self.min_algor, constraints=False)
            self.interpreter.eliminate()
            self.interpreter.monte_carlo.error_analysis()

            # Finish.
            self.interpreter.results.write(file='results', force=True)

        # Clean up.
        finally:
            # Finish and unlock execution.
            status.exec_lock.release()

        # Save the final program state.
        self.interpreter.state.save('final_state', force=True)


    def check_vars(self):
        """Check that the user has set the variables correctly."""

        # The pipe bundle.
        if not isinstance(self.pipe_bundle, str):
            raise RelaxError("The pipe bundle name '%s' is invalid." % self.pipe_bundle)

        # Min vars.
        if not isinstance(self.grid_inc, int):
            raise RelaxError("The grid_inc user variable '%s' is incorrectly set.  It should be an integer." % self.grid_inc)
        if not isinstance(self.min_algor, str):
            raise RelaxError("The min_algor user variable '%s' is incorrectly set.  It should be a string." % self.min_algor)
        if not isinstance(self.mc_sim_num, int):
            raise RelaxError("The mc_sim_num user variable '%s' is incorrectly set.  It should be an integer." % self.mc_sim_num)


    def custom_grid_incs(self, model):
        """Set up a customised grid search increment number for each model.

        @param model:   The frame order model.
        @type model:    str
        """

        # The rotor model.
        if model == 'rotor':
            return [None, None, None, self.grid_inc, self.grid_inc, self.grid_inc]

        # The free rotor model.
        if model == 'free rotor':
            return [None, None, self.grid_inc, self.grid_inc]

        # The torsionless isotropic cone model.
        if model == 'iso cone, torsionless':
            return [None, None, None, self.grid_inc, self.grid_inc, self.grid_inc]

        # The free rotor isotropic cone model.
        if model == 'iso cone, free rotor':
            return [None, None, None, None, self.grid_inc]

        # The isotropic cone model.
        if model == 'iso cone':
            return [None, None, None, self.grid_inc, self.grid_inc, self.grid_inc, None]

        # The torsionless pseudo-elliptic cone model.
        if model == 'pseudo-ellipse, torsionless':
            return [None, None, None, self.grid_inc, self.grid_inc, self.grid_inc, self.grid_inc, None]

        # The free rotor pseudo-elliptic cone model.
        if model == 'pseudo-ellipse, free rotor':
            return [None, None, None, self.grid_inc, self.grid_inc, self.grid_inc, self.grid_inc, None]

        # The pseudo-elliptic cone model.
        if model == 'pseudo-ellipse':
            return [None, None, None, self.grid_inc, self.grid_inc, self.grid_inc, self.grid_inc, None, None]


    def nested_params(self, model):
        """Copy the parameters from the simpler nested models for faster optimisation.

        @param model:   The frame order model.
        @type model:    str
        """

        # The average position from the rigid model.
        if model not in []:
            # Get the rigid data pipe.
            rigid_pipe = get_pipe(self.models['rigid'])

            # Copy the average position parameters from the rigid model.
            if model not in ['free rotor', 'iso cone, free rotor']:
                cdp.ave_pos_alpha = rigid_pipe.ave_pos_alpha
            cdp.ave_pos_beta = rigid_pipe.ave_pos_beta
            cdp.ave_pos_gamma = rigid_pipe.ave_pos_gamma

        # The cone axis from the rotor model.
        if model in ['iso cone']:
            # Get the rotor data pipe.
            rotor_pipe = get_pipe(self.models['rotor'])

            # Copy the cone axis.
            cdp.axis_theta = rotor_pipe.axis_theta
            cdp.axis_phi = rotor_pipe.axis_phi

        # The cone axis from the free rotor model.
        if model in ['iso cone, free rotor']:
            # Get the rotor data pipe.
            free_rotor_pipe = get_pipe(self.models['free rotor'])

            # Copy the cone axis.
            cdp.axis_theta = free_rotor_pipe.axis_theta
            cdp.axis_phi = free_rotor_pipe.axis_phi

        # The torsion from the rotor model.
        if model in ['iso cone', 'pseudo-ellipse']:
            # Get the rotor data pipe.
            rotor_pipe = get_pipe(self.models['rotor'])

            # Copy the cone axis.
            cdp.cone_sigma_max = rotor_pipe.cone_sigma_max

        # The cone angles from from the torsionless isotropic cone model.
        if model in ['pseudo-ellipse, torsionless', 'pseudo-ellipse, free rotor', 'pseudo-ellipse']:
            # Get the rotor data pipe.
            pipe = get_pipe(self.models['iso cone, torsionless'])

            # Copy the cone axis.
            cdp.cone_theta_x = pipe.cone_theta
            cdp.cone_theta_y = pipe.cone_theta


    def optimise(self):
        """Protocol for the nested optimisation of the frame order models."""

        # First optimise the rigid model using all data.
        self.optimise_rigid()

        # Iteratively optimise the frame order models.
        models = ['rotor', 'free rotor', 'iso cone, torsionless', 'iso cone, free rotor', 'iso cone', 'pseudo-ellipse, torsionless', 'pseudo-ellipse, free rotor', 'pseudo-ellipse']
        for model in models:
            # The model title.
            title = model[0].upper() + model[1:]

            # Print out.
            self.print_title(title)

            # The data pipe name.
            self.models[model] = '%s - %s' % (title, self.pipe_bundle)
            self.pipes.append(self.models[model])

            # The results file already exists, so read its contents instead.
            if self.read_results(model=model, pipe_name=self.models[model]):
                # Re-perform model elimination just in case.
                self.interpreter.eliminate()

                # Skip to the next model.
                continue

            # Create the data pipe using the full data set, and switch to it.
            self.interpreter.pipe.copy(self.data_pipe_subset, self.models[model], bundle_to=self.pipe_bundle)
            self.interpreter.pipe.switch(self.models[model])

            # Select the Frame Order model.
            self.interpreter.frame_order.select_model(model=model)

            # Copy nested parameters.
            self.nested_params(model)

            # The optimisation settings.
            self.interpreter.frame_order.num_int_pts(num=self.num_int_pts_grid)
            self.interpreter.frame_order.quad_int(flag=False)

            # Grid search.
            incs = self.custom_grid_incs(model)
            self.interpreter.grid_search(inc=incs, constraints=False)

            # Minimise (for the PCS data subset and full RDC set).
            for i in range(len(self.num_int_pts_subset)):
                self.interpreter.frame_order.num_int_pts(num=self.num_int_pts_subset[i])
                self.interpreter.minimise(self.min_algor, func_tol=self.func_tol_subset[i], constraints=False)

            # Copy the PCS data.
            self.interpreter.pcs.copy(pipe_from=self.data_pipe_full, pipe_to=self.models[model])

            # Minimise (for the full data set).
            for i in range(len(self.num_int_pts_full)):
                self.interpreter.frame_order.num_int_pts(num=self.num_int_pts_full[i])
                self.interpreter.minimise(self.min_algor, func_tol=self.func_tol_full[i], constraints=False)

            # Results printout.
            self.print_results()

            # Model elimination.
            self.interpreter.eliminate()

            # Save the results.
            self.interpreter.results.write(dir=model, force=True)


    def optimise_rigid(self):
        """Optimise the rigid frame order model.

        The Sobol' integration is not used here, so the algorithm is different to the other frame order models.
        """

        # The model.
        model = 'rigid'
        title = model[0].upper() + model[1:]

        # Print out.
        self.print_title(title)

        # The data pipe name.
        self.models[model] = '%s - %s' % (title, self.pipe_bundle)
        self.pipes.append(self.models[model])

        # The results file already exists, so read its contents instead.
        if self.read_results(model=model, pipe_name=self.models[model]):
            return

        # Create the data pipe using the full data set, and switch to it.
        self.interpreter.pipe.copy(self.data_pipe_full, self.models[model], bundle_to=self.pipe_bundle)
        self.interpreter.pipe.switch(self.models[model])

        # Select the Frame Order model.
        self.interpreter.frame_order.select_model(model=model)

        # Grid search.
        self.interpreter.grid_search(inc=self.grid_inc_rigid, constraints=False)

        # Minimise.
        self.interpreter.minimise(self.min_algor, constraints=False)

        # Results printout.
        self.print_results()

        # Save the results.
        self.interpreter.results.write(dir=model, force=True)


    def print_results(self):
        """Print out the optimisation results for the current data pipe."""

        # Header.
        sys.stdout.write("\nFinal optimisation results:\n")

        # Formatting string.
        format_float = "    %-20s %20.15f\n"
        format_vect = "    %-20s %20s\n"

        # Average position.
        if hasattr(cdp, 'ave_pos_alpha') or hasattr(cdp, 'ave_pos_beta') or hasattr(cdp, 'ave_pos_gamma'):
            sys.stdout.write("\nAverage moving domain position Euler angles:\n")
        if hasattr(cdp, 'ave_pos_alpha'):
            sys.stdout.write(format_float % ('alpha:', cdp.ave_pos_alpha))
        if hasattr(cdp, 'ave_pos_beta'):
            sys.stdout.write(format_float % ('beta:', cdp.ave_pos_beta))
        if hasattr(cdp, 'ave_pos_gamma'):
            sys.stdout.write(format_float % ('gamma:', cdp.ave_pos_gamma))

        # Frame order eigenframe.
        if hasattr(cdp, 'eigen_alpha') or hasattr(cdp, 'eigen_beta') or hasattr(cdp, 'eigen_gamma') or hasattr(cdp, 'axis_theta') or hasattr(cdp, 'axis_phi'):
            sys.stdout.write("\nFrame order eigenframe:\n")
        if hasattr(cdp, 'eigen_alpha'):
            sys.stdout.write(format_float % ('eigen alpha:', cdp.eigen_alpha))
        if hasattr(cdp, 'eigen_beta'):
            sys.stdout.write(format_float % ('eigen beta:', cdp.eigen_beta))
        if hasattr(cdp, 'eigen_gamma'):
            sys.stdout.write(format_float % ('eigen gamma:', cdp.eigen_gamma))

        # The cone axis.
        if hasattr(cdp, 'axis_theta'):
            # The angles.
            sys.stdout.write(format_float % ('axis theta:', cdp.axis_theta))
            sys.stdout.write(format_float % ('axis phi:', cdp.axis_phi))

            # The axis.
            axis = zeros(3, float64)
            spherical_to_cartesian([1.0, cdp.axis_theta, cdp.axis_phi], axis)
            sys.stdout.write(format_vect % ('axis:', axis))

        # Frame ordering.
        if hasattr(cdp, 'cone_theta_x') or hasattr(cdp, 'cone_theta_y') or hasattr(cdp, 'cone_theta') or hasattr(cdp, 'cone_s1') or hasattr(cdp, 'cone_sigma_max'):
            sys.stdout.write("\nFrame ordering:\n")
        if hasattr(cdp, 'cone_theta_x'):
            sys.stdout.write(format_float % ('cone theta_x:', cdp.cone_theta_x))
        if hasattr(cdp, 'cone_theta_y'):
            sys.stdout.write(format_float % ('cone theta_y:', cdp.cone_theta_y))
        if hasattr(cdp, 'cone_theta'):
            sys.stdout.write(format_float % ('cone theta:', cdp.cone_theta))
        if hasattr(cdp, 'cone_s1'):
            sys.stdout.write(format_float % ('cone s1:', cdp.cone_s1))
        if hasattr(cdp, 'cone_sigma_max'):
            sys.stdout.write(format_float % ('sigma_max:', cdp.cone_sigma_max))

        # Minimisation statistics.
        if hasattr(cdp, 'chi2'):
            sys.stdout.write("\nMinimisation statistics:\n")
        if hasattr(cdp, 'chi2'):
            sys.stdout.write(format_float % ('chi2:', cdp.chi2))

        # Final spacing.
        sys.stdout.write("\n")


    def print_title(self, name):
        """Title print out for each frame order model.

        @param name:    The frame order model name.
        @type name:     str
        """

        text = "# %s frame order model #" % name
        print("\n\n\n\n\n" + "#"*len(text))
        print("%s" % text)
        print("#"*len(text) + "\n")


    def read_results(self, model=None, pipe_name=None):
        """Attempt to read old results files.

        @keyword model:     The frame order model.
        @type model:        str
        @keyword pipe_name: The name of the data pipe to use for this model.
        @type pipe_name:    str
        @return:            True if the file exists and has been read, False otherwise.
        @rtype:             bool
        """

        # The file name.
        path = model + sep + 'results.bz2'

        # The file does not exist.
        if not access(path, F_OK):
            return False

        # Create an empty data pipe.
        self.interpreter.pipe.create(pipe_name=pipe_name, pipe_type='frame order')

        # Read the results file.
        self.interpreter.results.read(path)

        # Results printout.
        self.print_results()

        # Success.
        return True
