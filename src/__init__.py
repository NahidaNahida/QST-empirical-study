# utils\__init__.py

from .file_processing import (
    read_csv, 
    read_config_json, 
    tex_command_template,
    tex_file_generation,
    number2camelform,
    paperids2citation
)

from .figure_templates import(
    line_chart_frequencies,
    line_chart_general,
    bar_chart_general,
    pie_chart,
    horizontal_bar_chart,
    horizontal_histogram,
    vertical_bar_chart,
    horizontal_stacked_bar_chart,
    horizontal_boxplot,
    upset_plot,
    two_labels_venn,
    two_dimensional_heatmap
)

from .table_templates import(
    vertical_tables,
    vertical_grouped_table,
    two_dimensional_table
)

from .bib_title_regulator import normalize_bibtex_str

from .data_frame import (
    data_clean,
    data_preprocess,
    parse_column,
    get_min_max,
    dict2upsetform
)

__all__ = [
    # General utilities
    "read_csv",
    "read_config_json",
    "tex_command_template",
    "tex_file_generation",
    "normalize_bibtex_str",
    "number2camelform",
    "paperids2citation",

    # Templates for figure
    "line_chart_frequencies",
    "line_chart_general",
    "pie_chart",
    "bar_chart_general",
    "horizontal_bar_chart",
    "horizontal_histogram",
    "vertical_bar_chart",
    "horizontal_stacked_bar_chart",
    "horizontal_boxplot",
    "upset_plot",
    "two_labels_venn",
    "two_dimensional_heatmap",

    # Templates for tables
    "vertical_tables",
    "vertical_grouped_table",
    "two_dimensional_table",

    # Parse data for results and analysis
    "data_clean",
    "data_preprocess",
    "parse_column",
    "get_min_max",
    "dict2upsetform"
]