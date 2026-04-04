#!/usr/bin/env bash
# Credential Loader — Source this to load all tokens

CREDS_DIR="$HOME/roadmap-ai/.credentials"

# GitHub Token
if [ -f "$CREDS_DIR/github_token" ]; then
  export GITHUB_TOKEN=$(cat "$CREDS_DIR/github_token")
  echo "✅ GITHUB_TOKEN loaded (${#GITHUB_TOKEN} chars)"
fi

# Stripe Token
if [ -f "$CREDS_DIR/stripe_token" ]; then
  export STRIPE_API_KEY=$(cat "$CREDS_DIR/stripe_token")
  echo "✅ STRIPE_API_KEY loaded (${#STRIPE_API_KEY} chars)"
fi

# Vipps Token
if [ -f "$CREDS_DIR/vipps_token" ]; then
  export VIPPS_API_KEY=$(cat "$CREDS_DIR/vipps_token")
  echo "✅ VIPPS_API_KEY loaded"
fi

# Cowork Token
if [ -f "$CREDS_DIR/cowork_token" ]; then
  export COWORK_TOKEN=$(cat "$CREDS_DIR/cowork_token")
  echo "✅ COWORK_TOKEN loaded"
fi

# Tailscale check
if command -v tailscale &> /dev/null; then
  echo "✅ Tailscale installed"
fi
