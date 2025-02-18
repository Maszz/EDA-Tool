cimport cython
from libc.string cimport memset, strcmp
from cpython.ref cimport Py_INCREF, Py_DECREF
from libc.stdlib cimport malloc, free
from cpython.object cimport PyObject
cdef extern from "string.h":
    char* strdup(const char*)

#cdef extern from "test.h":
#    void foo()

# MurmurHash for better string hashing
cdef inline unsigned int murmur_hash(const unsigned char* key):
    """Efficient hash function for strings."""
    cdef unsigned int hash = 0
    while key[0] != b'\0':
        hash = (hash * 31) + key[0]
        key += 1
    return hash

ctypedef struct Entry:
    char* key
    PyObject* value

@cython.final
cdef class CHashTable:
    cdef:
        int size
        int count
        Entry* table

    def __cinit__(self, int size=8):
        """Initialize the hash table with a given size."""
        self.size = size
        self.count = 0
        self.table = <Entry*> malloc(self.size * sizeof(Entry))
        memset(self.table, 0, self.size * sizeof(Entry))
        # foo()

    def __dealloc__(self):
        """Deallocate memory when the object is destroyed."""
        cdef int i
        for i in range(self.size):
            if self.table[i].value is not NULL:
                Py_DECREF(<object> self.table[i].value)
                free(self.table[i].key)
        free(self.table)

    
    cdef int _hash(self, const char* key):
        """Compute hash modulo table size."""
        return murmur_hash(<const unsigned char*> key) % self.size

    cdef int _probe(self, const char* key, int i):
        """Quadratic probing with correct wraparound."""
        cdef int index = (self._hash(key) + i * i) % self.size
        if index < 0:
            index += self.size  # ✅ Fix negative indices
        ## print(f"🔍 DEBUG: Probing key='{key.decode()}', i={i}, index={index}")
        return index

  
    @cython.optimize.unpack_method_calls(True)
    cdef void _resize(self):
        """Resize the hash table when load factor is exceeded."""
        cdef int old_size = self.size
        cdef Entry* old_table = self.table
        cdef int i, j, new_index

        ## print(f"🔄 DEBUG: Resizing table from {old_size} to {self.size * 2}")

        self.size *= 2
        self.count = 0  # Reset count (it will be recalculated)
        self.table = <Entry*> malloc(self.size * sizeof(Entry))
        memset(self.table, 0, self.size * sizeof(Entry))

        for i in range(old_size):
            if old_table[i].value is not NULL and old_table[i].key is not NULL:
                j = 0
                while True:
                    new_index = self._probe(old_table[i].key, j)
                    if self.table[new_index].value is NULL:
                        self.table[new_index].key = strdup(old_table[i].key)  # ✅ Preserve original key
                        self.table[new_index].value = old_table[i].value
                        Py_INCREF(<object> self.table[new_index].value)  # ✅ Keep reference count correct
                        self.count += 1
                        ## print(f"✅ DEBUG: Moved key='{old_table[i].key.decode()}' to new index={new_index}")  # Debug log
                        break
                    j += 1  # ✅ Keep probing until a valid slot is found

                free(old_table[i].key)  # ✅ Free old key

        free(old_table)  # ✅ Free old memory
        ## print(f"✅ DEBUG: Resize complete! New size={self.size}, Count={self.count}")


    def __delitem__(self, key: str):
        """Enable del d[key] to remove an item."""
        self.remove(key)

    def __getitem__(self, key: str):
        """Enable d[key] to retrieve an item."""
        return self.get(key)

    def __setitem__(self, key: str, value: object):
        """Enable d[key] = value to insert an item."""
        self.insert(key, value)

    @cython.optimize.unpack_method_calls(True)
    cpdef void insert(self, key: str, value: object):
        """Insert a key-value pair into the hash table."""
        cdef int index, i = 0
        cdef bytes key_bytes = key.encode("utf-8")
        cdef char* c_key = key_bytes

        ## print(f"🔍 DEBUG: Inserting key='{key}'")

        # Check if resizing is needed
        if self.count * 2 >= self.size:
            ## print(f"🔄 DEBUG: Resizing triggered (count={self.count}, size={self.size})")
            self._resize()

        # Inserting key-value pair with probing for collision handling
        while True:
            index = self._probe(c_key, i)
            ## print(f"🔍 DEBUG: Inserting key='{key}' at index={index}, probing step={i}")

            # Check for an empty slot
            if self.table[index].value is NULL:
                self.table[index].key = strdup(c_key)
                self.table[index].value = <PyObject*> value
                Py_INCREF(value)
                self.count += 1
                ## print(f"✅ DEBUG: Inserted key='{key}' at index={index}")
                return  # Successfully inserted

            # If key already exists, replace its value
            elif strcmp(self.table[index].key, c_key) == 0:
                Py_DECREF(<object> self.table[index].value)  # Clean up old reference
                self.table[index].value = <PyObject*> value
                Py_INCREF(value)
                ## print(f"✅ DEBUG: Updated key='{key}' at index={index}")
                return

            i += 1  # Continue probing for the next slot

    @cython.optimize.unpack_method_calls(True)
    cpdef object get(self, str key):
        """Retrieve a value from the hash table using linear probing, correctly handling deleted slots."""
        cdef bytes key_bytes = key.encode("utf-8")
        cdef char* c_key = key_bytes
        cdef int index, i = 0

        while i < self.size:  # Ensure it does not probe infinitely
            index = self._probe(c_key, i)

            if self.table[index].key is <char*>NULL:
                # If NULL is reached, key does not exist
                raise KeyError(f"Key '{key}' not found")

            elif strcmp(self.table[index].key, c_key) == 0:
                # Key is found, return the value
                if self.table[index].value is not <PyObject*>NULL:
                    return <object> self.table[index].value
                else:
                    raise KeyError(f"Key '{key}' has been deleted")

            # Continue probing
            i += 1

        raise KeyError(f"Key '{key}' not found after full probing")

    @cython.optimize.unpack_method_calls(True)
    cpdef void remove(self, str key):
        """Remove a key from the hash table with full probing support."""
        cdef bytes key_bytes = key.encode("utf-8")
        cdef char* c_key = key_bytes

        cdef int index, i = 0
        ## print(f"🗑️ DEBUG: Attempting to remove key='{key}'")

        while i < self.size:  # Avoid infinite loop
            ## print("START")
            index = self._probe(c_key, i)
            ## print(f"🔍 DEBUG: Probing key='{key}', i={i}, index={index}")

            if self.table[index].value is <PyObject*>NULL:  # Fix NULL usage
                # If NULL is reached, it means the key was not found
                ## print(f"❌ ERROR: Key '{key}' not found at index={index}, i={i} (Reached NULL)")
                ## print(f"📊 DEBUG: Table size={self.size}, Count={self.count}")
                return  # Explicitly return None

            elif self.table[index].key is not <char*>NULL and strcmp(self.table[index].key, c_key) == 0:
                # If the key is found, proceed with removal
                ## print(f"✅ DEBUG: Removing key='{key}' at index={index}")
                Py_DECREF(<object> self.table[index].value)
                self.table[index].value = <PyObject*>NULL  # Mark as removed
                free(self.table[index].key)  # Free key memory
                self.table[index].key = <char*>NULL  # Ensure key is also marked NULL
                self.count -= 1
                ## print("RETURNS")
                return  # Explicitly return None

            # Continue probing for the next index
            i += 1

        # If we reach this point, it means the key was not found after probing all slots
        ## print(f"🛑 ERROR: Probing exceeded table size for key='{key}'")
        raise KeyError(f"Key '{key}' not found")