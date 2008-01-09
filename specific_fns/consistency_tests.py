###############################################################################
#                                                                             #
# Copyright (C) 2004-2007 Edward d'Auvergne                                   #
# Copyright (C) 2007-2008 Sebastien Morin                                     #
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
from re import search
from string import replace

# relax module imports.
from data import Data as relax_data_store
from base_class import Common_functions
from maths_fns.consistency_tests import Consistency
from relax_errors import RelaxError, RelaxFuncSetupError, RelaxNoPipeError, RelaxNoSequenceError, RelaxNoValueError, RelaxNucleusError, RelaxParamSetError
from physical_constants import N15_CSA, NH_BOND_LENGTH


class Consistency_tests(Common_functions):
    def __init__(self):
        """Class containing functions specific to consistency testing."""


    def calculate(self, run=None, verbosity=1, sim_index=None):
        """Calculation of the consistency functions."""

        # Run argument.
        self.run = run

        # Test if the frequency has been set.
        if not hasattr(relax_data_store, 'ct_frq') or not relax_data_store.ct_frq.has_key(self.run) or type(relax_data_store.ct_frq[self.run]) != float:
            raise RelaxError, "The frequency for the run " + `self.run` + " has not been set up."

        # Test if the nucleus type has been set.
        if not hasattr(relax_data_store, 'gx'):
            raise RelaxNucleusError

        # Test if the sequence data is loaded.
        if not relax_data_store.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run

        # Test if the CSA, bond length, angle Theta and correlation time values have been set.
        for i in xrange(len(relax_data_store.res[self.run])):
            # Skip unselected residues.
            if not relax_data_store.res[self.run][i].select:
                continue

            # CSA value.
            if not hasattr(relax_data_store.res[self.run][i], 'csa') or relax_data_store.res[self.run][i].csa == None:
                raise RelaxNoValueError, "CSA"

            # Bond length value.
            if not hasattr(relax_data_store.res[self.run][i], 'r') or relax_data_store.res[self.run][i].r == None:
                raise RelaxNoValueError, "bond length"

            # Angle Theta
            if not hasattr(self.relax.data.res[self.run][i], 'orientation') or self.relax.data.res[self.run][i].orientation == None:
                raise RelaxNoValueError, "angle Theta"

            # Correlation time
            if not hasattr(self.relax.data.res[self.run][i], 'tc') or self.relax.data.res[self.run][i].tc == None:
                raise RelaxNoValueError, "correlation time"

        # Frequency index.
        if relax_data_store.ct_frq[self.run] not in relax_data_store.frq[self.run]:
            raise RelaxError, "No relaxation data corresponding to the frequency " + `relax_data_store.ct_frq[self.run]` + " has been loaded."

        # Consistency testing.
        for i in xrange(len(relax_data_store.res[self.run])):
            # Reassign data structure.
            data = relax_data_store.res[self.run][i]

            # Skip unselected residues.
            if not data.select:
                continue

            # Residue specific frequency index.
            frq_index = None
            for j in xrange(data.num_frq):
                if data.frq[j] == relax_data_store.ct_frq[self.run]:
                    frq_index = j
            if frq_index == None:
                continue

            # Set the r1, r2, and NOE to None.
            r1 = None
            r2 = None
            noe = None

            # Get the R1, R2, and NOE values corresponding to the set frequency.
            for j in xrange(data.num_ri):
                # R1.
                if data.remap_table[j] == frq_index and data.ri_labels[j] == 'R1':
                    if sim_index == None:
                        r1 = data.relax_data[j]
                    else:
                        r1 = data.relax_sim_data[sim_index][j]

                # R2.
                if data.remap_table[j] == frq_index and data.ri_labels[j] == 'R2':
                    if sim_index == None:
                        r2 = data.relax_data[j]
                    else:
                        r2 = data.relax_sim_data[sim_index][j]

                # NOE.
                if data.remap_table[j] == frq_index and data.ri_labels[j] == 'NOE':
                    if sim_index == None:
                        noe = data.relax_data[j]
                    else:
                        noe = data.relax_sim_data[sim_index][j]

            # Skip the residue if not all of the three value exist.
            if r1 == None or r2 == None or noe == None:
                continue

            # Initialise the function to calculate.
            self.ct = Consistency(frq=relax_data_store.ct_frq[self.run], gx=relax_data_store.gx, gh=relax_data_store.gh, mu0=relax_data_store.mu0, h_bar=relax_data_store.h_bar)

            # Calculate the spectral density values.
            j0, f_eta, f_r2 = self.ct.func(orientation=data.orientation, tc=data.tc, r=data.r, csa=data.csa, r1=r1, r2=r2, noe=noe)

            # Reduced spectral density values.
            if sim_index == None:
                data.j0 = j0
                data.f_eta = f_eta
                data.f_r2 = f_r2

            # Monte Carlo simulated reduced spectral density values.
            else:
                # Initialise the simulation data structures.
                self.data_init(data, sim=1)
                if data.j0_sim == None:
                    data.j0_sim = []
                    data.f_eta_sim = []
                    data.f_r2_sim = []

                # Reduced spectral density values.
                data.j0_sim.append(j0)
                data.f_eta_sim.append(f_eta)
                data.f_r2_sim.append(f_r2)


    def data_init(self, data, sim=0):
        """Function for initialising the data structures."""

        # Get the data names.
        data_names = self.data_names()

        # Loop over the data structure names.
        for name in data_names:
            # Simulation data structures.
            if sim:
                # Add '_sim' to the names.
                name = name + '_sim'

            # If the name is not in 'data', add it.
            if not hasattr(data, name):
                # Set the attribute.
                setattr(data, name, None)


    def data_names(self):
        """Function for returning a list of names of data structures.

        Description
        ~~~~~~~~~~~

        r:  Bond length.

        csa:  CSA value.

        nucleus:  The heteronucleus type.

        orientation:  Angle between the 15N-1H vector and the principal axis of the 15N chemical
                      shift tensor.

        tc:  Correlation time.

        j0:  Spectral density value at 0 MHz.

        f_eta:  Eta-test (from Fushman D. et al. (1998) JACS, 120: 10947-10952).

        f_r2:  R2-test (from Fushman D. et al. (1998) JACS, 120: 10947-10952).

        """

        # Initialise.
        names = []

        # Values.
        names.append('r')
        names.append('csa')
        names.append('nucleus')
        names.append('orientation')
        names.append('tc')

        # Spectral density values.
        names.append('j0')
        names.append('f_eta')
        names.append('f_r2')

        return names


    def default_value(self, param):
        """
        Consistency testing default values
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
        These default values are found in the file 'physical_constants.py'.

        ________________________________________________________________________________________
        |                                       |               |                              |
        | Data type                             | Object name   | Value                        |
        |_______________________________________|_______________|______________________________|
        |                                       |               |                              |
        | Bond length                           | 'r'           | 1.02 * 1e-10                 |
        |                                       |               |                              |
        | CSA                                   | 'csa'         | -172 * 1e-6                  |
        |                                       |               |                              |
        | Heteronucleus type                    | 'nucleus'     | 'N'                          |
        |                                       |               |                              |
        | Angle Theta                           | 'orientation' | 15.7                         |
        |                                       |               |                              |
        | Correlation time                      | 'tc'          | 13 * 1e-9                    |
        |_______________________________________|_______________|______________________________|

        """
        __docformat__ = "plaintext"

        # Bond length.
        if param == 'r':
            return NH_BOND_LENGTH

        # CSA.
        elif param == 'csa':
            return N15_CSA

        # Heteronucleus type.
        elif param == 'nucleus':
            return 'N'

        # Angle Theta (default value)
        elif param == 'orientation':
            return 15.7

        # Correlation time (default value)
        elif param == 'tc':
            return 13 * 1e-9


    def num_instances(self, run=None):
        """Function for returning the number of instances."""

        # Arguments.
        self.run = run

        # Test if sequence data is loaded.
        if not relax_data_store.res.has_key(self.run):
            return 0

        # Return the number of residues.
        return len(relax_data_store.res[self.run])


    def overfit_deselect(self, run):
        """Function for deselecting residues without sufficient data to support calculation"""

        # Test the sequence data exists:
        if not relax_data_store.res.has_key(run):
            raise RelaxNoSequenceError, run

        # Loop over residue data:
        for residue in relax_data_store.res[run]:

            # Check for sufficient data
            if not hasattr(residue, 'relax_data'):
                residue.select = 0
                continue

            # Require 3 or more data points
            if len(residue.relax_data) < 3:
                residue.select = 0
                continue


    def return_conversion_factor(self, stat_type):
        """Dummy function for returning 1.0. This function is essential when writing grace files."""

        return 1.0


    def return_data_name(self, name):
        """
        Consistency testing data type string matching patterns
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        ____________________________________________________________________________________________
        |                       |               |                                                  |
        | Data type             | Object name   | Patterns                                         |
        |_______________________|_______________|__________________________________________________|
        |                       |               |                                                  |
        | J(0)                  | 'j0'          | '^[Jj]0$' or '[Jj]\(0\)'                         |
        |                       |               |                                                  |
        | F_eta                 | 'f_eta'       | '^[Ff]_[Ee][Tt][Aa]$'                            |
        |                       |               |                                                  |
        | F_R2                  | 'f_r2'        | '^[Ff]_[Rr]2$'                                   |
        |                       |               |                                                  |
        | Bond length           | 'r'           | '^r$' or '[Bb]ond[ -_][Ll]ength'                 |
        |                       |               |                                                  |
        | CSA                   | 'csa'         | '^[Cc][Ss][Aa]$'                                 |
        |                       |               |                                                  |
        | Heteronucleus type    | 'nucleus'     | '^[Nn]ucleus$'                                   |
        |                       |               |                                                  |
        | Angle Theta           | 'orientation' | '^[Oo][Rr][Ii][Ee][Nn][Tt][Aa][Tt][Ii][Oo][Nn]$' |
        |                       |               |                                                  |
        | Correlation time      | 'tc'          | '^[Tt]c$'                                        |
        |_______________________|_______________|__________________________________________________|
        """
        __docformat__ = "plaintext"

        # J(0).
        if search('^[Jj]0$', name) or search('[Jj]\(0\)', name):
            return 'j0'

        # J(wX).
        if search('^[Jj]w[Xx]$', name) or search('[Jj]\(w[Xx]\)', name):
            return 'jwx'

        # J(wH).
        if search('^[Jj]w[Hh]$', name) or search('[Jj]\(w[Hh]\)', name):
            return 'jwh'

        # Bond length.
        if search('^r$', name) or search('[Bb]ond[ -_][Ll]ength', name):
            return 'r'

        # CSA.
        if search('^[Cc][Ss][Aa]$', name):
            return 'csa'

        # Heteronucleus type.
        if search('^[Nn]ucleus$', name):
            return 'nucleus'

        # Angle Theta
        if search('^[Oo][Rr][Ii][Ee][Nn][Tt][Aa][Tt][Ii][Oo][Nn]$', name):
            return 'orientation'

        # Correlation time
        if search('^[Tt]c$', name):
            return 'tc'


    def return_grace_string(self, data_type):
        """Function for returning the Grace string representing the data type for axis labelling."""

        # Get the object name.
        object_name = self.return_data_name(data_type)

        # J(0).
        if object_name == 'j0':
            return '\\qJ(0)\\Q'

        # J(wX).
        elif object_name == 'jwx':
            return '\\qJ(\\xw\\f{}\\sX\\N)\\Q'

        # J(wH).
        elif object_name == 'jwh':
            return '\\qJ(\\xw\\f{}\\sH\\N)\\Q'

        # Bond length.
        elif object_name == 'r':
            return 'Bond length'

        # CSA.
        elif object_name == 'csa':
            return '\\qCSA\\Q'

        # Angle Theta
        elif object_name == 'orientation':
            return '\\q\\xq\\Q'

        # Correlation time
        elif object_name == 'tc':
            return '\\q\\xt\\f{}c\\Q'


    def return_units(self, data_type):
        """Function for returning a string representing the parameters units.

        For example, the internal representation of te is in seconds, whereas the external
        representation is in picoseconds, therefore this function will return the string
        'picoseconds' for te.
        """

        # Get the object name.
        object_name = self.return_data_name(data_type)

        # Bond length (Angstrom).
        if object_name == 'r':
            return 'Angstrom'

        # CSA (ppm).
        elif object_name == 'csa':
            return 'ppm'

        # Angle Theta
        elif object_name == 'orientation':
            return 'degrees'

        # Correlation time
        elif object_name == 'tc':
            return 'ns'


    def set_doc(self, value=None, error=None, param=None, spin=None):
        """
        Consistency testing set details
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        In consistency testing, only four values can be set, the bond length, CSA, angle
        Theta ('orientation') and correlation time values. These must be set prior to the
        calculation of consistency functions.

        """
        __docformat__ = "plaintext"

    def set_frq(self, run=None, frq=None):
        """Function for selecting which relaxation data to use in the consistency tests."""

        # Run argument.
        self.run = run

        # Test if the run exists.
        if not self.run in relax_data_store.run_names:
            raise RelaxNoPipeError, self.run

        # Test if the run type is set to 'ct'.
        function_type = relax_data_store.run_types[relax_data_store.run_names.index(self.run)]
        if function_type != 'ct':
            raise RelaxFuncSetupError, self.relax.specific_setup.get_string(function_type)

        # Test if the frequency has been set.
        if hasattr(relax_data_store, 'ct_frq') and relax_data_store.ct_frq.has_key(self.run):
            raise RelaxError, "The frequency for the run " + `self.run` + " has already been set."

        # Create the data structure if it doesn't exist.
        if not hasattr(relax_data_store, 'ct_frq'):
            relax_data_store.ct_frq = {}

        # Set the frequency.
        relax_data_store.ct_frq[self.run] = frq


    def set_error(self, run, instance, index, error):
        """Function for setting parameter errors."""

        # Arguments.
        self.run = run

        # Return J(0) sim data.
        if index == 0:
            relax_data_store.res[self.run][instance].j0_err = error

        # Return F_eta sim data.
        if index == 1:
            relax_data_store.res[self.run][instance].f_eta_err = error

        # Return F_R2 sim data.
        if index == 2:
            relax_data_store.res[self.run][instance].f_r2_err = error


    def sim_return_param(self, run, instance, index):
        """Function for returning the array of simulation parameter values."""

        # Arguments.
        self.run = run

        # Skip unselected residues.
        if not relax_data_store.res[self.run][instance].select:
                return

        # Return J(0) sim data.
        if index == 0:
            return relax_data_store.res[self.run][instance].j0_sim

        # Return F_eta sim data.
        if index == 1:
            return relax_data_store.res[self.run][instance].f_eta_sim

        # Return F_R2 sim data.
        if index == 2:
            return relax_data_store.res[self.run][instance].f_r2_sim


    def sim_return_selected(self, run, instance):
        """Function for returning the array of selected simulation flags."""

        # Arguments.
        self.run = run

        # Multiple instances.
        return relax_data_store.res[self.run][instance].select_sim


    def set_selected_sim(self, run, instance, select_sim):
        """Function for returning the array of selected simulation flags."""

        # Arguments.
        self.run = run

        # Multiple instances.
        relax_data_store.res[self.run][instance].select_sim = select_sim


    def sim_pack_data(self, run, i, sim_data):
        """Function for packing Monte Carlo simulation data."""

        # Test if the simulation data already exists.
        if hasattr(relax_data_store.res[run][i], 'relax_sim_data'):
            raise RelaxError, "Monte Carlo simulation data already exists."

        # Create the data structure.
        relax_data_store.res[run][i].relax_sim_data = sim_data


    def write_columnar_line(self, file=None, num=None, name=None, select=None, data_set=None, nucleus=None, wH=None, j0=None, f_eta=None, f_r2=None, r=None, csa=None, orientation=None, tc=None, ri_labels=None, remap_table=None, frq_labels=None, frq=None, ri=None, ri_error=None):
        """Function for printing a single line of the columnar formatted results."""

        # Residue number and name.
        file.write("%-4s %-5s " % (num, name))

        # Selected flag and data set.
        file.write("%-9s %-9s " % (select, data_set))

        # Nucleus.
        file.write("%-7s " % nucleus)

        # Proton frequency.
        file.write("%-25s " % wH)

        # Parameters.
        file.write("%-25s " % j0)
        file.write("%-25s " % f_eta)
        file.write("%-25s " % f_r2)
        file.write("%-25s " % r)
        file.write("%-25s " % csa)
        file.write("%-25s " % orientation)
        file.write("%-25s " % tc)

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

        # Test if the run exists.
        if not self.run in relax_data_store.run_names:
            raise RelaxNoPipeError, self.run

        # Test if sequence data is loaded.
        if not relax_data_store.res.has_key(self.run):
            raise RelaxNoSequenceError, self.run


        # Header.
        #########

        # Relaxation data and errors.
        ri = []
        ri_error = []
        if hasattr(relax_data_store, 'num_ri'):
            for i in xrange(relax_data_store.num_ri[self.run]):
                ri.append('Ri_(' + relax_data_store.ri_labels[self.run][i] + "_" + relax_data_store.frq_labels[self.run][relax_data_store.remap_table[self.run][i]] + ")")
                ri_error.append('Ri_error_(' + relax_data_store.ri_labels[self.run][i] + "_" + relax_data_store.frq_labels[self.run][relax_data_store.remap_table[self.run][i]] + ")")

        # Write the header line.
        self.write_columnar_line(file=file, num='Num', name='Name', select='Selected', data_set='Data_set', nucleus='Nucleus', wH='Proton_frq_(MHz)', j0='J(0)', f_eta='F_eta', f_r2='F_R2', r='Bond_length_(A)', csa='CSA_(ppm)', orientation='Angle_Theta_(degrees)', tc='Correlation_time_(ns)', ri_labels='Ri_labels', remap_table='Remap_table', frq_labels='Frq_labels', frq='Frequencies', ri=ri, ri_error=ri_error)


        # Values.
        #########

        # Nucleus.
        nucleus = self.relax.generic.nuclei.find_nucleus()

        # The proton frequency in MHz.
        wH = relax_data_store.ct_frq[self.run] / 1e6

        # Relaxation data setup.
        try:
            ri_labels = replace(`relax_data_store.ri_labels[self.run]`, ' ', '')
            remap_table = replace(`relax_data_store.remap_table[self.run]`, ' ', '')
            frq_labels = replace(`relax_data_store.frq_labels[self.run]`, ' ', '')
            frq = replace(`relax_data_store.frq[self.run]`, ' ', '')
        except AttributeError:
            ri_labels = `None`
            remap_table = `None`
            frq_labels = `None`
            frq = `None`

        # Loop over the sequence.
        for i in xrange(len(relax_data_store.res[self.run])):
            # Reassign data structure.
            data = relax_data_store.res[self.run][i]

            # J(0).
            j0 = None
            if hasattr(data, 'j0'):
                j0 = data.j0

            # F_eta.
            f_eta = None
            if hasattr(data, 'f_eta'):
                f_eta = data.f_eta

            # F_R2.
            f_r2 = None
            if hasattr(data, 'f_r2'):
                f_r2 = data.f_r2

            # Bond length.
            r = None
            if hasattr(data, 'r') and data.r != None:
                r = data.r / 1e-10

            # CSA.
            csa = None
            if hasattr(data, 'csa') and data.csa != None:
                csa = data.csa / 1e-6

            # Relaxation data and errors.
            ri = []
            ri_error = []
            if hasattr(relax_data_store, 'num_ri'):
                for i in xrange(relax_data_store.num_ri[self.run]):
                    try:
                        # Find the residue specific data corresponding to i.
                        index = None
                        for j in xrange(data.num_ri):
                            if data.ri_labels[j] == relax_data_store.ri_labels[self.run][i] and data.frq_labels[data.remap_table[j]] == relax_data_store.frq_labels[self.run][relax_data_store.remap_table[self.run][i]]:
                                index = j

                        # Data exists for this data type.
                        ri.append(`data.relax_data[index]`)
                        ri_error.append(`data.relax_error[index]`)

                    # No data exists for this data type.
                    except:
                        ri.append(None)
                        ri_error.append(None)

            # Write the line.
            self.write_columnar_line(file=file, num=data.num, name=data.name, select=data.select, data_set='value', nucleus=nucleus, wH=`wH`, j0=`j0`, f_eta=`f_eta`, f_r2=`f_r2`, r=`r`, csa=`csa`, orientation=`orientation`, tc=`tc`, ri_labels=ri_labels, remap_table=remap_table, frq_labels=frq_labels, frq=frq, ri=ri, ri_error=ri_error)


        # Errors.
        #########

        # Skip this section and the next if no simulations have been setup.
        if not hasattr(relax_data_store, 'sim_state'):
            return
        elif relax_data_store.sim_state[self.run] == 0:
            return

        # Loop over the sequence.
        for i in xrange(len(relax_data_store.res[self.run])):
            # Reassign data structure.
            data = relax_data_store.res[self.run][i]

            # J(0).
            j0 = None
            if hasattr(data, 'j0_err'):
                j0 = data.j0_err

            # F_eta.
            f_eta = None
            if hasattr(data, 'f_eta_err'):
                f_eta = data.f_eta_err

            # F_R2.
            f_r2 = None
            if hasattr(data, 'f_r2_err'):
                f_r2 = data.f_r2_err

            # Bond length.
            r = None
            if hasattr(data, 'r_err') and data.r_err != None:
                r = data.r_err / 1e-10

            # CSA.
            csa = None
            if hasattr(data, 'csa_err') and data.csa_err != None:
                csa = data.csa_err / 1e-6

            # Angle Theta.
            orientation = None
            if hasattr(data, 'orientation_err') and data.orientation_err != None:
                orientation = data.orientation_err

            # Correlation time.
            tc = None
            if hasattr(data, 'tc_err') and data.tc_err != None:
                tc = data.tc_err / 1e-6

            # Relaxation data and errors.
            ri = []
            ri_error = []
            for i in xrange(relax_data_store.num_ri[self.run]):
                ri.append(None)
                ri_error.append(None)

            # Write the line.
            self.write_columnar_line(file=file, num=data.num, name=data.name, select=data.select, data_set='error', nucleus=nucleus, wH=`wH`, j0=`j0`, f_eta=`f_eta`, f_r2=`f_r2`, r=`r`, csa=`csa`, orientation=`orientation`, tc=`tc`, ri_labels=ri_labels, remap_table=remap_table, frq_labels=frq_labels, frq=frq, ri=ri, ri_error=ri_error)


        # Simulation values.
        ####################

        # Loop over the simulations.
        for i in xrange(relax_data_store.sim_number[self.run]):
            # Loop over the sequence.
            for j in xrange(len(relax_data_store.res[self.run])):
                # Reassign data structure.
                data = relax_data_store.res[self.run][j]

                # J(0).
                j0 = None
                if hasattr(data, 'j0_sim'):
                    j0 = data.j0_sim[i]

                # F_eta.
                f_eta = None
                if hasattr(data, 'f_eta_sim'):
                    f_eta = data.f_eta_sim[i]

                # F_R2.
                f_r2 = None
                if hasattr(data, 'f_r2_sim'):
                    f_r2 = data.f_r2_sim[i]

                # Bond length.
                r = None
                if hasattr(data, 'r_sim') and data.r_sim != None and data.r_sim[i] != None:
                    r = data.r_sim[i] / 1e-10

                # CSA.
                csa = None
                if hasattr(data, 'csa_sim') and data.csa_sim != None and data.csa_sim[i] != None:
                    csa = data.csa_sim[i] / 1e-6

                # Angle Theta.
                orientation = None
                if hasattr(data, 'orientation_sim') and data.orientation_sim != None and data.orientation_sim[i] != None:
                    orientation = data.orientation_sim[i]

                # Correlation time.
                tc = None
                if hasattr(data, 'tc_sim') and data.tc_sim != None and data.tc_sim[i] != None:
                    tc = data.tc_sim[i] / 1e-6

                # Relaxation data and errors.
                ri = []
                ri_error = []
                if hasattr(self.relax.data, 'num_ri'):
                    for k in xrange(relax_data_store.num_ri[self.run]):
                        try:
                            # Find the residue specific data corresponding to k.
                            index = None
                            for l in xrange(data.num_ri):
                                if data.ri_labels[l] == relax_data_store.ri_labels[self.run][k] and data.frq_labels[data.remap_table[l]] == relax_data_store.frq_labels[self.run][relax_data_store.remap_table[self.run][k]]:
                                    index = l

                            # Data exists for this data type.
                            ri.append(`data.relax_sim_data[i][index]`)
                            ri_error.append(`data.relax_error[index]`)

                        # No data exists for this data type.
                        except:
                            ri.append(None)
                            ri_error.append(None)

                # Write the line.
                self.write_columnar_line(file=file, num=data.num, name=data.name, select=data.select, data_set='sim_'+`i`, nucleus=nucleus, wH=`wH`, j0=`j0`, f_eta=`f_eta`, f_r2=`f_r2`, r=`r`, csa=`csa`, orientation=`orientation`, tc=`tc`, ri_labels=ri_labels, remap_table=remap_table, frq_labels=frq_labels, frq=frq, ri=ri, ri_error=ri_error)
