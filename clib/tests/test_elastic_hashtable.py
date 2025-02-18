import unittest
import src.cython_modules as eh
import sys


class TestCythonHashTable(unittest.TestCase):

    def setUp(self):
        """Initialize a hash table before each test."""
        self.hash_table = eh.CHashTable(size=8)

    def test_insert(self):
        """Test inserting key-value pairs into the hash table."""
        self.hash_table.insert("apple", 5)
        self.hash_table.insert("banana", 10)
        self.hash_table.insert("apple", 7)  # Update existing key

        self.assertEqual(self.hash_table.get("apple"), 7)  # Ensure updated value
        self.assertEqual(self.hash_table.get("banana"), 10)

    def test_get(self):
        """Test retrieving values from the hash table."""
        self.hash_table.insert("grape", "fruit")
        self.hash_table.insert("orange", [1, 2, 3])

        self.assertEqual(self.hash_table.get("grape"), "fruit")
        self.assertEqual(self.hash_table.get("orange"), [1, 2, 3])

        # Test retrieving a non-existent key
        with self.assertRaises(KeyError):
            self.hash_table.get("watermelon")

    def test_remove(self):
        """Test deleting keys from the hash table."""
        self.hash_table.insert("cherry", 25)
        self.hash_table.remove("cherry")

        # Key should no longer exist
        with self.assertRaises(KeyError):
            self.hash_table.get("cherry")

        # Removing again should raise an error
        self.assertEqual(None, self.hash_table.remove("cherry"))

    def test_resize(self):
        """Test behavior when inserting more elements than the initial table size, triggering resizing."""
        for i in range(15):  # More than initial size to ensure resizing
            self.hash_table.insert(f"key{i}", i)

        # Ensure all inserted values are retrievable
        for i in range(15):
            self.assertEqual(self.hash_table.get(f"key{i}"), i)

        # Insert extra key after resize
        self.hash_table.insert("extra_key", 100)
        self.assertEqual(self.hash_table.get("extra_key"), 100)

    def test_collision_handling(self):
        """Test collision handling by forcing hash collisions."""
        # Manually setting keys with known hash collisions
        self.hash_table.insert("keyA", 100)
        self.hash_table.insert("keyB", 200)
        self.hash_table.insert("keyC", 300)

        self.assertEqual(self.hash_table.get("keyA"), 100)
        self.assertEqual(self.hash_table.get("keyB"), 200)
        self.assertEqual(self.hash_table.get("keyC"), 300)


if __name__ == "__main__":
    unittest.main()
