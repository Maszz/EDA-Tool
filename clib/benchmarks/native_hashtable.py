class Entry:
    def __init__(self, key, value):
        self.key = key
        self.value = value


class HashTable:
    def __init__(self, size=8):
        """Initialize the hash table with a given size."""
        self.size = size
        self.count = 0
        self.table = [None] * self.size  # Reverting back to list

    def _hash(self, key):
        """Compute hash modulo table size."""
        hash_value = 0
        for char in key:
            hash_value = (hash_value * 31) + ord(char)
        return hash_value % self.size

    def _probe(self, key, i):
        """Quadratic probing with wraparound."""
        return (self._hash(key) + i * i) % self.size

    def _resize(self):
        """Resize the hash table when load factor exceeds 50%."""
        old_table = self.table
        self.size *= 2
        self.count = 0
        self.table = [None] * self.size

        for entry in old_table:
            if entry is not None:
                self.insert(entry.key, entry.value)

    def insert(self, key, value):
        """Insert a key-value pair into the hash table."""
        if self.count * 2 >= self.size:
            self._resize()

        i = 0
        while True:
            index = self._probe(key, i)
            if self.table[index] is None or self.table[index].key == key:
                self.table[index] = Entry(key, value)
                self.count += 1
                return
            i += 1

    def get(self, key):
        """Retrieve a value from the hash table using probing."""
        i = 0
        while i < self.size:
            index = self._probe(key, i)
            entry = self.table[index]
            if entry is None:
                raise KeyError(f"Key '{key}' not found")
            if entry.key == key:
                return entry.value
            i += 1
        raise KeyError(f"Key '{key}' not found")

    def remove(self, key):
        """Remove a key from the hash table with probing."""
        i = 0
        while i < self.size:
            index = self._probe(key, i)
            entry = self.table[index]
            if entry is None:
                return
            if entry.key == key:
                self.table[index] = None
                self.count -= 1
                return
            i += 1
        raise KeyError(f"Key '{key}' not found")

    def __delitem__(self, key):
        """Enable del d[key] to remove an item."""
        self.remove(key)

    def __setitem__(self, key, value):
        """Enable d[key] = value to insert an item."""
        self.insert(key, value)

    def __getitem__(self, key):
        """Enable d[key] to retrieve an item."""
        return self.get(key)

    def __repr__(self):
        return (
            "{"
            + ", ".join(
                f"{entry.key}: {entry.value}"
                for entry in self.table
                if entry is not None
            )
            + "}"
        )
