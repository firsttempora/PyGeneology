#!/usr/bin/env python3

"""
TODO:
-- add gender classes, add gender to Person. these classes should be used to define relationship names
-- get relationship names
-- handle in-law relations
-- add nicknames
-- more flexible search (substring or any name)
"""


class GenError(Exception):
    pass


class Family(object):
    def __init__(self):
        self.members = []
        self.oldest_generation = None

    def add_member(self, person):
        self.members.append(person)
        if self.oldest_generation is None:
            self.oldest_generation = person.generation
        elif person.generation < self.oldest_generation:
            self.oldest_generation = person.generation

    def remove_member(self, person):
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

            person.delete_me()

    def search_by_name(self, first=None, middle=None, last=None, unmarried_name=None, suffix=None):
        result = []
        for p in self.members:
            if p.name_eq(first=first, middle=middle, last=last, unmarried=unmarried_name, suffix=suffix):
                result.append(p)
        return result

    def find_members_in_generation(self, generation):
        gen_mems = []
        for p in self.members:
            if p.generation == generation:
                gen_mems.append()

    def ancestors_in_generation(self, person, generation):
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
                return older

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


class Person(object):
    curr_id = 0

    def __init__(self, gender, first="", middle="", last="", unmarried_name="", suffix="",
                 parent=None, spouse=None, child=None):
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
        if not isinstance(other, Person):
            return False
        else:
            return self.id == other.id

    def __repr__(self):
        return "<Person {0}, id {1}>".format(self.initials(), self.id)

    def name_eq(self, first=None, middle=None, last=None, unmarried=None, suffix=None):
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
        mname = " " + self.middle_name if len(self.middle_name) > 0 else ""
        lname = " " + self.last_name if len(self.last_name) > 0 else ""
        sffx = " " + self.suffix if len(self.suffix) > 0 else ""
        return self.first_name + mname + lname + sffx

    def initials(self):
        first_initial = "{0}.".format(self.first_name[0].upper()) if len(self.first_name) > 0 else ""
        middle_initial = "{0}.".format(self.middle_name[0].upper()) if len(self.middle_name) > 0 else ""
        last_initial = "{0}.".format(self.last_name[0].upper()) if len(self.last_name) > 0 else ""
        return first_initial + middle_initial + last_initial

    def iterrels(self):
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
        self.__add_relation(parent, "parent", force_add=force_add)

    def add_child(self, child, force_add=False):
        self.__add_relation(child, "child", force_add=force_add)

    def add_spouse(self, spouse, force_add=False):
        self.__add_relation(spouse, "spouse", force_add=force_add)

    def remove_relation(self, person):
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

    def __init__(self, parental_title, child_title, sibling_title, spouse_title, auntuncle_title):
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

        self._parent = parental_title
        self._child = child_title
        self._sibling = sibling_title
        self._spouse = spouse_title
        self._auntuncle = auntuncle_title

male = Gender("father", "son", "brother", "husband", "uncle")
female = Gender("mother", "son", "sister", "wife", "aunt")



def import_test():
    print("Successful import of {0}".format(__name__))
