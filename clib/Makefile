# clib Makefile

.PHONY: build test clean

# Build Cython extensions
build:
	@echo "Building Cython extensions..."
	python setup.py build_ext --inplace

# Run tests for clib
test: build
	@echo "Running tests for clib..."
	python -m unittest discover tests

# Clean Cython build artifacts
clean:
	@echo "Cleaning Cython build artifacts..."
	rm -rf build/ src/cython_modules/*.c src/cython_modules/*.so src/cython_modules/__pycache__ test/__pycache__

bench:
	@echo "Running benchmarks..."
	python ./benchmarks/benchmarks_hashtable.py