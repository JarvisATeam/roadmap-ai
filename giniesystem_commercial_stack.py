#!/usr/bin/env python3
"""
GinieSystem Commercial Stack
Håndterer bedriftsinformasjon og kommersielle data for GinieSystem.
"""

from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import sys


@dataclass
class CompanyInfo:
    """Bedriftsinformasjon for OLSEN'S A-TEAM."""
    name: str = "OLSEN'S A-TEAM"
    org_number: str = "922288909"  # Faktisk orgnr fra Brønnøysundregistrene
    vat_registered: bool = True

    address_line: str = "Amdalsvegen 129"
    postal_code: str = "4208"
    city: str = "Saudasjøen"
    country: str = "NO"

    email: str = "olsensateam@gmail.com"
    phone: str = "+4791720162"
    website: str | None = None

    currency: str = "NOK"
    locale: str = "nb-NO"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Konverter til dictionary."""
        return {
            "name": self.name,
            "org_number": self.org_number,
            "vat_registered": self.vat_registered,
            "address_line": self.address_line,
            "postal_code": self.postal_code,
            "city": self.city,
            "country": self.country,
            "email": self.email,
            "phone": self.phone,
            "website": self.website,
            "currency": self.currency,
            "locale": self.locale,
            "created_at": self.created_at,
        }
    
    def to_json(self) -> str:
        """Konverter til JSON-streng."""
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)
    
    def validate(self) -> bool:
        """Validerer at orgnummer er gyldig format (9 siffer)."""
        return len(self.org_number) == 9 and self.org_number.isdigit()


@dataclass
class CommercialStack:
    """Kommersiell stack for GinieSystem."""
    company: CompanyInfo = field(default_factory=CompanyInfo)
    version: str = "1.0.0"
    environment: str = "production"
    
    def get_status(self) -> Dict[str, Any]:
        """Hent status for kommersiell stack."""
        return {
            "company": self.company.to_dict(),
            "version": self.version,
            "environment": self.environment,
            "timestamp": datetime.now().isoformat(),
            "valid": self.company.validate(),
        }


def main():
    """Hovedfunksjon for testing av kommersiell stack."""
    print("=" * 60)
    print("GinieSystem Commercial Stack - Test")
    print("=" * 60)
    
    # Opprett kommersiell stack med default verdier
    stack = CommercialStack()
    
    # Vis CompanyInfo
    print("\n📋 CompanyInfo:")
    print(f"  Name:           {stack.company.name}")
    print(f"  Org Number:     {stack.company.org_number}")
    print(f"  VAT Registered: {stack.company.vat_registered}")
    print(f"  Address:        {stack.company.address_line}, {stack.company.postal_code} {stack.company.city}")
    print(f"  Country:        {stack.company.country}")
    print(f"  Email:          {stack.company.email}")
    print(f"  Phone:          {stack.company.phone}")
    print(f"  Website:        {stack.company.website or 'N/A'}")
    print(f"  Currency:       {stack.company.currency}")
    print(f"  Locale:         {stack.company.locale}")
    
    # Validering
    print(f"\n✅ Org number valid: {stack.company.validate()}")
    
    # Full status
    print("\n📊 Full Status:")
    status = stack.get_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))
    
    print("\n" + "=" * 60)
    print("Test completed successfully!")
    print("=" * 60)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
