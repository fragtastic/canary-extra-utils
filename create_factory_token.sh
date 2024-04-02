#!/bin/bash
set -e

# Help
show_help() {
    echo "Usage: $0 -d <domain> -a <auth_token> -f <flock_id> -m <memo>" >&2
    echo "Options:"
    echo "  -d <domain>: Domain"
    echo "  -a <auth_token>: Auth Token"
    echo "  -f <flock_id>: Flock ID"
    echo "  -m <memo>: Memo"
    exit 1
}

# Parse command line arguments
while getopts ":a:f:m:d:" opt; do
    case ${opt} in
        a ) auth_token=$OPTARG;;
        f ) flock_id=$OPTARG;;
        m ) memo=$OPTARG;;
        d ) domain=$OPTARG;;
        \? ) show_help;;
        : ) echo "Invalid option: $OPTARG requires an argument"
            exit 1;;
    esac
done

# Check if all required arguments are provided
if [ -z "$auth_token" ] || [ -z "$flock_id" ] || [ -z "$memo" ]; then
    show_help
fi

# Get the factory auth token
curl https://$domain.canary.tools/api/v1/canarytoken/create_factory \
  -d "auth_token=$auth_token" \
  -d "flock_id=$flock_id" \
  -d "memo=$memo"
