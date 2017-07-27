###############################################################################
#                                                                             #
# Copyright (C) 2013 Edward d'Auvergne                                        #
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
"""Script for testing the fitting of signless T data (J+D)."""

# Python module imports.
from os import sep

# relax module imports.
from status import Status; status = Status()



# Path of the alignment data and structure.
DATA_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'align_data'
STRUCT_PATH = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'structures'

# Create the data pipe.
self._execute_uf(uf_name='pipe.create', pipe_name='1J RDCs', pipe_type='N-state')

# Load the structure.
self._execute_uf(uf_name='structure.read_xyz', file='strychnine.xyz', dir=STRUCT_PATH)

# Set up the 13C and 1H spins information.
self._execute_uf(uf_name='structure.load_spins', spin_id='@C*', ave_pos=False)
self._execute_uf(uf_name='structure.load_spins', spin_id='@H*', ave_pos=False)

# Define the nuclear isotopes of all spins.
self._execute_uf(uf_name='spin.isotope', isotope='13C', spin_id='@C*')
self._execute_uf(uf_name='spin.isotope', isotope='1H', spin_id='@H*')

# Define the magnetic dipole-dipole relaxation interaction.
self._execute_uf(uf_name='interatom.read_dist', file='one_bond_RDC_data_strychnine.txt', dir=DATA_PATH, unit='Angstrom', spin_id1_col=1, spin_id2_col=2, data_col=8)
self._execute_uf(uf_name='interatom.unit_vectors', ave=False)

# Load the J and J+D data.
self._execute_uf(uf_name='rdc.read', align_id='Gel', file='one_bond_RDC_data_strychnine.txt', dir=DATA_PATH, data_type='T', spin_id1_col=1, spin_id2_col=2, data_col=3, error_col=4, absolute=True)
self._execute_uf(uf_name='j_coupling.read', file='one_bond_RDC_data_strychnine.txt', dir=DATA_PATH, spin_id1_col=1, spin_id2_col=2, data_col=5, error_col=6, sign_col=7)

# Set up the model.
self._execute_uf(uf_name='n_state_model.select_model', model='fixed')

# Minimisation.
self._execute_uf(uf_name='minimise.grid_search', inc=3)
self._execute_uf(uf_name='minimise.execute', min_algor='simplex')

# Bootstrapping simulations.
self._execute_uf(uf_name='monte_carlo.setup', number=10)
self._execute_uf(uf_name='monte_carlo.create_data', method='direct')
self._execute_uf(uf_name='monte_carlo.initial_values')
self._execute_uf(uf_name='minimise.execute', min_algor='simplex')
self._execute_uf(uf_name='monte_carlo.error_analysis')

# Show the tensors.
self._execute_uf(uf_name='align_tensor.display')

# Create a correlation plot.
self._execute_uf(uf_name='rdc.corr_plot', file='devnull', force=True)

# Print out.
print(cdp)
