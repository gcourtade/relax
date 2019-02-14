###############################################################################
#                                                                             #
# Copyright (C) 2003-2004,2006-2014 Edward d'Auvergne                         #
#                                                                             #
# This file is part of the program relax (http://www.nmr-relax.com).          #
#                                                                             #
# This program is free software: you can redistribute it and/or modify        #
# it under the terms of the GNU General Public License as published by        #
# the Free Software Foundation, either version 3 of the License, or           #
# (at your option) any later version.                                         #
#                                                                             #
# This program is distributed in the hope that it will be useful,             #
# but WITHOUT ANY WARRANTY; without even the implied warranty of              #
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the               #
# GNU General Public License for more details.                                #
#                                                                             #
# You should have received a copy of the GNU General Public License           #
# along with this program.  If not, see <http://www.gnu.org/licenses/>.       #
#                                                                             #
###############################################################################

# Module docstring.
"""Module for interfacing with PyMOL."""

# Dependency check module.
import dep_check

# Python module imports.
if dep_check.pymol_module:
    import pymol
from os import F_OK, access, getcwd, pardir, sep
PIPE, Popen = None, None
if dep_check.subprocess_module:
    from subprocess import PIPE, Popen
from tempfile import mkstemp
from time import sleep
from warnings import warn

# relax module imports.
from lib.errors import RelaxError, RelaxNoPdbError, RelaxNoSequenceError
from lib.warnings import RelaxWarning
from lib.io import delete, file_root, get_file_path, open_read_file, open_write_file, test_binary
from lib.structure.files import find_pdb_files
from pipe_control.mol_res_spin import exists_mol_res_spin_data
from pipe_control.pipes import check_pipe
from pipe_control.result_files import add_result_file
from specific_analyses.api import return_api
from status import Status; status = Status()


