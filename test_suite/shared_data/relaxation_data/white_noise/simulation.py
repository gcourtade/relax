"""Simulation of white noise through an exponential.

To run the script, type:

$ ../../../../relax simulation.py
"""

# relax module imports.
from lib.statistics import bucket, gaussian
from pipe_control.mol_res_spin import return_spin


# Create the data pipe.
pipe.create('white noise', 'relax_fit')

# Add a single spin.
spin.create(res_num=1, res_name='Gly', spin_name='N')

# Get the spin.
spin_cont = return_spin(':1@N')

# Set up the synthetic peak intensities (rx = 2.25, i0 = 10000).
cdp.spectrum_ids = ['ncyc_1', 'ncyc_2', 'ncyc_3', 'ncyc_4', 'ncyc_5', 'ncyc_6', 'ncyc_7', 'ncyc_8', 'ncyc_9', 'ncyc_10']
times = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
intensities = [7985.162187593771, 6376.281516217733, 5091.564206075492, 4065.6965974059913, 3246.5246735834976, 2592.4026064589157, 2070.0755268115263, 1652.9888822158653, 1319.9384318783023, 1053.9922456186434]
cdp.relax_times = {}
spin_cont.intensities = {}
spin_cont.intensity_err = {}
for i in range(len(times)):
    cdp.relax_times[cdp.spectrum_ids[i]] = times[i]
    spin_cont.intensities[cdp.spectrum_ids[i]] = intensities[i]
    spin_cont.intensity_err[cdp.spectrum_ids[i]] = 1000.0

# Set the relaxation curve type.
relax_fit.select_model('exp')

# Grid search.
grid_search(inc=11)

# Minimise.
minimise('simplex', constraints=False)

# Monte Carlo simulations.
monte_carlo.setup(number=100000)
monte_carlo.create_data()
monte_carlo.initial_values()
minimise('simplex', constraints=False)
monte_carlo.error_analysis()

# Bucket and write out the data.
dist = bucket(spin_cont.rx_sim, lower=0, upper=5, inc=100, verbose=True)
file = open('dist.agr', 'w')
file.write("@target G0.S0\n@type xy\n")
for i in range(len(dist)):
    file.write("%s %s\n" % (dist[i][0], dist[i][1]))
file.write("&\n")

# The Gaussian distribution.
file.write("@target G0.S1\n@type xy\n")
for i in range(len(dist)):
    pr = gaussian(dist[i][0], mu=2.25, sigma=spin_cont.rx_err)
    file.write("%s %s\n" % (dist[i][0], pr*0.05))
file.write("&\n")
file.close()

# Save the state.
state.save('state', force=True)
