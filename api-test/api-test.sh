#!/usr/bin/env bash

# Script to test cache-server HTTP and WebSocket APIs
#
# Author: Marek Križan
# Date: 1.5.2024

hostname=""
cache=""
agent=""
cachetoken=""
agenttoken=""
deploytoken=""

export CACHIX_AUTH_TOKEN=$cachetoken
export CACHIX_AGENT_TOKEN=$agenttoken
export CACHIX_ACTIVATE_TOKEN=$deploytoken

assert() {
    if ! $@; then
        echo "RESULT: Test failed"
        exit 1
    fi
}

echo "---Building test.nix---"
path=$(nix-build --no-out-link test.nix)
assert [ $? -eq 0 ]
echo "RESULT: Success"
echo ""

echo "---Setting cache-server hostname to cachix config---"
cachix config set hostname http://$hostname
assert [ $? -eq 0 ]
echo "RESULT: Success"
echo ""

echo "---Adding the $cache binary cache to nix.conf"
cachix use $cache
assert [ $? -eq 0 ]
echo "RESULT: Success"
echo ""

echo "---Rebuilding the configuration for nix.conf changes to take effect"
nixos-rebuild switch
assert [ $? -eq 0 ]
echo "RESULT: Success"
echo ""

echo "---Pushing testhello path to cachix---"
echo $path | cachix push $cache
assert [ $? -eq 0 ]
echo "RESULT: Success"
echo ""

echo "---Get binary cache info from cache-server---"
out=$(curl -i http://$hostname/api/v1/cache/$cache?)
responsecode=$(echo $out | head -n 1 | awk '{print $2}')
assert [ "$responsecode" = "200" ]
echo "$out"
echo "RESULT: Success"
echo ""

echo "---Get binary cache info from binary cache---"
out=$(curl -i http://$cache.$hostname/nix-cache-info)
responsecode=$(echo $out | head -n 1 | awk '{print $2}')
assert [ "$responsecode" = "200" ]
echo "$out"
echo "RESULT: Success"
echo ""

echo "---Get narinfo from binary cache (HEAD)---"
storehash=$(echo $path | cut -d '-' -f 1 | cut -d '/' -f 4)
out=$(curl --head -i http://$cache.$hostname/$storehash.narinfo)
responsecode=$(echo $out | head -n 1 | awk '{print $2}')
assert [ "$responsecode" = "200" ]
echo "$out"
echo "RESULT: Success"
echo ""

echo "---Get narinfo from binary cache (GET)---"
storehash=$(echo $path | cut -d '-' -f 1 | cut -d '/' -f 4)
out=$(curl -i http://$cache.$hostname/$storehash.narinfo)
responsecode=$(echo $out | head -n 1 | awk '{print $2}')
assert [ "$responsecode" = "200" ]
echo "$out"
echo "RESULT: Success"
echo ""

echo "---Deployment test---"
spec="{
    \"agents\": {
        \"$agent\": \"$path\"
    }
}"
echo "$spec" > deploy.json
nix-store --delete $path
cachix deploy agent $agent &
pid=$!
sleep 2
cachix deploy activate deploy.json
res=$?
kill $pid
rm deploy.json
assert [ $res -eq 0 ]
echo "RESULT: Success"
echo ""
