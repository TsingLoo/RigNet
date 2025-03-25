# If you have core rigging logic in a separate module (e.g., instaRig/core.py)
# from instaRig import core

from instaRig.core import InstaRigCore

import maya.cmds as cmds
import maya.api.OpenMaya as om


_rigCore = InstaRigCore()

def maya_useNewAPI():
    """
    Required when using Python API 2.0 plugin classes, even if empty.
    """
    pass

class InstaRigCommand(om.MPxCommand):
    """
    Simple plugin command class that just opens the UI.

    Example usage in Maya script editor:
        cmds.loadPlugin("InstaRig.py")
        cmds.InstaRig()
    """
    kPluginCmdName = "InstaRig"

    def __init__(self):
        super().__init__()

    @staticmethod
    def cmdCreator():
        return InstaRigCommand()

    def doIt(self, args):
        # Instantiate and show the UI
        ui = InstaRigUI()
        ui.show()


class InstaRigUI(object):

    _WINDOW_NAME = "instaRigWindow"

    def __init__(self):
        # We'll store control names here so we can reference them in callbacks.
        self.currentSelectionLabel = None
        self.logTextScroll = None
        self.skeletonTopologyList = None
        self.skinWeightsFrame = None
        self.skinWeightsList = None
        self.batchProcessingCheck = None
        self.batchFrame = None
        self.batchList = None
        self.symmetryAxisMenu = None
        self.skeletonFormatMenu = None
        self.skeletonDetailSlider = None

    def show(self):
        """
        Deletes any existing window of the same name, then builds and shows the UI.
        """
        if cmds.window(self._WINDOW_NAME, exists=True):
            cmds.deleteUI(self._WINDOW_NAME)

        self._build_ui()
        cmds.showWindow(self._WINDOW_NAME)

        # Call the "update selection" and "toggle batch" behaviors after UI is built
        self.update_selection_label()
        self.toggle_batch_frame()

    # --------------------------------
    # UI Layout
    # --------------------------------
    def _build_ui(self):
        """
        Constructs all controls, replicating the MEL layout as closely as possible.
        """
        cmds.window(self._WINDOW_NAME, 
                    title="InstaRig Auto-Rigging Tool", 
                    widthHeight=(400, 650))

        cmds.columnLayout(adjustableColumn=True, rowSpacing=10)

        # Title & Separator
        cmds.text(label="InstaRig Auto-Rigging Tool", 
                  align="center", 
                  font="boldLabelFont", 
                  height=30)
        cmds.separator(style="in", height=10)

        # Current Selection Label
        self.currentSelectionLabel = cmds.text(label="Using current scene selection as Geometry Group:")

        # Refresh / Import Buttons
        cmds.button(label="Refresh Selection", 
                    command=lambda _: self.update_selection_label())
        cmds.button(label="Import External Model File(s)", 
                    command=lambda _: self.import_external_model())
        cmds.separator(style="in", height=10)

        # Symmetry Axis Option
        cmds.text(label="Select Symmetry Axis:")
        self.symmetryAxisMenu = cmds.optionMenu(width=150)
        cmds.menuItem(label="None")
        cmds.menuItem(label="X")
        cmds.menuItem(label="Y")
        cmds.menuItem(label="Z")

        # Skeleton Format Option
        cmds.text(label="Skeleton Format:")
        self.skeletonFormatMenu = cmds.optionMenu(width=150)
        cmds.menuItem(label="Auto-Generated")
        cmds.menuItem(label="Standard Biped (BIP)")

        # Skeleton Detail Slider
        cmds.text(label="Skeleton Detail Level:")
        self.skeletonDetailSlider = cmds.floatSliderGrp(field=True, 
                                                        minValue=0.01, 
                                                        maxValue=0.1, 
                                                        value=0.05, 
                                                        step=0.01)

        # Frame: Skeleton Topology
        cmds.frameLayout(label="Skeleton Topology", 
                         collapsable=True, 
                         collapse=False)
        self.skeletonTopologyList = cmds.textScrollList(numberOfRows=6, allowMultiSelection=False)
        cmds.setParent("..")

        # Preload dummy text in Skeleton Topology
        cmds.textScrollList(self.skeletonTopologyList, edit=True, append=[
            "RootJoint",
            "    Spine",
            "        Head",
            "    LeftArm",
            "        LeftForeArm",
            "    RightArm",
            "        RightForeArm"
        ])

        # Frame: Skinning Weights (hidden by default)
        self.skinWeightsFrame = cmds.frameLayout(label="Skinning Weights", 
                                                 collapsable=True, 
                                                 collapse=False, 
                                                 visible=False)
        self.skinWeightsList = cmds.textScrollList(numberOfRows=4, allowMultiSelection=False)
        cmds.setParent("..")

        # Batch Processing Checkbox
        self.batchProcessingCheck = cmds.checkBox(label="Enable Batch Processing", 
                                                  changeCommand=lambda _: self.toggle_batch_frame())

        # Frame: Batch Processing List (hidden initially)
        self.batchFrame = cmds.frameLayout(label="Batch Processing List", 
                                           collapsable=True, 
                                           collapse=False, 
                                           visible=False)
        self.batchList = cmds.textScrollList(numberOfRows=4, allowMultiSelection=True)
        cmds.button(label="Add Selected to Batch List", 
                    command=lambda _: self.add_to_batch_list())
        cmds.button(label="Clear Batch List", 
                    command=lambda _: self.clear_batch_list())
        cmds.setParent("..")

        # One-Click Auto-Rigging
        cmds.button(label="One-Click Auto-Rigging", 
                    command=lambda _: self.auto_rig_procedure())

        # Process Log
        cmds.text(label="Process Log:")
        self.logTextScroll = cmds.textScrollList(numberOfRows=6, allowMultiSelection=False)

    # --------------------------------
    # Callbacks / Logic
    # --------------------------------
    def update_selection_label(self):
        """
        Replicates 'updateSelectionLabel()' from MEL:
          - Display the currently selected objects (or "No geometry selected").
        """
        sel = cmds.ls(selection=True)
        if not sel:
            label = "No geometry is selected now! Please select one or load external."
        else:
            label = "Using current scene selection as Geometry Group: " + " ".join(sel)

        cmds.text(self.currentSelectionLabel, edit=True, label=label)

    def import_external_model(self):
        """
        Replicates 'importExternalModel()' from MEL:
          - Opens file dialog, imports .obj or .fbx, appends to log, refreshes selection label.
        """
        # fileDialog2 returns a list of file paths
        file_paths = cmds.fileDialog2(fileMode=4,
                                      caption="Select Model Files to Import",
                                      fileFilter="Model Files (*.obj *.fbx)")
        if file_paths is None:
            self._append_log("No file selected for import.")
            return

        for fpath in file_paths:
            # Check extension
            ext = fpath.lower().rpartition(".")[-1]
            if ext == "obj":
                cmds.file(fpath, i=True, type="OBJ")
            else:
                cmds.file(fpath, i=True, type="FBX")

            self._append_log("Imported: " + fpath)

        self.update_selection_label()

    def toggle_batch_frame(self):
        """
        Replicates 'toggleBatchFrame()' from MEL:
          - Shows/hides the Batch Processing frame based on the checkbox value.
        """
        is_enabled = cmds.checkBox(self.batchProcessingCheck, query=True, value=True)
        cmds.frameLayout(self.batchFrame, edit=True, visible=is_enabled)

    def add_to_batch_list(self):
        """
        Replicates 'addToBatchList()' from MEL:
          - Adds selected objects to the batch list if not already in there.
        """
        sel = cmds.ls(selection=True)
        if not sel:
            self._append_log("No selection to add.")
            return

        current_items = cmds.textScrollList(self.batchList, query=True, allItems=True) or []
        for obj in sel:
            if obj not in current_items:
                cmds.textScrollList(self.batchList, edit=True, append=obj)

    def clear_batch_list(self):
        """
        Replicates 'clearBatchList()' from MEL: 
          - Clears all items from the batch list.
        """
        cmds.textScrollList(self.batchList, edit=True, removeAll=True)

    def auto_rig_procedure(self):
        """
        Replicates 'autoRigProcedure()' from MEL:
          - Uses batch list if enabled, otherwise current selection.
          - Reads UI fields (symmetry axis, detail slider, format).
          - Appends everything to log, mocks skeleton generation.
        """
        
        is_batch = cmds.checkBox(self.batchProcessingCheck, query=True, value=True)
        
        if is_batch:
            batch_items = cmds.textScrollList(self.batchList, query=True, allItems=True) or []
            if not batch_items:
                geo_group = "No objects in Batch List!"
            else:
                geo_group = " ".join(batch_items)
        else:
            sel = cmds.ls(selection=True)
            if not sel:
                geo_group = "Entire Mesh (No selection)"
            else:
                geo_group = " ".join(sel)

        sym_axis = cmds.optionMenu(self.symmetryAxisMenu, query=True, value=True)
        skel_format = cmds.optionMenu(self.skeletonFormatMenu, query=True, value=True)
        detail_level = cmds.floatSliderGrp(self.skeletonDetailSlider, query=True, value=True)

        # Summarize status
        status = "Auto-Rigging initiated with settings:\n"
        status += f"Geometry Group: {geo_group}\n"
        status += f"Symmetry Axis: {sym_axis}\n"
        status += f"Skeleton Detail: {detail_level}\n"
        status += f"Skeleton Format: {skel_format}\n"
        status += "Batch Processing: {}\n".format("Enabled" if is_batch else "Disabled")

        self._append_log(status)
        self._append_log("Generating joints, skin weights, and skeleton...")

        # Simulate hierarchy output for the "Skeleton Topology" textScrollList
        cmds.textScrollList(self.skeletonTopologyList, edit=True, removeAll=True)
        cmds.textScrollList(self.skeletonTopologyList, edit=True, append=[
            "RootJoint",
            "    Spine",
            "        Head",
            "    LeftArm",
            "        LeftForeArm",
            "    RightArm",
            "        RightForeArm"
        ])

        # The Skinning Weights Panel remains hidden, as in MEL logic
        self._append_log("Auto-Rigging completed successfully.")

    # --------------------------------
    # Private Helpers
    # --------------------------------
    def _append_log(self, text):
        """
        Adds a line to the log textScrollList.
        """
        cmds.textScrollList(self.logTextScroll, edit=True, append=text)


# ------------------------------------------------------------------------------------------
# Plugin lifecycle
# ------------------------------------------------------------------------------------------
def initializePlugin(mobject):
    pluginFn = om.MFnPlugin(mobject)
    try:
        pluginFn.registerCommand(InstaRigCommand.kPluginCmdName, 
                                 InstaRigCommand.cmdCreator)
        om.MGlobal.displayInfo("[InstaRig] Plugin loaded. Use `InstaRig` to launch.")
    except Exception as e:
        om.MGlobal.displayError(f"Failed to register InstaRig command: {e}")


def uninitializePlugin(mobject):
    pluginFn = om.MFnPlugin(mobject)
    try:
        pluginFn.deregisterCommand(InstaRigCommand.kPluginCmdName)
        om.MGlobal.displayInfo("[InstaRig] Plugin unloaded.")
    except Exception as e:
        om.MGlobal.displayError(f"Failed to deregister InstaRig command: {e}")
