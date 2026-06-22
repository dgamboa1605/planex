from __future__ import annotations

import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option(package_name="planex")
def cli() -> None:
    """planex — AI Software Factory CLI."""


@cli.command()
@click.argument("spec_path", type=click.Path(exists=True))
def validate(spec_path: str) -> None:
    """Validate a Project Spec JSON against the schema."""
    from planex.core.spec import ProjectSpec, SpecError

    try:
        spec = ProjectSpec.from_file(spec_path)
        console.print(
            f"[green]✓[/green] Spec [bold]{spec.slug}[/bold] is valid  "
            f"(type: {spec.project_type}, status: {spec.status})"
        )
    except SpecError as exc:
        console.print(f"[red]✗ Validation error:[/red] {exc}")
        raise SystemExit(1)


@cli.command()
@click.argument("spec_path", type=click.Path(exists=True))
def run(spec_path: str) -> None:
    """Run the full generation pipeline for an approved spec."""
    from planex.core.spec import ProjectSpec, SpecError

    try:
        spec = ProjectSpec.from_file(spec_path)
    except SpecError as exc:
        console.print(f"[red]✗ Spec error:[/red] {exc}")
        raise SystemExit(1)

    if not spec.is_approved():
        console.print(
            f"[yellow]⚠  Spec status is '{spec.status}'. "
            "Set meta.status to 'approved' before running.[/yellow]"
        )
        raise SystemExit(1)

    console.print(f"[cyan]→[/cyan] Pipeline for: [bold]{spec.name}[/bold] ({spec.slug})")
    console.print("[dim]Pipeline not yet implemented — Phase 1.[/dim]")
