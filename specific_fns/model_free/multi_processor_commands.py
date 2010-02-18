###############################################################################
#                                                                             #
# Copyright (C) 2007 Gary S Thompson (https://gna.org/users/varioustoxins)    #
# Copyright (C) 2008, 2010 Edward d'Auvergne                                  #
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

# Module docstring.
"""Module for the multi-processor command system."""

# Python module imports.
import sys
from re import match

# relax module imports.
from maths_fns.mf import Mf
from minfx.generic import generic_minimise
from minfx.grid import grid
from multi.processor import Capturing_exception, Memo, Result_command, Result_string, Slave_command



def spin_print(spin_id, verbosity):
    """Print out some header text for the spin.

    @param spin_id:     The spin ID string.
    @type spin_id:      str
    @param verbosity:   The amount of information to print.  The higher the value, the greater the verbosity.
    @type verbosity:    int
    """

    # Some extra spacing for verbose printouts.
    if verbosity >= 2:
        print("\n\n")

    # The header.
    string = "Fitting to spin " + repr(spin_id)
    print("\n\n" + string)
    print(len(string) * '~')


class MF_grid_memo(Memo):
    def __init__(self, super_grid_memo):

        # Execute the base class __init__() method.
        super(MF_grid_memo, self).__init__()

        self.super_grid_memo = super_grid_memo
        self.super_grid_memo.add_sub_memo(self)


    def add_result(self, results):
        self.super_grid_memo.add_result(self, results)


class MF_grid_result_command(Result_command):
    def __init__(self, processor, result_string, memo_id, param_vector, func, iter, fc, gc, hc, warning, completed):

        # Execute the base class __init__() method.
        super(MF_grid_result_command, self).__init__(processor=processor, completed=completed)

        self.result_string = result_string
        self.memo_id = memo_id
        self.param_vector = param_vector
        self.func = func
        self.iter = iter
        self.fc = fc
        self.gc = gc
        self.hc = hc
        self.warning = warning


    def run(self, processor, memo):
        # FIXME: Check against full result
        # FIXME: names not consistent in memo
        # FIXME: too much repacking
        results = (self.param_vector, self.func, self.iter, self.fc, self.gc, self.hc, self.warning)
        memo.add_result(results)

        sgm = memo.super_grid_memo

        print_prefix = sgm.print_prefix
        verbosity = sgm.verbosity
        full_output = sgm.full_output
        A = sgm.A
        b = sgm.b
        grid_size = sgm.grid_size

        if sgm.first_time:
            print()
            print("Unconstrained grid search size: " + repr(grid_size) + " (constraints may decrease this size).\n")
            if verbosity:
                if verbosity >= 2:
                    print(print_prefix)
                print(print_prefix)
                print(print_prefix + "Grid search")
                print(print_prefix + "~~~~~~~~~~~")

            # Linear constraints.
            if A != None and b != None:
                if verbosity >= 3:
                    print(print_prefix + "Linear constraint matrices.")
                    print(print_prefix + "A: " + repr(A))
                    print(print_prefix + "b: " + repr(b))

        # we don't want to prepend the masters stdout tag
        sys.stdout.write('\n'+self.result_string),

        if sgm.completed:
            if verbosity and results != None:
                if full_output:
                    print('')
                    print('')
                    print(print_prefix + "Parameter values: " + repr(sgm.xk))
                    print(print_prefix + "Function value:   " + repr(sgm.fk))
                    print(print_prefix + "Iterations:       " + repr(sgm.k))
                    print(print_prefix + "Function calls:   " + repr(sgm.f_count))
                    print(print_prefix + "Gradient calls:   " + repr(sgm.g_count))
                    print(print_prefix + "Hessian calls:    " + repr(sgm.h_count))
                    if sgm.warning:
                        print(print_prefix + "Warning:          " + sgm.warning)
                    else:
                        print(print_prefix + "Warning:          None")
                else:
                    print(print_prefix + "Parameter values: " + repr(sgm.short_results))
                print("")

            # Initialise the iteration counter and function, gradient, and Hessian call counters.
            sgm.model_free.iter_count = 0
            sgm.model_free.f_count = 0
            sgm.model_free.g_count = 0
            sgm.model_free.h_count = 0

            # Disassemble the results.
            sgm.model_free._disassemble_result(param_vector=sgm.xk, func=sgm.fk, iter=sgm.k, fc=sgm.f_count, gc=sgm.g_count, hc=sgm.h_count, warning=sgm.warning, spin=sgm.spin, sim_index=sgm.sim_index, model_type=sgm.model_type, scaling=sgm.scaling, scaling_matrix=sgm.scaling_matrix)


