import addons.entity.cmds as entity
import typer
import addons.project as project
import addons.items as items
import addons.blocks as blocks
# import conversions.app as conversions

app = typer.Typer()

app.add_typer(project.app, name='project')
app.add_typer(entity.app, name='entity')
app.add_typer(items.app, name='items')
app.add_typer(blocks.app, name='blocks')
# app.add_typer(conversions.app, name='convert')

if __name__ == '__main__':
    app()