class Pymol:
    """The PyMOL execution object."""

    def __init__(self, exec_mode=None):
        """Set up the PyMOL execution object.

        @keyword exec_mode: The execution mode which can be either 'module' or 'external'.
        @type exec_mode:    None or str
        """

        # Variable for storing the pymol command history.
        self.command_history = ""

        # The pymol mode of operation.
        self.exec_mode = exec_mode
        if not exec_mode:
            if dep_check.pymol_module:
                self.exec_mode = 'module'
                self.open = False
            else:
                self.exec_mode = 'external'


    def clear_history(self):
        """Clear the PyMOL command history."""

        self.command_history = ""


    def exec_cmd(self, command=None, store_command=True):
        """Execute a PyMOL command.

        @param command:         The PyMOL command to send into the program.
        @type command:          str
        @param store_command:   A flag specifying if the command should be stored in the history
                                variable.
        @type store_command:    bool
        """

        # Reopen the GUI if needed.
        if not self.running():
            self.open_gui()

        # Execute the command.
        if self.exec_mode == 'module':
            pymol.cmd.do(command)
        else:
            self.pymol.write(command + '\n')

        # Place the command in the command history.
        if store_command:
            self.command_history = self.command_history + command + "\n"


    def open_gui(self):
        """Open the PyMOL GUI."""

        # Use the PyMOL python modules.
        if self.exec_mode == 'module':
            # Open the GUI.
            pymol.finish_launching()
            self.open = True

        # Otherwise execute PyMOL on the command line.
        if self.exec_mode == 'external':
            # Test that the PyMOL binary exists.
            test_binary('pymol')

            # Python 2.3 and earlier.
            if Popen == None:
                raise RelaxError("The subprocess module is not available in this version of Python.")

            # Open PyMOL as a pipe.
            self.pymol = Popen(['pymol', '-qpK'], stdin=PIPE).stdin

        # Execute the command history.
        if len(self.command_history) > 0:
            self.exec_cmd(self.command_history, store_command=0)
            return

        # Test if the PDB file has been loaded.
        if hasattr(cdp, 'structure'):
            self.open_pdb()


    def open_pdb(self):
        """Open the PDB file in PyMOL."""

        # Test if PyMOL is running.
        if not self.running():
            return

        # Reinitialise PyMOL.
        self.exec_cmd("reinitialize")

        # Open the PDB files.
        open_files = []
        for model in cdp.structure.structural_data:
            for mol in model.mol:
                # No file path.
                if not hasattr(mol, 'file_name'):
                    warn(RelaxWarning("Cannot display the current molecular data in PyMOL as it has not been exported as a PDB file."))
                    continue

                # The file path as the current directory.
                file_path = None
                if access(mol.file_name, F_OK):
                    file_path = mol.file_name

                # The file path using the relative path.
                if file_path == None and hasattr(mol, 'file_path') and mol.file_path != None:
                    file_path = mol.file_path + sep + mol.file_name
                    if not access(file_path, F_OK):
                        file_path = None

                # The file path using the absolute path.
                if file_path == None and hasattr(mol, 'file_path_abs') and mol.file_path_abs != None:
                    file_path = mol.file_path_abs + sep + mol.file_name
                    if not access(file_path, F_OK):
                        file_path = None

                # Hmmm, maybe the absolute path no longer exists and we are in a results subdirectory?
                if file_path == None and hasattr(mol, 'file_path') and mol.file_path != None:
                    file_path = pardir + sep + mol.file_path + sep + mol.file_name
                    if not access(file_path, F_OK):
                        file_path = None

                # Fall back to the current directory.
                if file_path == None:
                    file_path = mol.file_name

                # Already loaded.
                if file_path in open_files:
                    continue

                # Already loaded.
                if file_path in open_files:
                    continue

                # Open the file in PyMOL.
                self.exec_cmd("load " + file_path)

                # Add to the open file list.
                open_files.append(file_path)


    def running(self):
        """Test if PyMOL is running.

        @return:    Whether the Molmol pipe is open or not.
        @rtype:     bool
        """

        # Test if PyMOL module interface is already running.
        if self.exec_mode == 'module':
            return self.open

        # Test if command line PyMOL is already running.
        if self.exec_mode == 'external':
            # Pipe exists.
            if not hasattr(self, 'pymol'):
                return False

            # Test if the pipe has been broken.
            try:
                self.pymol.write('\n')
            except IOError:
                return False

            # PyMOL is running.
            return True



# Initialise the Pymol executable object.
pymol_obj = Pymol('external')
"""Pymol data container instance."""



def cartoon():
    """Apply the PyMOL cartoon style and colour by secondary structure."""

    # Test if the current data pipe exists.
    check_pipe()

    # Test for the structure.
    if not hasattr(cdp, 'structure'):
        raise RelaxNoPdbError

    # Loop over the PDB files.
    open_files = []
    for model in cdp.structure.structural_data:
        for mol in model.mol:
            # Identifier.
            pdb_file = mol.file_name
            if mol.file_path:
                pdb_file = mol.file_path + sep + pdb_file
            id = file_root(pdb_file)

            # Already loaded.
            if pdb_file in open_files:
                continue

            # Add to the open file list.
            open_files.append(pdb_file)

            # Hide everything.
            pymol_obj.exec_cmd("cmd.hide('everything'," + repr(id) + ")")

            # Show the cartoon style.
            pymol_obj.exec_cmd("cmd.show('cartoon'," + repr(id) + ")")

            # Colour by secondary structure.
            pymol_obj.exec_cmd("util.cbss(" + repr(id) + ", 'red', 'yellow', 'green')")


def command(command):
    """Function for sending PyMOL commands to the program pipe.

    @param command: The command to send into the program.
    @type command:  str
    """

    # Pass the command to PyMOL.
    pymol_obj.exec_cmd(command)


def cone_pdb(file=None):
    """Display the cone geometric object.

    @keyword file:  The name of the file containing the cone geometric object.
    @type file:     str
    """

    # Read in the cone PDB file.
    pymol_obj.exec_cmd("load " + file)

    # The object ID.
    id = file_root(file)

    # The cone axes.
    represent_cone_axis(id=id)

    # The cone object.
    represent_cone_object(id=id)


