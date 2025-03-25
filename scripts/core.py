import maya.cmds as cmds
import maya.mel as mel
import os

RIGNET_PATH = r"C:\Users\david\anaconda3\envs\rignet\Lib\site-packages"
sys.path.append(RIGNET_PATH)

class InstaRigCore:
    _WINDOW_NAME = "instaRigWindow"

    def __init__(self):
        """loading MEL UI script"""
        mel_script = os.path.join(
            os.path.dirname(__file__),
            "scripts\\ui.mel"
        ).replace("\\", "/")
        if os.path.exists(mel_script):
            mel.eval(f'source "{mel_script}";')

    def show_ui(self):
        """显示主界面"""
        if cmds.window(self._WINDOW_NAME, exists=True):
            cmds.deleteUI(self._WINDOW_NAME)
        mel.eval("instaRig_createUI")

    # 以下为API占位方法
    def generate_skeleton(self, geometry, symmetry_axis, detail_level):
        """生成骨骼接口（待实现）"""
        print(f"Generating skeleton for {geometry}")
        return ["RootJoint", "Spine"]  # 示例返回

    def apply_skinning(self, geometry, skeleton_root):
        """应用蒙皮接口（待实现）"""
        print(f"Applying skinning to {geometry}")
        return True


_insta_rig_core = InstaRigCore()