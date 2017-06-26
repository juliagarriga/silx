# coding: utf-8
# /*##########################################################################
#
# Copyright (c) 2015-2017 European Synchrotron Radiation Facility
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
"""This module provides the Colormap object
"""

from __future__ import absolute_import

__authors__ = ["T. Vincent", "H.Payno"]
__license__ = "MIT"
__date__ = "05/12/2016"

from silx.gui import qt
import copy as copy_mdl
import numpy
from .matplotlib import Colormap as MPLColormap
import logging
from silx.math.combo import min_max

_logger = logging.getLogger(__file__)

_DEFAULT_COLORMAPS = {
    'gray': 0,
    'reversed gray': 1,
    'red': 2,
    'green': 3,
    'blue': 4,
    'temperature': 5
}
"""Dictionary of _DEFAULT_COLORMAPS with there GLProgram ids"""

DEFAULT_COLORMAPS = tuple(_DEFAULT_COLORMAPS.keys())
"""Tuple of supported colormap names."""

LINEAR = 'linear'
"""constante for linear normalization"""
LOGARITHM = 'log'
"""constante for logarithmic normalization"""

NORMALIZATIONS = (LINEAR, LOGARITHM)
"""Tuple of managed normalizations"""

DEFAULT_MIN_LIN = 0
"""Default min value if in linear normalization"""
DEFAULT_MAX_LIN = 1
"""Default max value if in linear normalization"""
DEFAULT_MIN_LOG = 1
"""Default min value if in log normalization"""
DEFAULT_MAX_LOG = 10
"""Default max value if in log normalization"""


