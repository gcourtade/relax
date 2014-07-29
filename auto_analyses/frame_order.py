###############################################################################
#                                                                             #
# Copyright (C) 2011-2014 Edward d'Auvergne                                   #
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
"""The full frame order analysis.


The nested model parameter copying protocol
===========================================

To allow the analysis to complete in under 1,000,000 years, the trick of copying parameters from simpler nested models is used in this auto-analysis.  The protocol is split into four categories for the average domain position, the pivot point, the motional eigenframe and the parameters of ordering.  These use the fact that the free rotor and torsionless models are the two extrema of the models where the torsion angle is restricted, whereby sigma_max is pi and 0 respectively.
"""


# Python module imports.
from numpy import float64, zeros
from os import F_OK, access, getcwd, sep
import sys

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from pipe_control.pipes import get_pipe
from lib.text.sectioning import section, subsection, title
from lib.geometry.coord_transform import spherical_to_cartesian
from prompt.interpreter import Interpreter
from lib.errors import RelaxError
from lib.frame_order.conversions import convert_axis_alpha_to_spherical
from lib.io import open_write_file
from lib.order import iso_cone_theta_to_S
from pipe_control.structure.mass import pipe_centre_of_mass
from specific_analyses.frame_order.data import generate_pivot
from specific_analyses.frame_order.variables import MODEL_FREE_ROTOR, MODEL_ISO_CONE, MODEL_ISO_CONE_FREE_ROTOR, MODEL_ISO_CONE_TORSIONLESS, MODEL_LIST_FREE_ROTORS, MODEL_LIST_NONREDUNDANT, MODEL_LIST_PSEUDO_ELLIPSE, MODEL_PSEUDO_ELLIPSE, MODEL_PSEUDO_ELLIPSE_FREE_ROTOR, MODEL_PSEUDO_ELLIPSE_TORSIONLESS, MODEL_RIGID, MODEL_ROTOR
from status import Status; status = Status()