def create_macro(data_type=None, style="classic", colour_start=None, colour_end=None, colour_list=None):
    """Create an array of PyMOL commands.

    @keyword data_type:     The data type to map to the structure.
    @type data_type:        str
    @keyword style:         The style of the macro.
    @type style:            str
    @keyword colour_start:  The starting colour of the linear gradient.
    @type colour_start:     str or RBG colour array (len 3 with vals from 0 to 1)
    @keyword colour_end:    The ending colour of the linear gradient.
    @type colour_end:       str or RBG colour array (len 3 with vals from 0 to 1)
    @keyword colour_list:   The colour list to search for the colour names.  Can be either 'molmol' or 'x11'.
    @type colour_list:      str or None
    @return:                The list of PyMOL commands.
    @rtype:                 list of str
    """

    # Get the specific macro.
    api = return_api()
    commands = api.pymol_macro(data_type, style, colour_start, colour_end, colour_list)

    # Return the macro commands.
    return commands


def frame_order(ave_pos="ave_pos", rep="frame_order", sim="simulation.pdb.gz", dir=None):
    """Display the frame order results (geometric object, average position and Brownian simulation).

    @keyword ave_pos:   The file root of the average molecule structure.
    @type ave_pos:      str or None
    @keyword rep:       The file root of the PDB representation of the frame order dynamics to create.
    @type rep:          str or None
    @keyword sim:       The full Brownian diffusion file name.
    @type sim:          str or None
    @keyword dir:       The name of the directory where the files are located.
    @type dir:          str or None
    """

    # The path.
    path = getcwd()
    if dir != None:
        path = dir + sep

    # First disable everything, so that the original domain positions and structures and previous frame order results are not shown by default.
    pymol_obj.exec_cmd("disable all")

    # Set up the respective objects.
    if ave_pos:
        frame_order_ave_pos(root=ave_pos, path=path)
    if rep:
        frame_order_geometric(root=rep, path=path)
    if sim:
        frame_order_sim(file=sim, path=path)

    # Centre all objects and zoom.
    pymol_obj.exec_cmd("center animate=3")
    pymol_obj.exec_cmd("zoom animate=3")


def frame_order_ave_pos(root=None, path=None):
    """Display the PDB structure for the frame order average domain position.

    @keyword root:  The file root of the PDB file containing the frame order average structure.
    @type root:     str
    """

    # Find all PDB files.
    pdb_files = find_pdb_files(path=path, file_root=root)
    pdb_files += find_pdb_files(path=path, file_root=root+'_sim')

    # Read in the PDB files.
    for file in pdb_files:
        pymol_obj.exec_cmd("load " + file)

        # The object ID.
        id = file_root(file)

    # Disable the MC simulation representation - the user can find this out for themselves.
    pymol_obj.exec_cmd("disable %s_sim" % root)


def frame_order_sim(file=None, path=None):
    """Display the PDB structure for the frame order Brownian simulation.

    @keyword root:  The full Brownian diffusion file name.
    @type root:     str
    """

    # Find all PDB files.
    pdb_files = find_pdb_files(path=path, file_root=file)

    # Read in the PDB files.
    for file in pdb_files:
        pymol_obj.exec_cmd("load " + file)


