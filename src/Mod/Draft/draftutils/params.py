# ***************************************************************************
# *   Copyright (c) 2023 FreeCAD Project Association                        *
# *                                                                         *
# *   This program is free software; you can redistribute it and/or modify  *
# *   it under the terms of the GNU Lesser General Public License (LGPL)    *
# *   as published by the Free Software Foundation; either version 2 of     *
# *   the License, or (at your option) any later version.                   *
# *   for detail see the LICENCE text file.                                 *
# *                                                                         *
# *   This program is distributed in the hope that it will be useful,       *
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *   GNU Library General Public License for more details.                  *
# *                                                                         *
# *   You should have received a copy of the GNU Library General Public     *
# *   License along with this program; if not, write to the Free Software   *
# *   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *   USA                                                                   *
# *                                                                         *
# ***************************************************************************

""" Contains a parameter observer class and several related functions."""

import FreeCAD as App
import FreeCADGui as Gui
from PySide import QtGui

from draftutils import init_draft_statusbar
from draftutils import utils
from draftutils.translate import translate
from draftviewproviders import view_base

class ParamObserver:

    def slotParamChanged(self, param, tp, name, value):
        if name in ("gridBorder", "gridShowHuman", "coloredGridAxes", "gridEvery",
                    "gridSpacing", "gridSize", "gridTransparency", "gridColor"):
            _param_observer_callback_grid()
            return
        if name in ("DisplayStatusbarSnapWidget", "DisplayStatusbarScaleWidget"):
            _param_observer_callback_statusbar()
            return
        if name == "snapStyle":
            _param_observer_callback_snapstyle()
            return
        if name == "snapcolor":
            _param_observer_callback_snapcolor()
            return
        if name == "patternFile":
            _param_observer_callback_svg_pattern()
            return


def _param_observer_callback_grid():
    if hasattr(App, "draft_working_planes") and hasattr(Gui, "Snapper"):
        try:
            trackers = Gui.Snapper.trackers
            for wp in App.draft_working_planes[1]:
                view = wp._view
                if view in trackers[0]:
                    i = trackers[0].index(view)
                    grid = trackers[1][i]
                    grid.pts = []
                    grid.reset()
                    grid.displayHumanFigure(wp)
                    grid.setAxesColor(wp)
        except Exception:
            pass


def _param_observer_callback_statusbar():
    init_draft_statusbar.hide_draft_statusbar()
    init_draft_statusbar.show_draft_statusbar()


def _param_observer_callback_snapstyle():
    if hasattr(Gui, "Snapper"):
        Gui.Snapper.set_snap_style()


def _param_observer_callback_snapcolor():
    if hasattr(Gui, "Snapper"):
        for snap_track in Gui.Snapper.trackers[2]:
            snap_track.setColor()


def _param_observer_callback_svg_pattern():
    utils.load_svg_patterns()
    if App.ActiveDocument is None:
        return
    msg = translate("draft", """Do you want to update the SVG pattern options
of existing objects in all opened documents?""")
    res = QtGui.QMessageBox.question(None, "Update SVG patterns", msg,
                                     QtGui.QMessageBox.Yes | QtGui.QMessageBox.No,
                                     QtGui.QMessageBox.No)
    if res == QtGui.QMessageBox.No:
        return
    pats = list(utils.svg_patterns())
    pats.sort()
    pats = ["None"] + pats
    for doc in App.listDocuments().values():
        doc.openTransaction("SVG pattern update")
        for obj in doc.Objects:
            if hasattr(obj, "ViewObject") \
                    and hasattr(obj.ViewObject, "Pattern") \
                    and hasattr(obj.ViewObject, "Proxy") \
                    and isinstance(obj.ViewObject.Proxy, view_base.ViewProviderDraft):
                vobj = obj.ViewObject
                old = vobj.Pattern
                if old in pats:
                    vobj.Pattern = pats
                else:
                    tmp_pats = [old] + pats[1:]
                    tmp_pats.sort()
                    vobj.Pattern = ["None"] + tmp_pats
                vobj.Pattern = old
        doc.commitTransaction()


def _param_observer_start(param = App.ParamGet("User parameter:BaseApp/Preferences/Mod/Draft")):
    param.AttachManager(ParamObserver())