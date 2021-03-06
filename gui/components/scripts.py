###############################################################################
#                                                                             #
# Copyright (C) 2009-2010 Michael Bieri                                       #
# Copyright (C) 2009-2012 Edward d'Auvergne                                   #
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
"""Module containing the scripts GUI element for listing the scripts used in the analysis."""

# relax module imports.
from graphics import fetch_icon
from gui.components.base_list import Base_list
from gui.string_conv import str_to_gui
from gui.uf_objects import Uf_storage; uf_store = Uf_storage()


class Scripts(Base_list):
    """The GUI element for listing the scripts used in the analysis."""

    def action_bmrb_script(self, event):
        """Launch the bmrb.script user function.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Launch the dialog.
        uf_store['bmrb.script'](wx_parent=self.parent)


    def setup(self):
        """Override the base variables."""

        # GUI variables.
        self.title = "Scripts"
        self.observer_base_name = "scripts"
        self.button_placement = 'bottom'

        # The column titles.
        self.columns = [
            "Script name"
        ]

        # Button set up.
        self.button_info = [
            {
                'object': 'button_add',
                'label': ' Add',
                'icon': fetch_icon('oxygen.actions.list-add-relax-blue', "22x22"),
                'method': self.action_bmrb_script,
                'tooltip': "Specify any scripts used for the analysis."
            }
        ]


    def update_data(self):
        """Method called from self.build_element_safe() to update the list data."""

        # Expand the number of rows to match the number of entries, and add the data.
        n = 0
        if hasattr(cdp, 'exp_info') and hasattr(cdp.exp_info, 'scripts'):
            n = len(cdp.exp_info.scripts)
            for i in range(n):
                # Set the scripts name.
                self.element.InsertStringItem(i, str_to_gui(cdp.exp_info.scripts[i].file))