def frame_order_geometric(root=None, path=None):
    """Display the frame order geometric object.

    @keyword root:  The file root of the PDB file containing the frame order geometric object.
    @type root:     str
    """

    # Find all PDB files.
    pdb_files = find_pdb_files(path=path, file_root=root)
    pdb_files += find_pdb_files(path=path, file_root=root+'_A')
    pdb_files += find_pdb_files(path=path, file_root=root+'_B')
    pdb_files += find_pdb_files(path=path, file_root=root+'_sim')
    pdb_files += find_pdb_files(path=path, file_root=root+'_sim_A')
    pdb_files += find_pdb_files(path=path, file_root=root+'_sim_B')

    # Read in the PDB files.
    for file in pdb_files:
        # Read in the PDB file.
        pymol_obj.exec_cmd("load " + file)

        # The object ID.
        id = file_root(file)

        # First hide everything.
        pymol_obj.exec_cmd("select %s" % id)
        pymol_obj.exec_cmd("hide ('sele')")
        pymol_obj.exec_cmd("cmd.delete('sele')")

        # Set up the titles.
        represent_titles(id=id)

        # Set up the pivot points.
        represent_pivots(id=id)

        # Set up the rotor objects.
        represent_rotor_object(id=id)

        # Set up the cone axis.
        represent_cone_axis(id=id)

        # Set up the cone object.
        represent_cone_object(id=id)

    # Disable the MC simulation representation - the user can find this out for themselves.
    pymol_obj.exec_cmd("disable %s_sim" % root)
    pymol_obj.exec_cmd("disable %s_sim_A" % root)
    pymol_obj.exec_cmd("disable %s_sim_B" % root)


def macro_apply(data_type=None, style="classic", colour_start_name=None, colour_start_rgb=None, colour_end_name=None, colour_end_rgb=None, colour_list=None):
    """Execute a PyMOL macro.

    @keyword data_type:         The data type to map to the structure.
    @type data_type:            str
    @keyword style:             The style of the macro.
    @type style:                str
    @keyword colour_start_name: The name of the starting colour of the linear gradient.
    @type colour_start_name:    str
    @keyword colour_start_rgb:  The RGB array starting colour of the linear gradient.
    @type colour_start_rgb:     RBG colour array (len 3 with vals from 0 to 1)
    @keyword colour_end_name:   The name of the ending colour of the linear gradient.
    @type colour_end_name:      str
    @keyword colour_end_rgb:    The RGB array ending colour of the linear gradient.
    @type colour_end_rgb:       RBG colour array (len 3 with vals from 0 to 1)
    @keyword colour_list:       The colour list to search for the colour names.  Can be either 'molmol' or 'x11'.
    @type colour_list:          str or None
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Test if sequence data exists.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Check the arguments.
    if colour_start_name != None and colour_start_rgb != None:
        raise RelaxError("The starting colour name and RGB colour array cannot both be supplied.")
    if colour_end_name != None and colour_end_rgb != None:
        raise RelaxError("The ending colour name and RGB colour array cannot both be supplied.")

    # Merge the colour args.
    if colour_start_name != None:
        colour_start = colour_start_name
    else:
        colour_start = colour_start_rgb
    if colour_end_name != None:
        colour_end = colour_end_name
    else:
        colour_end = colour_end_rgb

    # Clear the PyMOL history first.
    pymol_obj.clear_history()

    # Create the macro.
    commands = create_macro(data_type=data_type, style=style, colour_start=colour_start, colour_end=colour_end, colour_list=colour_list)

    # Save the commands as a temporary file, execute it, then delete it.
    try:
        # Temp file name.
        tmpfile_handle, tmpfile = mkstemp(suffix='.pml')

        # Open the file.
        file = open(tmpfile, 'w')

        # Loop over the commands and write them.
        for command in commands:
            file.write("%s\n" % command)
        file.close()

        # Execute the macro.
        pymol_obj.exec_cmd("@%s" % tmpfile)

        # Wait a bit for PyMOL to catch up (it takes time for PyMOL to start and the macro to execute).
        sleep(3)

    # Delete the temporary file (no matter what).
    finally:
        # Close the open file handle on the OS level.
        close(tmpfile_handle)

        # Delete the temporary file.
        delete(tmpfile, fail=False)


def macro_run(file=None, dir=None):
    """Execute the PyMOL macro from the given text file.

    @keyword file:          The name of the macro file to execute.
    @type file:             str
    @keyword dir:           The name of the directory where the macro file is located.
    @type dir:              str
    """

    # Open the file for reading.
    file_path = get_file_path(file, dir)
    file = open_read_file(file, dir)

    # Loop over the commands and apply them.
    for command in file.readlines():
        pymol_obj.exec_cmd(command)


def macro_write(data_type=None, style="classic", colour_start_name=None, colour_start_rgb=None, colour_end_name=None, colour_end_rgb=None, colour_list=None, file=None, dir=None, force=False):
    """Create a PyMOL macro file.

    @keyword data_type:         The data type to map to the structure.
    @type data_type:            str
    @keyword style:             The style of the macro.
    @type style:                str
    @keyword colour_start_name: The name of the starting colour of the linear gradient.
    @type colour_start_name:    str
    @keyword colour_start_rgb:  The RGB array starting colour of the linear gradient.
    @type colour_start_rgb:     RBG colour array (len 3 with vals from 0 to 1)
    @keyword colour_end_name:   The name of the ending colour of the linear gradient.
    @type colour_end_name:      str
    @keyword colour_end_rgb:    The RGB array ending colour of the linear gradient.
    @type colour_end_rgb:       RBG colour array (len 3 with vals from 0 to 1)
    @keyword colour_list:       The colour list to search for the colour names.  Can be either 'molmol' or 'x11'.
    @type colour_list:          str or None
    @keyword file:              The name of the macro file to create.
    @type file:                 str
    @keyword dir:               The name of the directory to place the macro file into.
    @type dir:                  str
    @keyword force:             Flag which if set to True will cause any pre-existing file to be overwritten.
    @type force:                bool
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Test if sequence data exists.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Check the arguments.
    if colour_start_name != None and colour_start_rgb != None:
        raise RelaxError("The starting colour name and RGB colour array cannot both be supplied.")
    if colour_end_name != None and colour_end_rgb != None:
        raise RelaxError("The ending colour name and RGB colour array cannot both be supplied.")

    # Merge the colour args.
    if colour_start_name != None:
        colour_start = colour_start_name
    else:
        colour_start = colour_start_rgb
    if colour_end_name != None:
        colour_end = colour_end_name
    else:
        colour_end = colour_end_rgb

    # Create the macro.
    commands = create_macro(data_type=data_type, style=style, colour_start=colour_start, colour_end=colour_end, colour_list=colour_list)

    # File name.
    if file == None:
        file = data_type + '.pml'

    # Open the file for writing.
    file_path = get_file_path(file, dir)
    file = open_write_file(file, dir, force)

    # Loop over the commands and write them.
    for command in commands:
        file.write(command + "\n")

    # Close the file.
    file.close()

    # Add the file to the results file list.
    add_result_file(type='pymol', label='PyMOL', file=file_path)


