###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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
"""Module for interfacing with the BMRB (http://www.bmrb.wisc.edu/) by handling NMR-STAR v3.1 files."""

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from relax_errors import RelaxError, RelaxNoPipeError


def display():
    """Display the results in the BMRB NMR-STAR v3.1 format."""

    # Test if the current data pipe exists.
    if not ds.current_pipe:
        raise RelaxNoPipeError

    # Specific results writing function.
    write_function = get_specific_fn('bmrb_write', ds[ds.current_pipe].pipe_type, raise_error=False)

    # Write the results.
    write_function(sys.stdout)


def read(file=None, directory=None):
    """Read the contents of a BMRB NMR-STAR v3.1 formatted file."""

    # Test if the current data pipe exists.
    if not ds.current_pipe:
        raise RelaxNoPipeError

    # Make sure that the data pipe is empty.
    if not ds[ds.current_pipe].is_empty():
        raise RelaxError, "The current data pipe is not empty."

    # Get the full file path, for later use.
    file_path = get_file_path(file_name=file, dir=directory)

    # Open the file.
    file = open_read_file(file_name=file, dir=directory)

    # Specific results reading function.
    read_function = get_specific_fn('bmrb_read', ds[ds.current_pipe].pipe_type, raise_error=False)

    # Read the results.
    read_function(file)


def write(file=None, directory=None, force=False, compress_type=0, verbosity=1):
    """Create a BMRB NMR-STAR v3.1 formatted file."""

    # Test if the current data pipe exists.
    if not ds.current_pipe:
        raise RelaxNoPipeError

    # The special data pipe name directory.
    if directory == 'pipe_name':
        directory = ds.current_pipe

    # Specific results writing function.
    write_function = get_specific_fn('bmrb_write', ds[ds.current_pipe].pipe_type, raise_error=False)

    # Open the file for writing.
    results_file = open_write_file(file_name=file, dir=directory, force=force, compress_type=compress_type, verbosity=verbosity)

    # Write the results.
    write_function(results_file)

    # Close the results file.
    results_file.close()
