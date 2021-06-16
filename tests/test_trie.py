import unittest

from import_guard.trie import Trie


class TestTrie(unittest.TestCase):
    def setUp(self):
        self.trie = Trie()
        self.trie.update(
            {
                "myproject": 1,
                "myproject.api": 2,
                "myproject.api.views": 3,
                "myproject.core": 2,
            }
        )

    def test_trie_size(self):
        #  myproject -> api -> views
        #           \-> core
        assert self.trie.size() == 4

    def test_find(self):
        node = self.trie.find("myproject.api.views")
        assert node.data == 3

    def test_find_not_exists(self):
        assert self.trie.find("myproject.api.urls") is None
        assert self.trie.find("myproject.models") is None

    def test_insert_override_existing(self):
        self.trie.insert("myproject.api.views", 2)
        node = self.trie.find("myproject.api.views")
        assert node.data == 2

    def test_start_with(self):
        nodes = self.trie.starts_with("myproject.api")
        assert [x.data for x in nodes] == [2, 3]

    def test_find_path(self):
        path = self.trie.path("myproject.api.views")
        assert [x.data for x in path] == [1, 2, 3]

    def test_find_longer_path(self):
        path = self.trie.path("myproject.api.views.auth.login")
        assert [x.data for x in path] == [1, 2, 3]
