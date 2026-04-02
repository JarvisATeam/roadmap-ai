"""CLI commands for validating JSON exports."""

from __future__ import annotations

import json
from pathlib import Path

import click

from roadmap.core.json_validator import (
    SCHEMAS,
    auto_schema_for_file,
    validate_json,
    validate_json_file,
)


@click.command("validate")
@click.argument("filepath", type=click.Path(exists=True))
@click.option("--schema", default="envelope", help="Schema name (auto if envelope)")
@click.option("--strict", is_flag=True, help="Exit with error on validation failure")
def validate_command(filepath: str, schema: str, strict: bool):
    """Validate a JSON export file."""
    path = Path(filepath)
    schema_name = schema
    if schema_name == "envelope":
        schema_name = auto_schema_for_file(path)
        click.echo(f"Auto-detected schema: {schema_name}")
    ok, error = validate_json_file(path, schema_name)
    if ok:
        click.echo(f"✅ {path.name} valid ({schema_name})")
    else:
        click.echo(f"❌ {path.name} invalid: {error}", err=True)
        if strict:
            raise SystemExit(1)


@click.command("validate-all")
@click.argument("directory", type=click.Path(exists=True))
@click.option("--strict", is_flag=True, help="Exit with error if any file fails")
def validate_all_command(directory: str, strict: bool):
    """Validate all JSON files within a directory."""
    dir_path = Path(directory)
    files = sorted(dir_path.glob("*.json"))
    if not files:
        click.echo(f"No JSON files found in {directory}")
        return
    failed = 0
    for file in files:
        schema_name = auto_schema_for_file(file)
        ok, error = validate_json_file(file, schema_name)
        if ok:
            click.echo(f"✅ {file.name} ({schema_name})")
        else:
            failed += 1
            click.echo(f"❌ {file.name}: {error}")
    if failed:
        click.echo(f"\n{failed} file(s) failed validation")
        if strict:
            raise SystemExit(1)
    else:
        click.echo("\nAll files valid")
