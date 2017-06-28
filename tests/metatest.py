#!/usr/bin/env python3

from .context import PyGeneology
from PyGeneology import pygenelib as pglib

pglib.import_test()

# To get these to work, they need to be run from the parent PyGeneology directory with
# python -m tests.metatest
# or whichever test function you wish to use.