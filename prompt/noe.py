###############################################################################
#                                                                             #
# Copyright (C) 2004-2008 Edward d'Auvergne                                   #
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
"""Module containing the 'noe' user function class."""
__docformat__ = 'plaintext'

# Python module imports.
import sys

# relax module imports.
import help
from generic_fns import noesy
from relax_errors import RelaxNoneIntError, RelaxNoneStrError, RelaxStrError
from specific_fns.setup import noe_obj


class Noe:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for handling steady-state NOE and NOESY data."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def read_restraints(self, file=None, dir=None, proton1_col=None, proton2_col=None, lower_col=None, upper_col=None, sep=None):
        """Read NOESY or ROESY restraints from a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        file:  The name of the file containing the relaxation data.

        dir:  The directory where the file is located.

        proton1_col:  The column containing the first proton of the NOE or ROE cross peak.

        proton2_col:  The column containing the second proton of the NOE or ROE cross peak.

        lower_col:  The column containing the lower NOE bound.

        upper_col:  The column containing the upper NOE bound.

        sep:  The column separator (the default is white space).


        Description
        ~~~~~~~~~~~

        This function can automatically determine the format of the file, for example Xplor
        formatted restraint files.  A generically formatted file is also supported if it contains
        minimally four columns with the two proton names and the upper and lower bounds, as
        specified by the *_col arguments.  The proton names need to be in the spin identification
        string format.


        Examples
        ~~~~~~~~

        To read the Xplor formatted restraint file 'NOE.xpl', type one of:

        relax> noe.read_restraints('NOE.xpl')
        relax> noe.read_restraints(file='NOE.xpl')


        To read the generic formatted file 'noes', type one of:

        relax> noe.read_restraints(file='NOE.xpl', proton1_col=0, proton2_col=1, lower_col=2, upper_col=3)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "noe.read_restraints("
            text = text + "file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", proton1_col=" + repr(proton1_col)
            text = text + ", proton2_col=" + repr(proton2_col)
            text = text + ", lower_col=" + repr(lower_col)
            text = text + ", upper_col=" + repr(upper_col)
            text = text + ", sep=" + repr(sep) + ")"
            print text

        # The file name.
        if type(file) != str:
            raise RelaxStrError, ('file', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # First proton column.
        if proton1_col != None and type(proton1_col) != int:
            raise RelaxNoneIntError, ('first proton column', proton1_col)

        # Second proton column.
        if proton2_col != None and type(proton2_col) != int:
            raise RelaxNoneIntError, ('second proton column', proton2_col)

        # Lower bound column.
        if lower_col != None and type(lower_col) != int:
            raise RelaxNoneIntError, ('lower bound column', lower_col)

        # Upper bound column.
        if upper_col != None and type(upper_col) != int:
            raise RelaxNoneIntError, ('upper bound column', upper_col)

        # Column separator.
        if sep != None and type(sep) != str:
            raise RelaxNoneStrError, ('column separator', sep)

        # Execute the functional code.
        noesy.read_restraints(file=file, dir=dir, proton1_col=proton1_col, proton2_col=proton2_col, lower_col=lower_col, upper_col=upper_col, sep=sep)


    def spectrum_type(self, spectrum_type=None, spectrum_id=None):
        """Set the steady-state NOE spectrum type for pre-loaded peak intensities.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        spectrum_type:  The type of steady-state NOE spectrum, one of 'ref' or 'sat'.

        spectrum_id:  The spectrum identification string.


        Description
        ~~~~~~~~~~~

        The spectrum_type argument can have the following values:
            'ref':  The steady-state NOE reference spectrum.
            'sat':  The steady-state NOE spectrum with proton saturation turned on.

        Peak intensities should be loaded before calling this user function via the
        'spectrum.read_intensities()' user function.  The intensity values will then be associated
        with a spectrum identifier which can be used here.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "noe.spectrum_type("
            text = text + "spectrum_type=" + repr(spectrum_type)
            text = text + ", spectrum_id=" + repr(spectrum_id) + ")"
            print text

        # The spectrum type.
        if type(spectrum_type) != str:
            raise RelaxStrError, ('spectrum type', spectrum_type)

        # The spectrum identification string.
        if type(spectrum_id) != str:
            raise RelaxStrError, ('spectrum identification string', spectrum_id)

        # Execute the functional code.
        noe_obj.spectrum_type(spectrum_type=spectrum_type, spectrum_id=spectrum_id)
