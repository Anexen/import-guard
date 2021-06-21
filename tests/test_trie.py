import unittest

from import_guard.trie import Trie


class TestTrie(unittest.TestCase):
    def setUp(self):
        self.trie = Trie()
        self.trie.update(
            {
                "test_proj": 1,
                "test_proj.api": 2,
                "test_proj.api.views": 3,
                "test_proj.core": 2,
            }
        )

    def test_trie_size(self):
        #  test_proj -> api -> views
        #           \-> core
        assert self.trie.size() == 4

    def test_find(self):
        node = self.trie.find("test_proj.api.views")
        assert node.data == 3

    def test_find_not_exists(self):
        assert self.trie.find("test_proj.api.urls") is None
        assert self.trie.find("test_proj.models") is None

    def test_insert_override_existing(self):
        self.trie.insert("test_proj.api.views", 2)
        node = self.trie.find("test_proj.api.views")
        assert node.data == 2

    def test_start_with(self):
        nodes = self.trie.starts_with("test_proj.api")
        assert [x.data for x in nodes] == [2, 3]

    def test_find_path(self):
        path = self.trie.path("test_proj.api.views")
        assert [x.data for x in path] == [1, 2, 3]

    def test_find_longer_path(self):
        path = self.trie.path("test_proj.api.views.auth.login")
        assert [x.data for x in path] == [1, 2, 3]