class Colormap(qt.QObject):
    """Description of a colormap

    :param str name: Name of the colormap
    :param tuple colors: optional, custom colormap.
            Nx3 or Nx4 numpy array of RGB(A) colors,
            either uint8 or float in [0, 1].
            If 'name' is None, then this array is used as the colormap.
    :param str norm: Normalization: 'linear' (default) or 'log'
    :param float vmin:
        Lower bound of the colormap or None for autoscale (default)
    :param float vmax:
        Upper bounds of the colormap or None for autoscale (default)
    """

    sigChanged = qt.Signal()

    def __init__(self, name='gray', colors=None, normalization=LINEAR, vmin=None, vmax=None):
        qt.QObject.__init__(self)
        assert normalization in NORMALIZATIONS
        if normalization is LOGARITHM:
            if (vmin is not None and vmin < 1.0) or (vmax is not None and vmax < 1.0):
                m = "Unsuported vmin (%s) and/or vmax (%s) given for a log scale" % (
                vmin, vmax)
                m += 'Autoscale will be performed'
                _logger.warning(m)
                vmin = None
                vmax = None

        self._name = str(name) if name is not None else None
        self._setColors(colors)
        self._normalization = str(normalization)
        self._vmin = float(vmin) if vmin is not None else None
        self._vmax = float(vmax) if vmax is not None else None

    def isAutoscale(self):
        """Return True if both min and max are in autoscale mode"""
        return self._vmin is None or self._vmax is None

    def getName(self):
        """Return the name of the colormap
        :rtype: str
        """
        return self._name

    def _setColors(self, colors):
        if not (type(colors) in (numpy.ndarray, list, tuple) or colors is None):
            m = "colors should be None or a numpy.ndarray or a list or a tuple"
            raise ValueError(m)

        if type(colors) in (list, tuple):
            self._colors = numpy.array(colors)
        else:
            self._colors = colors

    def setName(self, name):
        """Set the name of the colormap and load the colors corresponding to
        the name

        :param str name: the name of the colormap (should be in ['gray',
            'reversed gray', 'temperature', 'red', 'green', 'blue', 'jet',
            'viridis', 'magma', 'inferno', 'plasma']
        """
        self._name = str(name)
        self._colors = None
        self.sigChanged.emit()

    def getColorMapLUT(self, copy=True):
        """Return the list of colors for the colormap. None if not setted
        
        :param copy: True (Default) to get a copy, False to get the pointer

        :return: the list of colors for the colormap. None if not setted
        :rtype: numpy.ndarray
        """
        if copy:
            return copy_mdl.copy(self._colors)
        else:
            return self._colors

    def setColorMapLUT(self, colors, keepName=False):
        """
        Set the colors of the colormap.

        :param numpy.ndarray colors: the colors of the LUT
        :param bool keepName: should we keep the name of the colormap.
            This might bring conflicts with existing colormaps

        .. warning: this will set the value of name to an empty string
        """
        self._setColors(colors)
        if len(colors) is 0:
            self._colors = None
        if keepName is False:
            self._name = ""
        self.sigChanged.emit()

    def getNormalization(self):
        """Return the normalization of the colormap ('log' or 'linear')
        
        :return: the normalization of the colormap
        :rtype: str
        """
        return self._normalization

    def setNormalization(self, norm):
        """Set the norm ('log', 'linear')

        :param str norm: the norm to set
        """
        self._normalization = str(norm)
        self.sigChanged.emit()

    def getVMin(self):
        """Return the lower bound of the colormap
        
         :return: the lower bound of the colormap
         :rtype: float or None
         """
        return self._vmin

    def setVMin(self, vmin):
        """Set the minimal value of the colormap

        :param float vmin: Lower bound of the colormap or None for autoscale
            (default)
            value)
        """
        self._vmin = vmin
        self.sigChanged.emit()

    def getVMax(self):
        """Return the upper bounds of the colormap or None
        
        :return: the upper bounds of the colormap or None
        :rtype: float or None
        """
        return self._vmax

    def setVMax(self, vmax):
        """Set the maximal value of the colormap

        :param float vmax: Upper bounds of the colormap or None for autoscale
            (default)
        """
        self._vmax = vmax
        self.sigChanged.emit()

    def getColorMapRange(self, data=None):
        """Return (vmin, vmax)

        :return: the tuple vmin, vmax fitting vmin, vmax, normalization and
            data if any given
        :rtype: tuple
        """
        vmin = self._vmin
        vmax = self._vmax

        if data is not None:
            result = min_max(data, min_positive=True)

        if vmin is None:
            vmin = result.minimum if data is not None else self._getDefaultMin()
        if vmax is None:
            vmax = result.maximum if data is not None else self._getDefaultMax()

        if data is not None:
            if self.getNormalization() == LOGARITHM:
                if vmin < 0:
                    vmin = result.min_positive

                if vmax < 0:
                    vmax = result.min_positive, result.maximum

        return (vmin, vmax)

    def setVMinVMax(self, vmin, vmax):
        """
        Set bounds to the colormap

        :param vmin: Lower bound of the colormap or None for autoscale
            (default)
        :param vmax: Upper bounds of the colormap or None for autoscale
            (default)
        """
        self._vmin = vmin
        self._vmax = vmax
        self.sigChanged.emit()

    def __getitem__(self, item):
        if item == 'autoscale':
            return self.isAutoscale()
        elif item == 'name':
            return self.getName()
        elif item == 'normalization':
            return self.getNormalization()
        elif item == 'vmin':
            return self.getVMin()
        elif item == 'vmax':
            return self.getVMax()
        elif item == 'colors':
            return self.getColorMapLUT(copy=False)
        else:
            raise KeyError(item)

    def _toDict(self):
        """Return the equivalent colormap as a dictionary
        (old colormap representation)

        :return: the representation of the Colormap as a dictionary
        :rtype: dict
        """
        return {
            'name': self._name,
            'colors': copy_mdl.copy(self._colors),
            'vmin': self._vmin,
            'vmax': self._vmax,
            'autoscale': self.isAutoscale(),
            'normalization': self._normalization
        }

    def _setFromDict(self, dic):
        """Set values to the colormap from a dictionary

        :param dict dic: the colormap as a dictionary
        """
        name = dic['name'] if 'name' in dic else None
        colors = dic['colors'] if 'colors' in dic else None
        vmin = dic['vmin'] if 'vmin' in dic else None
        vmax = dic['vmax'] if 'vmax' in dic else None
        if 'normalization' in dic:
            normalization = dic['normalization']
        else:
            warn = 'Normalization not given in the dictionary, '
            warn += 'set by default to ' + LINEAR
            _logger.warning(warn)
            normalization = LINEAR

        if name is None and colors is None:
            err = 'The colormap should have a name defined or a tuple of colors'
            raise ValueError(err)
        if normalization not in NORMALIZATIONS:
            err = 'Given normalization is not recoginized (%s)' % normalization
            raise ValueError(err)

        if 'autoscale' in dic:
            if dic['autoscale'] is True:
                if vmin is not None or vmax is not None:
                    err = "Can't set the colormap from the dictionary because"
                    err += " autoscale is requested but vmin and vmax are also"
                    err += " defined (!= None)"
                    raise ValueError(err)
            elif dic['autoscale'] is False:
                if vmin is None and vmax is None:
                    err = "Can't set the colormap from the dictionary because"
                    err += " autoscale is not requested but vmin and vmax are"
                    err += " both set to None"
                    raise ValueError(err)
            else:
                raise ValueError('Autoscale value should be True or False')

        self._name = name
        self._colors = colors
        self._vmin = vmin
        self._vmax = vmax
        self._autoscale = True if (vmin is None and vmax is None) else False
        self._normalization = normalization

        self.sigChanged.emit()

    @staticmethod
    def _fromDict(dic):
        colormap = Colormap(name="")
        colormap._setFromDict(dic)
        return colormap

    def copy(self):
        """

        :return: a copy of the Colormap object
        """
        return Colormap(name=self._name,
                        colors=copy_mdl.copy(self._colors),
                        vmin=self._vmin,
                        vmax=self._vmax,
                        normalization=self._normalization)

    def applyToData(self, data):
        """Apply the colormap to the data

        :param numpy.ndarray data: The data to convert.
        """
        # TODO : what appen if matplotlib not here ?
        rgbaImage = MPLColormap.applyColormapToData(colormap=self, data=data)
        return rgbaImage

    @staticmethod
    def getSupportedColormaps():
        """Get the supported colormap names as a tuple of str.

        The list should at least contain and start by:
        ('gray', 'reversed gray', 'temperature', 'red', 'green', 'blue')
        :rtype: tuple
        """
        if MPLColormap is None:
            return DEFAULT_COLORMAPS
        else:
            maps = MPLColormap.getSupportedColormaps()
            return DEFAULT_COLORMAPS + maps

    def __str__(self):
        return str(self._toDict())

    def _getDefaultMin(self):
        return DEFAULT_MIN_LIN if self._normalization == LINEAR else DEFAULT_MIN_LOG

    def _getDefaultMax(self):
        return DEFAULT_MAX_LIN if self._normalization == LINEAR else DEFAULT_MAX_LOG

    def __eq__(self, other):
        """Compare colormap values and not pointers"""
        return (self.getName() == other.getName() and
                self.getNormalization() == other.getNormalization() and
                self.getVMin() == other.getVMin() and
                self.getVMax() == other.getVMax() and
                numpy.array_equal(self.getColorMapLUT(), other.getColorMapLUT())
                )

