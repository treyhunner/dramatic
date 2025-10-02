# Show available commands
_default:
    @just --list --unsorted

# Install project dependencies
setup:
    hatch env create

# Run the tests
test *args:
    hatch test {{ args }}

# Run tests with coverage
test-cov *args:
    hatch test --cover {{ args }}
    hatch run cov-report

# Run tests with coverage and generate HTML report
test-html *args:
    hatch test --cover {{ args }}
    hatch run cov-report
    @echo "Opening coverage report generated at htmlcov/index.html"
    python -m webbrowser htmlcov/index.html

# Run tests on all Python versions
test-all *args:
    hatch test --all {{ args }}

# Run tests on all Python versions with environments in parallel
test-all-parallel *args:
    #!/usr/bin/env bash
    set -e
    # Extract Python versions from hatch-test environments
    versions=$(hatch env show hatch-test --json 2>/dev/null | \
        grep -o '"hatch-test\.[^"]*"' | \
        sed 's/"hatch-test\.//' | sed 's/"//' | \
        sed 's/^py\([0-9]\)/\1/' | sort -V)

    # Store versions and pids in arrays
    declare -a pids
    declare -a vers
    for py in $versions; do
        hatch test -py "$py" {{ args }} &
        pids+=($!)
        vers+=("$py")
    done

    # Wait for all and track results
    declare -a results
    failed=0
    for i in "${!pids[@]}"; do
        if wait "${pids[$i]}"; then
            results[$i]="✓"
        else
            results[$i]="✗"
            failed=1
        fi
    done

    # Print summary
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Test Summary:"
    for i in "${!vers[@]}"; do
        printf "  %s  Python %s\n" "${results[$i]}" "${vers[$i]}"
    done
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    if [ $failed -eq 0 ]; then
        echo "All environments passed! 🎉"
    else
        echo "Some environments failed. ❌"
    fi
    exit $failed

# Format and lint code with ruff
fmt:
    hatch run lint

# Run formatting check without modifying files
lint-check:
    hatch run lint-check

# Run all quality checks and tests
check:
    just fmt
    just test-all-parallel

# Bump version
bump value:
    hatch version {{ value }}

# Build Python package
build:
    hatch build

# Publish to PyPI
publish:
    hatch publish
