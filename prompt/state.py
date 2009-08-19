###############################################################################
#                                                                             #
# Copyright (C) 2003-2005, 2007 Edward d'Auvergne                             #
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
"""Module containing the 'state' user function class."""
__docformat__ = 'plaintext'

# Python module imports.
import sys

# relax module imports.
import help
from relax_errors import RelaxBoolError, RelaxIntError, RelaxNoneStrError, RelaxStrFileError
from generic_fns.state import load_state, save_state


class State:
    def __init__(self, relax):
        # Help.
        self.__relax_help__ = \
        """Class for saving or loading the program state."""

        # Add the generic help string.
        self.__relax_help__ = self.__relax_help__ + "\n" + help.relax_class_help

        # Place relax in the class namespace.
        self.__relax__ = relax


    def load(self, state=None, dir_name=None):
        """Function for loading a saved program state.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        state:  The file name, which can be a string or a file descriptor object, of a saved program
                state.

        dir_name:  The name of the directory in which the file is found.


        Description
        ~~~~~~~~~~~

        This function is able to handle uncompressed, bzip2 compressed files, or gzip compressed
        files automatically.  The full file name including extension can be supplied, however, if
        the file cannot be found, this function will search for the file name with '.bz2' appended
        followed by the file name with '.gz' appended.  For more advanced users, file descriptor
        objects are also supported.


        Examples
        ~~~~~~~~

        The following commands will load the state saved in the file 'save'.

        relax> state.load('save')
        relax> state.load(state='save')


        The following commands will load the state saved in the bzip2 compressed file 'save.bz2'.

        relax> state.load('save')
        relax> state.load(state='save')
        relax> state.load('save.bz2')
        relax> state.load(state='save.bz2')
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "state.load("
            text = text + "state=" + repr(state)
            text = text + ", dir_name=" + repr(dir_name) + ")"
            print text

        # File name.
        if type(state) != str and type(state) != file:
            raise RelaxStrFileError, ('file name', state)

        # Directory.
        if dir_name != None and type(dir_name) != str:
            raise RelaxNoneStrError, ('directory', dir_name)

        # Execute the functional code.
        load_state(state=state, dir_name=dir_name)


    def save(self, state=None, dir_name=None, force=False, compress_type=1):
        """Function for saving the program state.

        Keyword Arguments
        ~~~~~~~~~~~~~~~~~

        state:  The file name, which can be a string or a file descriptor object, to save the
                current program state in.

        dir_name:  The name of the directory in which to place the file.

        force:  A boolean flag which if set to True will cause the file to be overwritten.


        Description
        ~~~~~~~~~~~

        The default behaviour of this function is to compress the file using bzip2 compression.  If
        the extension '.bz2' is not included in the file name, it will be added.  The compression
        can, however, be changed to either no compression or gzip compression.  This is controlled
        by the compress_type argument which can be set to

            0:  No compression (no file extension).
            1:  bzip2 compression ('.bz2' file extension).
            2:  gzip compression ('.gz' file extension).


        Examples
        ~~~~~~~~

        The following commands will save the current program state into the file 'save':

        relax> state.save('save', compress_type=0)
        relax> state.save(state='save', compress_type=0)


        The following commands will save the current program state into the bzip2 compressed file
        'save.bz2':

        relax> state.save('save')
        relax> state.save(state='save')
        relax> state.save('save.bz2')
        relax> state.save(state='save.bz2')


        If the file 'save' already exists, the following commands will save the current program
        state by overwriting the file.

        relax> state.save('save', True)
        relax> state.save(state='save', force=True)
        """

        # Function intro text.
        if self.__relax__.interpreter.intro:
            text = sys.ps3 + "state.save("
            text = text + "state=" + repr(state)
            text = text + ", dir_name=" + repr(dir_name)
            text = text + ", force=" + repr(force)
            text = text + ", compress_type=" + repr(compress_type) + ")"
            print text

        # File name.
        if type(state) != str and type(state) != file:
            raise RelaxStrFileError, ('file name', state)

        # Directory.
        if dir_name != None and type(dir_name) != str:
            raise RelaxNoneStrError, ('directory', dir_name)

        # The force flag.
        if type(force) != bool:
            raise RelaxBoolError, ('force flag', force)

        # Compression type.
        if type(compress_type) != int:
            raise RelaxIntError, ('compression type', compress_type)

        # Execute the functional code.
        save_state(state=state, dir_name=dir_name, force=force, compress_type=compress_type)
