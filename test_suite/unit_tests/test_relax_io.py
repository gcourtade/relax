###############################################################################
#                                                                             #
# Copyright (C) 2007 Edward d'Auvergne                                        #
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
from os import sep
from unittest import TestCase

# relax module imports.
import relax_io


class Test_relax_io(TestCase):
    """Unit tests for the functions of the 'relax_io' module."""


    def test_get_file_path(self):
        """Test for file paths which should remain unmodified by relax_io.get_file_path."""

        # Some file paths that shouldn't change.
        file1 = 'test'
        file2 = 'test'+sep+'aaa'
        file3 = sep+'home'+sep+'test'+sep+'aaa'

        # Check that nothing changes.
        self.assertEqual(relax_io.get_file_path(file1), file1)
        self.assertEqual(relax_io.get_file_path(file2), file2)
        self.assertEqual(relax_io.get_file_path(file3), file3)


    def test_get_file_path_with_dir(self):
        """The modification of file paths by relax_io.get_file_path when a directory is supplied."""

        # Some file paths.
        file1 = 'test'
        file2 = 'test'+sep+'aaa'
        file3 = sep+'home'+sep+'test'+sep+'aaa'

        # Some directories.
        dir1 = sep+'usr'
        dir2 = 'usr'
        dir3 = sep+'usr'

        # Check that nothing changes.
        self.assertEqual(relax_io.get_file_path(file1, dir1), dir1+sep+file1)
        self.assertEqual(relax_io.get_file_path(file2, dir2), dir2+sep+file2)
        self.assertEqual(relax_io.get_file_path(file3, dir=dir3), dir3+sep+file3)


    def test_get_file_path_with_homedir(self):
        """The modification of file paths with '~', by relax_io.get_file_path."""

        # Some file paths.
        file1 = '~'+sep+'test'
        file2 = '~'+sep+'test'+sep+'aaa'

        # Check that nothing changes.
        self.assertNotEqual(relax_io.get_file_path(file1), file1)
        self.assertNotEqual(relax_io.get_file_path(file2), file2)
