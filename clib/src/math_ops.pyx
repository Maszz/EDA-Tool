cdef class MathOps:
    """Class for mathematical operations"""

    cpdef int add(self, int a, int b):
        return a + b

    cpdef int multiply(self, int a, int b):
        return a * b
