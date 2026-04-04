#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
CREDS_DIR="$ROOT/.credentials"

mkdir -p "$CREDS_DIR"
chmod 700 "$CREDS_DIR"

echo "╔════════════════════════════════════════════════════════════╗"
echo "║         Roadmap-AI Credential Setup                        ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Dette scriptet hjelper deg med å sette opp API-tokens sikkert."
echo "Alle tokens lagres i .credentials/ (gitignored)."
echo ""

# GitHub Token
echo "─────────────────────────────────────────────────────────────"
echo "1. GitHub Personal Access Token (PAT)"
echo "─────────────────────────────────────────────────────────────"
echo ""
echo "Brukes til: P6-001 GitHub PR Lane"
echo ""
echo "Slik får du token:"
echo "  1. Gå til: https://github.com/settings/tokens"
echo "  2. Klikk 'Generate new token' → 'Classic'"
echo "  3. Gi beskrivelse: 'Roadmap-AI PR Lane'"
echo "  4. Velg scope: ✓ repo (full control)"
echo "  5. Klikk 'Generate token'"
echo "  6. Kopier token (starter med ghp_)"
echo ""

if [ -f "$CREDS_DIR/github_token" ]; then
  EXISTING=$(cat "$CREDS_DIR/github_token")
  echo "✅ GitHub token eksisterer allerede (${#EXISTING} chars)"
  read -p "Vil du overskrive den? (y/N): " -n 1 -r
  echo
  if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Beholder eksisterende token."
  else
    read -sp "Lim inn GitHub token (ghp_xxxxx): " GITHUB_TOKEN
    echo
    echo "$GITHUB_TOKEN" > "$CREDS_DIR/github_token"
    chmod 600 "$CREDS_DIR/github_token"
    echo "✅ GitHub token lagret"
  fi
else
  read -sp "Lim inn GitHub token (ghp_xxxxx): " GITHUB_TOKEN
  echo
  if [ -z "$GITHUB_TOKEN" ]; then
    echo "⏭️  Hoppet over GitHub token"
  else
    echo "$GITHUB_TOKEN" > "$CREDS_DIR/github_token"
    chmod 600 "$CREDS_DIR/github_token"
    echo "✅ GitHub token lagret"
  fi
fi

echo ""

# Stripe Token
echo "─────────────────────────────────────────────────────────────"
echo "2. Stripe API Key (valgfri for nå)"
echo "─────────────────────────────────────────────────────────────"
echo ""
echo "Brukes til: P6-003 Revenue Bridge"
echo ""
echo "Slik får du nøkkel:"
echo "  1. Gå til: https://dashboard.stripe.com/apikeys"
echo "  2. Bruk 'Secret key' (starter med sk_test_ eller sk_live_)"
echo ""
read -p "Vil du sette opp Stripe nå? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  read -sp "Lim inn Stripe API key: " STRIPE_KEY
  echo
  echo "$STRIPE_KEY" > "$CREDS_DIR/stripe_token"
  chmod 600 "$CREDS_DIR/stripe_token"
  echo "✅ Stripe token lagret"
else
  echo "⏭️  Hoppet over Stripe (kan settes opp senere)"
fi

echo ""

# Cowork Token
echo "─────────────────────────────────────────────────────────────"
echo "3. Cowork Endpoint Token (valgfri for nå)"
echo "─────────────────────────────────────────────────────────────"
echo ""
echo "Brukes til: P0 Live Dispatch"
echo ""
read -p "Vil du sette opp Cowork token nå? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
  read -sp "Lim inn Cowork token: " COWORK_TOKEN
  echo
  echo "$COWORK_TOKEN" > "$CREDS_DIR/cowork_token"
  chmod 600 "$CREDS_DIR/cowork_token"
  echo "✅ Cowork token lagret"
else
  echo "⏭️  Hoppet over Cowork (kan settes opp senere)"
fi

echo ""
echo "╔════════════════════════════════════════════════════════════╗"
echo "║                  Setup Complete!                            ║"
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "Last tokens i hver terminal-sesjon med:"
echo "  source ~/roadmap-ai/.credentials/load_credentials.sh"
echo ""
echo "Eller legg til i ~/.zshrc / ~/.bashrc:"
echo "  echo 'source ~/roadmap-ai/.credentials/load_credentials.sh' >> ~/.zshrc"
echo ""