class Frame_order_analysis:
    """The frame order auto-analysis protocol."""

    def __init__(self, data_pipe_full=None, data_pipe_subset=None, pipe_bundle=None, results_dir=None, grid_inc=11, grid_inc_rigid=21, min_algor='simplex', num_int_pts_grid=200, num_int_pts_subset=[500, 1000], func_tol_subset=[1e-2, 1e-3], num_int_pts_full=[500, 1000, 10000, 100000], func_tol_full=[1e-2, 1e-3, 5e-3, 1e-4], mc_sim_num=500, mc_int_pts=10000, mc_func_tol=1e-3, models=MODEL_LIST_NONREDUNDANT):
        """Perform the full frame order analysis.

        @param data_pipe_full:          The name of the data pipe containing all of the RDC and PCS data.
        @type data_pipe_full:           str
        @param data_pipe_subset:        The name of the data pipe containing all of the RDC data but only a small subset of ~5 PCS points.
        @type data_pipe_subset:         str
        @keyword pipe_bundle:           The data pipe bundle to associate all spawned data pipes with.
        @type pipe_bundle:              str
        @keyword results_dir:           The directory where files are saved in.
        @type results_dir:              str
        @keyword grid_inc:              The number of grid increments to use in the grid search of certain models.
        @type grid_inc:                 int
        @keyword grid_inc_rigid:        The number of grid increments to use in the grid search of the initial rigid model.
        @type grid_inc_rigid:           int
        @keyword min_algor:             The minimisation algorithm (in most cases this should not be changed).
        @type min_algor:                str
        @keyword num_int_pts_grid:      The number of Sobol' points for the PCS numerical integration in the grid searches.
        @type num_int_pts_grid:         int
        @keyword num_int_pts_subset:    The list of the number of Sobol' points for the PCS numerical integration to use iteratively in the optimisations after the grid search (for the PCS data subset).
        @type num_int_pts_subset:       list of int
        @keyword func_tol_subset:       The minimisation function tolerance cutoff to terminate optimisation (for the PCS data subset, see the minimise user function).
        @type func_tol_subset:          list of float
        @keyword num_int_pts_full:      The list of the number of Sobol' points for the PCS numerical integration to use iteratively in the optimisations after the grid search (for all PCS and RDC data).
        @type num_int_pts_full:         list of int
        @keyword func_tol_full:         The minimisation function tolerance cutoff to terminate optimisation (for all PCS and RDC data, see the minimise user function).
        @type func_tol_full:            list of float
        @keyword mc_sim_num:            The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
        @type mc_sim_num:               int
        @keyword mc_int_num:            The number of Sobol' points for the PCS numerical integration during Monte Carlo simulations.
        @type mc_int_num:               int
        @keyword mc_func_tol:           The minimisation function tolerance cutoff to terminate optimisation during Monte Carlo simulations.
        @type mc_func_tol:              float
        @keyword models:                The frame order models to use in the analysis.  The 'rigid' model must be included as this is essential for the analysis.
        @type models:                   list of str
        """

        # Execution lock.
        status.exec_lock.acquire(pipe_bundle, mode='auto-analysis')

        # Initial printout.
        title(file=sys.stdout, text="Frame order auto-analysis", prespace=7)

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
        self.mc_int_pts = mc_int_pts
        self.mc_func_tol = mc_func_tol
        self.models = models

        # A dictionary and list of the data pipe names.
        self.pipe_name_dict = {}
        self.pipe_name_list = []

        # Project directory (i.e. directory containing the model-free model results and the newly generated files)
        if results_dir:
            self.results_dir = results_dir + sep
        else:
            self.results_dir = getcwd() + sep

        # Data checks.
        self.check_vars()

        # Load the interpreter.
        self.interpreter = Interpreter(show_script=False, raise_relax_error=True)
        self.interpreter.populate_self()
        self.interpreter.on(verbose=False)

        # Execute the full protocol.
        try:
            # The nested model optimisation protocol.
            self.nested_models()

            # The final results does not already exist.
            if not self.read_results(model='final', pipe_name='final'):
                # Model selection.
                self.interpreter.model_selection(method='AIC', modsel_pipe='final', pipes=self.pipe_name_list)

                # The number of integration points.
                self.interpreter.frame_order.num_int_pts(num=self.mc_int_pts)

                # Monte Carlo simulations.
                self.interpreter.monte_carlo.setup(number=self.mc_sim_num)
                self.interpreter.monte_carlo.create_data()
                self.interpreter.monte_carlo.initial_values()
                self.interpreter.minimise.execute(self.min_algor, func_tol=self.mc_func_tol)
                self.interpreter.eliminate()
                self.interpreter.monte_carlo.error_analysis()

                # Finish.
                self.interpreter.results.write(file='results', dir=self.results_dir+'final', force=True)

            # Visualisation of the final results.
            self.visualisation(model='final')

        # Clean up.
        finally:
            # Finish and unlock execution.
            status.exec_lock.release()

        # Save the final program state.
        self.interpreter.state.save('final_state', dir=self.results_dir, force=True)


    def check_vars(self):
        """Check that the user has set the variables correctly."""

        # The pipe bundle.
        if not isinstance(self.pipe_bundle, str):
            raise RelaxError("The pipe bundle name '%s' is invalid." % self.pipe_bundle)

        # Minimisation variables.
        if not isinstance(self.grid_inc, int):
            raise RelaxError("The grid_inc user variable '%s' is incorrectly set.  It should be an integer." % self.grid_inc)
        if not isinstance(self.grid_inc_rigid, int):
            raise RelaxError("The grid_inc_rigid user variable '%s' is incorrectly set.  It should be an integer." % self.grid_inc)
        if not isinstance(self.min_algor, str):
            raise RelaxError("The min_algor user variable '%s' is incorrectly set.  It should be a string." % self.min_algor)
        if not isinstance(self.num_int_pts_grid, int):
            raise RelaxError("The num_int_pts_grid user variable '%s' is incorrectly set.  It should be an integer." % self.mc_sim_num)
        if not isinstance(self.mc_sim_num, int):
            raise RelaxError("The mc_sim_num user variable '%s' is incorrectly set.  It should be an integer." % self.mc_sim_num)
        if not isinstance(self.mc_int_pts, int):
            raise RelaxError("The mc_int_pts user variable '%s' is incorrectly set.  It should be an integer." % self.mc_int_pts)
        if not isinstance(self.mc_func_tol, float):
            raise RelaxError("The mc_func_tol user variable '%s' is incorrectly set.  It should be a floating point number." % self.mc_func_tol)

        # Zooming minimisation (PCS subset).
        if len(self.num_int_pts_subset) != len(self.func_tol_subset):
            raise RelaxError("The num_int_pts_subset and func_tol_subset user variables of '%s' and '%s' respectively must be of the same length." % (self.num_int_pts_subset, self.func_tol_subset))
        for i in range(len(self.num_int_pts_subset)):
            if not isinstance(self.num_int_pts_subset[i], int):
                raise RelaxError("The num_int_pts_subset user variable '%s' must be a list of integers." % self.num_int_pts_subset)
            if not isinstance(self.func_tol_subset[i], float):
                raise RelaxError("The func_tol_subset user variable '%s' must be a list of floats." % self.func_tol_subset)

        # Zooming minimisation (all RDC and PCS data).
        if len(self.num_int_pts_full) != len(self.func_tol_full):
            raise RelaxError("The num_int_pts_full and func_tol_full user variables of '%s' and '%s' respectively must be of the same length." % (self.num_int_pts_full, self.func_tol_full))
        for i in range(len(self.num_int_pts_full)):
            if not isinstance(self.num_int_pts_full[i], int):
                raise RelaxError("The num_int_pts_full user variable '%s' must be a list of integers." % self.num_int_pts_full)
            if not isinstance(self.func_tol_full[i], float):
                raise RelaxError("The func_tol_full user variable '%s' must be a list of floats." % self.func_tol_full)


    def custom_grid_incs(self, model):
        """Set up a customised grid search increment number for each model.

        @param model:   The frame order model.
        @type model:    str
        @return:        The list of increment values.
        @rtype:         list of int and None
        """

        # Initialise the structure.
        incs = []
        if hasattr(cdp, 'pivot_fixed') and not cdp.pivot_fixed:
            incs += [None, None, None]
        incs += [None, None, None]

        # The rotor model.
        if model == MODEL_ROTOR:
            incs += [None, None, None, self.grid_inc, self.grid_inc, self.grid_inc]

        # The free rotor model.
        if model == MODEL_FREE_ROTOR:
            incs += [self.grid_inc, self.grid_inc, self.grid_inc, self.grid_inc]

        # The torsionless isotropic cone model.
        if model == MODEL_ISO_CONE_TORSIONLESS:
            incs += [None, None, None, self.grid_inc, self.grid_inc, self.grid_inc]

        # The free rotor isotropic cone model.
        if model == MODEL_ISO_CONE_FREE_ROTOR:
            incs += [None, None, None, None, self.grid_inc]

        # The isotropic cone model.
        if model == MODEL_ISO_CONE:
            incs += [None, None, None, self.grid_inc, self.grid_inc, self.grid_inc, None]

        # The torsionless pseudo-elliptic cone model.
        if model == MODEL_PSEUDO_ELLIPSE_TORSIONLESS:
            incs += [None, None, None, self.grid_inc, self.grid_inc, self.grid_inc, self.grid_inc, None]

        # The free rotor pseudo-elliptic cone model.
        if model == MODEL_PSEUDO_ELLIPSE_FREE_ROTOR:
            incs += [None, None, None, self.grid_inc, self.grid_inc, self.grid_inc, self.grid_inc, None]

        # The pseudo-elliptic cone model.
        if model == MODEL_PSEUDO_ELLIPSE:
            incs += [None, None, None, self.grid_inc, self.grid_inc, self.grid_inc, self.grid_inc, None, None]

        # Return the increment list.
        return incs


    def nested_params_ave_dom_pos(self, model):
        """Copy the average domain parameters from simpler nested models for faster optimisation.

        @param model:   The frame order model.
        @type model:    str
        """

        # Skip the following models to allow for full optimisation.
        if model in [MODEL_RIGID, MODEL_FREE_ROTOR]:
            # Printout.
            print("No nesting of the average domain position parameters.")

            # Exit.
            return

        # The average position from the rigid model.
        if model not in MODEL_LIST_FREE_ROTORS:
            # Printout.
            print("Obtaining the average position from the rigid model.")

            # Get the rigid data pipe.
            pipe = get_pipe(self.pipe_name_dict[MODEL_RIGID])

            # Copy the average position parameters from the rigid model.
            cdp.ave_pos_x = pipe.ave_pos_x
            cdp.ave_pos_y = pipe.ave_pos_y
            cdp.ave_pos_z = pipe.ave_pos_z
            cdp.ave_pos_alpha = pipe.ave_pos_alpha
            cdp.ave_pos_beta = pipe.ave_pos_beta
            cdp.ave_pos_gamma = pipe.ave_pos_gamma

        # The average position from the free rotor model.
        else:
            # Printout.
            print("Obtaining the average position from the free rotor model.")

            # Get the free rotor data pipe.
            pipe = get_pipe(self.pipe_name_dict[MODEL_FREE_ROTOR])

            # Copy the average position parameters from the free rotor model.
            cdp.ave_pos_x = pipe.ave_pos_x
            cdp.ave_pos_y = pipe.ave_pos_y
            cdp.ave_pos_z = pipe.ave_pos_z
            cdp.ave_pos_beta = pipe.ave_pos_beta
            cdp.ave_pos_gamma = pipe.ave_pos_gamma


    def nested_params_eigenframe(self, model):
        """Copy the eigenframe parameters from simpler nested models for faster optimisation.

        @param model:   The frame order model.
        @type model:    str
        """

        # Skip the following models to allow for full optimisation.
        if model in [MODEL_ROTOR, MODEL_PSEUDO_ELLIPSE]:
            # Printout.
            print("No nesting of the eigenframe parameters.")

            # Exit.
            return

        # The cone axis from the rotor model.
        if model in [MODEL_FREE_ROTOR, MODEL_ISO_CONE]:
            # Printout.
            print("Obtaining the cone axis from the rotor model.")

            # Get the rotor data pipe.
            pipe = get_pipe(self.pipe_name_dict[MODEL_ROTOR])

            # The cone axis as the axis alpha angle.
            if model == MODEL_FREE_ROTOR:
                cdp.axis_alpha = pipe.axis_alpha

            # The cone axis from the axis alpha angle to spherical angles.
            if model == MODEL_ISO_CONE:
                cdp.axis_theta, cdp_axis_phi = convert_axis_alpha_to_spherical(alpha=pipe.axis_alpha, pivot=generate_pivot(order=1, pipe_name=self.pipe_name_dict[MODEL_ROTOR]), point=pipe_centre_of_mass(verbosity=0))

        # The cone axis from the isotropic cone model.
        elif model in [MODEL_ISO_CONE_FREE_ROTOR, MODEL_ISO_CONE_TORSIONLESS]:
            # Printout.
            print("Obtaining the cone axis from the isotropic cone model.")

            # Get the iso cone data pipe.
            pipe = get_pipe(self.pipe_name_dict[MODEL_ISO_CONE])

            # Copy the cone axis parameters.
            cdp.axis_theta = pipe.axis_theta
            cdp.axis_phi = pipe.axis_phi

        # The full eigenframe from the pseudo-ellipse model.
        elif model in [MODEL_PSEUDO_ELLIPSE_FREE_ROTOR, MODEL_PSEUDO_ELLIPSE_TORSIONLESS, MODEL_DOUBLE_ROTOR]:
            # Printout.
            print("Obtaining the full eigenframe from the pseudo-ellipse model.")

            # Get the pseudo-ellipse data pipe.
            pipe = get_pipe(self.pipe_name_dict[MODEL_PSEUDO_ELLIPSE])

            # Copy the three Euler angles.
            cdp.eigen_alpha = pipe.eigen_alpha
            cdp.eigen_beta = pipe.eigen_beta
            cdp.eigen_gamma = pipe.eigen_gamma


    def nested_params_order(self, model):
        """Copy the order parameters from simpler nested models for faster optimisation.

        @param model:   The frame order model.
        @type model:    str
        """

        # Skip the following models to allow for full optimisation.
        if model in [MODEL_ROTOR, MODEL_DOUBLE_ROTOR]:
            # Printout.
            print("No nesting of the order parameters.")

            # Exit.
            return

        # The cone angle from the isotropic cone model.
        if model in [MODEL_ISO_CONE_TORSIONLESS, MODEL_PSEUDO_ELLIPSE, MODEL_ISO_CONE_FREE_ROTOR]:
            # Get the iso cone data pipe.
            pipe = get_pipe(self.pipe_name_dict[MODEL_ISO_CONE])

            # Copy the cone angle directly.
            if model == MODEL_ISO_CONE_TORSIONLESS:
                print("Obtaining the cone angle from the isotropic cone model.")
                cdp.cone_theta = pipe.cone_theta

            # Copy as the X cone angle.
            elif model == MODEL_PSEUDO_ELLIPSE:
                print("Obtaining the cone X angle from the isotropic cone model.")
                cdp.cone_theta_x = pipe.cone_theta

            # Convert to the order parameter S.
            elif model == MODEL_ISO_CONE_FREE_ROTOR:
                print("Obtaining the cone order parameter from the isotropic cone model.")
                cdp.cone_s1 = iso_cone_theta_to_S(pipe.cone_theta)

        # The X and Y cone angles from the pseudo-ellipse model.
        elif model in [MODEL_PSEUDO_ELLIPSE_TORSIONLESS, MODEL_PSEUDO_ELLIPSE_FREE_ROTOR]:
            # Printout.
            print("Obtaining the cone X and Y angles from the pseudo-ellipse model.")

            # Get the pseudo-ellipse data pipe.
            pipe = get_pipe(self.pipe_name_dict[MODEL_PSEUDO_ELLIPSE])

            # Copy the cone axis.
            cdp.cone_theta_x = pipe.cone_theta_x
            cdp.cone_theta_y = pipe.cone_theta_y


        # The torsion from the rotor model.
        if model in [MODEL_ISO_CONE, MODEL_PSEUDO_ELLIPSE]:
            # Get the rotor data pipe.
            pipe = get_pipe(self.pipe_name_dict[MODEL_ROTOR])

            # Copy the cone axis.
            cdp.cone_sigma_max = pipe.cone_sigma_max


    def nested_params_pivot(self, model):
        """Copy the pivot parameters from simpler nested models for faster optimisation.

        @param model:   The frame order model.
        @type model:    str
        """

        # Skip the following models to allow for full optimisation.
        if model in [MODEL_ROTOR]:
            # Printout.
            print("No nesting of the pivot parameters.")

            # Exit.
            return

        # The pivot from the rotor model.
        if model in [MODEL_ISO_CONE, MODEL_FREE_ROTOR]:
            # Printout.
            print("Obtaining the pivot point from the rotor model.")

            # Get the iso cone data pipe.
            pipe = get_pipe(self.pipe_name_dict[MODEL_ROTOR])

            # Copy the pivot parameters.
            cdp.pivot_x = pipe.pivot_x
            cdp.pivot_y = pipe.pivot_y
            cdp.pivot_z = pipe.pivot_z

        # The pivot from the isotropic cone model.
        else:
            # Printout.
            print("Obtaining the pivot point from the isotropic cone model.")

            # Get the iso cone data pipe.
            pipe = get_pipe(self.pipe_name_dict[MODEL_ISO_CONE])

            # Copy the cone axis parameters.
            cdp.pivot_x = pipe.pivot_x
            cdp.pivot_y = pipe.pivot_y
            cdp.pivot_z = pipe.pivot_z


    def nested_models(self):
        """Protocol for the nested optimisation of the frame order models."""

        # First optimise the rigid model using all data.
        self.optimise_rigid()

        # Iteratively optimise the frame order models.
        for model in self.models:
            # Skip the already optimised rigid model.
            if model == MODEL_RIGID:
                continue

            # The model title.
            title = model[0].upper() + model[1:]

            # Printout.
            section(file=sys.stdout, text="%s frame order model"%title, prespace=5)

            # The data pipe name.
            self.pipe_name_dict[model] = '%s - %s' % (title, self.pipe_bundle)
            self.pipe_name_list.append(self.pipe_name_dict[model])

            # The results file already exists, so read its contents instead.
            if self.read_results(model=model, pipe_name=self.pipe_name_dict[model]):
                # Re-perform model elimination just in case.
                self.interpreter.eliminate()

                # The PDB representation of the model and visualisation script (in case this was not completed correctly).
                self.visualisation(model=model)

                # Skip to the next model.
                continue

            # Create the data pipe using the full data set, and switch to it.
            self.interpreter.pipe.copy(self.data_pipe_subset, self.pipe_name_dict[model], bundle_to=self.pipe_bundle)
            self.interpreter.pipe.switch(self.pipe_name_dict[model])

            # Select the Frame Order model.
            self.interpreter.frame_order.select_model(model=model)

            # Copy nested parameters.
            subsection(file=sys.stdout, text="Parameter nesting.")
            self.nested_params_ave_dom_pos(model)
            self.nested_params_eigenframe(model)
            self.nested_params_pivot(model)
            self.nested_params_order(model)

            # The optimisation settings.
            self.interpreter.frame_order.num_int_pts(num=self.num_int_pts_grid)

            # Grid search.
            incs = self.custom_grid_incs(model)
            self.interpreter.minimise.grid_search(inc=incs)

            # Minimise (for the PCS data subset and full RDC set).
            for i in range(len(self.num_int_pts_subset)):
                self.interpreter.frame_order.num_int_pts(num=self.num_int_pts_subset[i])
                self.interpreter.minimise.execute(self.min_algor, func_tol=self.func_tol_subset[i])

            # Copy the PCS data.
            self.interpreter.pcs.copy(pipe_from=self.data_pipe_full, pipe_to=self.pipe_name_dict[model])

            # Minimise (for the full data set).
            for i in range(len(self.num_int_pts_full)):
                self.interpreter.frame_order.num_int_pts(num=self.num_int_pts_full[i])
                self.interpreter.minimise.execute(self.min_algor, func_tol=self.func_tol_full[i])

            # Results printout.
            self.print_results()

            # Model elimination.
            self.interpreter.eliminate()

            # Save the results.
            self.interpreter.results.write(dir=self.results_dir+model, force=True)

            # The PDB representation of the model and visualisation script.
            self.visualisation(model=model)


    def optimise_rigid(self):
        """Optimise the rigid frame order model.

        The Sobol' integration is not used here, so the algorithm is different to the other frame order models.
        """

        # The model.
        model = MODEL_RIGID
        title = model[0].upper() + model[1:]

        # Print out.
        section(file=sys.stdout, text="%s frame order model"%title, prespace=5)

        # The data pipe name.
        self.pipe_name_dict[model] = '%s - %s' % (title, self.pipe_bundle)
        self.pipe_name_list.append(self.pipe_name_dict[model])

        # The results file already exists, so read its contents instead.
        if self.read_results(model=model, pipe_name=self.pipe_name_dict[model]):
            # The PDB representation of the model (in case this was not completed correctly).
            self.interpreter.frame_order.pdb_model(dir=self.results_dir+model, force=True)

            # Nothing more to do.
            return

        # Create the data pipe using the full data set, and switch to it.
        self.interpreter.pipe.copy(self.data_pipe_full, self.pipe_name_dict[model], bundle_to=self.pipe_bundle)
        self.interpreter.pipe.switch(self.pipe_name_dict[model])

        # Select the Frame Order model.
        self.interpreter.frame_order.select_model(model=model)

        # Split grid search for the translation.
        print("\n\nTranslation active - splitting the grid search and iterating.")
        for i in range(2):
            # First optimise the rotation.
            self.interpreter.grid_search(inc=[None, None, None, self.grid_inc_rigid, self.grid_inc_rigid, self.grid_inc_rigid])

            # Then the translation.
            self.interpreter.minimise.grid_search(inc=[self.grid_inc_rigid, self.grid_inc_rigid, self.grid_inc_rigid, None, None, None])

        # Minimise.
        self.interpreter.minimise.execute(self.min_algor)

        # Results printout.
        self.print_results()

        # Save the results.
        self.interpreter.results.write(dir=self.results_dir+model, force=True)

        # The PDB representation of the model.
        self.interpreter.frame_order.pdb_model(dir=self.results_dir+model, force=True)


    def print_results(self):
        """Print out the optimisation results for the current data pipe."""

        # Header.
        sys.stdout.write("\nFinal optimisation results:\n")

        # Formatting string.
        format_float = "    %-20s %20.15f\n"
        format_vect = "    %-20s %20s\n"

        # Average position.
        if hasattr(cdp, 'ave_pos_x') or hasattr(cdp, 'ave_pos_alpha') or hasattr(cdp, 'ave_pos_beta') or hasattr(cdp, 'ave_pos_gamma'):
            sys.stdout.write("\nAverage moving domain position:\n")
        if hasattr(cdp, 'ave_pos_x'):
            sys.stdout.write(format_float % ('x:', cdp.ave_pos_x))
        if hasattr(cdp, 'ave_pos_y'):
            sys.stdout.write(format_float % ('y:', cdp.ave_pos_y))
        if hasattr(cdp, 'ave_pos_z'):
            sys.stdout.write(format_float % ('z:', cdp.ave_pos_z))
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
        path = self.results_dir + model + sep + 'results.bz2'

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


    def visualisation(self, model=None):
        """Create visual representations of the frame order results for the given model.

        This includes a PDB representation of the motions (the 'cone.pdb' file located in each model directory) together with a relax script for displaying the average domain positions together with the cone/motion representation in PyMOL (the 'pymol_display.py' file, also created in the model directory).

        @keyword model:     The frame order model to visualise.  This should match the model of the current data pipe, unless the special value of 'final' is used to indicate the visualisation of the final results.
        @type model:        str
        """

        # Sanity check.
        if model != 'final' and model != cdp.model:
            raise RelaxError("The model '%s' does not match the model '%s' of the current data pipe." % (model, cdp.model))

        # The PDB representation of the model.
        self.interpreter.frame_order.pdb_model(dir=self.results_dir+model, force=True)

        # Create the visualisation script.
        subsection(file=sys.stdout, text="Creating a PyMOL visualisation script.")
        script = open_write_file(file_name='pymol_display.py', dir=self.results_dir+model, force=True)

        # Add a comment for the user.
        script.write("# relax script for displaying the frame order results of this '%s' model in PyMOL.\n\n" % model)

        # The script contents.
        script.write("# PyMOL visualisation.\n")
        script.write("pymol.frame_order()\n")

        # Close the file.
        script.close()
