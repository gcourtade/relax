###############################################################################
#                                                                             #
# Copyright (C) 2008-2009 Edward d'Auvergne                                   #
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
"""Module containing functions for BMRB support."""

# Python module imports.
from os import F_OK, access

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from data.exp_info import ExpInfo
from generic_fns import exp_info
from relax_errors import RelaxError, RelaxFileError, RelaxFileOverwriteError, RelaxNoPipeError
from relax_io import get_file_path, mkdir_nofail
from specific_fns.setup import get_specific_fn
from version import version_full


def display(version='3.1'):
    """Display the results in the BMRB NMR-STAR format."""

    # Test if the current data pipe exists.
    if not ds.current_pipe:
        raise RelaxNoPipeError

    # Specific results writing function.
    write_function = get_specific_fn('bmrb_write', ds[ds.current_pipe].pipe_type, raise_error=False)

    # Write the results.
    write_function(sys.stdout, version=version)


def read(file=None, directory=None, version='3.1'):
    """Read the contents of a BMRB NMR-STAR formatted file."""

    # Test if the current data pipe exists.
    if not ds.current_pipe:
        raise RelaxNoPipeError

    # Make sure that the data pipe is empty.
    if not ds[ds.current_pipe].is_empty():
        raise RelaxError("The current data pipe is not empty.")

    # Get the full file path.
    file_path = get_file_path(file_name=file, dir=directory)

    # Fail if the file does not exist.
    if not access(file_path, F_OK):
        raise RelaxFileError(file_path)

    # Specific results reading function.
    read_function = get_specific_fn('bmrb_read', ds[ds.current_pipe].pipe_type)

    # Read the results.
    read_function(file_path, version=version)


def write(file=None, directory=None, version='3.1', force=False):
    """Create a BMRB NMR-STAR formatted file."""

    # Test if the current data pipe exists.
    if not ds.current_pipe:
        raise RelaxNoPipeError

    # The special data pipe name directory.
    if directory == 'pipe_name':
        directory = ds.current_pipe

    # Specific results writing function.
    write_function = get_specific_fn('bmrb_write', ds[ds.current_pipe].pipe_type)

    # Get the full file path.
    file_path = get_file_path(file, directory)

    # Fail if the file already exists and the force flag is False.
    if access(file_path, F_OK) and not force:
        raise RelaxFileOverwriteError(file_path, 'force flag')

    # Print out.
    print("Opening the file '%s' for writing." % file_path)

    # Create the directories.
    mkdir_nofail(directory, verbosity=0)

    # Add the relax citations.
    cdp.exp_info.add_citation(cite_id='relax_ref1', authors=exp_info.RELAX_CITE1_AUTHORS, doi=exp_info.RELAX_CITE1_DOI, pubmed_id=exp_info.RELAX_CITE1_PUBMED_ID, full_citation=exp_info.RELAX_CITE1_FULL_CITATION, title=exp_info.RELAX_CITE1_TITLE, status=exp_info.RELAX_CITE1_STATUS, type=exp_info.RELAX_CITE1_TYPE, journal_abbrev=exp_info.RELAX_CITE1_JOURNAL_ABBREV, journal_full=exp_info.RELAX_CITE1_JOURNAL_FULL, volume=exp_info.RELAX_CITE1_VOLUME, issue=exp_info.RELAX_CITE1_ISSUE, page_first=exp_info.RELAX_CITE1_PAGE_FIRST, page_last=exp_info.RELAX_CITE1_PAGE_LAST, year=exp_info.RELAX_CITE1_YEAR)
    cdp.exp_info.add_citation(cite_id='relax_ref2', authors=exp_info.RELAX_CITE2_AUTHORS, doi=exp_info.RELAX_CITE2_DOI, pubmed_id=exp_info.RELAX_CITE2_PUBMED_ID, full_citation=exp_info.RELAX_CITE2_FULL_CITATION, title=exp_info.RELAX_CITE2_TITLE, status=exp_info.RELAX_CITE2_STATUS, type=exp_info.RELAX_CITE2_TYPE, journal_abbrev=exp_info.RELAX_CITE2_JOURNAL_ABBREV, journal_full=exp_info.RELAX_CITE2_JOURNAL_FULL, volume=exp_info.RELAX_CITE2_VOLUME, issue=exp_info.RELAX_CITE2_ISSUE, page_first=exp_info.RELAX_CITE2_PAGE_FIRST, page_last=exp_info.RELAX_CITE2_PAGE_LAST, year=exp_info.RELAX_CITE2_YEAR)

    # Add the relax software package.
    cdp.exp_info.software_setup(name=exp_info.RELAX_NAME, version=version_full(), vendor_name=exp_info.RELAX_AUTHORS, url=exp_info.RELAX_URL, cite_ids=['relax_ref1', 'relax_ref2'], tasks=exp_info.RELAX_TASKS)

    # Execute the specific BMRB writing code.
    write_function(file_path, version=version)