def represent_cone_axis(id=None):
    """Set up the PyMOL cone axis representation.

    @keyword id:    The PyMOL object ID.
    @type id:       str
    """

    # Sanity check.
    if id == None:
        raise RelaxError("The PyMOL object ID must be supplied.")

    # Select the AXE residues.
    pymol_obj.exec_cmd("select (%s & resn AXE)" % id)

    # Show the vector as a stick.
    pymol_obj.exec_cmd("show stick, 'sele'")

    # Colour it blue.
    pymol_obj.exec_cmd("color cyan, 'sele'")

    # Select the atom used for labelling.
    pymol_obj.exec_cmd("select (%s & resn AXE and symbol N)" % id)

    # Hide the atom.
    pymol_obj.exec_cmd("hide ('sele')")

    # Label using the atom name.
    pymol_obj.exec_cmd("cmd.label(\"sele\",\"name\")")

    # Remove the selection.
    pymol_obj.exec_cmd("cmd.delete('sele')")


def represent_cone_object(id=None):
    """Set up the PyMOL cone object representation.

    @keyword id:    The PyMOL object ID.
    @type id:       str
    """

    # Sanity check.
    if id == None:
        raise RelaxError("The PyMOL object ID must be supplied.")

    # Select the CON and CNE residues.
    pymol_obj.exec_cmd("select (%s & resn CON,CNE)" % id)

    # Hide everything.
    pymol_obj.exec_cmd("hide ('sele')")

    # Show as 'sticks'.
    pymol_obj.exec_cmd("show sticks, 'sele'")

    # Colour it white.
    pymol_obj.exec_cmd("color white, 'sele'")

    # Shorten the stick width from 0.25 to 0.15.
    pymol_obj.exec_cmd("set stick_radius, 0.15, 'sele'")

    # Set a bit of transparency.
    pymol_obj.exec_cmd("set stick_transparency, 0.3, 'sele'")

    # Remove the selection.
    pymol_obj.exec_cmd("cmd.delete('sele')")


