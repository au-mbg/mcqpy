from mcqpy_pdf.cli.utils.main import utils_group
import rich_click as click
from pathlib import Path


@utils_group.command(
    name="check-filter",
    help="Check that filter expressions are valid",
)
@click.option(
    "-c",
    "--config",
    type=click.Path(exists=True, path_type=Path),
    help="Path to the config file",
    required=False,
)
@click.option('-fn', '--filter-name', type=str, help="Name of the filter to check", required=False)
@click.option('-fp', '--filter-params', type=str, help="Parameters of the filter as a YAML string", required=False)
@click.option('-y', '--yaml_input', help="YAML input specifying one or more filters to check", required=False)
def check_filter_command(config, filter_name, filter_params, yaml_input):
    """
    CLI command to check that filter expressions are valid.
    """
    from mcqpy_pdf.cli.config import SelectionConfig, QuizConfig
    from mcqpy_pdf.cli.build import _build_filter
    from rich.console import Console
    import yaml

    # Load config
    if config is not None:
        config = QuizConfig.read_yaml(config).selection
    elif filter_name is not None and filter_params is not None:
        config = SelectionConfig(filters={filter_name: yaml.safe_load(filter_params)})
    elif yaml_input is not None:
        yaml_data = yaml.safe_load(yaml_input)
        config = SelectionConfig(filters=yaml_data)
    else:
        raise click.UsageError("Either --config or both --filter-name and --filter-params must be provided.")

    # Check each filter expression in the config
    console = Console()
    for filter_name, filter_params in config.filters.items():
        try:
            _build_filter(filter_name, filter_params)
            console.print(f"[bold green]Filter '{filter_name}' is valid.[/bold green]")
        except Exception as e:
            console.print(f"[bold red]Filter '{filter_name}' is invalid: {e}[/bold red]")


