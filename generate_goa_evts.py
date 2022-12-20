# Some annoying permission issues preventing this from working
import os, shutil

outdir = os.path.join(os.path.dirname(__file__), "khbr", "KH2", "data", "goa", "ard")
if os.path.exists(outdir):
    shutil.rmtree(outdir)
os.makedirs(outdir)

goadir = "GoA-ROM-Edition"
if os.path.exists(goadir):
    shutil.rmtree(goadir)

cloneurl = "https://github.com/KH2FM-Mods-Num/GoA-ROM-Edition.git"

import subprocess
subprocess.check_output(["git", "clone", cloneurl])

shutil.copy(os.path.join(goadir, "ard"), outdir)

goadir = "GoA-ROM-Edition"
if os.path.exists(goadir):
    shutil.rmtree(goadir)