def represent_pivots(id=None):
    """Set up the PyMOL pivot object representation.

    @keyword id:    The PyMOL object ID.
    @type id:       str
    """

    # Sanity check.
    if id == None:
        raise RelaxError("The PyMOL object ID must be supplied.")

    # Select the PIV residues.
    pymol_obj.exec_cmd("select (%s & resn PIV)" % id)

    # Hide the atom.
    pymol_obj.exec_cmd("hide ('sele')")

    # Label using the atom name.
    pymol_obj.exec_cmd("cmd.label(\"sele\",\"name\")")

    # Remove the selection.
    pymol_obj.exec_cmd("cmd.delete('sele')")


def represent_titles(id=None):
    """Set up the PyMOL title object representation.

    @keyword id:    The PyMOL object ID.
    @type id:       str
    """

    # Sanity check.
    if id == None:
        raise RelaxError("The PyMOL object ID must be supplied.")

    # Frame order representation A.
    pymol_obj.exec_cmd("select (%s & resn TLE & name a)" % id)
    pymol_obj.exec_cmd("hide ('sele')")
    pymol_obj.exec_cmd("label 'sele', 'Representation A'")
    pymol_obj.exec_cmd("cmd.delete('sele')")

    # Frame order representation B.
    pymol_obj.exec_cmd("select (%s & resn TLE & name b)" % id)
    pymol_obj.exec_cmd("hide ('sele')")
    pymol_obj.exec_cmd("label 'sele', 'Representation B'")
    pymol_obj.exec_cmd("cmd.delete('sele')")

    # Frame order MC sim representation.
    pymol_obj.exec_cmd("select (%s & resn TLE & name mc)" % id)
    pymol_obj.exec_cmd("hide ('sele')")
    pymol_obj.exec_cmd("label 'sele', 'MC sim representation'")
    pymol_obj.exec_cmd("cmd.delete('sele')")

    # Frame order MC sim representation A.
    pymol_obj.exec_cmd("select (%s & resn TLE & name mc-a)" % id)
    pymol_obj.exec_cmd("hide ('sele')")
    pymol_obj.exec_cmd("label 'sele', 'MC sim representation A'")
    pymol_obj.exec_cmd("cmd.delete('sele')")

    # Frame order MC sim representation B.
    pymol_obj.exec_cmd("select (%s & resn TLE & name mc-b)" % id)
    pymol_obj.exec_cmd("hide ('sele')")
    pymol_obj.exec_cmd("label 'sele', 'MC sim representation B'")
    pymol_obj.exec_cmd("cmd.delete('sele')")


