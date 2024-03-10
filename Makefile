.PHONY: test

# Define your environments
ENVS := py3.8 py3.9 py3.10 py3.11 pypy3.10

# Define the test command for a specific environment
define TEST_COMMAND
hatch -e all.$(1) run test
endef

# Default target to run when the make command is executed without arguments
test:
	$(foreach env,$(ENVS),$(call TEST_COMMAND,$(env));)