class MF_memo(Memo):
    """The model-free memo class.

    Not quite a momento so a memo.
    """

    def __init__(self, model_free=None, model_type=None, spin=None, sim_index=None, scaling=None, scaling_matrix=None):
        """Initialise the model-free memo class.

        This memo stores the model-free class instance so that the _disassemble_result() method can be called to store the optimisation results.  The other args are those required by this method but not generated through optimisation.

        @keyword model_free:        The model-free class instance.
        @type model_free:           specific_fns.model_free.Model_free instance
        @keyword spin:              The spin data container.  If this argument is supplied, then the spin_id argument will be ignored.
        @type spin:                 SpinContainer instance
        @keyword sim_index:         The optional MC simulation index.
        @type sim_index:            int
        @keyword scaling:           If True, diagonal scaling is enabled.
        @type scaling:              bool
        @keyword scaling_matrix:    The diagonal, square scaling matrix.
        @type scaling_matrix:       numpy diagonal matrix
        """

        # Execute the base class __init__() method.
        super(MF_memo, self).__init__()

        # Store the arguments.
        self.model_free = model_free
        self.model_type = model_type
        self.spin = spin
        self.sim_index = sim_index
        self.scaling = scaling
        self.scaling_matrix = scaling_matrix



class MF_minimise_command(Slave_command):
    """Command class for standard model-free minimisation."""

    def __init__(self):
        """Initialise the base class."""

        # Execute the base class __init__() method.
        super(MF_minimise_command, self).__init__()


    def optimise(self):
        """Model-free optimisation.

        @return:    The optimisation results consisting of the parameter vector, function value, iteration count, function count, gradient count, Hessian count, and warnings.
        @rtype:     tuple of numpy array, float, int, int, int, int, str
        """

        # Minimisation.
        results = generic_minimise(func=self.mf.func, dfunc=self.mf.dfunc, d2func=self.mf.d2func, args=(), x0=self.opt_params.param_vector, min_algor=self.opt_params.min_algor, min_options=self.opt_params.min_options, func_tol=self.opt_params.func_tol, grad_tol=self.opt_params.grad_tol, maxiter=self.opt_params.max_iterations, A=self.opt_params.A, b=self.opt_params.b, full_output=True, print_flag=self.opt_params.verbosity)

        # Return the minfx results unmodified.
        return results


    def run(self, processor, completed):
        """Setup and perform the model-free optimisation."""

        # Run catching all errors.
        try:
            # Initialise the function to minimise.
            self.mf = Mf(init_params=self.opt_params.param_vector, model_type=self.data.model_type, diff_type=self.data.diff_type, diff_params=self.data.diff_params, scaling_matrix=self.data.scaling_matrix, num_spins=self.data.num_spins, equations=self.data.equations, param_types=self.data.param_types, param_values=self.data.param_values, relax_data=self.data.relax_data, errors=self.data.relax_error, bond_length=self.data.r, csa=self.data.csa, num_frq=self.data.num_frq, frq=self.data.frq, num_ri=self.data.num_ri, remap_table=self.data.remap_table, noe_r1_table=self.data.noe_r1_table, ri_labels=self.data.ri_labels, gx=self.data.gx, gh=self.data.gh, h_bar=self.data.h_bar, mu0=self.data.mu0, num_params=self.data.num_params, vectors=self.data.xh_unit_vectors)

            # Print out.
            if self.opt_params.verbosity >= 1 and (self.data.model_type == 'mf' or self.data.model_type == 'local_tm'):
                spin_print(self.data.spin_id, self.opt_params.verbosity)

            # Preform optimisation.
            results = self.optimise()

            # Disassemble the results list.
            param_vector, func, iter, fc, gc, hc, warning = results

            # Get the STDOUT and STDERR messages.
            #FIXME: we need to interleave stdout and stderr
            (stdout, stderr)= processor.get_stdio_capture()
            result_string = stdout.getvalue() + stderr.getvalue()
            stdout.truncate(0)
            stderr.truncate(0)

            processor.return_object(MF_result_command(processor, self.memo_id, param_vector, func, iter, fc, gc, hc, warning, completed=False))
            processor.return_object(Result_string(processor, result_string, completed=completed))

        # An error occurred.
        except Exception, e :
            if isinstance(e, Capturing_exception):
                raise e
            else:
                raise Capturing_exception(rank=processor.rank(), name=processor.get_name())


    def store_data(self, data, opt_params):
        """Store all the data required for model-free optimisation.

        @param data:        The data used to initialise the model-free target function class.
        @type data:         class instance
        @param opt_params:  The parameters and data required for optimisation using minfx.
        @type opt_params:   class instance
        """

        # Store the data.
        self.data = data
        self.opt_params = opt_params



