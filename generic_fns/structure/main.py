###############################################################################
#                                                                             #
# Copyright (C) 2003-2008 Edward d'Auvergne                                   #
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
from numpy import dot, float64, ndarray, zeros
from os import F_OK, access
from re import search
import sys
from warnings import warn

# relax module imports.
from data import Relax_data_store; ds = Relax_data_store()
from generic_fns import molmol, relax_re
from generic_fns.mol_res_spin import exists_mol_res_spin_data, generate_spin_id, return_molecule, return_residue, return_spin, spin_loop
from generic_fns.sequence import write_header, write_line
from generic_fns.structure.internal import Internal
from generic_fns.structure.scientific import Scientific_data
from relax_errors import RelaxError, RelaxFileError, RelaxNoPipeError, RelaxNoSequenceError, RelaxPdbError
from relax_io import get_file_path, open_write_file
from relax_warnings import RelaxWarning, RelaxNoPDBFileWarning, RelaxZeroVectorWarning



def load_spins(spin_id=None, str_id=None, ave_pos=False):
    """Load the spins from the structural object into the relax data store.

    @keyword spin_id:   The molecule, residue, and spin identifier string.
    @type spin_id:      str
    @keyword str_id:    The structure identifier.  This can be the file name, model number, or
                        structure number.
    @type str_id:       int or str
    @keyword ave_pos:   A flag specifying if the average atom position or the atom position from all
                        loaded structures is loaded into the SpinContainer.
    @type ave_pos:      bool
    """

    # Test if the current data pipe exists.
    if not ds.current_pipe:
        raise RelaxNoPipeError

    # Print out.
    print "Adding the following spins to the relax data store.\n"
    write_header(sys.stdout, mol_name_flag=True, res_num_flag=True, res_name_flag=True, spin_num_flag=True, spin_name_flag=True)

    # Alias the current data pipe.
    cdp = ds[ds.current_pipe]

    # Loop over all atoms of the spin_id selection.
    for mol_name, res_num, res_name, atom_num, atom_name, element, pos in cdp.structure.atom_loop(atom_id=spin_id, str_id=str_id, mol_name_flag=True, res_num_flag=True, res_name_flag=True, atom_num_flag=True, atom_name_flag=True, element_flag=True, pos_flag=True, ave=ave_pos):
        # Initialise the identification string.
        id = ''

        # Get the molecule container corresponding to the molecule name.
        if mol_name:
            # Update the ID string.
            id = id + '#' + mol_name

            # The container.
            mol_cont = return_molecule(id)

        # The is only one molecule and it is unnamed.
        elif cdp.mol[0].name == None and len(cdp.mol) == 1:
            mol_cont = cdp.mol[0]

        # Add the molecule if it doesn't exist.
        if mol_cont == None:
            # Add the molecule.
            cdp.mol.add_item(mol_name=mol_name)

            # Get the container.
            mol_cont = cdp.mol[-1]

        # Add the residue number to the ID string (residue name is ignored because only the number is unique).
        id = id + ':' + `res_num`

        # Get the corresponding residue container.
        res_cont = return_residue(id)

        # Add the residue if it doesn't exist.
        if res_cont == None:
            # Add the residue.
            mol_cont.res.add_item(res_name=res_name, res_num=res_num)

            # Get the container.
            res_cont = mol_cont.res[-1]

        # Add the atom number to the ID string (atom name is ignored because only the number is unique).
        id = id + '@' + `atom_num`

        # Get the corresponding spin container.
        spin_cont = return_spin(id)

        # Add the spin if it doesn't exist.
        if spin_cont == None:
            # Add the spin.
            res_cont.spin.add_item(spin_name=atom_name, spin_num=atom_num)

            # Get the container.
            spin_cont = res_cont.spin[-1]

            # Print out when a spin is appended.
            write_line(sys.stdout, mol_name, res_num, res_name, atom_num, atom_name, mol_name_flag=True, res_num_flag=True, res_name_flag=True, spin_num_flag=True, spin_name_flag=True)

        # Add the position vector and element type to the spin container.
        if ave_pos:
            spin_cont.pos = pos
        else:
            if not hasattr(spin_cont, 'pos'):
                spin_cont.pos = []
            spin_cont.pos.append(pos)
        spin_cont.element = element


