"""
Docstring for src.figure_templates
Templates for various types of figures used in data visualization.
"""

from collections import Counter
from typing import Literal
import matplotlib.pyplot as plt
from matplotlib import cm
import os
import numpy as np
import seaborn as sns
from matplotlib.ticker import FuncFormatter, MaxNLocator
from upsetplot import UpSet, from_memberships
import matplotlib.colors as mcolors
from matplotlib_venn import venn2
from matplotlib.transforms import Affine2D
import pandas as pd


def common_configuration(config_figure: dict) -> None:
    mapping_dict = {
        "rcParams": plt.rcParams
    }
    
    for key, sub_dict in config_figure.items():
        if isinstance(sub_dict, dict):
            for sub_key, config in sub_dict.items():
                if key in mapping_dict.keys():
                    mapping_dict[key][sub_key] = config
    return

def line_chart_frequencies(
    data: list, 
    legends: dict[Literal["x", "y"], str], 
    save_path: str,
    config_figure: dict,
    fig_offset: float = 0.7,
    fig_figsize: tuple = (3.5, 2.25),
    fig_ylim: list = [0, 25]
) -> None:
    common_configuration(config_figure)

    # Count the frequency of each value
    data_count = Counter(data)

    # Sort the values in ascending order
    data_vals = sorted(data_count.keys())
    counts = [data_count[y] for y in data_vals]

    # Plot the line chart
    plt.figure(figsize=fig_figsize)
    plt.plot(
        data_vals, 
        counts, 
        marker='o', 
        markersize=config_figure["size"]["markersize"],
        linestyle='-', 
        linewidth=config_figure["width"]["linewidth"]
    )

    # Annotate each data point with its value
    for x, y in zip(data_vals, counts):
        plt.text(
            x, 
            y + fig_offset, 
            str(y), 
            ha='center', 
            va='bottom', 
            fontsize=config_figure["size"]["usual_fontsize"]
        )

    # Set axis labels
    plt.xlabel(legends["x"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')
    plt.ylabel(legends["y"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.6)

    # Set ticks
    plt.xticks(data_vals, fontsize=config_figure["size"]["usual_fontsize"])
    plt.yticks(fontsize=config_figure["size"]["usual_fontsize"])

    # Set y-axis limits
    plt.ylim(fig_ylim)

    # Save the figure to the specified path
    # Ensure the directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format='pdf', bbox_inches='tight')
    print(f"The line chart has been saved to {save_path}")


def line_chart_general(
    x_data: list,                         # X-axis values
    y_data: dict[str, list],              # Multiple line series; key = label, value = list of Y values
    legends: dict[Literal["x", "y"], str],
    save_path: str,
    config_figure: dict,
    fig_offset: float = 0.3,              # Text offset above each data point
    fig_figsize: tuple = (5, 3),
    fig_ylim: list | None = None          # Optional Y-axis limit
) -> None:
    """
    Plot multiple line charts on the same figure.

    Parameters
    ----------
    x_data : list
        X-axis values (e.g., years, steps, etc.)
    y_data : dict[str, list]
        Dictionary of Y-axis series; each key represents a line label,
        and its value is a list of Y values.
    legends : dict
        Axis labels, e.g. {"x": "Year", "y": "Count"}
    save_path : str
        Path to save the generated PDF figure.
    config_figure : dict
        Dictionary defining marker size, line width, and font sizes.
    fig_offset : float, optional
        Vertical offset for the text labels above data points.
    fig_figsize : tuple, optional
        Figure size (width, height).
    fig_ylim : list, optional
        Y-axis limits [min, max].
    """

    common_configuration(config_figure)  

    plt.figure(figsize=fig_figsize)

    for label, y_vals in y_data.items():
        if len(x_data) != len(y_vals):
            raise ValueError(
                f"The length of y_data for '{label}' ({len(y_vals)}) "
                f"does not match the length of x_data ({len(x_data)})!"
            )

        # Plot a single line
        plt.plot(
            x_data, y_vals,
            marker='o',
            markersize=config_figure["size"]["markersize"],
            linewidth=config_figure["width"]["linewidth"],
            label=label
        )

        # Annotate each point with its value
        for x, y in zip(x_data, y_vals):
            plt.text(
                x,
                y + fig_offset,
                f"{y:.2f}" if isinstance(y, float) else str(y),
                ha='center',
                va='bottom',
                fontsize=config_figure["size"]["usual_fontsize"]
            )

    # Axis labels and styles
    plt.xlabel(legends["x"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')
    plt.ylabel(legends["y"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.xticks(x_data, fontsize=config_figure["size"]["usual_fontsize"])
    plt.yticks(fontsize=config_figure["size"]["usual_fontsize"])
    if fig_ylim:
        plt.ylim(fig_ylim)

    # Add legend to distinguish multiple lines
    plt.legend(title="Legend", fontsize=config_figure["size"]["usual_fontsize"])
    plt.tight_layout()

    # Save the figure
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format='pdf', bbox_inches='tight')
    print(f"Line chart is saved to {save_path}")

def horizontal_stacked_bar_chart(
    counts: list[int],         # Frequencies for each category
    labels: list[str],
    save_path: str,
    config_figure: dict,
    fig_figsize: tuple = (5, 3),
    fig_anno_color: str = 'black',
    fig_edge_color: str = 'white',
    fig_title: str = ""
):
    common_configuration(config_figure)  
    
    #  Calculate ratios
    total = sum(counts)
    ratios = [c / total for c in counts]

    #  Plot horizontal stacked bar chart
    colors = plt.cm.Pastel1.colors # type: ignore

    fig, ax = plt.subplots(figsize=fig_figsize)

    left = 0
    for i, (ratio, label, count) in enumerate(zip(ratios, labels, counts)):
        ax.barh(
            0,
            ratio,
            left=left,
            color=colors[i % len(colors)],
            edgecolor=fig_edge_color
        )
        ax.text(
            left + ratio / 2,
            0,
            f'{label}\n{ratio * 100:.1f}% ({count})',  # Display label, percentage, and count
            ha='center',
            va='center',
            color=fig_anno_color,
            fontsize=config_figure["size"]["usual_fontsize"],
            fontweight='bold'  # Bold font for better visibility
        )
        left += ratio

    # Customize axes
    ax.set_xlim(0, 1)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_frame_on(False)

    plt.title(fig_title, fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')

    # Save the figure
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format='pdf', bbox_inches='tight')
    print(f"Horizontal stacked bar chart saved to {save_path}")

def bar_chart_general(
    x_data: list,                               # X-axis values
    y_data: dict[str, list],                    # Multiple bar series
    legends: dict[Literal["x", "y"], str],
    save_path: str,
    config_figure: dict,
    fig_offset: float = 0.3,                    # Text offset above each bar
    fig_figsize: tuple = (5, 3),
    fig_ylim: list | None = None,               # Optional Y-axis limit
    if_data: bool = True,                       # Show values above bars
    if_legend: bool = True,                     # Show legend
    legend_bbox_to_anchor: tuple = (0.5, -0.25),
    legend_handletextpad: float = 0.3,          
    legend_columnspacing: float = 0.5,    
    legend_labelspacing: float = 0.2,    
    legend_nlocal: float | None = None
) -> None:
    """
    Plot multiple bar charts on the same figure (grouped bars) with optional features.
    """
    common_configuration(config_figure)  

    plt.figure(figsize=fig_figsize)

    n_series = len(y_data)
    bar_width = config_figure.get("width", {}).get("barwidth", 0.8 / n_series)
    x_indices = range(len(x_data))

    # Assign colors to each series, cycling through a predefined color list if necessary
    base_colors = list(mcolors.TABLEAU_COLORS.values())
    if len(y_data) > len(base_colors):
        # Extend the color list by repeating it
        base_colors *= (len(y_data) // len(base_colors) + 1)
    colors = [mcolors.to_rgba(c, alpha=0.7) for c in base_colors[:n_series]]

    for i, (label, y_vals) in enumerate(y_data.items()):
        if len(x_data) != len(y_vals):
            raise ValueError(
                f"The length of y_data for '{label}' ({len(y_vals)}) "
                f"does not match the length of x_data ({len(x_data)})!"
            )

        # Calculate x positions for grouped bars
        x_positions = [x + i * bar_width - (bar_width * (n_series - 1) / 2) for x in x_indices]

        # Plot bars for the current series
        bars = plt.bar(
            x_positions,
            y_vals,
            width=bar_width,
            label=label,
            color=colors[i],
            edgecolor='black'
        )

        # Annotate each bar with its value
        if if_data:
            for bar, y in zip(bars, y_vals):
                plt.text(
                    bar.get_x() + bar.get_width() / 2,
                    y + fig_offset,
                    f"{y:.2f}" if isinstance(y, float) else str(y),
                    ha='center',
                    va='bottom',
                    fontsize=config_figure["size"]["usual_fontsize"]
                )

    # Axis labels and styles
    plt.xlabel(legends["x"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')
    plt.ylabel(legends["y"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')
    plt.grid(True, axis='y', linestyle='--', alpha=0.6)
    plt.xticks(x_indices, x_data, fontsize=config_figure["size"]["usual_fontsize"])
    plt.yticks(fontsize=config_figure["size"]["usual_fontsize"])
    if fig_ylim:
        plt.ylim(fig_ylim)

    # Add legend if required
    if if_legend:
        if legend_nlocal == None:
            legend_nlocal = n_series

        plt.legend(
            title=None,
            fontsize=config_figure["size"]["usual_fontsize"],
            loc='upper center',
            bbox_to_anchor=legend_bbox_to_anchor,
            ncol=legend_nlocal,
            handletextpad=legend_handletextpad,   
            columnspacing=legend_columnspacing,   
            labelspacing=legend_labelspacing      
        )

    plt.tight_layout()

    # Save the figure
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format='pdf', bbox_inches='tight')
    print(f"Bar chart is saved to {save_path}")

def pie_chart(
    data: list[str],
    save_path: str,
    config_figure: dict,
    fig_figsize: tuple = (3, 3),
    fig_explode = None,
    fig_startangle: int = 90,
    fig_offset: float = 0.25,
    title: str | None = None
) -> None:
    """
    Draw a pie chart from the data, showing percentages with counts.
    """
    common_configuration(config_figure)

    # Count the frequency of each category
    data_count = Counter(data)
    labels = list(data_count.keys())
    sizes = list(data_count.values())

    if fig_explode is None:
        fig_explode = [0] * len(labels)

    # Custom function to show percentage + count
    def autopct_with_count(pct):
        total = sum(sizes)
        count = int(round(pct * total / 100.0))
        return f"{pct:.1f}% ({count})"

    # Generate pastel colors for each slice
    num_slices = len(labels)
    colors = cm.Pastel1.colors # type: ignore
    colors = [colors[i % len(colors)] for i in range(num_slices)]

    # Create the pie chart
    _, ax = plt.subplots(figsize=fig_figsize)
    wedges, _, autotexts = ax.pie( # type: ignore
        sizes,
        labels=None,  
        autopct=autopct_with_count,
        startangle=fig_startangle,
        explode=fig_explode,
        colors=colors,
        textprops={'fontsize': config_figure["size"]["usual_fontsize"]}
    )

    # Adjust the position of percentage texts and add labels above them
    for i, (wedge, autotext) in enumerate(zip(wedges, autotexts)):
        # Calculate the angle for the current wedge
        angle = (wedge.theta2 + wedge.theta1) / 2
        x = 0.6 * np.cos(np.deg2rad(angle))  # Use np.cos
        y = 0.6 * np.sin(np.deg2rad(angle))  # Use np.sin

        # Adjust the position of the percentage text
        autotext.set_position((x, y))

        # Add label text above the percentage
        ax.text(
            x, y - fig_offset,              # Position above the percentage
            labels[i],
            ha='center',
            va='bottom',
            fontweight='bold',
            fontsize=config_figure["size"]["usual_fontsize"]
        )

    plt.axis('equal')

    if title:
        ax.set_title(title, fontsize=config_figure["size"]["usual_fontsize"], pad=2)

    # Save the figure
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format='pdf', bbox_inches='tight')
    print(f"The pie chart has been saved to {save_path}")

def horizontal_bar_chart(
    data: list[str] | list[int],
    legends: dict[Literal["x", "y"], str], 
    save_path: str,
    config_figure: dict,
    fig_figsize: tuple = (3.5, 2.25),
    fig_barheight: float = 0.25,
    fig_color: str = "#B7B5B7F8",
    fig_xinteger: bool = True,      # Whether ticks on the x-axis should be integers
    title: str | None = None,
    if_freq_sort: bool = True,
    req_sort: list | None = None
) -> None:
    # Common configuration
    common_configuration(config_figure)

    # Statistics
    data_count = Counter(data)

    # Detect if data is integer type
    is_int_data = all(isinstance(x, int) for x in data)

    # Sorting logic
    if req_sort is not None and not if_freq_sort:
        # If req_sort is provided, sort keys according to req_sort order
        sorted_items = sorted(
            data_count.items(),
            key=lambda x: req_sort.index(x[0]) if x[0] in req_sort else len(req_sort)
        )
    elif if_freq_sort:
        if is_int_data:
            # If it's an integer list, sort by numerical value ascending
            sorted_items = sorted(data_count.items(), key=lambda x: x[0])
        else:
            # Otherwise, sort by frequency ascending + name descending
            sorted_items = sorted(
                data_count.items(),
                key=lambda x: (x[1], -ord(str(x[0])[0].lower())),  
                reverse=False
            )
    else:
        # No sorting, keep original order
        sorted_items = list(data_count.items())
        
    # Extract sorted data and counts
    data_vals = [item[0] for item in sorted_items]
    counts = [item[1] for item in sorted_items]

    # Plot Bar Chart
    _, ax = plt.subplots(figsize=fig_figsize)
    y = np.arange(len(data_vals))
    bar_height = fig_barheight

    bars = ax.barh(y, counts, height=bar_height, color=fig_color, alpha=0.85, edgecolor="black")
    ax.set_ylim(-0.5, len(data_vals)-0.5)
    ax.set_xlim(0, max(counts)*1.18)

    # Annotate frequencies on bars
    for i, bar in enumerate(bars):
        value = counts[i]
        ax.text(bar.get_width() + max(counts)*0.01, bar.get_y() + bar.get_height()/2,
                f"{value}", va="center", ha="left", fontsize=10)

    # Axes and labels
    ax.set_yticks(y)
    ax.set_yticklabels(data_vals, fontsize=config_figure["size"]["usual_fontsize"]) # type: ignore
    ax.set_ylabel(legends["y"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')

    ax.set_xlabel(legends["x"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')
    ax.tick_params(axis='x', labelsize=config_figure["size"]["usual_fontsize"])

    # x-axis integer ticks
    if fig_xinteger:
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    # Appearance
    ax.grid(axis="x", linestyle="--", alpha=0.6)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    if title:
        ax.set_title(title, fontsize=config_figure["size"]["axis_fontsize"], pad=10)

    # Save
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format='pdf', bbox_inches='tight')

    # print(f"Number of categories: {len(set(data_vals))}.")
    print(f"The horizontal bar chart has been saved to {save_path}")
 
import os
from typing import Optional
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

def horizontal_histogram(
    data: list[int] | list[float],
    legends: dict[str, str],
    save_path: str,
    config_figure: dict,
    fig_figsize: tuple = (3.5, 2.25),
    fig_barheight: float = 0.25,
    fig_color: str = "#B7B5B7F8",
    fig_xinteger: bool = True,
    title: str | None = None,
    bins: int | list[float] | list[int] = 10,
    upper_limit: float | None = None,
) -> None:
    # Check data type
    if not all(isinstance(x, (int, float)) for x in data):
        raise ValueError("Data must be a list of int or float values.")
 
    common_configuration(config_figure)

    if len(data) == 0:
        raise ValueError("data is empty")

    arr = np.asarray(data)

    # When upper_limit exists: lower < upper_limit, upper >= upper_limit
    if upper_limit is not None:
        lower_data = arr[arr < upper_limit].tolist()
        upper_data = arr[arr >= upper_limit].tolist()
    else:
        lower_data = arr.tolist()
        upper_data = []

    # Handle bins argument: construct bin_edges
    # (covering lower_data range up to upper_limit if provided)
    if isinstance(bins, (list, np.ndarray)):
        bin_edges = np.asarray(bins, dtype=float)
        if upper_limit is not None:
            # Drop edges larger than upper_limit and ensure the last edge equals upper_limit
            bin_edges = bin_edges[bin_edges <= upper_limit]
            if bin_edges.size == 0:
                raise ValueError("bins list has no edges <= upper_limit")
            if bin_edges[-1] < upper_limit:
                bin_edges = np.concatenate([bin_edges, [upper_limit]])
    elif isinstance(bins, int):
        # Auto-generate bins: from lower bound to upper_limit (if any),
        # or from min(data) to max(data)
        if upper_limit is not None:
            left = np.nanmin(lower_data) if len(lower_data) > 0 else 0.0
            right = upper_limit
        else:
            left = float(np.min(arr))
            right = float(np.max(arr))
            if left == right:
                # Single-value case: slightly expand the range
                left = left - 0.5
                right = right + 0.5
        bin_edges = np.linspace(left, right, bins + 1, dtype=float)
    else:
        raise TypeError("bins must be either int or list[float|int]")

    # If lower_data is empty, set all counts to zero
    if len(lower_data) == 0:
        counts = np.zeros(len(bin_edges) - 1, dtype=int)
    else:
        # Use np.digitize to build left-closed right-open intervals [edge_i, edge_{i+1})
        # np.digitize indices range from 1 to N_edges-1
        indices = np.digitize(lower_data, bin_edges, right=False)
        counts = np.zeros(len(bin_edges) - 1, dtype=int)
        for idx in indices:
            # idx in 1..len(bin_edges)-1 maps to counts[idx-1]
            if 1 <= idx <= counts.size:
                counts[idx - 1] += 1
            # idx == 0 means value < bin_edges[0]
            elif idx == 0:
                # Put into the first bin (optional strategy)
                counts[0] += 1
            # idx > counts.size means value >= bin_edges[-1]
            else:
                # Ignore overflow
                pass

    # Build bin labels: all regular bins shown as [left, right)
    # If upper_limit is None, keep the last bin right-closed
    bin_labels = []
    n_bins = len(bin_edges) - 1
    for i in range(n_bins):
        left, right = bin_edges[i], bin_edges[i + 1]

        # Format values: show integers when possible
        def fmt(x):
            return f"{int(x)}" if float(x).is_integer() else f"{x:.2f}"

        left_s, right_s = fmt(left), fmt(right)

        if upper_limit is None and i == n_bins - 1:
            # Last bin right-closed when no upper_limit (consistent with np.histogram)
            label = fr"$[{left_s},\, {right_s}]$"
        else:
            label = fr"$[{left_s},\, {right_s})$"
        bin_labels.append(label)

    # If upper_limit exists, append [upper_limit, +∞)
    if upper_limit is not None:
        upper_count = len(upper_data)
        counts = np.append(counts, upper_count)
        upper_s = f"{int(upper_limit)}" if float(upper_limit).is_integer() else f"{upper_limit:.2f}"
        bin_labels.append(fr"$[{upper_s},\, +\infty)$")

    # Force integer x-axis if bins are integer edges
    if isinstance(bins, (list, np.ndarray)) and all(float(b).is_integer() for b in bin_edges):
        fig_xinteger = True

    # Plot
    _, ax = plt.subplots(figsize=fig_figsize)
    y = np.arange(len(bin_labels))
    bars = ax.barh(y, counts, height=fig_barheight,
                   color=fig_color, alpha=0.85, edgecolor="black")

    ax.set_ylim(-0.5, len(bin_labels) - 0.5)
    ax.set_xlim(0, max(counts) * 1.18 if max(counts) > 0 else 1)

    # Annotate frequencies
    max_c = max(counts) if len(counts) > 0 else 0
    for i, bar in enumerate(bars):
        value = int(counts[i])
        ax.text(
            bar.get_width() + (max_c * 0.01 if max_c > 0 else 0.1),
            bar.get_y() + bar.get_height() / 2,
            f"{value}", va="center", ha="left", fontsize=10
        )

    # Axes and labels
    ax.set_yticks(y)
    ax.set_yticklabels(bin_labels, fontsize=config_figure["size"]["usual_fontsize"])  # type: ignore
    ax.set_ylabel(legends["y"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')
    ax.set_xlabel(legends["x"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')
    ax.tick_params(axis='x', labelsize=config_figure["size"]["usual_fontsize"])

    if fig_xinteger:
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    # Appearance
    ax.grid(axis="x", linestyle="--", alpha=0.6)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    if title:
        ax.set_title(title, fontsize=config_figure["size"]["axis_fontsize"], pad=10)

    # Save figure
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format='pdf', bbox_inches='tight')
    plt.close()

    print(f"The horizontal histogram has been saved to {save_path}")

def vertical_bar_chart(
    data: list[str],
    legends: dict[str, str], 
    save_path: str,
    config_figure: dict,
    fig_figsize: tuple = (3.5, 2.25),
    fig_barwidth: float = 0.5,
    fig_color: str = "#B7B5B7F8",
    fig_yinteger: bool = True,
    title: str | None = None,
    rotate_xticks: bool = True,
    rotation_angle: int = 30,
    if_freq_sort: bool = True,          # If sort by frequency
    is_int_data: bool = False,          # Whether data is integer type
    req_sort: list | None = None
) -> None:
    """
    Draw a vertical bar chart from the data, showing frequencies.
    """

    common_configuration(config_figure)

    # Count the frequency of each category
    data_count = Counter(data)

    # Sorting logic
    if req_sort is not None and not if_freq_sort:
        # If req_sort is provided, sort keys according to req_sort order
        sorted_items = sorted(
            data_count.items(),
            key=lambda x: req_sort.index(x[0]) if x[0] in req_sort else len(req_sort)
        )
    elif if_freq_sort:
        if is_int_data:
            # If it's an integer list, sort by numerical value ascending
            sorted_items = sorted(data_count.items(), key=lambda x: x[0])
        else:
            # Otherwise, sort by frequency ascending + name descending
            sorted_items = sorted(
                data_count.items(),
                key=lambda x: (x[1], -ord(str(x[0])[0].lower())),  
                reverse=False
            )
    else:
        # No sorting, keep original order
        sorted_items = list(data_count.items())

    data_vals = [item[0] for item in sorted_items]
    counts = [item[1] for item in sorted_items]

    # Plot Bar Chart
    _, ax = plt.subplots(figsize=fig_figsize)
    x = np.arange(len(data_vals))
    bars = ax.bar(x, counts, width=fig_barwidth, color=fig_color, alpha=0.85, edgecolor="black")

    # Set limits
    ax.set_ylim(0, max(counts) * 1.18)
    ax.set_xlim(-0.5, len(data_vals) - 0.5)

    # Annotate frequencies on bars
    for i, bar in enumerate(bars):
        value = counts[i]
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + max(counts) * 0.01,
            f"{value}",
            ha="center",
            va="bottom",
            fontsize=10
        )

    # Axes and labels
    ax.set_xticks(x)
    ax.set_xticklabels(data_vals, fontsize=config_figure["size"]["usual_fontsize"])
    if rotate_xticks or any(len(label) > 8 for label in data_vals):
        plt.setp(ax.get_xticklabels(), rotation=rotation_angle, ha="right")

    ax.set_xlabel(legends["x"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')
    ax.set_ylabel(legends["y"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')
    ax.tick_params(axis='y', labelsize=config_figure["size"]["usual_fontsize"])
    if fig_yinteger:
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

    ax.grid(axis="y", linestyle="--", alpha=0.6)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    if title:
        ax.set_title(title, fontsize=config_figure["size"]["axis_fontsize"], pad=10)

    # Save
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format='pdf', bbox_inches='tight')
    print(f"The vertical bar chart has been saved to {save_path}")


def horizontal_boxplot(
    data: list[np.ndarray],
    legends: dict[Literal["x", "y"], str],
    save_path: str,
    config_figure: dict,
    fig_figsize: tuple = (4, 2.5),
    fig_color: str = "#B7B5B7F8",
    fig_pointsize: float = 3.0,
    fig_boxwidth: float = 0.1,
    fig_scatteralpha: float = 0.5,          # Transparency for scatters
    fig_extremesize: float = 25.0,
    fig_xinteger: bool = True,
    fig_datainteger: bool = True,
    fig_median_offset: tuple = (-2, 25), 
    fig_max_offset: tuple = (0, 6), 
    samplesize_name = None,
    show_points: bool = True,
    point_mode: Literal["strip", "swarm"] = "swarm",
    no_ytick: bool = False,
    legend_only: bool = False
) -> None:
    # Show only integers on the x-axis & automatically simplify large values (1K, 1M, etc.)
    def format_large_ticks(x, pos):
 
        if abs(x) >= 1_000_000:
            if fig_xinteger:
                # Strict mode: allow only integer millions
                return f"{x/1_000_000:.0f}M"
            else:
                # Non-integer mode: allow decimal millions
                return f"{x/1_000_000:.2f}M".rstrip('0').rstrip('.')

        elif abs(x) >= 1_000:
            return f"{x/1_000:.0f}K"

        else:
            if fig_xinteger and abs(x - round(x)) < 1e-6:
                return f"{int(round(x))}"
            return f"{x:.2f}"
        
    """Draw a horizontal boxplot with data points and statistical annotations"""
    common_configuration(config_figure)

    plt.figure(figsize=fig_figsize)
    ax = sns.boxplot(
        data=data,
        color=fig_color,
        width=fig_boxwidth,
        fliersize=3,
        zorder=1,
        orient='h'
    )

    # Draw scatter points
    if show_points:
        if point_mode == "strip":
            sns.stripplot(
                data=data,
                color='grey',
                size=fig_pointsize,
                alpha=fig_scatteralpha,
                jitter=True,
                zorder=3,
                orient='h'
            )
        elif point_mode == "swarm":
            sns.swarmplot(
                data=data,
                color='grey',
                size=fig_pointsize,
                alpha=fig_scatteralpha,
                zorder=3,
                orient='h'
            )

    # Axis labels
    ax.set_xlabel(legends["x"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')
    ax.set_ylabel(legends["y"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')

    # If no_ytick is True, hide y-axis ticks and labels
    if no_ytick:
        ax.set_yticks([])                      # Remove tick positions
        ax.set_yticklabels([])                 # Remove tick labels
        ax.tick_params(axis='y', length=0)     # Remove tick marks

    # Show only integers on the x-axis ---
    ax.xaxis.set_major_formatter(FuncFormatter(format_large_ticks))

    if fig_xinteger:
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    # Add gray grid
    ax.grid(True, color="#E0E0E0", linestyle="--", linewidth=0.8, axis="x")
    ax.set_axisbelow(True)

    # Automatically extract boxplot whiskers
    # matplotlib boxplot objects
    box_dict = ax.artists  # Each box
    whiskers = ax.lines    # Whiskers are stored in lines; note the indexing rule

    for i, vals in enumerate(data):
        vals = np.asarray(vals)
        n = len(vals)
        # Median
        q2 = np.percentile(vals, 50)

        # Get whiskers
        lower_whisker = whiskers[2*i].get_xdata()[1]      # type: ignore # Lower whisker of the i-th box
        upper_whisker = whiskers[2*i+1].get_xdata()[1]    # type: ignore # Upper whisker of the i-th box

        min_v, max_v, median = lower_whisker, upper_whisker, q2
        y_pos = i

        if samplesize_name is not None:
            if len(data) == 1:
                ax.set_title(f"{samplesize_name} = {n}", fontsize=config_figure["size"]["axis_fontsize"])
            else:
                ax.text(
                    max_v + (max_v - min_v) * 0.05, y_pos,  # type: ignore
                    f"{samplesize_name} = {n}",
                    va='center', ha='left', fontsize=8, color='black', zorder=5
                )

        # Control data display format (independent from axis formatting)
        def format_data_value(v):
            if fig_datainteger:
                return f"{int(round(v))}"
            else:
                return f"{v:.2f}"

        annotated_data = {
            "median": format_data_value(median),
            "maximum": format_data_value(max_v),
            "minimum": format_data_value(min_v),
        }

        # Median
        ax.scatter(median, y_pos, color='red', marker='o', s=30,
                   zorder=5, label='Median' if i == 0 else "")
        ax.annotate(
            annotated_data["median"], (median, y_pos), xytext=fig_median_offset,  # type: ignore
            textcoords='offset points',
            fontsize=config_figure["size"]["usual_fontsize"],
            color='red', va='center', fontweight='bold'
        )

        # Maximum (upper whisker)
        ax.scatter(max_v, y_pos, color='#8E44AD', marker='>',
                   s=fig_extremesize, zorder=5, label='Upper whisker' if i == 0 else "")
        ax.annotate(
            annotated_data["maximum"], (max_v, y_pos), xytext=fig_max_offset,  # type: ignore
            textcoords='offset points',
            fontsize=config_figure["size"]["usual_fontsize"],
            color='#8E44AD', va='bottom', fontweight='bold'
        )

        # Minimum (lower whisker)
        ax.scatter(min_v, y_pos, color='#16A085', marker='<',
                   s=fig_extremesize, zorder=5, label='Lower whisker' if i == 0 else "")
        ax.annotate(
            annotated_data["minimum"], (min_v, y_pos), xytext=(-20, -2),  # type: ignore
            textcoords='offset points',
            fontsize=config_figure["size"]["usual_fontsize"],
            color='#16A085', va='top', fontweight='bold'
        )

    # Save figure or legend only
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    if legend_only:
        handles, labels = ax.get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        if by_label:
            legend_fig = plt.figure(figsize=fig_figsize)
            leg = legend_fig.legend(
                handles=by_label.values(),
                labels=by_label.keys(),
                loc='center',
                ncol=len(by_label),
                frameon=True,   # Must be True, otherwise the frame will not be rendered
                fontsize=config_figure["size"]["axis_fontsize"],
                handlelength=1.2,
                columnspacing=0.8
            )

            # Configure legend frame style
            frame = leg.get_frame()
            frame.set_edgecolor('black')   # Black border
            frame.set_linewidth(0.8)       # Border width
            frame.set_facecolor('white')   # Optional: white background
            frame.set_alpha(1.0)           # Optional: fully opaque
            legend_fig.savefig(save_path, bbox_inches='tight', pad_inches=0)
    else:
        plt.savefig(save_path, format='pdf', bbox_inches='tight')

    figure_type = "legend" if legend_only else "boxplot"
    print(f"The {figure_type} has been saved to {save_path}")



def upset_plot(
    data: dict[Literal["memberships", "values"], list],
    save_path: str,
    config_figure: dict,
    fig_figsize: tuple = (2, 2.5),
    fig_color: str = "#B7B5B7F8",
    fig_wspace: float = -0.5
):
    memberships = data["memberships"]
    values = data["values"]

    # Apply common configuration (e.g., fonts, styles, etc.)
    common_configuration(config_figure)

    # Build data
    req_data = from_memberships(memberships, data=values)

    # Define figsize directly inside UpSet
    upset = UpSet(
        req_data,
        show_counts=True,  # type: ignore
        sort_by="cardinality",
        facecolor=fig_color
    )

    # Draw the UpSet plot
    upset.plot(fig=plt.figure(figsize=fig_figsize))
    fig = plt.gcf()                       # Get the current figure
    fig.set_size_inches(*fig_figsize)     # Adjust size again afterwards

    # Adjust subplot parameters to make left and right subplots more compact
    plt.subplots_adjust(wspace=fig_wspace)

    # Save the image
    plt.savefig(save_path, format='pdf', bbox_inches='tight')
    print(f"The upset plot has been saved to {save_path}")



def two_labels_venn(
    counts: tuple,
    labels: tuple,
    save_path: str,
    config_figure: dict,
    fig_figsize: tuple = (2, 2.5),
    ellipse: float | None = None,               # Circle → ellipse scaling factor
    label_offset: dict | None = None            # New: label offset configuration
):
    # Common configuration
    common_configuration(config_figure)

    plt.figure(figsize=fig_figsize)

    # Pastel colors
    colors = cm.Pastel1.colors  # type: ignore
    colors = [colors[i % len(colors)] for i in range(2)]

    # Draw Venn diagram
    v = venn2(subsets=counts, set_labels=labels)

    # Set colors
    if v.get_patch_by_id("10"):
        v.get_patch_by_id("10").set_color(colors[0])
        v.get_patch_by_id("10").set_alpha(0.8)
    if v.get_patch_by_id("01"):
        v.get_patch_by_id("01").set_color(colors[1])
        v.get_patch_by_id("01").set_alpha(0.8)
    if v.get_patch_by_id("11"):
        v.get_patch_by_id("11").set_alpha(0.6)

    # === Bold region labels ===
    for region in ["10", "01", "11"]:
        label = v.get_label_by_id(region)
        if label:
            label.set_fontweight("bold")

    # Outer set labels
    for side in ["A", "B"]:
        label = v.get_label_by_id(side)
        if label:
            label.set_fontweight("bold")

    # Ellipse support
    if ellipse is not None:
        for region in ["10", "01", "11"]:
            patch = v.get_patch_by_id(region)
            if patch is not None:
                trans = Affine2D().scale(ellipse, 1.0) + plt.gca().transData
                patch.set_transform(trans)

    # Label offset feature
    if label_offset is None:
        label_offset = {}

    for key, offset in label_offset.items():
        label = v.get_label_by_id(key)
        if label:
            x, y = label.get_position()
            dx, dy = offset
            label.set_position((x + dx, y + dy))

    # Save figure
    plt.savefig(save_path, format='pdf', bbox_inches='tight')
    print(f"The Venn plot has been saved to {save_path}")



def two_dimensional_heatmap(
    data_dict: dict[str, dict[str, str]],
    legends: dict[Literal["x", "y"], str],
    desired_order: list[str],
    save_path: str,
    config_figure: dict,
    fig_figsize: tuple = (2, 2.5),
    cmap: str = "Blues",
    annot: bool = True
) -> None:
    """
    Convert a two-dimensional dictionary into a heatmap and save it as an image
    (e.g., .png / .jpg / .pdf).

    data_dict: dict[row][col] = value
               (stored as strings, but will be converted to numbers when possible)
    """

    common_configuration(config_figure)  # Assume a custom configuration function exists

    # Rows
    rows = sorted(data_dict.keys())

    # Collect all column names
    col_set = set()
    for r in rows:
        col_set.update(data_dict[r].keys())
    
    # X-axis column order: follow desired_order, keep only columns existing in data
    cols = [c for c in desired_order if c in col_set]

    # Construct DataFrame
    table = []
    for r in rows:
        row_vals = []
        for c in cols:
            v = data_dict[r].get(c, "")
            try:
                v = float(v)
            except:
                v = np.nan
            row_vals.append(v)
        table.append(row_vals)

    df = pd.DataFrame(table, index=rows, columns=cols)

    # Draw heatmap
    plt.figure(figsize=fig_figsize)
    ax = sns.heatmap(
        df,
        cmap=cmap,
        annot=annot,
        fmt=".0f",
        linewidths=1,               # Cell border width
        linecolor="black",          # Cell border color
        annot_kws={
            "fontsize": config_figure["size"]["usual_fontsize"],
            "fontweight": "bold"    # Bold annotations
        },
        cbar_kws={"shrink": 0.8}    # Colorbar size reduction
    )

    # Ensure ticks are centered
    ax.set_xticks(np.arange(len(cols)) + 0.5)
    ax.set_yticks(np.arange(len(rows)) + 0.5)
    ax.set_xticklabels(
        cols,
        rotation=30,
        fontsize=config_figure["size"]["usual_fontsize"],
        ha='right'
    )
    ax.set_yticklabels(
        rows,
        rotation=0,
        fontsize=config_figure["size"]["usual_fontsize"]
    )

    ax.set_xlabel(
        legends["x"],
        fontsize=config_figure["size"]["axis_fontsize"],
        fontweight='bold'
    )
    ax.set_ylabel(
        legends["y"],
        fontsize=config_figure["size"]["axis_fontsize"],
        fontweight='bold'
    )

    # Remove minor ticks
    ax.tick_params(which='minor', length=0)

    # Set tick parameters
    ax.tick_params(axis="x", labelrotation=30)
    ax.tick_params(axis="y", labelrotation=0)

    # Save the figure
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format='pdf', bbox_inches='tight')

    print(f"Heatmap saved to {save_path}")
