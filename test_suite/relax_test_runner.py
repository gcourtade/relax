###############################################################################
#                                                                             #
# Copyright (C) 2008 Edward d'Auvergne                                        #
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
import sys
from unittest import _TextTestResult, TextTestRunner
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

# relax module imports.
from status import Status; status = Status()


class _RelaxTestResult(_TextTestResult):
    """A replacement for the _TextTestResult class used by the normal TextTestRunner.

    This class is designed to catch STDOUT and STDERR during the execution of each test and to
    prepend the output to the failure and error reports normally generated by TextTestRunner.
    """

    def startTest(self, test):
        """Override of the _TextTestResult.startTest() method.

        The start of STDOUT and STDERR capture occurs here.
        """

        # Store the original STDOUT and STDERR for restoring later on.
        self.orig_stdout = sys.stdout
        self.orig_stderr = sys.stderr

        # Catch stdout and stderr.
        self.capt = StringIO()
        sys.stdout = self.capt
        sys.stderr = self.capt

        # Place the test name in the status object.
        status.exec_lock.test_name = str(test)

        # Execute the normal startTest method.
        _TextTestResult.startTest(self, test)


    def stopTest(self, test):
        """Override of the TestResult.stopTest() method.

        The end of STDOUT and STDERR capture occurs here.
        """

        # Restore the IO streams.
        sys.stdout = self.orig_stdout
        sys.stderr = self.orig_stderr


    def addError(self, test, err):
        """Override of the TestResult.addError() method.

        The STDOUT and STDERR captured text is prepended to the error text here.
        """

        # Execute the normal addError method.
        _TextTestResult.addError(self, test, err)

        # Prepend the STDOUT and STDERR messages to the second element of the tuple.
        self.errors[-1] = (self.errors[-1][0], self.capt.getvalue() + self.errors[-1][1])


    def addFailure(self, test, err):
        """Override of the TestResult.addFailure() method.

        The STDOUT and STDERR captured text is prepended to the failure text here.
        """

        # Execute the normal addFailure method.
        _TextTestResult.addFailure(self, test, err)

        # Prepend the STDOUT and STDERR messages to the second element of the tuple.
        self.failures[-1] = (self.failures[-1][0], self.capt.getvalue() + self.failures[-1][1])




class RelaxTestRunner(TextTestRunner):
    """A replacement unittest runner.

    This runner is designed to catch STDOUT during the execution of each test and to prepend the
    output to the failure and error reports normally generated by TextTestRunner.
    """

    def _makeResult(self):
        """Override of the TextTestRunner._makeResult() method."""

        # Run the tests.
        return _RelaxTestResult(self.stream, self.descriptions, self.verbosity)