class MF_split_grid_command(MF_minimise_command):
    pass


class MF_grid_command(MF_minimise_command):
    """Command class for the model-free grid search."""

    def __init__(self):
        """Initialise all the data."""

        # Execute the base class __init__() method.
        super(MF_grid_command, self).__init__()


    def optimise(self):
        """Model-free grid search.

        @return:    The optimisation results consisting of the parameter vector, function value, iteration count, function count, gradient count, Hessian count, and warnings.
        @rtype:     tuple of numpy array, float, int, int, int, int, str
        """

        # Grid search.
        results = grid(func=self.mf.func, args=(), num_incs=self.opt_params.inc, lower=self.opt_params.lower, upper=self.opt_params.upper, A=self.opt_params.A, b=self.opt_params.b, verbosity=self.opt_params.verbosity)

        # Unpack the results.
        param_vector, func, iter, warning = results
        fc = iter
        gc = 0.0
        hc = 0.0

        # Return everything.
        return param_vector, func, iter, fc, gc, hc, warning


class MF_result_command(Result_command):
    """Class for processing the model-free results."""

    def __init__(self, processor, memo_id, param_vector, func, iter, fc, gc, hc, warning, completed):
        """Set up the class, placing the minimisation results here."""

        # Execute the base class __init__() method.
        super(MF_result_command, self).__init__(processor=processor, completed=completed)

        # Store the arguments.
        self.memo_id = memo_id
        self.param_vector = param_vector
        self.func = func
        self.iter = iter
        self.fc = fc
        self.gc = gc
        self.hc = hc
        self.warning = warning


    def run(self, processor, memo):
        """Disassemble the model-free optimisation results.

        @param processor:   Unused!
        @type processor:    None
        @param memo:        The model-free memo.
        @type memo:         memo
        """

        # Disassemble the results.
        memo.model_free._disassemble_result(param_vector=self.param_vector, func=self.func, iter=self.iter, fc=self.fc, gc=self.gc, hc=self.hc, warning=self.warning, spin=memo.spin, sim_index=memo.sim_index, model_type=memo.model_type, scaling=memo.scaling, scaling_matrix=memo.scaling_matrix)


class MF_split_grid_memo(MF_memo):
    def __init__(self, model_free, spin, sim_index, model_type, scaling, scaling_matrix, print_prefix, verbosity, full_output, A, b, grid_size):

        # Execute the base class __init__() method.
        super(MF_split_grid_memo, self).__init__(model_free, spin, sim_index, model_type, scaling, scaling_matrix)

        self.full_output = full_output
        self.print_prefix = print_prefix
        self.verbosity = verbosity
        self.sub_memos = []
        self.completed = False

        self.A = A
        self.b = b
        self.grid_size = grid_size
        # aggregated results
        #             min_params, f_min, k
        self.xk = None
        self.fk = 1e300
        self.k = 0
        self.f_count = 0
        self.g_count = 0
        self.h_count = 0
        self.warning = []
        self.first_time = None


    def add_result(self, sub_memo, results):

        # Normal minimisation.
        if self.full_output:
            # Unpack the results.
            param_vector, func, iter, fc, gc, hc, warning = results

            if func < self.fk:
                self.xk = param_vector
                self.fk = func
            self.k += iter
            self.f_count += fc

            self.g_count += gc
            self.h_count += hc
            if warning != None:
                self.warning.append(warning)

        # Grid search.
        #FIXME: TESTME: do we use short results?
        else:
            # Unpack the results.
            param_vector, func, iter, warning = results

            if results[OFFSET_SHORT_FK] < self.short_result[OFFSET_SHORT_FK]:
                self.short_result[OFFSET_SHORT_MIN_PARAMS] = results[OFFSET_SHORT_MIN_PARAMS]
                self.short_result[OFFSET_SHORT_FK] = results[OFFSET_SHORT_FK]
            self.short_result[OFFSET_SHORT_K] += results[OFFSET_SHORT_K]
        self.sub_memos.remove(sub_memo)

        if len(self.sub_memos) < 1:
            self.completed = True
            if len(self.warning) == 0:
                self.warning = None
            else:
                self.warning = ', '.join(self.warning)

        # the order here is important !
        if self.first_time == True:
            self.first_time = False

        if self.first_time == None:
            self.first_time = True


    def add_sub_memo(self, memo):
        self.sub_memos.append(memo)
