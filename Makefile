.PHONY: test

# Define your environments
ENVS := 3.8 3.9 3.10 3.11

# Define the test command for a specific environment
define TEST_COMMAND
hatch -e all.py$(1) run test
endef

# Default target to run when the make command is executed without arguments
test:
	$(foreach env,$(ENVS),$(call TEST_COMMAND,$(env));)
