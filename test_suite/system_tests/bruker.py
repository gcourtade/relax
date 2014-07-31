##############################################################################
#                                                                             #
# Copyright (C) 2011-2013 Edward d'Auvergne                                   #
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
from pipe_control.mol_res_spin import spin_loop
from status import Status; status = Status()
from test_suite.system_tests.base_classes import SystemTestCase


class Bruker(SystemTestCase):
    """TestCase class for the Bruker Dynamics Center files."""

    def setUp(self):
        """Set up for all the functional tests."""

        # Create a data pipe.
        self.interpreter.pipe.create('mf', 'mf')


    def test_bug_22411_T1_read_fail(self):
        """Test catching U{bug #22411<https://gna.org/bugs/?22411>}, the failure in reading a Bruker DC T1 file as submitted by Olena Dobrovolska."""

        # The data path.
        path = status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'bruker_files'

        # Create a data pipe, read the sequence, and read the Bruker DC file to trigger the bug.
        self.interpreter.pipe.create('bug_22411', 'mf')
        self.interpreter.sequence.read(file='bug_22411_T1_sequence', dir=path, res_num_col=2, res_name_col=1)
        self.interpreter.bruker.read(ri_id='T1', file='bug_22411_T1.txt', dir=path)


    def test_bruker_read_noe(self):
        """Test the reading of a DC NOE file."""

        # Read the sequence data.
        self.interpreter.sequence.read(file="seq", dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'bruker_files', res_num_col=2, res_name_col=1)

        # The ID string.
        ri_id = 'NOE_600'

        # Read the DC file.
        self.interpreter.bruker.read(ri_id=ri_id, file="testNOE.txt", dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'bruker_files')

        # Check the data pipe structures.
        self.assertEqual(cdp.ri_ids, [ri_id])
        self.assertEqual(cdp.spectrometer_frq[ri_id], 600.13*1e6)
        self.assertEqual(cdp.ri_type[ri_id], 'NOE')

        # The NOE values and errors.
        noe = [0.70140000000000002, 0.72260000000000002, 0.78410000000000002, 0.71389999999999998, 0.72219999999999995, 0.73450000000000004, 0.65800000000000003, 0.61319999999999997, 0.64359999999999995, 0.55810000000000004, 0.64349999999999996, 0.72719999999999996, 0.76690000000000003, 0.78159999999999996, 0.78320000000000001, 0.71179999999999999, 0.73529999999999995, 0.7339, 0.76639999999999997, 0.79600000000000004, 0.76980000000000004, 0.76090000000000002, 0.77000000000000002, 0.76839999999999997, 0.746, 0.75119999999999998, 0.7258, 0.76139999999999997, 0.75970000000000004, 0.76270000000000004, 0.71899999999999997, 0.7752, 0.78710000000000002, 0.75270000000000004, 0.75860000000000005, 0.73709999999999998, 0.76649999999999996, 0.78059999999999996, 0.77710000000000001, 0.74419999999999997, 0.71909999999999996, 0.73429999999999995, 0.69320000000000004, 0.60419999999999996, 0.71460000000000001, 0.73599999999999999, 0.78359999999999996, 0.79749999999999999, 0.75949999999999995, 0.76659999999999995, 0.77559999999999996, 0.73729999999999996, 0.73080000000000001, 0.78420000000000001, 0.70409999999999995, 0.6069, 0.79710000000000003, 0.74829999999999997, 0.72860000000000003, 0.73939999999999995, 0.751, 0.73150000000000004, 0.7238, 0.72529999999999994, 0.7218, 0.62980000000000003, 0.3004, 0.15970000000000001, -0.41570000000000001, -1.3540000000000001]

        noe_err = [0.0071371999999999998, 0.0071482999999999998, 0.0090542000000000001, 0.0073617999999999999, 0.0071636, 0.0067083000000000004, 0.0067882000000000003, 0.0076052000000000003, 0.0046737000000000003, 0.0047003000000000001, 0.0061779000000000001, 0.0087358000000000002, 0.0064637999999999996, 0.0084919999999999995, 0.0067708000000000004, 0.0064495999999999998, 0.0079068000000000003, 0.0059157999999999997, 0.0053657000000000002, 0.0088774000000000006, 0.0096562999999999996, 0.0078910000000000004, 0.0066074000000000003, 0.0091068, 0.0079459000000000005, 0.0088655999999999995, 0.0071831000000000004, 0.0069040999999999998, 0.0070117000000000001, 0.0065712000000000001, 0.0063590000000000001, 0.0054622999999999998, 0.0061237000000000002, 0.0058399999999999997, 0.0072487000000000003, 0.0082611999999999998, 0.010810999999999999, 0.010808999999999999, 0.010059999999999999, 0.0091409999999999998, 0.012137999999999999, 0.0063179999999999998, 0.0080087000000000005, 0.0067654999999999998, 0.0090647000000000002, 0.0085708999999999994, 0.0071379, 0.0088193999999999998, 0.010037000000000001, 0.0074373, 0.0059819000000000001, 0.0065192999999999996, 0.006594, 0.0057096999999999998, 0.0078305000000000007, 0.0062278999999999998, 0.0053839999999999999, 0.0085550000000000001, 0.0064421000000000001, 0.0066708000000000002, 0.0089885, 0.0095670000000000009, 0.0073683999999999998, 0.0092160000000000002, 0.0079343999999999994, 0.0059852999999999998, 0.0039353000000000001, 0.0040734999999999999, 0.0060822000000000003, 0.0067099000000000004]

        # Loop over the spins.
        i = 0
        for spin in spin_loop():
            # Check the R1 value and error.
            self.assertAlmostEqual(spin.ri_data[ri_id], noe[i])
            self.assertAlmostEqual(spin.ri_data_err[ri_id], noe_err[i])

            # Increment the data index.
            i += 1


    def test_bruker_read_r1(self):
        """Test the reading of a DC R1 file."""

        # Read the sequence data.
        self.interpreter.sequence.read(file="seq", dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'bruker_files', res_num_col=2, res_name_col=1)

        # The ID string.
        ri_id = 'NOE_600'

        # Read the DC file.
        self.interpreter.bruker.read(ri_id=ri_id, file="testT1.txt", dir=status.install_path + sep+'test_suite'+sep+'shared_data'+sep+'bruker_files')

        # Check the data pipe structures.
        self.assertEqual(cdp.ri_ids, [ri_id])
        self.assertEqual(cdp.spectrometer_frq[ri_id], 600.13*1e6)
        self.assertEqual(cdp.ri_type[ri_id], 'R1')

        # The R1 values and errors.
        r1 = [2.1931556000035091, 2.3314642761386288, 2.3482998309224121, 2.2490812503092488, 2.2794204801371301, 2.2197311905528241, 2.2402487572220018, 1.9682404717478763, 2.0880183244488153, 1.9977625059932875, 2.1644881093845711, 2.2725568309649504, 2.1992861117281328, 2.2794360675168961, 2.0871205875661878, 2.2847272835278019, 2.1080324468354217, 2.2433596554199569, 2.3491493730120321, 2.2750850881822982, 2.4672959916309321, 2.3956227181693608, 2.1334016021846032, 2.3625860867305351, 2.3848078202618042, 2.3269721670859096, 2.4206451987712803, 2.3722597434638315, 2.343270361847809, 2.1927612565399106, 2.2380977959212909, 2.2461360844008094, 1.9912266553564995, 2.2936831964769029, 2.25463891957703, 2.2244169803094609, 2.280408101833904, 2.172312143876578, 2.2795451851446598, 2.266191370796498, 2.1729305009908564, 2.1917183729559486, 2.201809006279559, 2.1141693745652739, 2.2445782213064343, 2.133488082335572, 2.0460023160746217, 2.1921507848995887, 2.2750902642062325, 2.3691236848402144, 2.2981479225891852, 2.377233708223089, 2.2256001887308958, 2.2846020109066898, 2.3422878999749375, 1.973756927886817, 2.1651301459730745, 2.3191578673951914, 2.1891945734244915, 2.1815674998800136, 2.2678668217887572, 2.2465094858863042, 2.248479465761279, 2.3154901661132645, 2.1756630333094011, 2.1637200405913881, 1.8566309574645847, 1.6125599066005301, 1.1626041402658644, 0.76306229106400647]

        r1_err = [0.014883089934780979, 0.016303964816225223, 0.020363318742260723, 0.016687709376937879, 0.015718752396670817, 0.014518431475680691, 0.021886132469627697, 0.031556287075440621, 0.013515188095333659, 0.012453357417944776, 0.017587242385253953, 0.019302908234606619, 0.01371059959156644, 0.018437979357718477, 0.011698687778157989, 0.014869218069149722, 0.015737214115414941, 0.01390943018668532, 0.011941067694394526, 0.018293553488398374, 0.02261268912683069, 0.018087051681058786, 0.011598407444726788, 0.020469296587543661, 0.016620045900872408, 0.018909060457610323, 0.016739624643405365, 0.014806679126327058, 0.014476089754057037, 0.013123976098001535, 0.014050407715829098, 0.011838554421252851, 0.010844835351527457, 0.012711044971238742, 0.014752794876103476, 0.018227294017845289, 0.021723973501089892, 0.023441165299977383, 0.020591141498844744, 0.021778249169927173, 0.048387937817301517, 0.014867254858784009, 0.015546891671168217, 0.0142895492367403, 0.019750595476352866, 0.018562225014765673, 0.01329331372822814, 0.017647341591456655, 0.022969665803225174, 0.017861428710653073, 0.013099301992997067, 0.016245795194826523, 0.01547652953130973, 0.012508928370486994, 0.018321615170728861, 0.012861357034233434, 0.0098069239594803376, 0.019462269334464877, 0.015102761537490045, 0.015366805452534153, 0.020263438728953861, 0.020365125023511663, 0.015793641211181965, 0.020435935240713243, 0.014399976749920211, 0.012424600763085578, 0.0098441373116733167, 0.011085457618140082, 0.013079658707916478, 0.0029578895055556633]

        # Loop over the spins.
        i = 0
        for spin in spin_loop():
            # Check the R1 value and error.
            self.assertAlmostEqual(spin.ri_data[ri_id], r1[i], 5)
            self.assertAlmostEqual(spin.ri_data_err[ri_id], r1_err[i], 5)

            # Increment the data index.
            i += 1
