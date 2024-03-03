import sys
import logging
import importlib
from pathlib import Path
import inspect
import re

def load_plugins(plugin_name):
    path = Path(f"ban_all/modules/{plugin_name}.py")
    name = "ban_all.modules.{}".format(plugin_name)
    spec = importlib.util.spec_from_file_location(name, path)
    load = importlib.util.module_from_spec(spec)
    load.logger = logging.getLogger(plugin_name)
    spec.loader.exec_module(load)
    sys.modules["LegendGirl.LegendBoy." + plugin_name] = load
    print("💝[Bot Spam] Has Imported " + plugin_name)
