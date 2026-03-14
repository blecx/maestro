#!/bin/bash

# Preload Mock LLM Server Responses
MOCK_SERVER_URL=${MOCK_SERVER_URL:-"http://localhost:9090"}
MOCKS_DIR=${MOCKS_DIR:-"tests/mocks"}

echo "Preloading mocks to $MOCK_SERVER_URL/admin/mocks..."

# Clear existing mocks
curl -s -X DELETE "$MOCK_SERVER_URL/admin/mocks"
echo ""

for mock_file in "$MOCKS_DIR"/*.json; do
  if [ -f "$mock_file" ]; then
    echo "Loading $mock_file..."
    curl -s -X POST "$MOCK_SERVER_URL/admin/mocks" \
         -H "Content-Type: application/json" \
         -d @"$mock_file"
    echo ""
  fi
done

echo "Done preloading mocks."
