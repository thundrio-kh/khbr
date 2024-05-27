import shutil
import time, json, os, random, yaml
from khbr.KH2.AreaDataScript import AreaDataScript
from khbr.KH2.AssetGenerator import AssetGenerator
from khbr.KH2.KingdomHearts2 import KingdomHearts2
from khbr.KH2.ModWriter import ModWriter
from khbr.randomizer import Randomizer
from khbr.randutils import log_output

import os, subprocess
#### Mostly for debug purposes
class openKH:
    def __init__(self, workdir):
        self.workdir = workdir
    def _check_binary(self, binary):
        if not os.path.isfile(os.path.join(self.workdir, binary)):
            raise Exception("{} not found".format(binary))
    def _run_binary(self, binary, args=[], inp='', debug=True):
        self._check_binary(binary)
        if debug:
            log_output(args)
            import sys; sys.stdout.flush()
        proc = subprocess.Popen([binary] + args, cwd=self.workdir, shell=True)
        output = proc.communicate(inp)
        if debug:
            log_output(output)
        return output[0]
    def bar_list(self, bar):
        # given a bar file, list the contents
        log_output(self._run_binary('OpenKh.Command.Bar.exe', args=['list', bar]).decode('utf-8'))
    def bar_extract(self, bar, outdir):
        # extract bar file to a directory (directory must exist prior to running this)
        self._run_binary('OpenKh.Command.Bar.exe', args=['unpack', '-o', outdir, bar])
    def bar_build(self, projectfn, outputfn):
        self._run_binary('OpenKh.Command.Bar.exe', args=['pack', '-o', outputfn, projectfn])
    def spawnscript_extract(self, pth, outfn):
        self._run_binary('OpenKh.Command.SpawnScript.exe', args=['decompile', '-o', outfn, pth], debug=True)
    def spawnscript_compile(self, pth, outfn):
        self._run_binary('OpenKh.Command.SpawnScript.exe', args=['compile', '-o', outfn, pth])
    def spawnpoint_extract(self, pth, outfn):
        self._run_binary('OpenKh.Command.SpawnScript.exe', args=['unpoint', '-o', outfn, pth])
    def spawnpoint_build(self, pth, outfn):
        self._run_binary('OpenKh.Command.SpawnScript.exe', args=['repoint', '-o', outfn, pth])
                


from gooey import Gooey, GooeyParser

@Gooey(program_name="Kingdom Hearts 2Enemy Tester")
def main_ui():
    main()

def main(cli_args: list=[]):
    last_settings = {
        "enemy": "shadow",
    }
    default_config = {
        "openkh_dir": ""
    }
    if os.path.exists("se_last_settings.json"):
        last_settings = json.load(open("se_last_settings.json"))
    if os.path.exists("se_config.json"):
        default_config = json.load(open("se_config.json"))

    parser = GooeyParser()

    options = parser.add_argument_group(
        "Options",
        """prototype boss rush mod
    selected boss replacement
    start in selected boss room
    start with good stuff for combat
    winning the fight is seed over
    """
    )

    log_output(last_settings, log_level=0)

    kh2 = KingdomHearts2()
    enemies = kh2.get_valid_enemies()
    options.add_argument("-select_enemy", choices=sorted(enemies), default=last_settings.get("enemy"))

    options.add_argument("-openkh_dir", help="Path to OpenKH folder.", default=default_config.get("openkh_dir"), widget='DirChooser')

    # Parse and print the results
    if cli_args:
        args = parser.parse_args(cli_args)
    else:
        args = parser.parse_args()


    settings_to_write = {
        "enemy": args.select_enemy
    }
    config_to_write = {
        "openkh_dir": args.openkh_dir
    }
    json.dump(config_to_write, open("se_config.json", "w"))
    json.dump(settings_to_write, open("se_last_settings.json", "w"))

    openkh_dir = args.openkh_dir

    seed_options = {
        "memory_expansion": True,
        "selected_enemy": args.select_enemy,
        "other_enemies": True
    }

    moddir = "C:\\Users\\12sam\\Desktop\\openkh\\mods\\kh2\\thundrio-kh"
    fn = "devmod"
    if os.path.exists(os.path.join(moddir, fn)):
        shutil.rmtree(os.path.join(moddir, fn))
    rando = Randomizer(tempdir=moddir, tempfn=fn, deletetmp=False)
    b64 = rando.generate_seed("kh2", seed_options)


    log_output("All Done!", log_level=0)

if __name__ == "__main__":
    import sys
    main()
    # if "cmd" in sys.argv:
    #     main()
    # else:
    #     main_ui()
