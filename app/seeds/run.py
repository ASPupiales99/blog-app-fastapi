import typer

from app.seeds.service import run_users, run_categories, run_tags, run_all

app = typer.Typer(help='Seeds: users, categories, tags')


@app.command("all")
def all_():
    run_all()
    typer.echo("All seeds seeded")


@app.command("users")
def users():
    run_users()
    typer.echo("Users seeded")


@app.command("categories")
def categories():
    run_categories()
    typer.echo("Categories seeded")


@app.command("tags")
def tags():
    run_tags()
    typer.echo("Tags seeded")
