import typer
from pathlib import Path
from . convert import convert_bp, convert_datapack, convert_mcbe_rp, convert_java_rp_structure

app = typer.Typer()

@app.command()
def bedrock_rp(
    bedrock_rp: Path = typer.Argument(default=None, help='Path to the rp being converted'),
    output_path: Path = typer.Argument(default=None, help='Path where the converted rp is saved'),
    pack_name: str = typer.Option(default='',help='Change the name out the output pack'),
    namespace: str = typer.Option(default='custom', help='The namespace used for the rp')
):
    convert_mcbe_rp(output_path, bedrock_rp, namespace=namespace, pack_name=pack_name)

@app.command()
def java_rp(
    java_rp: Path = typer.Argument(help='Path to the rp being converted'), 
    output_path: Path = typer.Argument(help='Path where the converted rp is saved'),
    pack_name: str = typer.Option(default='',help='Change the name out the output pack')
):
    pass

@app.command()
def behavior_pack(
    bp_path: Path = typer.Argument(help='Path to the bp being converted'),
    output_path: Path = typer.Argument(help='Where to save the new datapack'),
    pack_name: str = typer.Option(default='',help='Change the name out the output pack')
):
    pass

@app.command()
def data_pack(
    dp_path: Path = typer.Argument(help='Path to datapack being converted'),
    output_path: Path = typer.Argument(help='Where the new bp is saved'),
    pack_name: str = typer.Option(default='',help='Change the name out the output pack')
):
    pass

