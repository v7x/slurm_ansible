#!/bin/bash
# Test runner script for SLURM Ansible modules
# Follows Ansible testing best practices

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
RUN_UNIT=true
RUN_INTEGRATION=false
RUN_SANITY=true
COVERAGE=false
VERBOSE=false
SLURM_AVAILABLE=false

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
usage() {
    cat << EOF
Usage: $0 [OPTIONS]

Test runner for SLURM Ansible modules

OPTIONS:
    -u, --unit              Run unit tests (default: true)
    -i, --integration       Run integration tests (default: false, requires SLURM)
    -s, --sanity           Run sanity tests (default: true)
    -c, --coverage         Generate coverage report
    -v, --verbose          Verbose output
    --no-unit              Skip unit tests
    --no-sanity            Skip sanity tests
    -h, --help             Show this help message

EXAMPLES:
    $0                     # Run unit and sanity tests
    $0 -i                  # Run all tests including integration
    $0 -u -c               # Run unit tests with coverage
    $0 --no-unit -i        # Run only integration tests

REQUIREMENTS:
    - Python 3.6+
    - pytest
    - ansible-core
    - For integration tests: SLURM environment with sacctmgr available

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--unit)
            RUN_UNIT=true
            shift
            ;;
        -i|--integration)
            RUN_INTEGRATION=true
            shift
            ;;
        -s|--sanity)
            RUN_SANITY=true
            shift
            ;;
        -c|--coverage)
            COVERAGE=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        --no-unit)
            RUN_UNIT=false
            shift
            ;;
        --no-sanity)
            RUN_SANITY=false
            shift
            ;;
        -h|--help)
            usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            usage
            exit 1
            ;;
    esac
done

# Check if we're in the right directory
if [[ ! -d "tests" ]]; then
    print_error "This script must be run from the project root directory"
    exit 1
fi

# Check for required tools
check_requirements() {
    print_status "Checking requirements..."
    
    # Check Python
    if ! command -v python3 &> /dev/null; then
        print_error "Python 3 is required but not installed"
        exit 1
    fi
    
    # Check pytest
    if ! python3 -c "import pytest" &> /dev/null; then
        print_error "pytest is required. Install with: pip install -r tests/requirements.txt"
        exit 1
    fi
    
    # Check ansible-core
    if ! python3 -c "import ansible" &> /dev/null; then
        print_error "ansible-core is required. Install with: pip install -r tests/requirements.txt"
        exit 1
    fi
    
    # Check for SLURM if integration tests are requested
    if [[ "$RUN_INTEGRATION" == "true" ]]; then
        if command -v sacctmgr &> /dev/null; then
            SLURM_AVAILABLE=true
            print_status "SLURM detected - integration tests will run"
        else
            print_warning "SLURM not available - integration tests will be skipped"
            RUN_INTEGRATION=false
        fi
    fi
}

# Run unit tests
run_unit_tests() {
    print_status "Running unit tests..."
    
    local pytest_args=("tests/unit/")
    
    if [[ "$COVERAGE" == "true" ]]; then
        pytest_args+=("--cov=module_utils" "--cov-report=html" "--cov-report=term")
    fi
    
    if [[ "$VERBOSE" == "true" ]]; then
        pytest_args+=("-v")
    fi
    
    python3 -m pytest "${pytest_args[@]}"
    
    if [[ $? -eq 0 ]]; then
        print_status "Unit tests passed"
    else
        print_error "Unit tests failed"
        exit 1
    fi
}

# Run integration tests
run_integration_tests() {
    print_status "Running integration tests..."
    
    if [[ "$SLURM_AVAILABLE" != "true" ]]; then
        print_warning "Skipping integration tests - SLURM not available"
        return 0
    fi
    
    # Use ansible-test for integration tests
    local ansible_test_args=("integration" "sacctmgr_helper")
    
    if [[ "$VERBOSE" == "true" ]]; then
        ansible_test_args+=("-v")
    fi
    
    cd tests/integration
    ansible-test "${ansible_test_args[@]}"
    local result=$?
    cd ../..
    
    if [[ $result -eq 0 ]]; then
        print_status "Integration tests passed"
    else
        print_error "Integration tests failed"
        exit 1
    fi
}

# Run sanity tests
run_sanity_tests() {
    print_status "Running sanity tests..."
    
    # Use ansible-test for sanity checks
    local ansible_test_args=("sanity" "--python" "3.8")
    
    if [[ "$VERBOSE" == "true" ]]; then
        ansible_test_args+=("-v")
    fi
    
    ansible-test "${ansible_test_args[@]}"
    
    if [[ $? -eq 0 ]]; then
        print_status "Sanity tests passed"
    else
        print_error "Sanity tests failed"
        exit 1
    fi
}

# Main execution
main() {
    print_status "Starting test suite..."
    
    check_requirements
    
    # Run tests based on flags
    if [[ "$RUN_UNIT" == "true" ]]; then
        run_unit_tests
    fi
    
    if [[ "$RUN_SANITY" == "true" ]]; then
        run_sanity_tests
    fi
    
    if [[ "$RUN_INTEGRATION" == "true" ]]; then
        run_integration_tests
    fi
    
    print_status "All requested tests completed successfully!"
    
    if [[ "$COVERAGE" == "true" ]]; then
        print_status "Coverage report generated in htmlcov/"
    fi
}

# Run main function
main "$@" 