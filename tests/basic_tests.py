#!/usr/bin/env python3

from .context import PyGeneology
from PyGeneology import pygenelib as pglib
from .example_families import *
import pdb

common_anc_pairs = [(albus, hugo), (albus, percy), (albus, teddy)]

def print_test_head(s):
    accent = "*" * len(s)
    print("\n{0}\n{1}\n{0}\n".format(accent, s.upper()))

def print_person(person):
    print("  {0}: {1}".format(person, person.fullname()))

def search_test(fam):
    print("Searching for first name 'Albus':")
    result = fam.search_by_name(first="Albus")
    for r in result:
        print_person(r)

    print("Searching for last name 'Potter'")
    result = fam.search_by_name(last="Potter")
    for r in result:
        print_person(r)

    print("Searching for FIRST name 'Weasley' (should yield nothing")
    result = fam.search_by_name(first="Weasley")
    for r in result:
        print_person(r)

    print("Searching for LAST name 'weasley'")
    result = fam.search_by_name(last="Weasley")
    for r in result:
        print_person(r)

def ancestor_test(fam):
    print("Albus's immediate ancestors:")
    anc = fam.ancestors_in_generation(albus, albus.generation-1)
    for a in anc:
        print_person(a)

    print("Albus's ancestors, two generations back:")
    anc = fam.ancestors_in_generation(albus, albus.generation-2)
    for a in anc:
        print_person(a)

def common_ancestor_test(fam):
    for a,b in common_anc_pairs:
        print("Common ancestors for {0} and {1}:".format(a.fullname(), b.fullname()))
        commons = fam.common_ancestors(a, b)
        for p in commons:
            print_person(p)

if __name__ == "__main__":
    print_test_head("search test")
    search_test(weasleys)

    print_test_head("ancestor list test")
    ancestor_test(weasleys)

    print_test_head("common ancestor test")
    common_ancestor_test(weasleys)