def represent_rotor_object(id=None):
    """Set up the PyMOL rotor object representation.

    @keyword id:    The PyMOL object ID.
    @type id:       str
    """

    # Sanity check.
    if id == None:
        raise RelaxError("The PyMOL object ID must be supplied.")

    # Rotor objects:  Set up the rotor axis.
    pymol_obj.exec_cmd("select (%s & resn RTX)" % id)
    pymol_obj.exec_cmd("show stick, 'sele'")
    pymol_obj.exec_cmd("color red, 'sele'")
    pymol_obj.exec_cmd("cmd.delete('sele')")

    # Rotor objects:  Display the central point.
    pymol_obj.exec_cmd("select (%s & name CTR)" % id)
    pymol_obj.exec_cmd("show spheres, 'sele'")
    pymol_obj.exec_cmd("color red, 'sele'")
    pymol_obj.exec_cmd("set sphere_scale, 0.3, 'sele'")
    pymol_obj.exec_cmd("cmd.delete('sele')")

    # Rotor objects:  Set up the propellers.
    pymol_obj.exec_cmd("select (%s & resn RTB)" % id)
    pymol_obj.exec_cmd("show line, 'sele'")
    pymol_obj.exec_cmd("cmd.delete('sele')")
    pymol_obj.exec_cmd("select (%s & resn RTB & name BLD)" % id)
    pymol_obj.exec_cmd("show spheres, 'sele'")
    pymol_obj.exec_cmd("set sphere_scale, 0.1, 'sele'")
    pymol_obj.exec_cmd("cmd.delete('sele')")

    # Rotor objects:  The labels.
    pymol_obj.exec_cmd("select (%s & resn RTL)" % id)
    pymol_obj.exec_cmd("cmd.label(\"sele\",\"name\")")
    pymol_obj.exec_cmd("cmd.delete('sele')")


def tensor_pdb(file=None):
    """Display the diffusion tensor geometric structure.

    @keyword file:  The name of the file containing the diffusion tensor geometric object.
    @type file:     str
    """

    # Test if the current data pipe exists.
    check_pipe()

    # Read in the tensor PDB file.
    pymol_obj.exec_cmd("load " + file)


    # The tensor object.
    ####################

    # Select the TNS residue.
    pymol_obj.exec_cmd("select resn TNS")

    # Hide everything.
    pymol_obj.exec_cmd("hide ('sele')")

    # Show as 'sticks'.
    pymol_obj.exec_cmd("show sticks, 'sele'")


    # Centre of mass.
    #################

    # Select the COM residue.
    pymol_obj.exec_cmd("select resn COM")

    # Show the centre of mass as the dots representation.
    pymol_obj.exec_cmd("show dots, 'sele'")

    # Colour it blue.
    pymol_obj.exec_cmd("color blue, 'sele'")


    # The diffusion tensor axes.
    ############################

    # Select the AXS residue.
    pymol_obj.exec_cmd("select resn AXS")

    # Hide everything.
    pymol_obj.exec_cmd("hide ('sele')")

    # Show as 'sticks'.
    pymol_obj.exec_cmd("show sticks, 'sele'")

    # Colour it cyan.
    pymol_obj.exec_cmd("color cyan, 'sele'")

    # Select the N atoms of the AXS residue (used to display the axis labels).
    pymol_obj.exec_cmd("select (resn AXS and elem N)")

    # Label the atoms.
    pymol_obj.exec_cmd("label 'sele', name")



    # Monte Carlo simulations.
    ##########################

    # Select the SIM residue.
    pymol_obj.exec_cmd("select resn SIM")

    # Colour it.
    pymol_obj.exec_cmd("colour cyan, 'sele'")


    # Clean up.
    ###########

    # Remove the selection.
    pymol_obj.exec_cmd("cmd.delete('sele')")


def vector_dist(file=None):
    """Display the XH bond vector distribution.

    @keyword file:   The vector distribution PDB file.
    @type file:     str
    """

    # Test if the current data pipe exists.
    check_pipe()

    # The file root.
    id = file_root(file)

    # Read in the vector distribution PDB file.
    pymol_obj.exec_cmd("load " + file)


    # Create a surface.
    ###################

    # Select the vector distribution.
    pymol_obj.exec_cmd("cmd.show('surface', " + repr(id) + ")")


def view():
    """Start PyMOL."""

    # Open PyMOL.
    if pymol_obj.running():
        raise RelaxError("PyMOL is already running.")
    else:
        pymol_obj.open_gui()
