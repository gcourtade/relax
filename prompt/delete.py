###############################################################################
#                                                                             #
# Copyright (C) 2003, 2004 Edward d'Auvergne                                  #
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


class Delete:
    def __init__(self, relax):
        """Class containing functions for deleting data."""

        self.relax = relax


    def delete(self, run=None, data_type=None):
        """Function for deleting data.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        run:  The name of the run.

        data_type:  The type of data to delete.


        Description
        ~~~~~~~~~~~

        The data_type argument specifies what type of data is to be deleted and must be one of the
        following strings:
            res:  All residue specific data.
            diff:  Diffusion tensor.
            None:  All data associated with the run.
        """

        # Function intro text.
        if self.relax.interpreter.intro:
            text = sys.ps3 + "delete("
            text = text + "run=" + `run`
            text = text + ", data_type=" + `data_type` + ")"
            print text

        # The run argument.
        if type(run) != str:
            raise RelaxStrError, ('run', run)

        # Data_type.
        if type != None and type(data_type) != str:
            raise RelaxNoneStrError, ('data type', data_type)

        # Execute the functional code.
        self.relax.generic.delete.data(run=run, data_type=data_type)
