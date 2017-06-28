#!/usr/bin/env python3

from .context import PyGeneology
from PyGeneology import pygenelib as pglib
from .example_families import *
import pdb

common_anc_pairs = [(albus, hugo), (albus, percy), (albus, teddy)]
relation_pairs = [{"people":(harry, lily), "reln": ("son", "mother")},
                  {"people":(harry, james), "reln": ("son", "father")},
                  {"people":(lp2, ginny), "reln": ("daughter", "mother")},
                  {"people":(albus, lily), "reln": ("grandson", "grandmother")},
                  {"people":(albus, james), "reln": ("grandson", "grandfather")},
                  {"people":(lp2, lily), "reln": ("granddaughter", "grandmother")},
                  {"people":(lp2, james), "reln": ("granddaughter", "grandfather")},
                  {"people":(albus, ron), "reln": ("nephew", "uncle")},
                  {"people":(albus, hermione), "reln": ("nephew", "aunt")},
                  {"people":(rose, harry), "reln": ("niece", "uncle")},
                  {"people":(rose, ginny), "reln": ("niece", "aunt")},
                  {"people":(albus, hugo), "reln": ("first cousin", "first cousin")}]

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
    for pair in relation_pairs:
        a = pair['people'][0]
        b = pair['people'][1]
        print("Common ancestors for {0} and {1}:".format(a.fullname(), b.fullname()))
        commons = fam.common_ancestors(a, b)
        for p in commons:
            print_person(p)

def relation_test(fam):
    for pair in relation_pairs:
        reln1 = fam.get_relationship(pair['people'][1], pair['people'][0])
        reln2 = fam.get_relationship(pair['people'][0], pair['people'][1])
        print("{} and {} are {} and {} (should be {} and {})".format(
            pair['people'][0].fullname(), pair['people'][1].fullname(), reln1, reln2,
            pair['reln'][0], pair['reln'][1]
        ))


if __name__ == "__main__":
    print_test_head("search test")
    search_test(weasleys)

    print_test_head("ancestor list test")
    ancestor_test(weasleys)

    print_test_head("common ancestor test")
    common_ancestor_test(weasleys)

    print_test_head("relationship test")
    relation_test(weasleys)
