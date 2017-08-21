###############################################################################
#                                                                             #
# Copyright (C) 2013-2014 Edward d'Auvergne                                   #
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
"""Script for generating a save file of the R2eff fitted model."""

# Python module imports.
from os import sep

# relax module imports.
from auto_analyses.relax_disp import Relax_disp
from data_store import Relax_data_store; ds = Relax_data_store()
from status import Status; status = Status()


# Analysis variables.
#####################

# The dispersion models.
MODELS = ['R2eff']

# The grid search size (the number of increments per dimension).
GRID_INC = 10

# The number of Monte Carlo simulations to be used for error analysis at the end of the analysis.
MC_NUM = 500


# Set up the data pipe.
#######################

# Create the data pipe.
pipe_name = 'base pipe'
pipe_bundle = 'relax_disp'
pipe.create(pipe_name=pipe_name, bundle=pipe_bundle, pipe_type='relax_disp')

# The path to the data files.
data_path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'r1rho_off_res_tp02'

# Create the sequence data.
spin.create(res_name='Trp', res_num=1, spin_name='N')
spin.create(res_name='Trp', res_num=2, spin_name='N')

# Set the isotope information.
spin.isotope(isotope='15N')

# Loop over the frequencies.
frq = [500, 800]
frq_label = ['500MHz', '800MHz']
error = 200000.0
for frq_index in range(len(frq)):
    # Load the R1 data.
    label = 'R1_%s' % frq_label[frq_index]
    relax_data.read(ri_id=label, ri_type='R1', frq=frq[frq_index]*1e6, file='%s.out'%label, dir=data_path, mol_name_col=1, res_num_col=2, res_name_col=3, spin_num_col=4, spin_name_col=5, data_col=6, error_col=7)

    # The spectral data - spectrum ID, peak lists, offset frequency (Hz).
    data = []
    spin_lock = [1000.0, 1500.0, 2000.0, 2500.0, 3000.0, 3500.0, 4000.0, 4500.0, 5000.0, 5500.0, 6000.0]
    for spin_lock_index in range(len(spin_lock)):
        data.append(["nu_%s_%s" % (spin_lock[spin_lock_index], frq_label[frq_index]), "nu_%s_%s.list" % (spin_lock[spin_lock_index], frq_label[frq_index]), spin_lock[spin_lock_index]])

    # Load the reference spectrum.
    id = 'ref_%s' % frq_label[frq_index]
    spectrum.read_intensities(file="ref_%s.list" % frq_label[frq_index], dir=data_path, spectrum_id=id, int_method='height', dim=1)
    spectrum.baseplane_rmsd(spectrum_id=id, error=error)

    # Set the relaxation dispersion experiment type.
    relax_disp.exp_type(spectrum_id=id, exp_type='R1rho')

    # Set as the reference.
    relax_disp.spin_lock_field(spectrum_id=id, field=None)
    relax_disp.spin_lock_offset(spectrum_id=id, offset=110.0)
    relax_disp.relax_time(spectrum_id=id, time=0.1)

    # Set the spectrometer frequency.
    spectrometer.frequency(id=id, frq=frq[frq_index], units='MHz')

    # Loop over the spectral data, loading it and setting the metadata.
    for id, file, field in data:
        # Load the peak intensities and set the errors.
        spectrum.read_intensities(file=file, dir=data_path, spectrum_id=id, int_method='height')
        spectrum.baseplane_rmsd(spectrum_id=id, error=error)

        # Set the relaxation dispersion experiment type.
        relax_disp.exp_type(spectrum_id=id, exp_type='R1rho')

        # Set the relaxation dispersion spin-lock field strength (nu1).
        relax_disp.spin_lock_field(spectrum_id=id, field=field)

        # Set the spin-lock offset.
        relax_disp.spin_lock_offset(spectrum_id=id, offset=110.0)

        # Set the relaxation times.
        relax_disp.relax_time(spectrum_id=id, time=0.1)

        # Set the spectrometer frequency.
        spectrometer.frequency(id=id, frq=frq[frq_index], units='MHz')

# Clustering.
#relax_disp.cluster(cluster_id='cluster', spin_id='@N,NE1')

# Read the chemical shift data.
chemical_shift.read(file='ref_500MHz.list', dir=data_path)



# Auto-analysis execution.
##########################

# Do not change!
Relax_disp(pipe_name=pipe_name, pipe_bundle=pipe_bundle, results_dir='.', models=MODELS, grid_inc=GRID_INC, mc_sim_num=MC_NUM)

# Save the program state.
state.save('r2eff_values', force=True)
