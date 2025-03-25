import maya.cmds as cmds
import maya.mel as mel

import os
import sys

RIGNET_PATH = r"C:\Users\cosine\anaconda3\envs\rignet"

# Let Maya locate the DLLs (like MKL, CUDA, etc.)
os.environ["PATH"] += ";" + RIGNET_PATH + r"\Library\bin"
os.environ["PATH"] += ";" + RIGNET_PATH + r"\Lib\site-packages\torch\lib"


# Append the actual Python packages to sys.path
sys.path.append(RIGNET_PATH + r"\Lib\site-packages")


import numpy
import torch


class InstaRigCore:
    _WINDOW_NAME = "instaRigWindow"

    def __init__(self):
        print(f"[InstaRig] Backend Starts with RIGNET_PATH {RIGNET_PATH}")
        print("[InstaRig] PyTorch:", torch.__version__)
        print("[InstaRig] CUDA Available:", torch.cuda.is_available())
        print("[InstaRig] CUDA Version:", torch.version.cuda)

    # 以下为API占位方法
    def generate_skeleton(self, geometry, symmetry_axis, detail_level):
        """生成骨骼接口（待实现）"""
        print(f"Generating skeleton for {geometry}")
        return ["RootJoint", "Spine"]  # 示例返回

    def apply_skinning(self, geometry, skeleton_root):
        """应用蒙皮接口（待实现）"""
        print(f"Applying skinning to {geometry}")
        return True
    
    def log(self, s):
        print(f"[InstaRig] {s}")


#_insta_rig_core = InstaRigCore()