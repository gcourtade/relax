###############################################################################
#                                                                             #
# Copyright (C) 2003-2005,2007-2009 Edward d'Auvergne                         #
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
"""Module containing the 'pcs' pseudocontact shift user function class."""
__docformat__ = 'plaintext'

# Python module imports.
import sys

# relax module imports.
from base_class import User_fn_class
import check
from generic_fns import pcs
from relax_errors import RelaxError


class PCS(User_fn_class):
    """Class for handling pseudo-contact shifts."""

    def back_calc(self, id=None):
        """Back calculate the pseudocontact shifts.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        id:  The alignment identification string.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "pcs.back_calc("
            text = text + "id=" + repr(id) + ")"
            print(text)

        # The argument checks.
        check.is_str(id, 'alignment identification string')

        # Execute the functional code.
        pcs.back_calc(id=id)


    def centre(self, atom_id=None, pipe=None, ave_pos=True):
        """Specify which atom is the paramagnetic centre.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        atom_id:  The atom identification string.

        pipe:  The data pipe containing the structures to extract the centre from.

        ave_pos:  A flag specifying if the position of the atom is to be averaged across all models.


        Description
        ~~~~~~~~~~~

        This function is required for specifying where the paramagnetic centre is located in the
        loaded structure file.  If no structure number is given, then the average atom position will
        be calculated if multiple structures are loaded.

        A different set of structures than those loaded into the current data pipe can also be used
        to determine the position, or its average.  This can be achieved by loading the alternative
        structures into another data pipe, and then specifying that pipe through the pipe argument.

        If the ave_pos flag is set to True, the average position from all models will be used as the
        position of the paramagnetic centre.  If False, then the positions from all structures will
        be used.  If multiple positions are used, then a fast PCS centre motion will be assumed so
        that PCSs for a single tensor will be calculated for each position, and the PCS values
        linearly averaged.


        Examples
        ~~~~~~~~

        If the paramagnetic centre is the lanthanide Dysprosium which is labelled as Dy in a loaded
        PDB file, then type one of:

        relax> pcs.centre('Dy')
        relax> pcs.centre(atom_id='Dy')

        If the carbon atom 'C1' of residue '4' in the PDB file is to be used as the paramagnetic
        centre, then type:

        relax> pcs.centre(':4@C1')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "pcs.centre("
            text = text + "atom_id=" + repr(atom_id)
            text = text + ", pipe=" + repr(pipe)
            text = text + ", ave_pos=" + repr(ave_pos) + ")"
            print(text)

        # The argument checks.
        check.is_str(atom_id, 'atom identification string')
        check.is_str(pipe, 'data pipe', can_be_none=True)
        check.is_bool(ave_pos, 'average position flag')

        # Execute the functional code.
        pcs.centre(atom_id=atom_id, pipe=pipe, ave_pos=ave_pos)


    def copy(self, pipe_from=None, pipe_to=None, id=None):
        """Copy PCS data from pipe_from to pipe_to.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        pipe_from:  The name of the pipe to copy the PCS data from.

        pipe_to:  The name of the pipe to copy the PCS data to.

        id:  The alignment identification string.


        Description
        ~~~~~~~~~~~

        This function will copy PCS data from 'pipe_from' to 'pipe_to'.  If id is not given then all
        PCS data will be copied, otherwise only a specific data set will be.


        Examples
        ~~~~~~~~

        To copy all PCS data from pipe 'm1' to pipe 'm9', type one of:

        relax> pcs.copy('m1', 'm9')
        relax> pcs.copy(pipe_from='m1', pipe_to='m9')
        relax> pcs.copy('m1', 'm9', None)
        relax> pcs.copy(pipe_from='m1', pipe_to='m9', id=None)

        To copy only the 'Th' PCS data from 'm3' to 'm6', type one of:

        relax> pcs.copy('m3', 'm6', 'Th')
        relax> pcs.copy(pipe_from='m3', pipe_to='m6', id='Th')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "pcs.copy("
            text = text + "pipe_from=" + repr(pipe_from)
            text = text + ", pipe_to=" + repr(pipe_to)
            text = text + ", id=" + repr(id) + ")"
            print(text)

        # The argument checks.
        check.is_str(pipe_from, 'pipe from', can_be_none=True)
        check.is_str(pipe_to, 'pipe to', can_be_none=True)
        check.is_str(id, 'alignment identification string', can_be_none=True)

        # Both pipe arguments cannot be None.
        if pipe_from == None and pipe_to == None:
            raise RelaxError("The pipe_from and pipe_to arguments cannot both be set to None.")

        # Execute the functional code.
        pcs.copy(pipe_from=pipe_from, pipe_to=pipe_to, id=id)


    def delete(self, id=None):
        """Delete the PCS data corresponding to the alignment id.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        id:  The alignment identification string.


        Examples
        ~~~~~~~~

        To delete the PCS data corresponding to id='PH_gel', type:

        relax> pcs.delete('PH_gel')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "pcs.delete("
            text = text + "id=" + repr(id) + ")"
            print(text)

        # The argument checks.
        check.is_str(id, 'alignment identification string')

        # Execute the functional code.
        pcs.delete(id=id)


    def display(self, id=None):
        """Display the PCS data corresponding to the alignment id.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        id:  The alignment identification string.


        Examples
        ~~~~~~~~

        To display the 'phage' PCS data, type:

        relax> pcs.display('phage')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "pcs.display("
            text = text + "id=" + repr(id) + ")"
            print(text)

        # The argument checks.
        check.is_str(id, 'alignment identification string')

        # Execute the functional code.
        pcs.display(id=id)


    def read(self, id=None, file=None, dir=None, spin_id=None, mol_name_col=None, res_num_col=None, res_name_col=None, spin_num_col=None, spin_name_col=None, data_col=None, error_col=None, sep=None):
        """Read the PCS data from file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        id:  The alignment identification string.

        file:  The name of the file containing the PCS data.

        dir:  The directory where the file is located.

        spin_id:  The spin identification string.

        mol_name_col:  The molecule name column (this defaults to no column).

        res_num_col:  The residue number column (the default is 0, i.e. the first column).

        res_name_col:  The residue name column (the default is 1, i.e. the second column).

        spin_num_col:  The spin number column (this defaults to no column).

        spin_name_col:  The spin name column (this defaults to no column).

        data_col:  The PCS data column (the default is 2).

        error_col:  The experimental error column (the default is 3).

        sep:  The column separator (the default is white space).


        Examples
        ~~~~~~~~

        The following commands will read the PCS data out of the file 'Tb.txt' where the columns are
        separated by the symbol ',', and store the PCSs under the identifier 'Tb'.

        relax> pcs.read('Tb', 'Tb.txt', sep=',')


        To read the 15N and 1H PCSs from the file 'Eu.txt', where the 15N values are in the 4th
        column and the 1H in the 9th, type both the following:

        relax> rdc.read('Tb', 'Tb.txt', spin_id='@N', res_num_col=0, data_col=3)
        relax> rdc.read('Tb', 'Tb.txt', spin_id='@H', res_num_col=0, data_col=8)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "pcs.read("
            text = text + "id=" + repr(id)
            text = text + ", file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", spin_id=" + repr(spin_id)
            text = text + ", mol_name_col=" + repr(mol_name_col)
            text = text + ", res_num_col=" + repr(res_num_col)
            text = text + ", res_name_col=" + repr(res_name_col)
            text = text + ", spin_num_col=" + repr(spin_num_col)
            text = text + ", spin_name_col=" + repr(spin_name_col)
            text = text + ", data_col=" + repr(data_col)
            text = text + ", error_col=" + repr(error_col)
            text = text + ", sep=" + repr(sep) + ")"
            print(text)

        # The argument checks.
        check.is_str(id, 'alignment identification string')
        check.is_str(file, 'file name')
        check.is_str(dir, 'directory name', can_be_none=True)
        check.is_str(spin_id, 'spin identification string', can_be_none=True)
        check.is_int(mol_name_col, 'molecule name column', can_be_none=True)
        check.is_int(res_num_col, 'residue number column', can_be_none=True)
        check.is_int(res_name_col, 'residue name column', can_be_none=True)
        check.is_int(spin_num_col, 'spin number column', can_be_none=True)
        check.is_int(spin_name_col, 'spin name column', can_be_none=True)
        check.is_int(data_col, 'data column', can_be_none=True)
        check.is_int(error_col, 'error column', can_be_none=True)
        check.is_str(sep, 'column separator', can_be_none=True)

        # Execute the functional code.
        pcs.read(id=id, file=file, dir=dir, spin_id=spin_id, mol_name_col=mol_name_col, res_num_col=res_num_col, res_name_col=res_name_col, spin_num_col=spin_num_col, spin_name_col=spin_name_col, data_col=data_col, error_col=error_col, sep=sep)


    def write(self, id=None, file=None, dir=None, force=False):
        """Write the PCS data to file.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        id:  The alignment identification string.

        file:  The name of the file.

        dir:  The directory name.

        force:  A flag which if True will cause the file to be overwritten.


        Description
        ~~~~~~~~~~~

        If no directory name is given, the file will be placed in the current working directory.
        The 'id' argument are required for selecting which PCS data set will be written to file.
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "pcs.write("
            text = text + "id=" + repr(id)
            text = text + ", file=" + repr(file)
            text = text + ", dir=" + repr(dir)
            text = text + ", force=" + repr(force) + ")"
            print(text)

        # The argument checks.
        check.is_str(id, 'alignment identification string')
        check.is_str(file, 'file name')
        check.is_str(dir, 'directory name', can_be_none=True)
        check.is_bool(force, 'force flag')

        # Execute the functional code.
        pcs.write(id=id, file=file, dir=dir, force=force)
