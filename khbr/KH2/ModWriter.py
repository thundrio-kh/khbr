import os, yaml

from khbr.KH2.EnmpManager import EnmpManager
class ModWriter:
    def __init__(self, outdir, writeMethod=None):
        self.write_method = writeMethod or self.default_write_method
        self.enmp_manager = EnmpManager()
        self.outdir = outdir

    @staticmethod
    def default_write_method(outfn, relfn, data):
        if not os.path.isdir(os.path.dirname(outfn)):
            os.makedirs(os.path.dirname(outfn))
        if type(data) == str:
            data = bytes(data, "utf-8")
        with open(outfn, "wb") as f:
            f.write(data)

    def writeSpawnpoint(self, ardname, spawnpoint, obj):
        outfn = os.path.join(self.outdir, "files", "ard", ardname, spawnpoint+".yml")
        fn = os.path.join("files", "ard", ardname, spawnpoint+".yml")
        self.write_method(outfn, fn, yaml.dump(obj))
        return {
            "method": "spawnpoint",
            "name": spawnpoint,
            "source": [{"name": fn}],
            "type": "AreaDataSpawn"
        }

    def writeObj(self, obj):
        outfn = os.path.join(self.outdir, "files", "root", "00objentry.bin")
        fn = os.path.join("files", "root", "00objentry.bin")
        self.write_method(outfn, fn, yaml.dump(obj))
        return {
            "name": "00objentry.bin",
            "method": "listpatch",
            "source": [
                {
                    "name": fn,
                    "type": "objentry"
                }
            ]
        }
    
    def writePlrp(self, plrp):
        outfn = os.path.join(self.outdir, "files", "root", "plrp.list")
        fn = os.path.join("files", "root", "plrp.list")
        self.write_method(outfn, fn, yaml.dump(plrp))
        return {
            "name": "00battle.bin",
            "method": "binarc",
            "source": [
                {
                    "name": "plrp",
                    "method": "listpatch",
                    "source": [
                        {
                            "name": fn,
                            "type": "plrp"
                        }
                    ],
                    "type": "List"
                }
            ]
        }
    
    def writeBons(self, bons):
        outfn = os.path.join(self.outdir, "files", "root", "bons.list")
        fn = os.path.join("files", "root", "bons.list")
        self.write_method(outfn, fn, yaml.dump(bons))
        return {
            "name": "00battle.bin",
            "method": "binarc",
            "source": [
                {
                    "name": "bons",
                    "method": "listpatch",
                    "source": [
                        {
                            "name": fn,
                            "type": "bons"
                        }
                    ],
                    "type": "List"
                }
            ]
        }
    
    def writeLvup(self, lvup):
        outfn = os.path.join(self.outdir, "files", "root", "lvup.list")
        fn = os.path.join("files", "root", "lvup.list")
        self.write_method(outfn, fn, yaml.dump(lvup))
        return {
            "name": "00battle.bin",
            "method": "binarc",
            "source": [
                {
                    "name": "lvup",
                    "method": "listpatch",
                    "source": [
                        {
                            "name": fn,
                            "type": "lvup"
                        }
                    ],
                    "type": "List"
                }
            ]
        }
    
    def writeFmlv(self, fmlv):
        outfn = os.path.join(self.outdir, "files", "root", "fmlv.list")
        fn = os.path.join("files", "root", "fmlv.list")
        self.write_method(outfn, fn, yaml.dump(fmlv))
        return {
            "name": "00battle.bin",
            "method": "binarc",
            "source": [
                {
                    "name": "fmlv",
                    "method": "listpatch",
                    "source": [
                        {
                            "name": fn,
                            "type": "fmlv"
                        }
                    ],
                    "type": "List"
                }
            ]
        }

    def writeEnmp(self, enmp):
        outfn = os.path.join(self.outdir, "files", "root", "enmp.list")
        fn = os.path.join("files", "root", "enmp.list")
        data = self.enmp_manager.dumpEnmpData(enmp)
        self.write_method(outfn, fn, data)
        return {
            "name": "00battle.bin",
            "method": "binarc",
            "source": [
                {
                    "name": "enmp",
                    "type": "List",
                    "method": "copy",
                    "source": [
                        {
                            "name": fn
                        }
                    ]
                }
            ]
        }

    def writeCmd(self, obj):
        outfn = os.path.join(self.outdir, "files", "root", "cmd.list")
        fn = os.path.join("files", "root", "cmd.list")
        self.write_method(outfn, fn, yaml.dump(obj))
        return {
            "name": "03system.bin",
            "method": "binarc",
            "source": [
                {
                    "name": "cmd",
                    "type": "list",
                    "method": "listpatch",
                    "source": [
                        {
                            "name": fn,
                            "type": "cmd"
                        }
                    ]
                }
            ]
        }
    
    def writeMemt(self, data):
        outfn = os.path.join(self.outdir, "files", "root", "memt.list")
        fn = os.path.join("files", "root", "memt.list")
        self.write_method(outfn, fn, data)
        return {
            "name": "03system.bin",
            "method": "binarc",
            "source": [
                {
                    "name": "memt",
                    "type": "list",
                    "method": "copy",
                    "source": [
                        {
                            "name": fn
                        }
                    ]
                }
            ]
        }

    def writeMset(self, mset_fn, data):
        outfn = os.path.join(self.outdir, "files", "obj", mset_fn)
        fn = os.path.join("files", "obj", mset_fn)
        self.write_method(outfn, fn, data)
        return {
            "name": f"obj/{mset_fn}",
            "method": "copy",
            "source": [
                {
                    "name": fn
                }
            ]
        }

    def writeMSG(self, name, obj):
        outfn = os.path.join(self.outdir, "files", "msg", name+".yml")
        fn = os.path.join("files", "msg", name+".yml")
        self.write_method(outfn, fn, yaml.dump(obj))
        # Whole binarc at once is maybe weird to return
        return {
            "name": f"msg/jp/{name}.bar",
            "multi": [
                {"name": f"msg/us/{name}.bar"},
                {"name": f"msg/uk/{name}.bar"}
            ],
            "method": "binarc",
            "source": [
                {
                    "name": name,
                    "type": "list",
                    "method": "kh2msg",
                    "source": [
                        {
                            "name": fn,
                            "language": "en"
                        }
                    ]
                }
            ]
        }

    def writeAreaDataProgram(self, ardname, scripttype, programnumber, program):
        filename = scripttype+"_"+str(programnumber)+".areadataprogram"
        outfn = os.path.join(self.outdir, "files", "ard", ardname, filename)
        fn = os.path.join("files", "ard", ardname, filename)
        self.write_method(outfn, fn, program)
        return {
            "method": "areadatascript",
            "name": scripttype,
            "source": [{"name": fn}],
            "type": "AreaDataScript"
        }
    
    
    def writeEvent(self, eventnumber, eventname, event, write=True):
        filename = eventname+".event"
        outfn = os.path.join(self.outdir, "files", "event", filename)
        fn = os.path.join("files", "event", filename)
        if write:
            self.write_method(outfn, fn, event)
        return {
            "method": "copy",
            "name": str(eventnumber),
            "source": [{"name": fn}],
            "type": "Event"
        }

    def writeBin(self, bincontent, binname, gamepath):
        outfn = os.path.join(self.outdir, "files", gamepath)
        fn = os.path.join("files", gamepath)
        self.write_method(outfn, fn, bincontent)
        return {
            "method": "copy",
            "name": binname,
            "source": [{"name": fn}]
        }

    def writeAi(self, aifn, modelname, tpe, data):
        relfn = os.path.join("files", "ai", modelname+"_"+aifn)
        outfn = os.path.join(self.outdir, relfn)
        
        self.write_method(outfn, relfn, data)
        formattedname = f"obj/{modelname}.mdlx" if tpe == "obj" else f"msn/jp/{modelname}.bar"
        asset = {
            "method": "binarc",
            "name": formattedname,
            "source": [
                {
                    "method": "bdscript",
                    "name": os.path.basename(aifn).split(".")[0][:4],
                    "source": [{"name": relfn}],
                    "type": "Bdx"
                }
            ]
        }
        if "msn" in formattedname:
            asset["multi"] = [{"name": formattedname.replace("jp", r)} for r in ["us","fr","gr","it","sp","uk"]]
        return asset

    def writeLua(self, luafn, data):
        relfn = os.path.join("files", "lua", luafn)
        outfn = os.path.join(self.outdir, relfn)

        self.write_method(outfn, relfn, data)
        return {
            "method": "copy",
            "name": f"scripts/{luafn}",
            "source": [{"name": relfn}]
        }

    def writeMsn(self, msnname, data):
        relfn = os.path.join("files", "msns", msnname + ".bar")
        outfn = os.path.join(self.outdir, relfn)
        self.write_method(outfn, relfn, data)
        formattedname = f"msn/jp/{msnname}.bar"
        # create the asset
        asset = {
            "method": "copy",
            "name": formattedname,
            "multi": [{"name": formattedname.replace("jp", r)} for r in ["us","fr","gr","it","sp","uk"]],
            "source": [{"name": relfn}]
        }
        return asset

    def writeCopiedSubfile(self, ardname, subfilename, filetype, assetpath):
        filename = os.path.basename(assetpath)
        outfn = os.path.join(self.outdir, "files", "ard", ardname, filename)
        fn = os.path.join("files", "ard", ardname, filename)
        filebytes = open(assetpath, "rb").read()
        self.write_method(outfn, fn, filebytes)
        return {
            "method": "copy",
            "name": subfilename,
            "source": [{"name": fn}],
            "type": filetype
        }