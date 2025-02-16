# Root Makefile

.PHONY: install

# Install command will invoke clean -> build -> test in clib/
install:
	$(MAKE) -C clib clean build test
