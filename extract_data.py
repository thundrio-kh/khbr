from kh2lib.kh2lib import kh2lib
import os, json
lib = kh2lib()

kh2_in_dir = os.path.join(lib.gamedir)


## Extract data from the obj/msn/ard BARs
kh2_out_dir = os.path.join(lib.gamedir, "bars")

folders = ["obj", "msn", "ard"]
# Extract all bars
# problem - output path shouldn't include the .
for root, dirs, files in os.walk(kh2_in_dir):
    path = root.split(os.sep)
    for file in files:
        fn = os.path.join(root, file)
        if open(fn, "rb").read(3) == b'BAR':
            subfn = fn.replace(kh2_in_dir, '')[1:]
            # make outfn, ensure output folder exists
            if len([c for c in subfn if c == os.sep]) == 0:
                subfn = os.path.join("root", *subfn.split(os.sep))
            basefolder = subfn.split(os.sep)[0]
            if basefolder in folders:
                outfn = os.path.join(kh2_out_dir, '.'.join(subfn.split(".")[:-1]))
                if not os.path.isdir(os.path.dirname(outfn)):
                    os.makedirs(os.path.dirname(outfn))
                print(fn, outfn)
                lib.editengine.bar_extract(fn, outfn)

## Create folders containing just bdx, spawnpoint, and spawanscript files

import shutil
subfiles = {
    "bdx": shutil.copy,
    "spawn": lib.openkh.spawnpoint_extract,
    "script": lib.openkh.spawnscript_extract
}
for sf in subfiles:
    subfile_out_dir = os.path.join(kh2_in_dir, "subfiles", sf)
    for root, dirs, files in os.walk(kh2_out_dir):
        path = root.split(os.sep)
        for f in files:
            fn = os.path.join(root, f)
            if fn.endswith(f".{sf}"):
                subfn = fn.replace(kh2_out_dir, '')
                if len([c for c in subfn if c == os.sep]) == 1:
                    subfn = os.path.join("root", *subfn.split(os.sep))
                subfoldername = subfn.split(os.sep)[1]
                catname = subfn.split(os.sep)[-2]
                # catname = '.'.join(catname.split(".")[:-1]) # Remove later
                outfn = os.path.join(subfile_out_dir, subfoldername, catname, f)
                if not os.path.isdir(os.path.dirname(outfn)):
                    os.makedirs(os.path.dirname(outfn))
                print(fn,outfn)
                subfiles[sf](fn, outfn)