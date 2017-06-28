#!/usr/bin/env python3
from jllutils import numtostr
import pdb

"""
TODO:
-- get relationship names
-- handle in-law relations
-- add nicknames
-- more flexible search (substring or any name)
-- figure out how to handle adoption
-- figure out how to deal with multiple spouses (due to divorce or death)
-- include lifespans?
"""


class GenError(Exception):
    pass


class Family(object):
    """
    A Family object is a collection of Person objects; it contains methods to identify relationships between family
    members. However, it does so based on the properties of the Person instances added to it, it does not itself
    contain that information.
    """
    def __init__(self):
        """
        Instantiates an empty Family object.
        :return: none.
        """
        self.members = []
        self.oldest_generation = None

    def add_member(self, person):
        """
        Add a member to the family. Adding a person to the family does not inherently indicate any relationships, those
        must be added using the relevant methods on the instance of Person in question.
        :param person:
        :return: none.
        """
        self.members.append(person)
        if self.oldest_generation is None:
            self.oldest_generation = person.generation
        elif person.generation < self.oldest_generation:
            self.oldest_generation = person.generation

    def remove_member(self, person):
        """
        Remove the specified member of the family. It will remove them from the list of family members and update the
        oldest generation of the family if necessary
        :param person: the instance of Person to remove.
        :return: none.
        """
        if person not in self.members:
            raise ValueError("Could not find {0} ({1}) in members".format(person.fullname(), person))
        else:
            self.members.remove(person)
            if person.generation == self.oldest_generation:
                # If the person belonged to the oldest generation, we need to update
                # the generation just to be sure we didn't remove the only member
                # of that generation
                gens = [x.generation for x in self.members]
                self.oldest_generation = min(gens)

            #person.delete_me()

    def search_by_name(self, first=None, middle=None, last=None, unmarried_name=None, suffix=None):
        """
        Search the family for a family member whose name matches the name given. Each component of the name can be given
        separately, components not given (i.e. left as None) will not be matched.
        :param first: first name, as a string
        :param middle: middle name, as a string
        :param last: last name, as a string
        :param unmarried_name: unmarried name, as a string
        :param suffix: suffix, as a string
        :return: a list of instances of Person that match the given names
        """
        result = []
        for p in self.members:
            if p.name_eq(first=first, middle=middle, last=last, unmarried=unmarried_name, suffix=suffix):
                result.append(p)
        return result

    def find_members_in_generation(self, generation):
        """
        Find all members of the family in the specified generation
        :param generation: the generation number as an integer
        :return: a list of instances of Person
        """
        gen_mems = []
        for p in self.members:
            if p.generation == generation:
                gen_mems.append()

    def ancestors_in_generation(self, person, generation):
        """
        Finds all members of the family that are ancestors of the given person and in the given generation
        :param person: the instance of Person that you wish to find ancestors of
        :param generation: the generation (as an integer) the ancestors must be in
        :return: a list of instances of Person
        """
        if not isinstance(person, Person):
            raise TypeError("person must be an instance of pygenelib.Person")
        elif not isinstance(generation, int):
            raise TypeError("generation must be an integer")
        elif person.generation <= generation:
            raise GenError("Cannot have ancestor in same or younger generation")

        # Iterate backwards through generations, finding parents at each step
        # May need to handle the possibility of mixed generations?
        curr_gen_people = [person]
        curr_gen = person.generation
        while curr_gen > generation:
            next_gen_people = []
            for p in curr_gen_people:
                next_gen_people += p.parents
            next_gen = [x.generation for x in next_gen_people]
            ng_test = [x != next_gen[0] for x in next_gen]
            if any(ng_test):
                raise GenError("Mixed generations found in ancestry for {0}".format(person))

            curr_gen_people = next_gen_people
            if len(curr_gen_people) == 0:
                return curr_gen_people

            curr_gen = next_gen[0]

        return curr_gen_people

    def common_ancestors(self, member1, member2):
        """
        Given two members of the family, finds the nearest common ancestors. For example, given two siblings, it will
        return their parents. Given two first cousins, it will return their common grandparents. If one is a direct
        ancestor of the other, a list containing only the older member will be returned.
        :param member1: one member of the family, an instance of Person
        :param member2: the other member of the family, an instance of Person. It does not matter whether member2 is
        older or younger than member1
        :return: a list of instances of Person
        """
        if member1.generation <= member2.generation:
            older = member1
            younger = member2
        else:
            older = member2
            younger = member1

        if older.generation != younger.generation:
            # Possible that the older one is a direct ancestor
            ancestors = self.ancestors_in_generation(younger, older.generation)
            if older in ancestors:
                return [older]

        for g in range(older.generation - 1, self.oldest_generation - 1, -1):
            anc_of_younger = self.ancestors_in_generation(younger, g)
            anc_of_older = self.ancestors_in_generation(older, g)

            commons = []
            for a in anc_of_younger:
                if a in anc_of_older:
                    commons.append(a)
            if len(commons) > 0:
                return commons

        # No common ancestors found
        return []

    def get_relationship(self, base_person, other_person):
        """
        Figure out the relationship of the other_person to the base_person
        :param base_person: an instance of Person within the family
        :param other_person: an instance of Person within the family, whose relationship to the base_person will be
        calculated
        :return: a string describing the relationship between the two people
        """
        if not isinstance(base_person, Person):
            raise TypeError("base_person must be an instance of Person")
        if not isinstance(other_person, Person):
            raise TypeError("other_person must be an instance of Person")

        if base_person == other_person:
            return "same person"

        common_ancestors = self.common_ancestors(base_person, other_person)
        if len(common_ancestors) == 0:
            return "unrelated"

        gen_diff = base_person.generation - other_person.generation
        ancestor_gen = common_ancestors[0].generation
        for anc in common_ancestors:
            if anc.generation != ancestor_gen:
                raise NotImplementedError("Not implemented: common ancestors have different generations")

        # Okay, this is going to be a bit of a mess. We need to handle all the "special" cases first, i.e. parents,
        # children, siblings, aunts, uncles, nieces, nephews. We'll start with direct relationships because those are
        # reasonably straightforward
        #pdb.set_trace()
        if base_person in common_ancestors or other_person in common_ancestors:

            if gen_diff > 0:
                relation = other_person.gender.parent
            else:
                relation = other_person.gender.child
                gen_diff = abs(gen_diff)

            if gen_diff > 1:
                relation = "grand" + relation
            if gen_diff > 2:
                relation = (gen_diff-2)*"great-" + relation

            return relation

        # Now it gets more complicated, because we're dealing with the pool of relationships that can be generically
        # called "cousin" but which have some special cases
        dist_to_anc = min(base_person.generation - ancestor_gen, other_person.generation - ancestor_gen)
        #print("dist_to_anc = {}; gen_diff = {}".format(dist_to_anc, gen_diff))
        if dist_to_anc == 1:
            # If one of the people in question is only one generation away from the common ancestors, we're in the
            # special cases
            if gen_diff == 0:
                # siblings
                return other_person.gender.sibling
            else:
                if gen_diff > 0:
                    # the other person is younger, will be some sort of niece or nephew
                    relation = other_person.gender.auntuncle
                else:
                    relation = other_person.gender.niecenephew

                if abs(gen_diff) > 1:
                    relation = abs(gen_diff)*"great-" + relation

                return relation
        else:
            # Now we're into the generic "cousin" territory. Remember, first cousins have grandparents in common, second
            # cousins have great grandparents in common, etc. Cousins once removed are one generation apart, and the
            # generation closer to the common ancestors is used to determine the degree.
            relation = other_person.gender.cousin
            relation = numtostr.ordinal_number(dist_to_anc) + " " + relation
            if gen_diff != 0:
                relation += " " + numtostr.repeat_number(abs(gen_diff)) + " removed"

            return relation


