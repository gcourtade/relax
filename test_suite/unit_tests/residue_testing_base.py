###############################################################################
#                                                                             #
# Copyright (C) 2007-2008 Edward d'Auvergne                                   #
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

# relax module imports.
from data import Data as relax_data_store
from relax_errors import RelaxError, RelaxNoPipeError, RelaxSpinSelectDisallowError


class Residue_base_class:
    """Testing base class for 'prompt.residue' and corresponding 'generic_fns.mol_res_spin' fns.

    This base class also contains many shared unit tests.
    """


    def setUp(self):
        """Set up for all the residue unit tests."""

        # Reset the relax data storage object.
        relax_data_store.__reset__()

        # Add a data pipe to the data store.
        relax_data_store.add(pipe_name='orig', pipe_type='mf')

        # Add a second data pipe for copying tests.
        relax_data_store.add(pipe_name='test', pipe_type='mf')

        # Set the current data pipe to 'orig'.
        relax_data_store.current_pipe = 'orig'


    def tearDown(self):
        """Reset the relax data storage object."""

        relax_data_store.__reset__()


    def setup_data(self):
        """Function for setting up some data for the unit tests."""

        # Create the first residue and add some data to its spin container.
        self.residue.create(1, 'Ala')
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 111
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 1
        relax_data_store['orig'].mol[0].name = 'Old mol'

        # Create a second molecule.
        relax_data_store['orig'].mol.add_item('New mol')

        # Copy the residue to the new molecule.
        self.residue.copy(res_from=':1', res_to='#New mol')
        self.residue.copy(res_from='#Old mol:1', res_to='#New mol:5')

        # Change the first residue's data.
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 222
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 2


    def test_copy_residue_between_molecules(self):
        """Test the copying of the residue data between different molecules.

        The function tested is both generic_fns.mol_res_spin.copy_residue() and
        prompt.residue.copy().
        """

        # Set up some data.
        self.setup_data()

        # Test the original residue.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, 222)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].x, 2)

        # Test the new residue 1.
        self.assertEqual(relax_data_store['orig'].mol[1].name, 'New mol')
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].spin[0].num, 111)
        self.assertEqual(relax_data_store['orig'].mol[1].res[0].spin[0].x, 1)

        # Test the new residue 5.
        self.assertEqual(relax_data_store['orig'].mol[1].res[1].num, 5)
        self.assertEqual(relax_data_store['orig'].mol[1].res[1].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[1].res[1].spin[0].num, 111)
        self.assertEqual(relax_data_store['orig'].mol[1].res[1].spin[0].x, 1)



    def test_copy_residue_between_pipes(self):
        """Test the copying of the residue data between different data pipes.

        The function tested is both generic_fns.mol_res_spin.copy_residue() and
        prompt.residue.copy().
        """

        # Create the first residue and add some data to its spin container.
        self.residue.create(1, 'Ala')
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 111
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 1

        # Copy the residue to the second data pipe.
        self.residue.copy(res_from=':1', pipe_to='test')
        self.residue.copy(pipe_from='orig', res_from=':1', pipe_to='test', res_to=':5')

        # Change the first residue's data.
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 222
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 2

        # Test the original residue.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, 222)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].x, 2)

        # Test the new residue 1.
        self.assertEqual(relax_data_store['test'].mol[0].res[0].num, 1)
        self.assertEqual(relax_data_store['test'].mol[0].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['test'].mol[0].res[0].spin[0].num, 111)
        self.assertEqual(relax_data_store['test'].mol[0].res[0].spin[0].x, 1)

        # Test the new residue 5.
        self.assertEqual(relax_data_store['test'].mol[0].res[1].num, 5)
        self.assertEqual(relax_data_store['test'].mol[0].res[1].name, 'Ala')
        self.assertEqual(relax_data_store['test'].mol[0].res[1].spin[0].num, 111)
        self.assertEqual(relax_data_store['test'].mol[0].res[1].spin[0].x, 1)


    def test_copy_residue_between_pipes_fail_no_pipe(self):
        """Test the copying of the residue data between different data pipes.

        The function tested is both generic_fns.mol_res_spin.copy_residue() and
        prompt.residue.copy().
        """

        # Create the first residue and add some data to its spin container.
        self.residue.create(1, 'Ala')
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 111
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 1

        # Copy the residue to the second data pipe.
        self.assertRaises(RelaxNoPipeError, self.residue.copy, res_from=':1', pipe_to='test2')


    def test_copy_residue_within_molecule(self):
        """Test the copying of the residue data within a single molecule.

        The function tested is both generic_fns.mol_res_spin.copy_residue() and
        prompt.residue.copy().
        """

        # Create the first residue and add some data to its spin container.
        self.residue.create(1, 'Ala')
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 111
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 1

        # Copy the residue a few times.
        self.residue.copy(res_from=':1', res_to=':2')
        self.residue.copy(res_from=':1', pipe_to='orig', res_to=':3')

        # Change the first residue's data.
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 222
        relax_data_store['orig'].mol[0].res[0].spin[0].x = 2

        # Copy the residue once more.
        self.residue.copy(res_from=':1', res_to=':4,Met')

        # Test the original residue.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, 222)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].x, 2)

        # Test the new residue 2.
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].num, 2)
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].spin[0].num, 111)
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].spin[0].x, 1)

        # Test the new residue 3.
        self.assertEqual(relax_data_store['orig'].mol[0].res[2].num, 3)
        self.assertEqual(relax_data_store['orig'].mol[0].res[2].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[0].res[2].spin[0].num, 111)
        self.assertEqual(relax_data_store['orig'].mol[0].res[2].spin[0].x, 1)

        # Test the new residue 4.
        self.assertEqual(relax_data_store['orig'].mol[0].res[3].num, 4)
        self.assertEqual(relax_data_store['orig'].mol[0].res[3].name, 'Met')
        self.assertEqual(relax_data_store['orig'].mol[0].res[3].spin[0].num, 222)
        self.assertEqual(relax_data_store['orig'].mol[0].res[3].spin[0].x, 2)


    def test_copy_residue_within_molecule_fail1(self):
        """The failure of copying residue data within a molecule of a non-existent residue.

        The function tested is both generic_fns.mol_res_spin.copy_residue() and
        prompt.residue.copy().
        """

        # Create a few residues.
        self.residue.create(1, 'Ala')
        self.residue.create(-1, 'His')

        # Copy a non-existent residue (1 Met).
        self.assertRaises(RelaxError, self.residue.copy, res_from=':Met', res_to=':2,Gly')


    def test_copy_residue_within_molecule_fail2(self):
        """The failure of copying residue data within a molecule to a residue which already exists.

        The function tested is both generic_fns.mol_res_spin.copy_residue() and
        prompt.residue.copy().
        """

        # Create a few residues.
        self.residue.create(1, 'Ala')
        self.residue.create(-1, 'His')

        # Copy a residue to a number which already exists.
        self.assertRaises(RelaxError, self.residue.copy, res_from=':1', res_to=':-1,Gly')


    def test_create_residue(self):
        """Test the creation of a residue.

        The function tested is both generic_fns.mol_res_spin.create_residue() and
        prompt.residue.create().
        """

        # Create a few new residues.
        self.residue.create(1, 'Ala')
        self.residue.create(2, 'Leu')
        self.residue.create(-3, 'Ser')

        # Test that the residue numbers are correct.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, 1)
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].num, 2)
        self.assertEqual(relax_data_store['orig'].mol[0].res[2].num, -3)

        # Test that the residue names are correct.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].name, 'Leu')
        self.assertEqual(relax_data_store['orig'].mol[0].res[2].name, 'Ser')


    def test_create_residue_fail(self):
        """Test the failure of residue creation (by supplying two residues with the same number).

        The function tested is both generic_fns.mol_res_spin.create_residue() and
        prompt.residue.create().
        """

        # Create the first residue.
        self.residue.create(1, 'Ala')

        # Assert that a RelaxError occurs when the next added residue has the same sequence number as the first.
        self.assertRaises(RelaxError, self.residue.create, 1, 'Ala')


    def test_delete_residue_name(self):
        """Test residue deletion using residue name identifiers.

        The function tested is both generic_fns.mol_res_spin.delete_residue() and
        prompt.residue.delete().
        """

        # Create some residues and add some data to the spin containers.
        self.residue.create(1, 'Ala')
        self.residue.create(2, 'Ala')
        self.residue.create(3, 'Ala')
        self.residue.create(4, 'Gly')
        relax_data_store['orig'].mol[0].res[3].spin[0].num = 111
        relax_data_store['orig'].mol[0].res[3].spin[0].x = 1

        # Delete the first residue.
        self.residue.delete(res_id=':Ala')

        # Test that the first residue is 4 Gly.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, 4)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, 'Gly')
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].spin[0].num, 111)
        self.assert_(hasattr(relax_data_store['orig'].mol[0].res[0].spin[0], 'x'))


    def test_delete_residue_num(self):
        """Test residue deletion using residue number identifiers.

        The function tested is both generic_fns.mol_res_spin.delete_residue() and
        prompt.residue.delete().
        """

        # Create some residues and add some data to the spin containers.
        self.residue.create(1, 'Ala')
        self.residue.create(2, 'Ala')
        self.residue.create(3, 'Ala')
        self.residue.create(4, 'Gly')
        relax_data_store['orig'].mol[0].res[3].spin[0].num = 111
        relax_data_store['orig'].mol[0].res[3].spin[0].x = 1

        # Delete the first residue.
        self.residue.delete(res_id=':1')

        # Test that the sequence.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, 2)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].num, 3)
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].name, 'Ala')
        self.assertEqual(relax_data_store['orig'].mol[0].res[2].num, 4)
        self.assertEqual(relax_data_store['orig'].mol[0].res[2].name, 'Gly')
        self.assertEqual(relax_data_store['orig'].mol[0].res[2].spin[0].num, 111)
        self.assert_(hasattr(relax_data_store['orig'].mol[0].res[2].spin[0], 'x'))


    def test_delete_residue_all(self):
        """Test the deletion of all residues.

        The function tested is both generic_fns.mol_res_spin.delete_residue() and
        prompt.residue.delete().
        """

        # Create some residues and add some data to the spin containers.
        self.residue.create(1, 'Ala')
        self.residue.create(2, 'Ala')
        self.residue.create(3, 'Ala')
        self.residue.create(4, 'Ala')
        relax_data_store['orig'].mol[0].res[3].spin[0].num = 111
        relax_data_store['orig'].mol[0].res[3].spin[0].x = 1

        # Delete all residues.
        self.residue.delete(res_id=':1-4')

        # Test that the first residue defaults back to the empty residue.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, None)
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, None)


    def test_delete_residue_shift(self):
        """Test the deletion of multiple residues.

        The function tested is both generic_fns.mol_res_spin.delete_residue() and
        prompt.residue.delete().
        """

        # Create some residues and add some data to the spin containers.
        self.residue.create(1, 'Ala')
        self.residue.create(2, 'Ala')
        self.residue.create(3, 'Ala')
        self.residue.create(4, 'Ala')
        relax_data_store['orig'].mol[0].res[3].spin[0].num = 111
        relax_data_store['orig'].mol[0].res[3].spin[0].x = 1

        # Delete the first and third residues.
        self.residue.delete(res_id=':1,3')

        # Test that the remaining residues.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, 2)
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].num, 4)
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].spin[0].num, 111)
        self.assert_(hasattr(relax_data_store['orig'].mol[0].res[1].spin[0], 'x'))


    def test_delete_residue_fail(self):
        """Test the failure of residue deletion when an atom id is supplied.

        The function tested is both generic_fns.mol_res_spin.delete_residue() and
        prompt.residue.delete().
        """

        # Supply an atom id.
        self.assertRaises(RelaxSpinSelectDisallowError, self.residue.delete, res_id='@2')


    def test_display_residue(self):
        """Test the display of residue information.

        The function tested is both generic_fns.mol_res_spin.display_residue() and
        prompt.residue.display().
        """

        # Set up some data.
        self.setup_data()

        # The following should all work without error.
        self.residue.display()
        self.residue.display(':1')
        self.residue.display('#New mol:5')
        self.residue.display('#Old mol:1')


    def test_display_residue_fail(self):
        """Test the failure of the display of residue information.

        The function tested is both generic_fns.mol_res_spin.display_residue() and
        prompt.residue.display().
        """

        # Set up some data.
        self.setup_data()

        # The following should fail.
        self.assertRaises(RelaxSpinSelectDisallowError, self.residue.display, '@N')


    def test_rename_residue(self):
        """Test the renaming of a residue.

        The function tested is both generic_fns.mol_res_spin.name_residue() and
        prompt.residue.name().
        """

        # Create the first residue and add some data to its spin container.
        self.residue.create(-10, 'His')

        # Rename the residue.
        self.residue.rename(res_id=':-10', new_name='K')

        # Test that the residue has been renamed.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, 'K')


    def test_rename_residue_many(self):
        """Test the renaming of multiple residues.

        The function tested is both generic_fns.mol_res_spin.name_residue() and
        prompt.residue.name().
        """

        # Create the first residue and add some data to its spin container.
        self.residue.create(1, 'Ala')
        relax_data_store['orig'].mol[0].res[0].spin[0].num = 111

        # Copy the residue a few times.
        self.residue.copy(res_from=':1', res_to=':2')
        self.residue.copy(res_from=':1', res_to=':3')

        # Change the first residue's data.
        relax_data_store['orig'].mol[0].res[0].name = 'His'

        # Copy the residue once more.
        self.residue.copy(res_from=':1', res_to=':4,Met')

        # Rename all alanines.
        self.residue.rename(res_id=':Ala', new_name='Gln')

        # Test the renaming of alanines.
        self.assertEqual(relax_data_store['orig'].mol[0].res[1].name, 'Gln')
        self.assertEqual(relax_data_store['orig'].mol[0].res[2].name, 'Gln')

        # Test that the other residues have not changed.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].name, 'His')
        self.assertEqual(relax_data_store['orig'].mol[0].res[3].name, 'Met')


    def test_rename_residue_no_spin(self):
        """Test the failure of renaming a residue when a spin id is given.

        The function tested is both generic_fns.mol_res_spin.name_residue() and
        prompt.residue.name().
        """

        # Try renaming using a atom id.
        self.assertRaises(RelaxSpinSelectDisallowError, self.residue.rename, res_id='@111', new_name='K')


    def test_renumber_residue(self):
        """Test the renumbering of a residue.

        The function tested is both generic_fns.mol_res_spin.number_residue() and
        prompt.residue.number().
        """

        # Create the first residue and add some data to its spin container.
        self.residue.create(-10, 'His')

        # Rename the residue.
        self.residue.renumber(res_id=':-10', new_number=10)

        # Test that the residue has been renumbered.
        self.assertEqual(relax_data_store['orig'].mol[0].res[0].num, 10)


    def test_renumber_residue_many_fail(self):
        """Test the renaming of multiple residues.

        The function tested is both generic_fns.mol_res_spin.number_residue() and
        prompt.residue.number().
        """

        # Create the first residue and add some data to its spin container.
        self.residue.create(1, 'Ala')

        # Copy the residue a few times.
        self.residue.copy(res_from=':1', res_to=':2')
        self.residue.copy(res_from=':1', res_to=':3')

        # Change the first residue's data.
        relax_data_store['orig'].mol[0].res[0].spin[0].name = 'His'

        # Copy the residue once more.
        self.residue.copy(res_from=':1', res_to=':4,Met')

        # Try renumbering all alanines.
        self.assertRaises(RelaxError, self.residue.renumber, res_id=':Ala', new_number=10)


    def test_renumber_residue_no_spin(self):
        """Test the failure of renaming a residue when a spin id is given.

        The function tested is both generic_fns.mol_res_spin.number_residue() and
        prompt.residue.number().
        """

        # Try renaming using a atom id.
        self.assertRaises(RelaxSpinSelectDisallowError, self.residue.renumber, res_id='@111', new_number=10)
