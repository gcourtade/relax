###############################################################################
#                                                                             #
# Copyright (C) 2004 Edward d'Auvergne                                        #
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

import sys

import help


class Relax_fit:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for relaxation curve fitting."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def read(self, run=None, file=None, dir=None, relax_time=0.0, fit_type='exp', format='sparky', heteronuc='N', proton='HN', int_col=None):
        """Function for reading peak intensities from a file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        file:  The name of the file containing the sequence data.

        dir:  The directory where the file is located.

        relax_time:  The time, in seconds, of the relaxation period.

        fit_type:  The type of relaxation curve to fit.

        format:  The type of file containing peak intensities.

        heteronuc:  The name of the heteronucleus as specified in the peak intensity file.

        proton:  The name of the proton as specified in the peak intensity file.

        int_col:  The column containing the peak intensity data (for a non-standard formatted file).


        Description
        ~~~~~~~~~~~

        The peak intensity can either be from peak heights or peak volumes.


        The supported relaxation experiments include the default two parameter exponential fit,
        selected by setting the 'fit_type' argument to 'exp', and the three parameter inversion
        recovery experiment in which the peak intensity limit is a non-zero value, selected by
        setting the argument to 'inv'.


        The format argument can currently be set to:
            'sparky'
            'xeasy'

        If the format argument is set to 'sparky', the file should be a Sparky peak list saved after
        typing the command 'lt'.  The default is to assume that columns 0, 1, 2, and 3 (1st, 2nd,
        3rd, and 4th) contain the Sparky assignment, w1, w2, and peak intensity data respectively.
        The frequency data w1 and w2 are ignored while the peak intensity data can either be the
        peak height or volume displayed by changing the window options.  If the peak intensity data
        is not within column 3, set the argument int_col to the appropriate value (column numbering
        starts from 0 rather than 1).

        If the format argument is set to 'xeasy', the file should be the saved XEasy text window
        output of the list peak entries command, 'tw' followed by 'le'.  As the columns are fixed,
        the peak intensity column is hardwired to number 10 (the 11th column) which contains either
        the peak height or peak volume data.  Because the columns are fixed, the int_col argument
        will be ignored.


        The heteronuc and proton arguments should be set respectively to the name of the
        heteronucleus and proton in the file.  Only those lines which match these labels will be
        used.


        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "relax_fit.read("
            text = text + "run=" + `run`
            text = text + ", file=" + `file`
            text = text + ", dir=" + `dir`
            text = text + ", relax_time=" + `relax_time`
            text = text + ", fit_type=" + `fit_type`
            text = text + ", format=" + `format`
            text = text + ", heteronuc=" + `heteronuc`
            text = text + ", proton=" + `proton`
            text = text + ", int_col=" + `int_col` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # The file name.
        if type(file) != str:
            raise RelaxStrError, ('file name', file)

        # Directory.
        if dir != None and type(dir) != str:
            raise RelaxNoneStrError, ('directory name', dir)

        # The relaxation time.
        if type(relax_time) != float:
            raise RelaxFloatError, ('relaxation time', relax_time)

        # The fit type.
        if type(fit_type) != str:
            raise RelaxStrError, ('fit type', fit_type)

        # The format.
        if type(format) != str:
            raise RelaxStrError, ('format', format)

        # The heteronucleus name.
        if type(heteronuc) != str:
            raise RelaxStrError, ('heteronucleus name', heteronuc)

        # The proton name.
        if type(proton) != str:
            raise RelaxStrError, ('proton name', proton)

        # The intensity column.
        if int_col and type(int_col) != int:
            raise RelaxNoneIntError, ('intensity column', int_col)

        # Execute the functional code.
        self.__relax__.specific.relax_fit.read(run=run, file=file, dir=dir, relax_time=relax_time, fit_type=fit_type, format=format, heteronuc=heteronuc, proton=proton, int_col=int_col)