def read_pdb(file=None, dir=None, model=None, parser='scientific', fail=True, verbosity=1):
    """The PDB loading function.

    Parsers
    =======

    A number of parsers are available for reading PDB files.  These include:
    
        - 'scientific', the Scientific Python PDB parser.
        - 'internal', a low quality yet fast PDB parser built into relax.


    @keyword file:          The name of the PDB file to read.
    @type file:             str
    @keyword dir:           The directory where the PDB file is located.  If set to None, then the
                            file will be searched for in the current directory.
    @type dir:              str or None
    @keyword model:         The PDB model to extract from the file.  If set to None, then all models
                            will be loaded.
    @type model:            int or None
    @keyword parser:        The parser to be used to read the PDB file.
    @type parser:           str
    @keyword fail:          A flag which, if True, will cause a RelaxError to be raised if the PDB
                            file does not exist.  If False, then a RelaxWarning will be trown
                            instead.
    @type fail:             bool
    @keyword verbosity:     The amount of information to print to screen.  Zero corresponds to
                            minimal output while higher values increase the amount of output.  The
                            default value is 1.
    @type verbosity:        int
    @raise RelaxFileError:  If the fail flag is set, then a RelaxError is raised if the PDB file
                            does not exist.
    """

    # Test if the current data pipe exists.
    if not ds.current_pipe:
        raise RelaxNoPipeError

    # Alias the current data pipe.
    cdp = ds[ds.current_pipe]

    # The file path.
    file_path = get_file_path(file, dir)

    # Try adding '.pdb' to the end of the file path, if the file can't be found.
    if not access(file_path, F_OK):
        file_path = file_path + '.pdb'

    # Test if the file exists.
    if not access(file_path, F_OK):
        if fail:
            raise RelaxFileError, ('PDB', file_path)
        else:
            warn(RelaxNoPDBFileWarning(file_path))
            return

    # Check that the parser is the same as the currently loaded PDB files.
    if hasattr(cdp, 'structure') and cdp.structure.id != parser:
        raise RelaxError, "The " + `parser` + " parser does not match the " + `cdp.structure.id` + " parser of the PDB loaded into the current pipe."

    # Place the parser specific structural object into the relax data store.
    if not hasattr(cdp, 'structure'):
        if parser == 'scientific':
            cdp.structure = Scientific_data()
        elif parser == 'internal':
            cdp.structure = Internal()

    # Load the structures.
    cdp.structure.load_pdb(file_path, model, verbosity)

    # Load into Molmol (if running).
    molmol.open_pdb()


def set_vector(spin=None, xh_vect=None):
    """Place the XH unit vector into the spin container object.

    @keyword spin:      The spin container object.
    @type spin:         SpinContainer instance
    @keyword xh_vect:   The unit vector parallel to the XH bond.
    @type xh_vect:      array of len 3
    """

    # Place the XH unit vector into the container.
    spin.xh_vect = xh_vect


