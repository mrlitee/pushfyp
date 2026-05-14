"""CLI untuk pushfyp toolkit."""
from __future__ import annotations

import json
from datetime import datetime

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from . import analyzer, hook, hashtag, schedule, threads_api

console = Console()


@click.group()
@click.version_option()
def cli() -> None:
    """pushfyp — toolkit optimasi postingan Threads secara organik."""


# --- analyze -------------------------------------------------------------

@cli.command()
@click.argument("url")
@click.option("--json", "as_json", is_flag=True, help="Output JSON mentah.")
def analyze(url: str, as_json: bool) -> None:
    """Analisa postingan Threads dari LINK publik, kasih skor + saran."""
    try:
        result = analyzer.analyze(url)
    except ValueError as e:
        console.print(f"[red]Error:[/] {e}")
        raise SystemExit(1)
    except Exception as e:  # noqa: BLE001
        console.print(f"[red]Gagal fetch:[/] {e}")
        raise SystemExit(2)

    if as_json:
        click.echo(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
        return

    color = "green" if result.score >= 75 else "yellow" if result.score >= 50 else "red"
    console.print(
        Panel.fit(
            f"[bold {color}]Score: {result.score}/100[/]\n"
            f"Author: @{result.meta.author or '-'}\n"
            f"Caption: {(result.meta.caption or '')[:200]}",
            title="FYP Readiness",
        )
    )

    table = Table(title="Breakdown", show_header=True)
    table.add_column("Aspek")
    table.add_column("Skor", justify="right")
    for k, v in result.breakdown.items():
        table.add_row(k, str(v))
    console.print(table)

    if result.suggestions:
        console.print("\n[bold]Saran perbaikan:[/]")
        for i, s in enumerate(result.suggestions, 1):
            console.print(f"  {i}. {s}")
    else:
        console.print("\n[green]Postingan sudah well-optimized untuk FYP![/]")


# --- hook ----------------------------------------------------------------

@cli.command()
@click.argument("topic")
@click.option("--no-llm", is_flag=True, help="Skip LLM, pakai template rule-based.")
def hook_cmd(topic: str, no_llm: bool) -> None:
    """Generate 10 variasi hook/kalimat pembuka dari TOPIC."""
    hooks = hook.generate(topic, use_llm=not no_llm)
    console.print(Panel.fit(f"Hooks untuk: [bold]{topic}[/]"))
    for i, h in enumerate(hooks, 1):
        console.print(f"  [cyan]{i:>2}.[/] [{h.style}] {h.text}")


cli.add_command(hook_cmd, name="hook")


# --- hashtags ------------------------------------------------------------

@cli.command()
@click.option("--niche", required=True, help="Nama niche, contoh: fitness, tech, bisnis.")
@click.option("--count", default=5, show_default=True, type=int)
@click.option("--no-fyp", is_flag=True, help="Jangan tambah hashtag fyp generic.")
def hashtags(niche: str, count: int, no_fyp: bool) -> None:
    """Rekomendasi hashtag berdasarkan NICHE."""
    try:
        tags = hashtag.suggest(niche, count=count, include_fyp=not no_fyp)
    except ValueError as e:
        console.print(f"[red]Error:[/] {e}")
        raise SystemExit(1)
    console.print(" ".join(tags))


@cli.command("list-niches")
def list_niches() -> None:
    """Lihat semua niche yang didukung."""
    console.print(", ".join(hashtag.niches()))


# --- schedule & post -----------------------------------------------------

@cli.command()
@click.option("--text", required=True, help="Isi postingan.")
@click.option(
    "--at",
    "when",
    required=False,
    help="Waktu publish ISO-8601 (mis. '2026-05-13 08:00'). "
    "Kalau kosong, pakai slot rekomendasi terdekat.",
)
def schedule_post(text: str, when: str | None) -> None:
    """Jadwalkan auto-post via Threads API resmi."""
    if when:
        try:
            target = datetime.fromisoformat(when)
        except ValueError:
            console.print(f"[red]Format waktu salah:[/] {when}")
            raise SystemExit(1)
    else:
        target = schedule.next_recommended_slot()

    console.print(f"[green]Dijadwalkan:[/] {target.isoformat()}")
    console.print("[dim]Proses akan block sampai job executed. Ctrl+C untuk cancel.[/]")
    try:
        schedule.schedule_once(text, target, blocking=True)
    except KeyboardInterrupt:
        console.print("\n[yellow]Dibatalkan.[/]")
    except Exception as e:  # noqa: BLE001
        console.print(f"[red]Gagal:[/] {e}")
        raise SystemExit(2)


cli.add_command(schedule_post, name="schedule")


@cli.command()
@click.argument("text")
def post(text: str) -> None:
    """Langsung post ke Threads (butuh .env dengan Threads API credentials)."""
    try:
        result = threads_api.post_text(text)
    except Exception as e:  # noqa: BLE001
        console.print(f"[red]Gagal:[/] {e}")
        raise SystemExit(2)
    console.print(f"[green]Posted[/] media_id={result.media_id}")


@cli.command()
@click.option("--host", default="127.0.0.1", show_default=True)
@click.option("--port", default=8000, show_default=True, type=int)
@click.option("--reload", is_flag=True, help="Auto-reload (dev mode).")
def serve(host: str, port: int, reload: bool) -> None:
    """Jalankan web app di http://HOST:PORT."""
    try:
        import uvicorn
    except ImportError:
        console.print("[red]Butuh fastapi+uvicorn. Install:[/] pip install 'pushfyp[web]'")
        raise SystemExit(1)
    console.print(f"[green]pushfyp web[/] running at http://{host}:{port}")
    uvicorn.run("pushfyp.web.main:app", host=host, port=port, reload=reload)


if __name__ == "__main__":
    cli()
