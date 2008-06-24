###############################################################################
#                                                                             #
# Copyright (C) 2003-2004, 2007-2008 Edward d'Auvergne                        #
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
from re import split
import sys

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from relax_errors import RelaxError, RelaxFileEmptyError, RelaxNoPipeError
from relax_io import extract_data, open_read_file, open_write_file, strip
from specific_fns.setup import get_specific_fn, get_string


def copy(run1=None, run2=None, sim=None):
    """Function for copying all results from run1 to run2."""

    # Test if run1 exists.
    if not run1 in ds.run_names:
        raise RelaxNoPipeError, run1

    # Test if run2 exists.
    if not run2 in ds.run_names:
        raise RelaxNoPipeError, run2

    # Function type.
    function_type = ds.run_types[ds.run_names.index(run1)]

    # Copy function.
    copy = self.relax.specific_setup.setup('copy', function_type, raise_error=0)

    # Copy the results.
    copy(run1=run1, run2=run2, sim=sim)


def determine_format(file=None, dir=None):
    """Determine the format of the results file.

    @keyword file:  The name of the results file.
    @type file:     str
    @keyword dir:   The directory containing the results file.
    @type dir:      str
    @return:        The results file format.  This can be 'xml' or 'columnar'.
    @rtype:         str or None
    """

    # Open the file.
    file = open_read_file(file_name=file, dir=dir)

    # First line.
    header = file.readline()

    # XML.
    if header == "<?xml version='1.0' encoding='UTF-8'?>":
        return 'xml'

    # Columnar.
    if split(header)[0:3] == ['Num', 'Name', 'Selected']:
        return 'columnar'


def display(format='xml'):
    """Displaying the results/contents of the current data pipe.

    @keyword format:    The format of the displayed results.
    @type format:       str
    """

    # Test if the current data pipe exists.
    if not ds.current_pipe:
        raise RelaxNoPipeError

    # Specific results writing function.
    if format == 'xml':
        write_function = ds.xml_write
    elif format == 'columnar':
        write_function = get_specific_fn('write_columnar_results', ds[ds.current_pipe].pipe_type, raise_error=False)
    else:
        raise RelaxError, "Unknown format " + `format` + "."

    # No function.
    if not write_function:
        raise RelaxError, "The " + format + " format is not currently supported for " + get_string(ds[ds.current_pipe].pipe_type) + "."

    # Write the results.
    write_function(sys.stdout)


def read(file='results', directory=None):
    """Function for reading the data out of a file."""

    # Test if the current data pipe exists.
    if not ds.current_pipe:
        raise RelaxNoPipeError

    # Determine the format of the file.
    format = determine_format(file, directory)

    # Specific results writing function.
    if format == 'xml':
        read_function = ds.xml_read
    elif format == 'columnar':
        read_function = get_specific_fn('read_columnar_results', ds[ds.current_pipe].pipe_type, raise_error=False)
    else:
        raise RelaxError, "Unknown format " + `format` + "."

    # No function.
    if not read_function:
        raise RelaxError, "The " + format + " format is not currently supported for " + self.relax.specific_setup.get_string(function_type) + "."

    # Make sure that the data pipe is empty.
    if not ds[ds.current_pipe].is_empty():
        raise RelaxError, "The current data pipe is not empty."

    # Extract the data from the file.
    file_data = extract_data(file_name=file, dir=directory, file_data=file_data)

    # Strip data.
    file_data = strip(file_data)

    # Do nothing if the file does not exist.
    if not file_data:
        raise RelaxFileEmptyError

    # Read the results.
    read_function(file_data, verbosity)


def write(file="results", directory=None, force=False, format='columnar', compress_type=1, verbosity=1):
    """Create the results file."""

    # Test if the current data pipe exists.
    if not ds.current_pipe:
        raise RelaxNoPipeError

    # The special data pipe name directory.
    if directory == 'pipe_name':
        directory = ds.current_pipe

    # Specific results writing function.
    if format == 'xml':
        write_function = ds.xml_write
    elif format == 'columnar':
        write_function = get_specific_fn('write_columnar_results', ds[ds.current_pipe].pipe_type, raise_error=False)
    else:
        raise RelaxError, "Unknown format " + `format` + "."

    # No function.
    if not write_function:
        raise RelaxError, "The " + format + " format is not currently supported for " + get_string(ds[ds.current_pipe].pipe_type) + "."

    # Open the file for writing.
    results_file = open_write_file(file_name=file, dir=directory, force=force, compress_type=compress_type, verbosity=verbosity)

    # Write the results.
    write_function(results_file)

    # Close the results file.
    results_file.close()