def vectors(attached=None, spin_id=None, struct_index=None, verbosity=1, ave=True, unit=True):
    """Extract the bond vectors from the loaded structures.

    @keyword attached:      The name of the atom attached to the spin, as given in the structural
                            file.  Regular expression can be used, for example 'H*'.  This uses
                            relax rather than Python regular expression (i.e. shell like syntax).
    @type attached:         str
    @keyword spin_id:       The spin identifier string.
    @type spin_id:          str
    @keyword struct_index:  The index of the structure to extract the vector from.  If None, all
                            vectors will be extracted.
    @type struct_index:     str
    @keyword verbosity:     The higher the value, the more information is printed to screen.
    @type verbosity:        int
    @keyword ave:           A flag which if True will cause the average of all vectors to be
                            extracted.
    @type ave:              bool
    @keyword unit:          A flag which if True will cause the function to calculate the unit
                            vectors.
    @type unit:             bool
    """

    # Alias the current data pipe.
    cdp = ds[ds.current_pipe]

    # Test if the PDB file has been loaded.
    if not hasattr(cdp, 'structure'):
        raise RelaxPdbError

    # Test if sequence data is loaded.
    if not exists_mol_res_spin_data():
        raise RelaxNoSequenceError

    # Print out.
    if verbosity:
        # Number of structures.
        num = cdp.structure.num_structures()

        # Multiple structures loaded.
        if num > 1:
            if struct_index:
                print "Extracting vectors for structure " + `struct_index` + "."
            else:
                print "Extracting vectors for all " + `num` + " structures."
                if ave:
                    print "Averaging all vectors."

        # Single structure loaded.
        else:
            print "Extracting vectors from the single structure."

        # Unit vectors.
        if unit:
            print "Calculating the unit vectors."

    # Determine if the attached atom is a proton.
    proton = False
    if relax_re.search('.*H.*', attached) or relax_re.search(attached, 'H'):
        proton = True
    if verbosity:
        if proton:
            print "The attached atom is a proton."
        else:
            print "The attached atom is not a proton."
        print

    # Set the variable name in which the vectors will be stored.
    if proton:
        object_name = 'xh_vect'
    else:
        object_name = 'bond_vect'

    # Loop over the spins.
    for spin, mol_name, res_num, res_name in spin_loop(selection=spin_id, full_info=True):
        # Skip deselected spins.
        if not spin.select:
            continue

        # The spin identification string.
        id = generate_spin_id(mol_name, res_num, res_name, spin.num, spin.name)

        # Test that the spin number or name are set (one or both are essential for the identification of the atom).
        if spin.num == None and spin.name == None:
            warn(RelaxWarning("Either the spin number or name must be set for the spin " + `id` + " to identify the corresponding atom in the structure."))
            continue

        # The bond vector already exists.
        if hasattr(spin, object_name):
            obj = getattr(spin, object_name)
            if obj:
                warn(RelaxWarning("The bond vector for the spin " + `id` + " already exists."))
                continue

        # Get the bond info.
        bond_vectors, attached_name, warnings = cdp.structure.bond_vectors(atom_id=id, attached_atom=attached, struct_index=struct_index, return_name=True, return_warnings=True)

        # No attached atom.
        if not bond_vectors:
            # Warning messages.
            if warnings:
                warn(RelaxWarning(warnings + " (atom ID " + `id` + ")."))

            # Skip the spin.
            continue

        # Set the attached atom name.
        if not hasattr(spin, 'attached_atom'):
            spin.attached_atom = attached_name
        elif spin.attached_atom != attached_name:
            raise RelaxError, "The " + `spin.attached_atom` + " atom already attached to the spin does not match the attached atom " + `attached_name` + "."

        # Initialise the average vector.
        if ave:
            ave_vector = zeros(3, float64)

        # Loop over the individual vectors.
        for i in xrange(len(bond_vectors)):
            # Unit vector.
            if unit:
                # Normalisation factor.
                norm_factor = sqrt(dot(bond_vectors[i], bond_vectors[i]))

                # Test for zero length.
                if norm_factor == 0.0:
                    warn(RelaxZeroVectorWarning(id))

                # Calculate the normalised vector.
                else:
                    bond_vectors[i] = bond_vectors[i] / norm_factor

            # Sum the vectors.
            if ave:
                ave_vector = ave_vector + bond_vectors[i]

        # Average.
        if ave:
            vector = ave_vector / float(len(bond_vectors))
        else:
            vector = bond_vectors

        # Set the vector.
        setattr(spin, object_name, vector)

        # Print out of modified spins.
        if verbosity:
            print "Extracted " + spin.name + "-" + attached_name + " vectors for " + `id` + '.'


def write_pdb(file=None, dir=None, struct_index=None, force=False):
    """The PDB writing function.

    @keyword file:          The name of the PDB file to write.
    @type file:             str
    @keyword dir:           The directory where the PDB file will be placed.  If set to None, then
                            the file will be placed in the current directory.
    @type dir:              str or None
    @keyword stuct_index:   The index of the structure to write.  If set to None, then all
                            structures will be written.
    @type stuct_index:      int or None
    @keyword force:         The force flag which if True will cause the file to be overwritten.
    @type force:            bool
    """

    # Test if the current data pipe exists.
    if not ds.current_pipe:
        raise RelaxNoPipeError

    # Alias the current data pipe.
    cdp = ds[ds.current_pipe]

    # Check if the structural object exists.
    if not hasattr(cdp, 'structure'):
        raise RelaxError, "No structural data is present in the current data pipe."

    # Check if the structural object is writable.
    if cdp.structure.id in ['scientific']:
        raise RelaxError, "The structures from the " + cdp.structure.id + " parser are not writable."

    # The file path.
    file_path = get_file_path(file, dir)

    # Add '.pdb' to the end of the file path if it isn't there yet.
    if not search(".pdb$", file_path):
        file_path = file_path + '.pdb'

    # Open the file for writing.
    file = open_write_file(file_path, force=force)

    # Write the structures.
    cdp.structure.write_pdb(file, struct_index=struct_index)
