import os
import click
import toml
from zuu.app.pandoc import pandoc_run
from zuu.app.xelatex import run_xelatex_in_temp, run_xelatex

_basepath = os.path.dirname(os.path.realpath(__file__))
respath = os.path.join(_basepath, "res")

@click.command()
@click.argument("data", required=False)
@click.argument("template", required=False)
@click.option("--delete-temp-file", "-d", help="Delete temporary files", is_flag=True)
@click.option(
    "--gen-pdf-local",
    "-l",
    help="Generate pdf locally, will contain quite some garbage",
    is_flag=True,
)
@click.option("--testmode", "-t", help="Test mode, will use example.toml", is_flag=True)
def CLICK(
    data=None,
    template=None,
    gen_pdf_local=False,
    delete_temp_file=False,
    testmode=False,
):
    if data is None:
        if not testmode:
            raise click.UsageError("Data is required")
        data = os.path.join(respath, "example.toml")

    loadedData = toml.load(data)

    if template is None:
        template = os.path.join(respath, "template.tex")

    os.makedirs("output", exist_ok=True)

    pandoc_run(
        loadedData,
        template_path=template,
        output_path="output/output.tex",
        delete_temporary=False,
        meta_path="output/input.md",
    )

    e = None
    try:
        if gen_pdf_local:
            run_xelatex("output.tex", texInputs=respath)
        else:
            os.environ["TEXINPUTS"] = respath
            run_xelatex_in_temp("output",captures=["*.pdf"], texInputs=respath)
    except Exception as e: #noqa
        e = e
        click.echo(f"Error: {e}")
    finally:
        if not delete_temp_file:
            return

        if os.path.exists("output/input.md"):
            os.remove("output/input.md")
        if os.path.exists("output/output.tex"):
            os.remove("output/output.tex")


if __name__ == "__main__":
    CLICK()
