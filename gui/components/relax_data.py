###############################################################################
#                                                                             #
# Copyright (C) 2009-2011 Michael Bieri                                       #
# Copyright (C) 2010-2011 Edward d'Auvergne                                   #
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

# Module docstring.
"""Module containing the classes for GUI components involving relaxation data."""

# Python module imports.
import wx
import wx.lib.buttons

# relax module imports.
from status import Status; status = Status()

# relax GUI module imports.
from gui.fonts import font
from gui.misc import add_border, float_to_gui, str_to_gui
from gui import paths


class Relax_data_list:
    """The GUI element for listing loaded relaxation data."""

    def __init__(self, gui=None, parent=None, box=None, id=None, buttons=True):
        """Build the relaxation data list GUI element.

        @keyword gui:       The main GUI object.
        @type gui:          wx.Frame instance
        @keyword parent:    The parent GUI element that this is to be attached to (the panel object).
        @type parent:       wx object
        @keyword data:      The data storage container.
        @type data:         class instance
        @keyword box:       The vertical box sizer to pack this GUI component into.
        @type box:          wx.BoxSizer instance
        @keyword id:        A unique identification string.  This is used to register the update method with the GUI user function observer object.
        @type id:           str
        @keyword buttons:   A flag which if True will display the buttons at the top.
        @type buttons:      bool
        """

        # Store the arguments.
        self.gui = gui
        self.parent = parent

        # GUI variables.
        self.spacing = 5
        self.border = 5
        self.height_buttons = 40

        # First create a panel (to allow for tooltips on the buttons).
        self.panel = wx.Panel(self.parent)
        box.Add(self.panel, 0, wx.ALL|wx.EXPAND, 0)

        # Add a sizer to the panel.
        panel_sizer = wx.BoxSizer(wx.VERTICAL)
        self.panel.SetSizer(panel_sizer)

        # A static box to hold all the widgets, and its sizer.
        stat_box = wx.StaticBox(self.panel, -1, "Relaxation data list")
        stat_box.SetFont(font.subtitle)
        sub_sizer = wx.StaticBoxSizer(stat_box, wx.VERTICAL)

        # Add the sizer to the static box and the static box to the main box.
        panel_sizer.Add(sub_sizer, 0, wx.ALL|wx.EXPAND, 0)

        # Add a border.
        box_centre = add_border(sub_sizer, border=self.border)

        # Add buttons.
        if buttons:
            self.add_buttons(box_centre)

        # Initialise the element.
        box_centre.AddSpacer(self.spacing)
        self.init_element(box_centre)

        # Build the element.
        self.build_element()

        # Initialise observer name.
        self.name = 'relaxation data list: %s' % id

        # Register the element for updating when a user function completes.
        status.observers.gui_uf.register(self.name, self.build_element)


    def add_buttons(self, sizer):
        """Add the buttons for peak list manipulation.

        @param box:     The sizer element to pack the buttons into.
        @type box:      wx.BoxSizer instance
        """

        # Button Sizer
        button_sizer = wx.BoxSizer(wx.HORIZONTAL)
        sizer.Add(button_sizer, 0, wx.ALL|wx.EXPAND, 0)

        # Add button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self.panel, -1, None, " Add")
        button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.add, wx.BITMAP_TYPE_ANY))
        button.SetSize((80, self.height_buttons))
        button_sizer.Add(button, 0, 0, 0)
        self.gui.Bind(wx.EVT_BUTTON, self.gui.user_functions.relax_data.read, button)
        button.SetToolTipString("Read relaxation data from file.")

        # Delete button.
        button = wx.lib.buttons.ThemedGenBitmapTextButton(self.panel, -1, None, " Delete")
        button.SetBitmapLabel(wx.Bitmap(paths.icon_22x22.list_remove, wx.BITMAP_TYPE_ANY))
        button.SetSize((80, self.height_buttons))
        button_sizer.Add(button, 0, 0, 0)
        self.gui.Bind(wx.EVT_BUTTON, self.gui.user_functions.relax_data.delete, button)
        button.SetToolTipString("Delete loaded relaxation data from the relax data store.")


    def build_element(self):
        """Build the relaxation data listing grid."""

        # First freeze the element, so that the GUI element doesn't update until the end.
        self.element.Freeze()

        # Delete the previous data.
        self.element.DeleteAllItems()

        # Expand the number of rows to match the number of relaxation IDs, and add the IDs.
        n = 0
        if hasattr(cdp, 'ri_ids'):
            # The number of IDs.
            n = len(cdp.ri_ids)

            # Add all the data.
            for i in range(n):
                # Set the IDs.
                id = cdp.ri_ids[i]
                self.element.InsertStringItem(i, str_to_gui(id))

                # Set the data types.
                self.element.SetStringItem(i, 1, str_to_gui(cdp.ri_type[id]))

                # Set the frequencies.
                self.element.SetStringItem(i, 2, float_to_gui(cdp.frq[id]))

        # Size the columns.
        self.size_cols()

        # Post a size event to get the scroll panel to update correctly.
        event = wx.PyCommandEvent(wx.EVT_SIZE.typeId, self.parent.GetId())
        wx.PostEvent(self.parent.GetEventHandler(), event)

        # Set the minimum height.
        height = self.height_base + self.height_char * n
        self.element.SetMinSize((-1, height))
        self.element.Layout()

        # Unfreeze.
        self.element.Thaw()


    def delete(self):
        """Unregister the class."""

        # Unregister the class.
        status.observers.gui_uf.unregister(self.name)


    def init_element(self, sizer):
        """Initialise the GUI element for the relaxation data listing.

        @param box:     The sizer element to pack the element into.
        @type box:      wx.BoxSizer instance
        """

        # List of relaxation data.
        self.element = wx.ListCtrl(self.panel, -1, style=wx.BORDER_SUNKEN|wx.LC_REPORT)

        # Initialise to 3 columns.
        self.element.InsertColumn(0, str_to_gui("Relaxation data ID"))
        self.element.InsertColumn(1, str_to_gui("Data type"))
        self.element.InsertColumn(2, str_to_gui("Frequency (Hz)"))

        # Properties.
        self.element.SetFont(font.normal)

        # Store the base heights.
        self.height_base = self.element.GetSize()[1]
        self.height_char = self.element.GetCharHeight()

        # Bind some events.
        self.element.Bind(wx.EVT_SIZE, self.resize)

        # Add list to sizer.
        sizer.Add(self.element, 0, wx.ALL|wx.EXPAND, 0)


    def resize(self, event):
        """Catch the resize to allow the element to be resized.

        @param event:   The wx event.
        @type event:    wx event
        """

        # Set the column sizes.
        self.size_cols()

        # Continue with the normal resizing.
        event.Skip()


    def size_cols(self):
        """Set the column sizes."""

        # The element size.
        x, y = self.element.GetSize()

        # Number of columns.
        n = self.element.GetColumnCount()

        # Set to equal sizes.
        width = int(x / n)

        # Set the column sizes.
        for i in range(n):
            self.element.SetColumnWidth(i, width)
