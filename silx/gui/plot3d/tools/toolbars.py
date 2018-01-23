# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2016-2017 European Synchrotron Radiation Facility
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
# ###########################################################################*/
"""This module provides toolbars with tools for a Plot3DWidget.

It provides the following toolbars:

- :class:`InteractiveModeToolBar` with:
  - Set interactive mode to rotation
  - Set interactive mode to pan

- :class:`OutputToolBar` with:
  - Copy
  - Save
  - Video
  - Print
"""

from __future__ import absolute_import

__authors__ = ["T. Vincent"]
__license__ = "MIT"
__date__ = "06/09/2017"

import logging
import weakref

from silx.gui import qt

from .ViewpointTools import ViewpointToolButton
from .. import actions

_logger = logging.getLogger(__name__)


class Plot3dWidgetToolBar(qt.QToolBar):
    """Base class for toolbar associated to a Plot3DWidget

    :param parent: See :class:`QWidget`
    :param str title: Title of the toolbar.
    """

    def __init__(self, parent=None, title=''):
        super(Plot3dWidgetToolBar, self).__init__(title, parent)

        self._plot3DRef = None

    def _plot3DWidgetChanged(self, widget):
        """Override in subclass to handle change of Plot3DWidget"""
        pass

    def setPlot3DWidget(self, widget):
        """Set the Plot3DWidget this toolbar is associated with

        :param Plot3DWidget widget: The widget to control
        """
        self._plot3DRef = None if widget is None else weakref.ref(widget)
        self._plot3DWidgetChanged(widget)

    def getPlot3DWidget(self):
        """Return the Plot3DWidget associated to this toolbar.

        If no widget is associated, it returns None.

        :rtype: qt.QWidget
        """
        return None if self._plot3DRef is None else self._plot3DRef()


class InteractiveModeToolBar(Plot3dWidgetToolBar):
    """Toolbar providing icons to change the interaction mode

    :param parent: See :class:`QWidget`
    :param str title: Title of the toolbar.
    """

    def __init__(self, parent=None, title='Plot3D Interaction'):
        super(InteractiveModeToolBar, self).__init__(parent, title)

        self._rotateAction = actions.mode.RotateArcballAction(parent=self)
        self.addAction(self._rotateAction)

        self._panAction = actions.mode.PanAction(parent=self)
        self.addAction(self._panAction)

    def _plot3DWidgetChanged(self, widget):
        self.getRotateAction().setPlot3DWidget(widget)
        self.getPanAction().setPlot3DWidget(widget)

    def getRotateAction(self):
        """Returns the QAction setting rotate interaction of the Plot3DWidget

        :rtype: qt.QAction
        """
        return self._rotateAction

    def getPanAction(self):
        """Returns the QAction setting pan interaction of the Plot3DWidget

        :rtype: qt.QAction
        """
        return self._panAction


class OutputToolBar(Plot3dWidgetToolBar):
    """Toolbar providing icons to copy, save and print the OpenGL scene

    :param parent: See :class:`QWidget`
    :param str title: Title of the toolbar.
    """

    def __init__(self, parent=None, title='Plot3D Output'):
        super(OutputToolBar, self).__init__(parent, title)

        self._copyAction = actions.io.CopyAction(parent=self)
        self.addAction(self._copyAction)

        self._saveAction = actions.io.SaveAction(parent=self)
        self.addAction(self._saveAction)

        self._videoAction = actions.io.VideoAction(parent=self)
        self.addAction(self._videoAction)

        self._printAction = actions.io.PrintAction(parent=self)
        self.addAction(self._printAction)

    def _plot3DWidgetChanged(self, widget):
        self.getCopyAction().setPlot3DWidget(widget)
        self.getSaveAction().setPlot3DWidget(widget)
        self.getVideoRecordAction().setPlot3DWidget(widget)
        self.getPrintAction().setPlot3DWidget(widget)

    def getCopyAction(self):
        """Returns the QAction performing copy to clipboard of the Plot3DWidget

        :rtype: qt.QAction
        """
        return self._copyAction

    def getSaveAction(self):
        """Returns the QAction performing save to file of the Plot3DWidget

        :rtype: qt.QAction
        """
        return self._saveAction

    def getVideoRecordAction(self):
        """Returns the QAction performing record video of the Plot3DWidget

        :rtype: qt.QAction
        """
        return self._videoAction

    def getPrintAction(self):
        """Returns the QAction performing printing of the Plot3DWidget

        :rtype: qt.QAction
        """
        return self._printAction


class ViewpointToolBar(Plot3dWidgetToolBar):
    """A toolbar providing icons to reset the viewpoint.

    :param parent: See :class:`QToolBar`
    :param str title: Title of the toolbar
    """

    def __init__(self, parent=None, title='Viewpoint control'):
        super(ViewpointToolBar, self).__init__(parent, title)

        self._viewpointToolButton = ViewpointToolButton(parent=self)
        self.addWidget(self._viewpointToolButton)
        self._rotateViewpointAction = actions.viewpoint.RotateViewpoint(parent=self)
        self.addAction(self._rotateViewpointAction)

    def _plot3DWidgetChanged(self, widget):
        self.getViewpointToolButton().setPlot3DWidget(widget)
        self.getRotateViewpointAction().setPlot3DWidget(widget)

    def getViewpointToolButton(self):
        """Returns the ViewpointToolButton to set viewpoint of the Plot3DWidget

        :rtype: ViewpointToolButton
        """
        return self._viewpointToolButton

    def getRotateViewpointAction(self):
        """Returns the QAction to start/stop rotation of the Plot3DWidget

        :rtype: qt.QAction
        """
        return self._rotateViewpointAction