class Person(object):
    curr_id = 0

    def __init__(self, gender, first="", middle="", last="", unmarried_name="", suffix="",
                 parent=None, spouse=None, child=None):
        """
        Create a new instance of Person, which represents a single member of a family
        :param gender: an instance of Gender that describes the gender of this person
        :param first: optional, if given, the first name as a string
        :param middle: optional, if given, the middle name as a string
        :param last: optional, if given, the last name as a string
        :param unmarried_name: optional, if given, the unmarried name (i.e. the last name prior to marriage) as a string
        :param suffix: optional, if given, the suffix as a string
        :param parent: optional, if given, an instance of Person that is one parent of this person.
        :param spouse: optional, if given, an instance of Person that is one spouse of this person.
        :param child: optional, if given, an instance of Person that is one child of this person.
        :return:
        """
        # Input type checking
        if not isinstance(gender, Gender):
            raise TypeError("gender must be an instance of Gender")
        if type(first) is not str:
            raise TypeError("first must be str, if given")
        if type(middle) is not str:
            raise TypeError("middle must be str, if given")
        if type(last) is not str:
            raise TypeError("last must be str, if given")
        if type(suffix) is not str:
            raise TypeError("suffix must be str, if given")

        self.id = Person.curr_id
        Person.curr_id += 1

        self.gender = gender
        self.first_name = first
        self.middle_name = middle
        self.last_name = last
        self.unmarried_name = unmarried_name
        self.suffix = suffix

        if parent is not None:
            self.generation = parent.generation + 1
        elif spouse is not None:
            self.generation = spouse.generation
        elif child is not None:
            self.generation = child.generation - 1
        else:
            self.generation = 0

        self.parents = []
        self.spouses = []
        self.children = []

        self.__add_relation(parent, "parent")
        self.__add_relation(spouse, "spouse")
        self.__add_relation(child, "child")



    def __eq__(self, other):
        """
        Check if "other" is the same person as this one
        :param other: another instance of Person, otherwise always returns False
        :return: boolean, True if other is the same instance
        """
        if not isinstance(other, Person):
            return False
        else:
            return self.id == other.id

    def __repr__(self):
        """
        String representation of this person
        :return: a string including the person's initials and memory address
        """
        return "<Person {0}, id {1}>".format(self.initials(), self.id)

    def name_eq(self, first=None, middle=None, last=None, unmarried=None, suffix=None):
        """
        Check if this person's name matches the given elements of the name. Any element of the name can be omitted; that
        element will not be checked. I.e., if only the first name "Bob" is given, this will return True if this person's
        first name is Bob, regardless of the other name elements.
        :param first: optional, first name as a string to match
        :param middle: optional, middle name as a string to match
        :param last: optional, last name as a string to match
        :param unmarried: optional, unmarried last name as a string to match
        :param suffix: optional, suffix as a string to match
        :return: boolean
        """
        if first is not None and first.lower() != self.first_name.lower():
            return False
        elif middle is not None and middle.lower() != self.middle_name.lower():
            return False
        elif last is not None and last.lower() != self.last_name.lower():
            return False
        elif unmarried is not None and unmarried.lower() != self.unmarried_name.lower():
            return False
        elif suffix is not None and suffix.lower() != self.suffix.lower():
            return False
        else:
            return True

    def fullname(self):
        """
        Return the full name of this person, which is "first middle last suffix".
        :return: the full name as a string
        """
        mname = " " + self.middle_name if len(self.middle_name) > 0 else ""
        lname = " " + self.last_name if len(self.last_name) > 0 else ""
        sffx = " " + self.suffix if len(self.suffix) > 0 else ""
        return self.first_name + mname + lname + sffx

    def initials(self):
        """
        Return the initials of this person (first, middle, last, with periods after each)
        :return: the initials as a string
        """
        first_initial = "{0}.".format(self.first_name[0].upper()) if len(self.first_name) > 0 else ""
        middle_initial = "{0}.".format(self.middle_name[0].upper()) if len(self.middle_name) > 0 else ""
        last_initial = "{0}.".format(self.last_name[0].upper()) if len(self.last_name) > 0 else ""
        return first_initial + middle_initial + last_initial

    def iterrels(self):
        """
        Returns a list of all direct relatives (parents, spouses, children) of this person, which can be iterated over
        :return: a list of instances of Person
        """
        rels = self.parents + self.spouses + self.children
        return rels

    def __add_relation(self, person, relation, force_add=False):
        """
        Internal method to add a relation, called by other specific methods
        :param person: the instance of Person to add
        :param relation: the relationship to this instance. May be father, mother, child, spouse.
        :param force_add: default False, set to True to override the error thrown if the generation is not one less for
        parents, one more for children, or equal for spouses.
        :return: nothing
        """
        if person is None:
            return
        elif not isinstance(person, Person):
            raise TypeError("{0} must be an instance of Person".format(relation))
        elif not force_add:
            if relation.lower() == "parent":
                target_gen = self.generation - 1
                error_str = "one less than"
            elif relation.lower() == "child":
                target_gen = self.generation + 1
                error_str = "one more than"
            elif relation.lower() == "spouse":
                target_gen = self.generation
                error_str = "equal to"
            else:
                raise ValueError("Relation {0} not recognized".format(relation))

            if person.generation != target_gen:
                raise GenError("Generation of {0} is not {1} mine".format(relation, error_str))

        if relation.lower() == "parent":
            self.parents.append(person)
            if self not in person.children:
                person.add_child(self)
        elif relation.lower() == "child":
            self.children.append(person)
            if self not in person.parents:
                person.add_parent(self)
        elif relation.lower() == "spouse":
            self.spouses.append(person)
            if self not in person.spouses:
                person.add_spouse(self)
        else:
            raise ValueError("Relation {0} not recognized".format(relation))

    def add_parent(self, parent, force_add=False):
        """
        Add a parent to this person (links another instance of Person as the parent to this instance)
        :param parent: an instance of Person to add as a parent
        :param force_add: optional, default = False, if false, an error is thrown if the generation of the proposed
        parent is not one less than the generation of this instance of person
        :return: none
        """
        self.__add_relation(parent, "parent", force_add=force_add)

    def add_child(self, child, force_add=False):
        """
        Add a child to this person (links another instance of Person as the child to this instance)
        :param child: an instance of Person to add as a child
        :param force_add: optional, default = False, if false, an error is thrown if the generation of the proposed
        child is not one greater than the generation of this instance of person
        :return: none
        """
        self.__add_relation(child, "child", force_add=force_add)

    def add_spouse(self, spouse, force_add=False):
        """
        Add a spouse to this person (links another instance of Person as the spouse to this instance)
        :param spouse: an instance of Person to add as a spouse
        :param force_add: optional, default = False, if false, an error is thrown if the generation of the proposed
        spouse is not equal to the generation of this instance of person
        :return: none
        """
        self.__add_relation(spouse, "spouse", force_add=force_add)

    def remove_relation(self, person):
        """
        Removes the given instance of Person as a relation to this instance
        :param person: the instance of Person to remove as a relation
        :return: none
        """
        if person in self.parents:
            self.parents.remove(person)
        elif person in self.children:
            self.children.remove(person)
        elif person in self.spouses:
            self.spouses.remove(person)

    def delete_me(self):
        for rel in self.iterrels():
            rel.remove_relation(self)
        del self


