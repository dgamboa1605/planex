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
@click.option(
    "--output",
    "output_root",
    default="output",
    show_default=True,
    help="Root directory where generated projects are placed.",
)
def run(spec_path: str, output_root: str) -> None:
    """Run the full generation pipeline for an approved spec."""
    from pathlib import Path

    from planex.core.orchestrator import Orchestrator
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

    console.print(f"[cyan]►[/cyan] Pipeline: [bold]{spec.name}[/bold] ({spec.slug})")

    try:
        orch = Orchestrator(spec, output_root=Path(output_root))
        output_dir = orch.run()
    except FileNotFoundError as exc:
        console.print(f"[red]✗ Template not found:[/red] {exc}")
        raise SystemExit(1)
    except Exception as exc:
        console.print(f"[red]✗ Pipeline error:[/red] {exc}")
        raise SystemExit(1)

    console.print(f"[green]✓ Done.[/green] Output: [bold]{output_dir.resolve()}[/bold]")
