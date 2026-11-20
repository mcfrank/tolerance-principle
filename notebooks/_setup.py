"""Shared setup for the chapters: make the simulation modules importable and fix plot style."""
import os
import sys
import warnings

warnings.filterwarnings("ignore")
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath("__file__")), "..", "sims"))

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

plt.rcParams.update({"figure.figsize": (6.2, 3.8), "figure.dpi": 110, "axes.spines.top": False,
                     "axes.spines.right": False, "legend.frameon": False, "font.size": 10})
pd.set_option("display.precision", 2)
