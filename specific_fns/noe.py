###############################################################################
#                                                                             #
# Copyright (C) 2004-2005,2007-2009 Edward d'Auvergne                         #
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
from math import sqrt
from re import match
from warnings import warn

# relax module imports.
from base_class import Common_functions
from generic_fns import pipes
from generic_fns.mol_res_spin import exists_mol_res_spin_data, spin_loop
from relax_errors import RelaxArgNotInListError, RelaxError, RelaxNoSequenceError
from relax_warnings import RelaxDeselectWarning


class Noe(Common_functions):
    """Class containing functions for relaxation data."""

    def assign_function(self, spin=None, intensity=None, spectrum_type=None):
        """Place the peak intensity data into the spin container.

        The intensity data can be either that of the reference or saturated spectrum.

        @keyword spin:          The spin container.
        @type spin:             SpinContainer instance
        @keyword intensity:     The intensity value.
        @type intensity:        float
        @keyword spectrum_type: The type of spectrum, one of 'ref' or 'sat'.
        @type spectrum_type:    str
        """

        # Add the data.
        if spectrum_type == 'ref':
            spin.ref = intensity
        elif spectrum_type == 'sat':
            spin.sat = intensity
        else:
            raise RelaxError("The spectrum type '%s' is unknown." % spectrum_type)


    def calculate(self, verbosity=1):
        """Calculate the NOE and its error.

        The error for each peak is calculated using the formula::
                          ___________________________________________
                       \/ {sd(sat)*I(unsat)}^2 + {sd(unsat)*I(sat)}^2
            sd(NOE) = -----------------------------------------------
                                          I(unsat)^2

        @keyword verbosity: The amount of information to print.  The higher the value, the greater the verbosity.
        @type verbosity:    int
        """

        # Test if the current pipe exists.
        pipes.test()

        # The spectrum types have not been set.
        if not hasattr(cdp, 'spectrum_type'):
            raise RelaxError("The spectrum types have not been set.")

        # Test if the 2 spectra types 'ref' and 'sat' exist.
        if not 'ref' in cdp.spectrum_type or not 'sat' in cdp.spectrum_type:
            raise RelaxError("The reference and saturated NOE spectra have not been loaded.")

        # Loop over the spins.
        for spin in spin_loop():
            # Skip deselected spins.
            if not spin.select:
                continue

            # Average intensities (if required).
            sat = 0.0
            sat_err = 0.0
            ref = 0.0
            ref_err = 0.0
            for i in xrange(len(cdp.spectrum_type)):
                # Sat spectra.
                if cdp.spectrum_type[i] == 'sat':
                    sat = sat + spin.intensities[i]
                    sat_err = sat_err + spin.intensity_err[i]

                # Ref spectra.
                if cdp.spectrum_type[i] == 'ref':
                    ref = ref + spin.intensities[i]
                    ref_err = ref_err + spin.intensity_err[i]

            # Calculate the NOE.
            spin.noe = sat / ref

            # Calculate the error.
            spin.noe_err = sqrt((sat_err * ref)**2 + (ref_err * sat)**2) / ref**2


    def overfit_deselect(self):
        """Deselect spins which have insufficient data to support calculation"""

        # Test the sequence data exists.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Loop over spin data.
        for spin, spin_id in spin_loop(return_id=True):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Check for sufficient data.
            if not hasattr(spin, 'intensities') or not len(spin.intensities) == 2:
                warn(RelaxDeselectWarning(spin_id, 'insufficient data'))
                spin.select = False

            # Check for sufficient errors.
            elif not hasattr(spin, 'intensity_err') or not len(spin.intensity_err) == 2:
                warn(RelaxDeselectWarning(spin_id, 'missing errors'))
                spin.select = False


    def read(self, file=None, dir=None, spectrum_type=None, format=None, heteronuc=None, proton=None, int_col=None):
        """Read in the peak intensity data.

        @keyword file:          The name of the file containing the peak intensities.
        @type file:             str
        @keyword dir:           The directory where the file is located.
        @type dir:              str
        @keyword spectrum_type: The type of spectrum, one of 'ref' or 'sat'.
        @type spectrum_type:    str
        @keyword format:        The type of file containing peak intensities.  This can currently be
                                one of 'sparky', 'xeasy' or 'nmrview'.
        @type format:           str
        @keyword heteronuc:     The name of the heteronucleus as specified in the peak intensity
                                file.
        @type heteronuc:        str
        @keyword proton:        The name of the proton as specified in the peak intensity file.
        @type proton:           str
        @keyword int_col:       The column containing the peak intensity data (for a non-standard
                                formatted file).
        @type int_col:          int
        """

        # Spectrum type argument.
        spect_type_list = ['ref', 'sat']
        if spectrum_type not in spect_type_list:
            raise RelaxArgNotInListError('spectrum type', spectrum_type, spect_type_list)
        if spectrum_type == 'ref':
            print("Reference spectrum.")
        if spectrum_type == 'sat':
            print("Saturated spectrum.")

        # Generic intensity function.
        intensity.read(file=file, dir=dir, format=format, heteronuc=heteronuc, proton=proton, int_col=int_col, assign_func=self.assign_function, spectrum_type=spectrum_type)


    return_data_name_doc = """
        NOE calculation data type string matching patterns
        ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

        ____________________________________________________________________________________________
        |                        |              |                                                  |
        | Data type              | Object name  | Patterns                                         |
        |________________________|______________|__________________________________________________|
        |                        |              |                                                  |
        | Reference intensity    | 'ref'        | '^[Rr]ef$' or '[Rr]ef[ -_][Ii]nt'                |
        |                        |              |                                                  |
        | Saturated intensity    | 'sat'        | '^[Ss]at$' or '[Ss]at[ -_][Ii]nt'                |
        |                        |              |                                                  |
        | NOE                    | 'noe'        | '^[Nn][Oo][Ee]$'                                 |
        |________________________|______________|__________________________________________________|

        """

    def return_data_name(self, name):
        """Return a unique identifying string for the steady-state NOE parameter.

        @param name:    The steady-state NOE parameter.
        @type name:     str
        @return:        The unique parameter identifying string.
        @rtype:         str
        """

        # Reference intensity.
        if match('^[Rr]ef$', name) or match('[Rr]ef[ -_][Ii]nt', name):
            return 'ref'

        # Saturated intensity.
        if match('^[Ss]at$', name) or match('[Ss]at[ -_][Ii]nt', name):
            return 'sat'

        # NOE.
        if match('^[Nn][Oo][Ee]$', name):
            return 'noe'


    def return_grace_string(self, data_type):
        """Function for returning the Grace string representing the data type for axis labelling."""

        # Get the object name.
        object_name = self.return_data_name(data_type)

        # Reference intensity.
        if object_name == 'ref':
            return 'Reference intensity'

        # Saturated intensity.
        if object_name == 'sat':
            return 'Saturated intensity'

        # NOE.
        if object_name == 'noe':
            return '\\qNOE\\Q'

        # Return the data type as the Grace string.
        return data_type


    def return_units(self, stat_type, spin_id=None):
        """Dummy function which returns None as the stats have no units.

        @param stat_type:   Not used.
        @type stat_type:    None
        @keyword spin_id:   Not used.
        @type spin_id:      None
        @return:            Nothing.
        @rtype:             None
        """

        return None


    def set_error(self, error=0.0, spectrum_id=None, spin_id=None):
        """Set the peak intensity errors.

        @param error:           The peak intensity error value defined as the RMSD of the base plane
                                noise.
        @type error:            float
        @keyword spectrum_id:   The id of spectrum, one of 'ref' or 'sat'.
        @type spectrum_id:      str
        @param spin_id:         The spin identification string.
        @type spin_id:          str
        """

        # Test if the current pipe exists
        pipes.test()

        # Test if the sequence data is loaded.
        if not exists_mol_res_spin_data():
            raise RelaxNoSequenceError

        # Loop over the spins.
        for spin in spin_loop(spin_id):
            # Skip deselected spins.
            if not spin.select:
                continue

            # Set the error.
            if spectrum_id == 'ref':
                spin.ref_err = float(error)
            elif spectrum_id == 'sat':
                spin.sat_err = float(error)


    def spectrum_type(self, spectrum_type=None, spectrum_id=None):
        """Set the spectrum type corresponding to the spectrum_id.

        @keyword spectrum_type: The type of NOE spectrum, one of 'ref' or 'sat'.
        @type spectrum_type:    str
        @keyword spectrum_id:   The spectrum id string.
        @type spectrum_id:      str
        """

        # Test if the current pipe exists
        pipes.test()

        # Test the spectrum id string.
        if spectrum_id not in cdp.spectrum_ids:
            raise RelaxError("The peak intensities corresponding to the spectrum id '%s' does not exist." % spectrum_id)

        # The spectrum id index.
        spect_index = cdp.spectrum_ids.index(spectrum_id)

        # Initialise or update the spectrum_type data structure as necessary.
        if not hasattr(cdp, 'spectrum_type'):
            cdp.spectrum_type = [None] * len(cdp.spectrum_ids)
        elif len(cdp.spectrum_type) < len(cdp.spectrum_ids):
            cdp.spectrum_type.append([None] * (len(cdp.spectrum_ids) - len(cdp.spectrum_type)))

        # Set the error.
        cdp.spectrum_type[spect_index] = spectrum_type