class Gender(object):
    """
    Class representing the gender of a person. Contains the proper titles for familial relations, even typically gender
    neutral relationships like "cousin" (just in case that also needs to become gender-specific)
    """
    @property
    def parent(self):
        return self._parent

    @property
    def child(self):
        return self._child

    @property
    def sibling(self):
        return self._sibling

    @property
    def spouse(self):
        return self._spouse

    @property
    def auntuncle(self):
        return self._auntuncle

    @property
    def niecenephew(self):
        return self._niecenephew

    @property
    def cousin(self):
        return self._cousin

    def __init__(self, parental_title, child_title, sibling_title, spouse_title, auntuncle_title,
                 niecenephew_title, cousin_title="cousin"):
        """
        Create an instance of Gender that contains all of the proper familial titles for a person of this gender
        :param parental_title: the title (e.g. "father" or "mother") to use if this person is a parent or grandparent
        :param child_title: the title (e.g. "son" or "daughter") to use if this person is a child or grandchild
        :param sibling_title: the title (e.g. "brother" or "sister") to use if this person is a sibling
        :param spouse_title: the title (e.g. "husband" or "wife") to use if this person is a spouse
        :param auntuncle_title: the title (e.g. "aunt" or "uncle") to use if this person is an aunt or uncle
        :param cousin_title: the title (e.g. "cousin") to use if this person is a cousin (i.e. this is essentially the
        default relationship if none of the others apply). This is the only title that has a default value ("cousin").
        :return: none.
        """
        if not isinstance(parental_title, str):
            raise TypeError("parental_title must be a string")
        if not isinstance(child_title, str):
            raise TypeError("child_title must be a string")
        if not isinstance(sibling_title, str):
            raise TypeError("sibling_title must be a string")
        if not isinstance(spouse_title, str):
            raise TypeError("spouse_title must be a string")
        if not isinstance(auntuncle_title, str):
            raise TypeError("auntuncle_title must be a string")
        if not isinstance(niecenephew_title, str):
            raise TypeError("niecenephew_title must be a string")
        if not isinstance(cousin_title, str):
            raise TypeError("cousin_title must be a string")

        self._parent = parental_title
        self._child = child_title
        self._sibling = sibling_title
        self._spouse = spouse_title
        self._auntuncle = auntuncle_title
        self._niecenephew = niecenephew_title
        self._cousin = cousin_title

male = Gender("father", "son", "brother", "husband", "uncle", "nephew")
female = Gender("mother", "daughter", "sister", "wife", "aunt", "niece")
neuter = Gender("parent", "child", "sibling", "spouse", "pibling", "nibling")

def import_test():
    print("Successful import of {0}".format(__name__))
