# -*- coding: utf-8 -*-
"""用系统默认程序打开复件 PPT，方便用户直接翻看。"""
import os
import subprocess

PPTX = r"C:\Users\Administrator\WorkBuddy\2026-09-12-17-10-27\微光成炬-星火自有燎原时-复件.pptx"
os.startfile(PPTX)
print("OPENED")
