###############################################################################
#                                                                             #
# Copyright (C) 2008-2014 Edward d'Auvergne                                   #
# Copyright (C) 2014 Troels E. Linnet                                         #
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

# Python module imports.
from os import sep

# relax module imports.
from data_store import Relax_data_store; ds = Relax_data_store()
from pipe_control import state
from specific_analyses.relax_disp.checks import get_times
from specific_analyses.relax_disp.disp_data import count_relax_times, get_curve_type, has_exponential_exp_type, loop_exp_frq, loop_exp_frq_offset, loop_exp_frq_offset_point, loop_exp_frq_offset_point_time, loop_time
from status import Status; status = Status()
from test_suite.unit_tests.base_classes import UnitTestCase


class Test_disp_data(UnitTestCase):
    """Unit tests for the functions of the specific_analyses.relax_disp.disp_data module."""

    def setUp(self):
        """Setup some structures for the unit tests."""

        # Create a dispersion data pipe.
        ds.add(pipe_name='orig', pipe_type='relax_disp')


    def test_count_relax_times_cpmg(self):
        """Unit test of the count_relax_times() function.

        This uses the data of the saved state attached to U{bug #21665<https://gna.org/bugs/?21665>}.
        """

        # Load the state.
        statefile = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21665.bz2'
        state.load_state(statefile, force=True)

        # Original data (exp_type, frq).
        data = [
            ['SQ CPMG', 499862140.0],
            ['SQ CPMG', 599890858.69999993]
        ]

        # Original indices (ei, mi).
        indices = [
            [0, 0],
            [0, 1]
        ]

        # Check the number of time counts.
        print("Checking the number of time counts.")
        for id in cdp.exp_type.keys():
            exp_type = cdp.exp_type[id]
            frq = cdp.spectrometer_frq[id]
            point = cdp.cpmg_frqs[id]
            count = count_relax_times(exp_type = exp_type, frq = frq, point = point, ei = cdp.exp_type_list.index(cdp.exp_type[id]))
            print(id, exp_type, frq, point, count)

            # Test the data
            if id.split('A')[0] == 'Z_':
                self.assertEqual(exp_type, data[0][0])
                self.assertEqual(frq, data[0][1])
            elif id.split('B')[0] == 'Z_':
                self.assertEqual(exp_type, data[1][0])
                self.assertEqual(frq, data[1][1])
            # Test the time count
            self.assertEqual(count, 1)


    def test_count_relax_times_r1rho(self):
        """Unit test of the count_relax_times() function.

        This uses the data of the saved state attached to U{bug #21344<https://gna.org/bugs/?21344>}.
        """

        # Load the state.
        statefile = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21344.bz2'
        state.load_state(statefile, force=True)

        # Original data (spectrum id: exp_type, frq, omega_rf_ppm, spin_lock_field_strength, time_spin_lock).
        data = {
        '46_0_35_0':['R1rho', 799777399.1, 118.078, 431.0, 0.0],
        '48_0_35_4':['R1rho', 799777399.1, 118.078, 431.0, 0.04],
        '47_0_35_10':['R1rho', 799777399.1, 118.078, 431.0, 0.1],
        '49_0_35_20':['R1rho', 799777399.1, 118.078, 431.0, 0.2],
        '36_0_39_0':['R1rho', 799777399.1, 118.078, 651.2, 0.0],
        '39_0_39_4':['R1rho', 799777399.1, 118.078, 651.2, 0.04],
        '37_0_39_10':['R1rho', 799777399.1, 118.078, 651.2, 0.1],
        '40_0_39_20':['R1rho', 799777399.1, 118.078, 651.2, 0.2],
        '38_0_39_40':['R1rho', 799777399.1, 118.078, 651.2, 0.4],
        '41_0_41_0':['R1rho', 799777399.1, 118.078, 800.5, 0.0],
        '44_0_41_4':['R1rho', 799777399.1, 118.078, 800.5, 0.04],
        '42_0_41_10':['R1rho', 799777399.1, 118.078, 800.5, 0.1],
        '45_0_41_20':['R1rho', 799777399.1, 118.078, 800.5, 0.2],
        '43_0_41_40':['R1rho', 799777399.1, 118.078, 800.5, 0.4],
        '31_0_43_0':['R1rho', 799777399.1, 118.078, 984.0, 0.0],
        '34_0_43_4':['R1rho', 799777399.1, 118.078, 984.0, 0.04],
        '32_0_43_10':['R1rho', 799777399.1, 118.078, 984.0, 0.1],
        '35_0_43_20':['R1rho', 799777399.1, 118.078, 984.0, 0.2],
        '33_0_43_40':['R1rho', 799777399.1, 118.078, 984.0, 0.4],
        '1_0_46_0':['R1rho', 799777399.1, 118.078, 1341.10, 0.0],
        '4_0_46_4':['R1rho', 799777399.1, 118.078, 1341.10, 0.04],
        '2_0_46_10':['R1rho', 799777399.1, 118.078, 1341.10, 0.1],
        '5_0_46_20':['R1rho', 799777399.1, 118.078, 1341.10, 0.2],
        '3_0_46_40':['R1rho', 799777399.1, 118.078, 1341.10, 0.4],
        '60_0_48_0':['R1rho', 799777399.1, 118.078, 1648.5, 0.0],
        '63_0_48_4':['R1rho', 799777399.1, 118.078, 1648.5, 0.04],
        '61_0_48_10':['R1rho', 799777399.1, 118.078, 1648.5, 0.1],
        '62_0_48_14':['R1rho', 799777399.1, 118.078, 1648.5, 0.14],
        '64_0_48_20':['R1rho', 799777399.1, 118.078, 1648.5, 0.2],
        '11_500_46_0':['R1rho', 799777399.1, 124.24703146206046, 1341.10, 0.0],
        '14_500_46_4':['R1rho', 799777399.1, 124.24703146206046, 1341.10, 0.04],
        '12_500_46_10':['R1rho', 799777399.1, 124.24703146206046, 1341.10, 0.1],
        '15_500_46_20':['R1rho', 799777399.1, 124.24703146206046, 1341.10, 0.2],
        '13_500_46_40':['R1rho', 799777399.1, 124.24703146206046, 1341.10, 0.4],
        '50_1000_41_0':['R1rho', 799777399.1, 130.41606292412092, 800.5, 0.0],
        '53_1000_41_4':['R1rho', 799777399.1, 130.41606292412092, 800.5, 0.04],
        '51_1000_41_10':['R1rho', 799777399.1, 130.41606292412092, 800.5, 0.1],
        '54_1000_41_20':['R1rho', 799777399.1, 130.41606292412092, 800.5, 0.2],
        '52_1000_41_40':['R1rho', 799777399.1, 130.41606292412092, 800.5, 0.4],
        '21_1000_46_0':['R1rho', 799777399.1, 130.41606292412092, 1341.10, 0.0],
        '24_1000_46_4':['R1rho', 799777399.1, 130.41606292412092, 1341.10, 0.04],
        '22_1000_46_10':['R1rho', 799777399.1, 130.41606292412092, 1341.10, 0.1],
        '25_1000_46_20':['R1rho', 799777399.1, 130.41606292412092, 1341.10, 0.2],
        '23_1000_46_40':['R1rho', 799777399.1, 130.41606292412092, 1341.10, 0.4],
        '65_1000_48_0':['R1rho', 799777399.1, 130.41606292412092, 1648.5, 0.0],
        '68_1000_48_4':['R1rho', 799777399.1, 130.41606292412092, 1648.5, 0.04],
        '66_1000_48_10':['R1rho', 799777399.1, 130.41606292412092, 1648.5, 0.1],
        '67_1000_48_14':['R1rho', 799777399.1, 130.41606292412092, 1648.5, 0.14],
        '69_1000_48_20':['R1rho', 799777399.1, 130.41606292412092, 1648.5, 0.2],
        '55_2000_41_0':['R1rho', 799777399.1, 142.75412584824184, 800.5, 0.0],
        '58_2000_41_4':['R1rho', 799777399.1, 142.75412584824184, 800.5, 0.04],
        '56_2000_41_10':['R1rho', 799777399.1, 142.75412584824184, 800.5, 0.1],
        '59_2000_41_20':['R1rho', 799777399.1, 142.75412584824184, 800.5, 0.2],
        '57_2000_41_40':['R1rho', 799777399.1, 142.75412584824184, 800.5, 0.4],
        '6_2000_46_0':['R1rho', 799777399.1, 142.75412584824184, 1341.10, 0.0],
        '9_2000_46_4':['R1rho', 799777399.1, 142.75412584824184, 1341.10, 0.04],
        '7_2000_46_10':['R1rho', 799777399.1, 142.75412584824184, 1341.10, 0.1],
        '10_2000_46_20':['R1rho', 799777399.1, 142.75412584824184, 1341.10, 0.2],
        '8_2000_46_40':['R1rho', 799777399.1, 142.75412584824184, 1341.10, 0.4],
        '16_5000_46_0':['R1rho', 799777399.1, 179.76831462060457, 1341.10, 0.0],
        '19_5000_46_4':['R1rho', 799777399.1, 179.76831462060457, 1341.10, 0.04],
        '17_5000_46_10':['R1rho', 799777399.1, 179.76831462060457, 1341.10, 0.1],
        '20_5000_46_20':['R1rho', 799777399.1, 179.76831462060457, 1341.10, 0.2],
        '18_5000_46_40':['R1rho', 799777399.1, 179.76831462060457, 1341.10, 0.4],
        '26_10000_46_0':['R1rho', 799777399.1, 241.45862924120914, 1341.10, 0.0],
        '29_10000_46_4':['R1rho', 799777399.1, 241.45862924120914, 1341.10, 0.04],
        '27_10000_46_10':['R1rho', 799777399.1, 241.45862924120914, 1341.10, 0.1],
        '30_10000_46_20':['R1rho', 799777399.1, 241.45862924120914, 1341.10, 0.2],
        '28_10000_46_40':['R1rho', 799777399.1, 241.45862924120914, 1341.10, 0.4]}

        time_comp = { 
        '118.078_431.0':4,
        '118.078_651.2':5,
        '118.078_800.5':5,
        '118.078_984.0':5,
        '118.078_1341.1':5,
        '118.078_1648.5':5,
        '124.247031462_1341.11':5,
        '130.416062924_800.5':5,
        '130.416062924_1341.11':5,
        '130.416062924_1648.5':5,
        '142.754125848_800.5':5,
        '142.754125848_1341.11':5,
        '179.768314621_1341.11':5,
        '241.458629241_1341.11':5}

        # Check the number of time counts.
        print("Checking the number of time counts.")
        for id in cdp.exp_type.keys():
            exp_type = cdp.exp_type[id]
            frq = cdp.spectrometer_frq[id]
            offset = cdp.spin_lock_offset[id]
            point = cdp.spin_lock_nu1[id]
            count = count_relax_times(exp_type = exp_type, frq = frq, offset=offset, point = point, ei = cdp.exp_type_list.index(cdp.exp_type[id]))
            print(id, exp_type, frq, offset, point, count)

            # Test the time count
            self.assertEqual(count, time_comp['%s_%s'%(offset, point)])


    def test_get_curve_type_cpmg(self):
        """Unit test of the get_curve_type() function.

        This uses the data of the saved state attached to U{bug #21665<https://gna.org/bugs/?21665>}.
        """

        # Load the state.
        statefile = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21665.bz2'
        state.load_state(statefile, force=True)

        # Check the return of get_curve_type function.
        curve_type = get_curve_type()
        print(curve_type)
        self.assertEqual(curve_type, 'fixed time')


    def test_get_times_cpmg(self):
        """Unit test of the get_times() function.

        This uses the data of the saved state attached to U{bug #21665<https://gna.org/bugs/?21665>}.
        """

        # Load the state.
        statefile = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21665.bz2'
        state.load_state(statefile, force=True)

        # Check the return of get_times().
        times = get_times()
        for exp_type in times:
            print(times[exp_type])
            self.assertEqual(len(times[exp_type]), 2)


    def test_has_exponential_exp_type_cpmg(self):
        """Unit test of the has_exponential_exp_type() function.

        This uses the data of the saved state attached to U{bug #21665<https://gna.org/bugs/?21665>}.
        """

        # Load the state.
        statefile = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21665.bz2'
        state.load_state(statefile, force=True)

        # Check the return of has_exponential_exp_type.
        exponential_exp_type = has_exponential_exp_type()
        print(exponential_exp_type)
        self.assertEqual(exponential_exp_type, False)


    def test_loop_exp_frq_cpmg(self):
        """Unit test of the loop_exp_frq() function.

        This uses the data of the saved state attached to U{bug #21665<https://gna.org/bugs/?21665>}.
        """

        # Load the state.
        statefile = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21665.bz2'
        state.load_state(statefile, force=True)

        # Original data (exp_type, frq).
        data = [
            ['SQ CPMG', 499862140.0],
            ['SQ CPMG', 599890858.69999993]
        ]

        # Original indices (ei, mi).
        indices = [
            [0, 0],
            [0, 1]
        ]

        # Check the number of iterations.
        print("Checking the number of iterations of the loop.")
        count = 0
        for exp_type, frq, ei, mi in loop_exp_frq(return_indices=True):
            print(exp_type, frq, ei, mi)
            count += 1
        self.assertEqual(count, 2)

        # Check the values.
        print("Checking the values returned by the loop.")
        index = 0
        for exp_type, frq, ei, mi in loop_exp_frq(return_indices=True):
            # Check the experiment info.
            self.assertEqual(exp_type, data[index][0])
            self.assertEqual(ei, indices[index][0])

            # Check the frequency info.
            self.assertEqual(frq, data[index][1])
            self.assertEqual(mi, indices[index][1])

            # Increment the data index.
            index += 1


    def test_loop_exp_frq_offset_cpmg(self):
        """Unit test of the loop_exp_frq_offset() function.

        This uses the data of the saved state attached to U{bug #21665<https://gna.org/bugs/?21665>}.
        """

        # Load the state.
        statefile = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21665.bz2'
        state.load_state(statefile, force=True)

        # Original data (exp_type, frq, offset).
        data = [
            ['SQ CPMG', 499862140.0, 0],
            ['SQ CPMG', 599890858.69999993, 0]
        ]

        # Original indices (ei, mi, oi).
        indices = [
            [0, 0, 0],
            [0, 1, 0]
        ]

        # Check the number of iterations.
        print("Checking the number of iterations of the loop.")
        count = 0
        for exp_type, frq, offset, ei, mi, oi in loop_exp_frq_offset(return_indices=True):
            print(exp_type, frq, offset, ei, mi, oi)
            count += 1
        self.assertEqual(count, 2)

        # Check the values.
        print("Checking the values returned by the loop.")
        index = 0
        for exp_type, frq, offset, ei, mi, oi in loop_exp_frq_offset(return_indices=True):
            # Check the experiment info.
            self.assertEqual(exp_type, data[index][0])
            self.assertEqual(ei, indices[index][0])

            # Check the frequency info.
            self.assertEqual(frq, data[index][1])
            self.assertEqual(mi, indices[index][1])

            # Check the offset info.
            self.assertEqual(offset, data[index][2])
            self.assertEqual(oi, indices[index][2])

            # Increment the data index.
            index += 1


    def test_loop_exp_frq_offset_point_cpmg(self):
        """Unit test of the loop_exp_frq_offset_point() function.

        This uses the data of the saved state attached to U{bug #21665<https://gna.org/bugs/?21665>}.
        """

        # Load the state.
        statefile = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21665.bz2'
        state.load_state(statefile, force=True)

        # Original data (exp_type, frq, offset, point).
        data = [
            ['SQ CPMG', 499862140.0, 0, [50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0, 650.0, 700.0, 800.0, 900.0, 1000.0]],
            ['SQ CPMG', 599890858.69999993, 0, [33.3333, 66.666, 100.0, 133.333, 166.666, 200.0, 233.333, 266.666, 300.0, 333.333, 366.666, 400.0, 466.666, 533.333, 666.666, 866.666, 1000.0]]
        ]

        # Original indices (ei, mi, oi).
        indices = [
            [0, 0, 0, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]],
            [0, 1, 0, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]]
        ]

        # Check the number of iterations.
        print("Checking the number of iterations of the loop.")
        count = 0
        for exp_type, frq, offset, point, ei, mi, oi, di in loop_exp_frq_offset_point(return_indices=True):
            print(exp_type, frq, offset, point, ei, mi, oi, di)
            count += 1
        self.assertEqual(count, 34)

        # Check the values.
        print("Checking the values returned by the loop.")
        frq_index = 0
        disp_index = 0
        for exp_type, frq, offset, point, ei, mi, oi, di in loop_exp_frq_offset_point(return_indices=True):
            # Check the experiment info.
            self.assertEqual(exp_type, data[frq_index][0])
            self.assertEqual(ei, indices[frq_index][0])

            # Check the frequency info.
            self.assertEqual(frq, data[frq_index][1])
            self.assertEqual(mi, indices[frq_index][1])

            # Check the offset info.
            self.assertEqual(offset, data[frq_index][2])
            self.assertEqual(oi, indices[frq_index][2])

            # Check the dispersion point info.
            self.assertAlmostEqual(point, data[frq_index][3][disp_index],2)
            self.assertEqual(di, indices[frq_index][3][disp_index])

            # Increment the data index.
            if disp_index == 16:
                frq_index += 1
                disp_index = 0
            else:
                disp_index += 1


    def test_loop_exp_frq_offset_point_time_cpmg(self):
        """Unit test of the loop_exp_frq_offset_point_time() function.

        This uses the data of the saved state attached to U{bug #21665<https://gna.org/bugs/?21665>}.
        """

        # Load the state.
        statefile = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21665.bz2'
        state.load_state(statefile, force=True)

        # Original data (exp_type, frq, offset, point).
        data = [
            ['SQ CPMG', 499862140.0, 0, [50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0, 650.0, 700.0, 800.0, 900.0, 1000.0],0.04],
            ['SQ CPMG', 599890858.69999993, 0, [33.3333, 66.666, 100.0, 133.333, 166.666, 200.0, 233.333, 266.666, 300.0, 333.333, 366.666, 400.0, 466.666, 533.333, 666.666, 866.666, 1000.0],0.06]
        ]

        # Original indices (ei, mi, oi).
        indices = [
            [0, 0, 0, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], 0],
            [0, 1, 0, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], 0]
        ]

        # Check the number of iterations.
        print("Checking the number of iterations of the loop.")
        count = 0
        for exp_type, frq, offset, point, time, ei, mi, oi, di, ti in loop_exp_frq_offset_point_time(return_indices=True):
            print(exp_type, frq, offset, point, time, ei, mi, oi, di, ti)
            count += 1
        self.assertEqual(count, 34)

        # Check the values.
        print("Checking the values returned by the loop.")
        frq_index = 0
        disp_index = 0
        for exp_type, frq, offset, point, time, ei, mi, oi, di, ti in loop_exp_frq_offset_point_time(return_indices=True):
            # Check the experiment info.
            self.assertEqual(exp_type, data[frq_index][0])
            self.assertEqual(ei, indices[frq_index][0])

            # Check the frequency info.
            self.assertEqual(frq, data[frq_index][1])
            self.assertEqual(mi, indices[frq_index][1])

            # Check the offset info.
            self.assertEqual(offset, data[frq_index][2])
            self.assertEqual(oi, indices[frq_index][2])

            # Check the dispersion point info.
            self.assertAlmostEqual(point, data[frq_index][3][disp_index],2)
            self.assertEqual(di, indices[frq_index][3][disp_index])

            # Check the time point info.
            self.assertEqual(time, data[frq_index][4])
            self.assertEqual(ti, indices[frq_index][4])

            # Increment the data index.
            if disp_index == 16:
                frq_index += 1
                disp_index = 0
            else:
                disp_index += 1


    def test_loop_exp_frq_offset_point_time_cpmg_setup(self):
        """U{Bug #21665<https://gna.org/bugs/?21665>} catch, the failure due to a a CPMG analysis recorded at two fields at two delay times, using calc()."""

        # Load the state.
        statefile = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21665.bz2'
        state.load_state(statefile, force=True)

        # Original data
        ncyc_1 = [20, 16, 10, 36, 2, 12, 4, 22, 18, 40, 14, 26, 8, 32, 24, 6, 28]
        sfrq_1 = 499.86214*1E6
        time_T2_1 = 0.04
        cpmg_1 = [ncyc/time_T2_1 for ncyc in ncyc_1]
        cpmg_1.sort()

        ncyc_2 = [28, 4, 32, 60, 2, 10, 16, 8, 20, 52, 18, 40, 6, 12, 24, 14, 22]
        sfrq_2 = 599.8908587*1E6
        time_T2_2 = 0.06
        cpmg_2 = [ncyc/time_T2_2 for ncyc in ncyc_2]
        cpmg_2.sort()

        # Test the loop function.
        # First initialize index for the two lists.
        i = -1
        j = -1
        for exp_type, frq, offset, point, time, ei, mi, oi, di, ti in loop_exp_frq_offset_point_time(return_indices=True):
            if frq == sfrq_1:
                i += 1
                self.assertEqual(time, time_T2_1)
                self.assertAlmostEqual(point, cpmg_1[i],3)
            if frq == sfrq_2:
                j += 1
                self.assertEqual(time, time_T2_2)
                self.assertAlmostEqual(point, cpmg_2[j],3)


    def test_loop_time_cpmg(self):
        """Unit test of the loop_time() function.

        This uses the data of the saved state attached to U{bug #21665<https://gna.org/bugs/?21665>}.
        """

        # Load the state.
        statefile = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21665.bz2'
        state.load_state(statefile, force=True)

        # Original data (exp_type, frq, offset, point).
        data = [
            ['SQ CPMG', 499862140.0, 0, [50.0, 100.0, 150.0, 200.0, 250.0, 300.0, 350.0, 400.0, 450.0, 500.0, 550.0, 600.0, 650.0, 700.0, 800.0, 900.0, 1000.0],0.04],
            ['SQ CPMG', 599890858.69999993, 0, [33.3333, 66.666, 100.0, 133.333, 166.666, 200.0, 233.333, 266.666, 300.0, 333.333, 366.666, 400.0, 466.666, 533.333, 666.666, 866.666, 1000.0],0.06]
        ]

        # Original indices (ei, mi, oi, ti).
        indices = [
            [0, 0, 0, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], 0],
            [0, 1, 0, [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16], 0]
        ]

        # Check the number of iterations.
        print("Checking the number of iterations of the loop.")
        count_frq = 0
        for dat in data:
            frq = dat[1]
            for time, ti in loop_time(frq=frq, return_indices=True):
                print(time, ti)
                count_frq += 1
        self.assertEqual(count_frq, 2)


    def test_loop_time_r1rho(self):
        """Unit test of the loop_time() function for R1rho setup.

        This uses the data of the saved state attached to U{bug #21344<https://gna.org/bugs/?21344>}.
        """

        # Load the state.
        statefile = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'dispersion'+sep+'bug_21344.bz2'
        state.load_state(statefile, force=True)

        # Original data, list of time points
        times_list = [0.0, 0.04, 0.1, 0.14, 0.2, 0.4]


        # Check the number of iterations.
        print("Checking the number of iterations of the loop.")
        count_frq = 0
        frq = 799777399.1

        for time, ti in loop_time(frq=frq, return_indices=True):
            print(time, ti)
            count_frq += 1
        self.assertEqual(count_frq, len(times_list))


