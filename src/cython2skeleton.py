from __future__ import annotations
import queue
from dataclasses import dataclass
from enum import IntEnum
from typing import Optional

import fire as fire
import binary2strings as b2s


class PythonEntityType(IntEnum):
    """
    Enum for the different types of python entities
    """
    CLASS = 0
    FUNCTION = 1
    METHOD = 2
    VARIABLE = 3
    CONSTANT = 4
    MODULE = 5
    PACKAGE = 6
    IMPORT = 7
    DOCSTRING = 8
    COMMENT = 9
    UNKNOWN = 10
    ROOT_TRAVERSAL_OBJECT = 99


@dataclass
class PythonEntity:
    """
    Represents a python entity, such as a class, a function, a method, a variable, etc.
    """
    name: str
    type: PythonEntityType
    docstring: str
    comments: list[str]
    parent: Optional[PythonEntity]
    children: list[PythonEntity]

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        return f"{self.type.name}: {self.name}"


class Cython2Skeleton:
    """
    Takes a cython compiled file (.elf, .so) as input and reconstructs the original class and function names
    from the python file.
    Adds as much information as possible into the produced python file, such as docstrings and comments.
    """

    CYTHON_KEYWORDS = ["pyobject", "pytype", "pycode", "pytuple", "pydict", "pylist", "pyint", "pyfloat", "pyexc",
                       "pymethod", "pybytes", "pyframe", "pyobject"]
    ELF_KEYWORDS = ["glibc", ".so."]

    COMMENT_KEYWORDS = [":param", ":return", "@param", "@return"]

    def __init__(self, filepath: str):
        self._filepath = filepath
        self._skeleton = None
        self._comments = None

    def _get_strings_from_file(self, min_chars: int = 5, only_interesting: bool = True) -> list[str]:
        """
        Get all strings from the file using python's binary2strings library
        """
        with open(self._filepath, "rb") as f:
            buffer = f.read()
            # [(string, encoding, span, is_interesting), ] \
            result = b2s.extract_all_strings(buffer, min_chars=min_chars, only_interesting=False)
            # only keep the strings from the result list using map
            result = list(map(lambda x: x[0], result))
            # remove duplicates
            result = list(set(result))
            # remove all strings that match a set of keywords
            result = list(filter(lambda x: not any([keyword in x.lower() for keyword in self.CYTHON_KEYWORDS]), result))
            return result

    def _get_comments(self, in_strings: list[str]) -> list[str]:
        # get all strings that contain COMMENT_KEYWORDS
        return list(filter(lambda x: any([keyword in x.lower() for keyword in self.COMMENT_KEYWORDS]), in_strings))

    def _get_python_symbolpaths(self, in_strings: list[str]):
        """
        Get all symbol paths from the file
        A symbol path must contain at least one dot.
        The dot separates package paths and the class name and the function name
        Each symbol name must at least occur twice in the list of strings
        """
        # 1.) filter for strings that contain at least one dot, but don't start with a dot
        symbol_candidates = filter(lambda x: "." in x and not x.startswith("."), in_strings)

        # 2.) comprise only dots, underscores, letters and numbers
        symbol_candidates = list(
            filter(lambda x: all([c.isalnum() or c == "." or c == "_" for c in x]), symbol_candidates))

        # 3.) remove all strings that match a set of elf keywords
        symbol_candidates = list(
            filter(lambda x: not any([keyword in x.lower() for keyword in self.ELF_KEYWORDS]), symbol_candidates))

        # 4.) if V1.1.1 is not a symbolpath, remove it, when it comprises only numbers and dots and the digit v or V
        symbol_candidates = list(filter(
            lambda x: not (x.startswith("v") or x.startswith("V")) and not all([c.isdigit() or c == "." for c in x]),
            symbol_candidates))

        # 4.) now remove all strings that occur within other strings
        unique_symbol_candidates = []
        for symbol in symbol_candidates:
            if not any([symbol in other_symbol for other_symbol in symbol_candidates if other_symbol != symbol]):
                unique_symbol_candidates.append(symbol)
        print(unique_symbol_candidates)
        return unique_symbol_candidates

    def _create_symbol_tree(self, in_strings: list[str]) -> dict[str:any]:
        """
        Create a tree of strings
        Each node is a string
        Each node has a parent and children
        """
        tree = {}
        for item in in_strings:
            keys = item.split('.')
            current_dict = tree
            for key in keys:
                current_dict = current_dict.setdefault(key, {})
        return tree

    def _determine_type(self, key):
        # if 'manager' in key:
        #    return PythonEntityType.CLASS
        if '__init__' in key or '__new__' in key:
            return PythonEntityType.METHOD
        else:
            return PythonEntityType.UNKNOWN

    def _assign_entities_to_tree(self, symbol_tree) -> PythonEntity:
        """
        Assign entities to the tree
        """

        # 1.) convert to python entities
        # 2.) use _determine_type to determine the type of each entity.
        # If a method is found, the parent is a class and so on
        q = queue.Queue()
        root = PythonEntity('root', PythonEntityType.ROOT_TRAVERSAL_OBJECT, '', [], None, [])
        q.put((root, symbol_tree))

        while not q.empty():
            parent_entity, node_dict = q.get()
            for child_key, child_dict in node_dict.items():
                child_entity = PythonEntity(child_key, self._determine_type(child_key), '', [], parent_entity, [])
                parent_entity.children.append(child_entity)

                # if a method is found, the parent is a class and so on
                if child_entity.type == PythonEntityType.METHOD:
                    parent_entity.type = PythonEntityType.CLASS
                    tmp_parent = parent_entity.parent
                    if tmp_parent != root:
                        tmp_parent.type = PythonEntityType.MODULE
                        tmp_parent = tmp_parent.parent

                        while tmp_parent != root:
                            tmp_parent.type = PythonEntityType.PACKAGE
                            tmp_parent = tmp_parent.parent

                q.put((child_entity, child_dict))

            # if a class is found, assign all children the type of PythonEntityType.METHOD
            if parent_entity.type == PythonEntityType.CLASS:
                # assign all children the type of PythonEntityType.METHOD
                for child in parent_entity.children:
                    child.type = PythonEntityType.METHOD

        return root

    def run(self):
        """
        Execute the different steps of the reconstruction process
        1.) get all strings from the file
        2.) get all comments from the file
        3.) get all symbol paths from the file
        4.) create a tree of symbol paths
        5.) assign entities to the tree
        """
        strings = self._get_strings_from_file()
        self._comments = self._get_comments(strings)
        candidates = self._get_python_symbolpaths(strings)
        symbol_tree = self._create_symbol_tree(candidates)
        self._skeleton = self._assign_entities_to_tree(symbol_tree)

    def _print_tree(self, node, level, file):
        """
        print the current level and call function recursively for all children
        :param node:
        :param level:
        :param file:
        :return:
        """
        indent = '--' * level
        if node.type == PythonEntityType.UNKNOWN:
            return  # don't print unknown nodes
        file.write(f'{indent}{node.name} - Type: {node.type.name}\n')
        for child in node.children:
            self._print_tree(child, level + 1, file)

    def persist_pseudo_skeleton(self, target_filepath: str):
        """
        Persist the pseudo skeleton to a file
        """
        with open(target_filepath, "w") as f:
            f.write(f"RECONSTRUCTED_SKELETON for file {self._filepath}:\n\n")
            self._print_tree(self._skeleton, 0, f)
            f.write("\n\nCOMMENTS:\n\n")
            f.write("\n".join(self._comments))


if __name__ == "__main__":
    fire.Fire(Cython2Skeleton)
