# Python imports
from os import getcwd, sep
from numpy import array, float64, zeros

# relax module imports.
from lib.io import open_write_file, write_data
from pipe_control.mol_res_spin import display_spin, generate_spin_string, return_spin
from pipe_control import value
from specific_analyses.api import return_api

# Create pipe
pipe.create('relax_disp', 'relax_disp')

# The specific analysis API object.
api = return_api()

# Variables
prev_data_path = getcwd()
result_filename = 'FT_-_TSMFK01_-_min_-_128_-_free_spins.bz2'

# Read data in
results.read(prev_data_path + sep + result_filename)

# Get residue of interest. L61 is 
cur_spin_id = ":%i@%s"%(61, 'N')

# Get the spin container.
mol_name, cur_resi, cur_resn, cur_spin = return_spin(spin_id=cur_spin_id, full_info=True)
cur_spin_num = cur_spin.num
cur_spin_name = cur_spin.name

# Get the chi2 value
pre_chi2 = cur_spin.chi2

# Define surface map settings.
dx_inc = 3

# Lower bounds
params = ['dw', 'k_AB']
lower = [9.9, 1.0]
upper = [11.1, 5.0]

# Get the current point for clustered mininimisation.
pcm = [cur_spin.dw, cur_spin.k_AB]
print("Min cluster point %s=%3.3f, %s=%3.3f, with chi2=%3.3f" % (params[0], pcm[0], params[1], pcm[1], pre_chi2))
headings = [params[0], params[1], "chi2"]

# Initialise.
# Number of parameters
n = 2

# Get the default map bounds.
bounds = zeros((n, 2), float64)

# Lower bounds.
bounds[:, 0] = array(lower, float64)

# Upper bounds.
bounds[:, 1] = array(upper, float64)

# Setup the step sizes.
step_size = zeros(n, float64)
step_size = (bounds[:, 1] - bounds[:, 0]) / dx_inc

# Placeholder to update values.
values = zeros(n, float64)

# Initial value of the first parameter.
values[0] = bounds[0, 0]
percent = 0.0
percent_inc = 100.0 / (dx_inc + 1.0)**(n)
print("%-10s%8.3f%-1s" % ("Progress:", percent, "%"))

# Collect all chi2, to help finding a reasobale chi level.
all_chi = []

# Collect data.
data = []
# Append point as first data.
data.append(["%3.3f"%pcm[0], "%3.3f"%pcm[1], "%3.3f"%pre_chi2 ])

# Loop over the spin blocks.
cluster_spin_ids = []
for spin_ids in api.model_loop():
    cluster_spin_ids.append(spin_ids)

cur_spin_ids = cluster_spin_ids[0]

# Display spins
#display_spin()

# Loop over the first parameter.
# Start counter from 1003, so values correspond to line number.
counter = 1003
for i in range((dx_inc + 1)):
    # Initial value of the second parameter.
    values[1] = bounds[1, 0]

    # Loop over the second parameter.
    for j in range((dx_inc + 1)):
        # Set the value.
        value.set(val=values, param=params, spin_id=cur_spin_id, force=True)

        # Calculate the function values.
        api.calculate(spin_id=cur_spin_id, verbosity=0)

        # Now copy the spin
        new_res_name = "%s_%s=%1.1f_%s=%1.1f" % (cur_resn, params[0], values[0], params[1], values[1])
        #spin.create(spin_name=cur_spin_name, spin_num=cur_spin_num, res_name=new_res_name, res_num=counter, mol_name=mol_name)
        residue.create(res_num=counter, res_name=new_res_name, mol_name=mol_name)
        new_spin_id =  ":%i@%s"%(counter, 'N')
        spin.copy(pipe_from=None, spin_from=cur_spin_id, pipe_to=None, spin_to=new_spin_id)

        # Get the minimisation statistics for the model.
        k_stat, n_stat, chi2 = api.model_statistics(spin_id=cur_spin_id)
        #print(k_stat, n_stat, chi2, "point is %s=%3.3f, %s=%3.3f"% (params[0], values[0], params[1], values[1]))

        # Progress incrementation and printout.
        percent = percent + percent_inc
        print("%-10s%8.3f%-8s%-8g" % ("Progress:", percent, "%,  " + repr(values) + ",  f(x): ", chi2))

        # Append to data.
        data.append(["%3.3f"%values[0], "%3.3f"%values[1], "%3.3f"%chi2 ])

        # Save all values of chi2. To help find reasonale level for the Innermost, Inner, Middle and Outer Isosurface.
        all_chi.append(chi2)

        # Increment the value of the second parameter.
        values[1] = values[1] + step_size[1]

        counter += 1

    # Increment the value of the first parameter.
    values[0] = values[0] + step_size[0]

print("\nMin cluster point %s=%3.3f, %s=%3.3f, with chi2=%3.3f" % (params[0], pcm[0], params[1], pcm[1], pre_chi2))

# Open file
file_name = '3_surface_chi2.txt'
surface_file = open_write_file(file_name=file_name, dir=None, force=True)
write_data(out=surface_file, headings=headings, data=data)

# Close file
surface_file.close()

# Check spins.
display_spin()

relax_disp.plot_disp_curves(dir='grace', y_axis='r2_eff', x_axis='disp', num_points=1000, extend_hz=500.0, extend_ppm=500.0, interpolate='disp', force=False)
