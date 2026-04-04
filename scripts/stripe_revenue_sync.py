#!/usr/bin/env python3
"""
Stripe Revenue Bridge — Sync revenue data to ORION forecasts
Usage: python scripts/stripe_revenue_sync.py
"""
import os
import sys
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path

try:
    import stripe
except ImportError:
    print("❌ Stripe SDK not installed: pip install stripe", file=sys.stderr)
    sys.exit(1)

ROOT = Path(__file__).parent.parent
OUTPUT = ROOT / "panel_output" / "revenue.json"

def main():
    # Check for API key
    api_key = os.getenv("STRIPE_API_KEY")
    if not api_key:
        error = {
            "roadmap_version": "0.3.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "command": "stripe-revenue-sync",
            "data": {"error": "STRIPE_API_KEY not set"},
            "metadata": {"status": "blocked"}
        }
        OUTPUT.parent.mkdir(exist_ok=True)
        OUTPUT.write_text(json.dumps(error, indent=2))
        print("❌ STRIPE_API_KEY not set", file=sys.stderr)
        return 1
    
    try:
        stripe.api_key = api_key
        
        # Fetch recent charges (last 30 days)
        thirty_days_ago = int((datetime.now(timezone.utc) - timedelta(days=30)).timestamp())
        charges = stripe.Charge.list(created={'gte': thirty_days_ago}, limit=100)
        
        # Calculate metrics
        total_revenue = 0
        successful_charges = 0
        failed_charges = 0
        currency = "usd"
        
        charge_details = []
        for charge in charges.data:
            amount_nok = charge.amount / 100  # Stripe uses cents
            
            if charge.currency.lower() != "usd":
                currency = charge.currency.upper()
            
            if charge.status == "succeeded":
                total_revenue += amount_nok
                successful_charges += 1
            else:
                failed_charges += 1
            
            charge_details.append({
                "id": charge.id,
                "amount": amount_nok,
                "currency": charge.currency.upper(),
                "status": charge.status,
                "description": charge.description or "No description",
                "created": datetime.fromtimestamp(charge.created, timezone.utc).isoformat()
            })
        
        # Build output
        output = {
            "roadmap_version": "0.3.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "command": "stripe-revenue-sync",
            "data": {
                "period": "last_30_days",
                "total_revenue": total_revenue,
                "currency": currency,
                "successful_charges": successful_charges,
                "failed_charges": failed_charges,
                "average_transaction": total_revenue / successful_charges if successful_charges > 0 else 0,
                "recent_charges": charge_details[:10]  # Last 10 charges
            },
            "metadata": {
                "status": "success",
                "charges_analyzed": len(charges.data),
                "stripe_mode": "live" if api_key.startswith("sk_live_") else "test"
            }
        }
        
        OUTPUT.parent.mkdir(exist_ok=True)
        OUTPUT.write_text(json.dumps(output, indent=2))
        
        print(f"✅ Synced Stripe revenue")
        print(f"   Total: {total_revenue:,.2f} {currency}")
        print(f"   Charges: {successful_charges} successful, {failed_charges} failed")
        print(f"   Output: {OUTPUT}")
        return 0
        
    except stripe.error.AuthenticationError:
        error = {
            "roadmap_version": "0.3.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "command": "stripe-revenue-sync",
            "data": {"error": "Invalid Stripe API key"},
            "metadata": {"status": "failed"}
        }
        OUTPUT.parent.mkdir(exist_ok=True)
        OUTPUT.write_text(json.dumps(error, indent=2))
        print("❌ Invalid Stripe API key", file=sys.stderr)
        return 1
    except Exception as e:
        error = {
            "roadmap_version": "0.3.0",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "command": "stripe-revenue-sync",
            "data": {"error": str(e)},
            "metadata": {"status": "failed"}
        }
        OUTPUT.parent.mkdir(exist_ok=True)
        OUTPUT.write_text(json.dumps(error, indent=2))
        print(f"❌ Stripe API error: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())
