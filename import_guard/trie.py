_missing = object()


class Node:
    def __init__(self, module, data=_missing):
        self.module = module
        self.data = data
        self.children = {}

    def __repr__(self):
        return "[{}] -> {}".format(
            self.data if self.data is not _missing else "-",
            repr(self.children),
        )


class Trie:
    def __init__(self):
        self.root = Node("")

    def insert(self, module_name, data):
        current = self.root
        prefix = ""

        for submodule in module_name.split("."):
            if submodule not in current.children:
                prefix += "." + submodule if prefix else submodule
                current.children[submodule] = Node(prefix)
            current = current.children[submodule]

        current.data = data

    def update(self, data_dict):
        for key, data in data_dict.items():
            self.insert(key, data)

    def find(self, module_name):
        """
        Returns the Node representing the given module if it exists
        and None otherwise.
        """
        current = self.root
        for submodule in module_name.split("."):
            if submodule not in current.children:
                return None
            current = current.children[submodule]

        if current.data is not _missing:
            return current

    def path(self, prefix):
        """
        Returns a list of all nodes along the way to the given module.
        """
        path = []

        current = self.root
        for submodule in prefix.split("."):
            if submodule not in current.children:
                return path

            current = current.children[submodule]
            if current.data is not _missing:
                path.append(current)

        return path

    def starts_with(self, prefix):
        """
        Returns a list of all nodes beginning with the given prefix, or
        an empty list if no node begin with that prefix.
        """
        modules = []
        current = self.root
        for submodule in prefix.split("."):
            if submodule not in current.children:
                # Could also just do return words since it's empty
                return []

            current = current.children[submodule]

        self._submodules_for(current, modules)
        return modules

    def size(self, current=None):
        """
        Returns the size of this prefix tree, defined
        as the total number of nodes in the tree.
        """
        # By default, get the size of the whole trie, but
        # allow the user to get the size of any subtrees as well
        if not current:
            current = self.root
            # don't count the root
            count = 0
        else:
            count = 1

        for submodule in current.children:
            count += self.size(current.children[submodule])

        return count

    def _submodules_for(self, current, nodes):
        if current.data is not _missing:
            nodes.append(current)

        for submodule in current.children:
            self._submodules_for(current.children[submodule], nodes)

    def __repr__(self):
        return repr(self.root)
