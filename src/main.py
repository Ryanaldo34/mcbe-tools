import addons.entity.define as entity
import typer
import addons.project as project
import addons.items as items
import addons.blocks as blocks

app = typer.Typer()

app.add_typer(project.app, name='project')
app.add_typer(entity.app, name='entity')
app.add_typer(items.app, name='items')
app.add_typer(blocks.app, name='blocks')

if __name__ == '__main__':
    app()