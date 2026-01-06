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
    x_data: list,                         # ✅ X-axis values
    y_data: dict[str, list],              # ✅ Multiple line series; key = label, value = list of Y values
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
    counts: list[int],         # 改为输入频数
    labels: list[str],
    save_path: str,
    config_figure: dict,
    fig_figsize: tuple = (5, 3),
    fig_anno_color: str = 'black',
    fig_edge_color: str = 'white',
    fig_title: str = ""
):
    common_configuration(config_figure)  
    
    # 计算总数与比例
    total = sum(counts)
    ratios = [c / total for c in counts]

    # 使用浅色系调色板
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
            f'{label}\n{ratio * 100:.1f}% ({count})',  # 显示“频数 (占比%)”
            ha='center',
            va='center',
            color=fig_anno_color,
            fontsize=config_figure["size"]["usual_fontsize"],
            fontweight='bold'  # 加粗显示
        )
        left += ratio

    # 美化
    ax.set_xlim(0, 1)
    ax.set_yticks([])
    ax.set_xticks([])
    ax.set_frame_on(False)

    plt.title(fig_title, fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')

    # 保存图像
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format='pdf', bbox_inches='tight')
    print(f"Horizontal stacked bar chart saved to {save_path}")

def bar_chart_general(
    x_data: list,                         # X-axis values
    y_data: dict[str, list],              # Multiple bar series
    legends: dict[Literal["x", "y"], str],
    save_path: str,
    config_figure: dict,
    fig_offset: float = 0.3,              # Text offset above each bar
    fig_figsize: tuple = (5, 3),
    fig_ylim: list | None = None,         # Optional Y-axis limit
    if_data: bool = True,                  # Show values above bars
    if_legend: bool = True,                 # Show legend
    legend_bbox_to_anchor: tuple = (0.5, -0.25),
    legend_handletextpad: float = 0.3,   # 标记与文字间距，默认0.8
    legend_columnspacing: float = 0.5,   # 列间距，默认2.0
    legend_labelspacing: float = 0.2,     # 行间距，默认0.5
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

    # 自动分配颜色（淡色系）
    base_colors = list(mcolors.TABLEAU_COLORS.values())
    if len(y_data) > len(base_colors):
        # 如果系列太多，扩展颜色
        base_colors *= (len(y_data) // len(base_colors) + 1)
    colors = [mcolors.to_rgba(c, alpha=0.7) for c in base_colors[:n_series]]

    for i, (label, y_vals) in enumerate(y_data.items()):
        if len(x_data) != len(y_vals):
            raise ValueError(
                f"The length of y_data for '{label}' ({len(y_vals)}) "
                f"does not match the length of x_data ({len(x_data)})!"
            )

        # 计算每组柱子的位置
        x_positions = [x + i * bar_width - (bar_width * (n_series - 1) / 2) for x in x_indices]

        # 绘制柱子，加入黑色边框
        bars = plt.bar(
            x_positions,
            y_vals,
            width=bar_width,
            label=label,
            color=colors[i],
            edgecolor='black'
        )

        # 显示柱子数值
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

    # 坐标轴标签与样式
    plt.xlabel(legends["x"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')
    plt.ylabel(legends["y"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')
    plt.grid(True, axis='y', linestyle='--', alpha=0.6)
    plt.xticks(x_indices, x_data, fontsize=config_figure["size"]["usual_fontsize"])
    plt.yticks(fontsize=config_figure["size"]["usual_fontsize"])
    if fig_ylim:
        plt.ylim(fig_ylim)

    # 图例
    if if_legend:
        if legend_nlocal == None:
            legend_nlocal = n_series

        plt.legend(
            title=None,
            fontsize=config_figure["size"]["usual_fontsize"],
            loc='upper center',
            bbox_to_anchor=legend_bbox_to_anchor,
            ncol=legend_nlocal,
            handletextpad=legend_handletextpad,   # 标记与文字间距，默认0.8
            columnspacing=legend_columnspacing,   # 列间距，默认2.0
            labelspacing=legend_labelspacing     # 行间距，默认0.5
        )

    plt.tight_layout()

    # 保存图表
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
        labels=None,  # 不使用默认 labels
        autopct=autopct_with_count,
        startangle=fig_startangle,
        explode=fig_explode,
        colors=colors,
        textprops={'fontsize': config_figure["size"]["usual_fontsize"]}
    )

    # 设置百分比文本和 label 的位置
    for i, (wedge, autotext) in enumerate(zip(wedges, autotexts)):
        # 获取扇形中心角度
        angle = (wedge.theta2 + wedge.theta1) / 2
        x = 0.6 * np.cos(np.deg2rad(angle))  # <-- 使用 np.cos
        y = 0.6 * np.sin(np.deg2rad(angle))  # <-- 使用 np.sin

        # 移动百分比文本到扇形中心
        autotext.set_position((x, y))

        # 在百分比上方添加 label
        ax.text(
            x, y - fig_offset,  # 微调 y 轴，让 label 在百分比上方
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
    # 统一配置
    common_configuration(config_figure)

    # 统计频数
    data_count = Counter(data)

    # 判断数据类型
    is_int_data = all(isinstance(x, int) for x in data)

    # ✅ 排序逻辑
    if req_sort is not None and not if_freq_sort:
        # 如果提供了 req_sort，按 req_sort 的顺序排列 keys
        sorted_items = sorted(
            data_count.items(),
            key=lambda x: req_sort.index(x[0]) if x[0] in req_sort else len(req_sort)
        )
    elif if_freq_sort:
        if is_int_data:
            # 如果是整数列表，按数值大小升序排列
            sorted_items = sorted(data_count.items(), key=lambda x: x[0])
        else:
            # 否则按频数升序 + 名称逆序排列
            sorted_items = sorted(
                data_count.items(),
                key=lambda x: (x[1], -ord(str(x[0])[0].lower())),  
                reverse=False
            )
    else:
        # 不排序，保持原始出现顺序
        sorted_items = list(data_count.items())
        
    # 拆解数据
    data_vals = [item[0] for item in sorted_items]
    counts = [item[1] for item in sorted_items]

    # 绘图
    _, ax = plt.subplots(figsize=fig_figsize)
    y = np.arange(len(data_vals))
    bar_height = fig_barheight

    bars = ax.barh(y, counts, height=bar_height, color=fig_color, alpha=0.85, edgecolor="black")
    ax.set_ylim(-0.5, len(data_vals)-0.5)
    ax.set_xlim(0, max(counts)*1.18)

    # 在柱右侧显示频数
    for i, bar in enumerate(bars):
        value = counts[i]
        ax.text(bar.get_width() + max(counts)*0.01, bar.get_y() + bar.get_height()/2,
                f"{value}", va="center", ha="left", fontsize=10)

    # 设置坐标轴
    ax.set_yticks(y)
    ax.set_yticklabels(data_vals, fontsize=config_figure["size"]["usual_fontsize"]) # type: ignore
    ax.set_ylabel(legends["y"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')

    ax.set_xlabel(legends["x"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')
    ax.tick_params(axis='x', labelsize=config_figure["size"]["usual_fontsize"])

    # ✅ x 轴整数化
    if fig_xinteger:
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    # 网格和外观
    ax.grid(axis="x", linestyle="--", alpha=0.6)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    if title:
        ax.set_title(title, fontsize=config_figure["size"]["axis_fontsize"], pad=10)

    # 保存图表
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
    # 检查数据类型
    if not all(isinstance(x, (int, float)) for x in data):
        raise ValueError("❌ data must be a list of int or float values.")
 
    common_configuration(config_figure)

    if len(data) == 0:
        raise ValueError("data is empty")

    arr = np.asarray(data)

    # 当存在 upper_limit 时：lower < upper_limit，upper >= upper_limit
    if upper_limit is not None:
        lower_data = arr[arr < upper_limit].tolist()
        upper_data = arr[arr >= upper_limit].tolist()
    else:
        lower_data = arr.tolist()
        upper_data = []

    # 处理 bins 参数：构造 bin_edges（针对 lower_data 范围到 upper_limit（如果有））
    if isinstance(bins, (list, np.ndarray)):
        bin_edges = np.asarray(bins, dtype=float)
        if upper_limit is not None:
            # 丢弃大于 upper_limit 的边界，并确保最后一个边界恰好等于 upper_limit
            bin_edges = bin_edges[bin_edges <= upper_limit]
            if bin_edges.size == 0:
                raise ValueError("bins list has no edges <= upper_limit")
            if bin_edges[-1] < upper_limit:
                bin_edges = np.concatenate([bin_edges, [upper_limit]])
    elif isinstance(bins, int):
        # 自动生成：从 lower_bound 到 upper_limit（若有），或从 min(data) 到 max(data)
        if upper_limit is not None:
            left = np.nanmin(lower_data) if len(lower_data) > 0 else 0.0
            right = upper_limit
        else:
            left = float(np.min(arr))
            right = float(np.max(arr))
            if left == right:
                # 单值情形，扩展一点范围
                left = left - 0.5
                right = right + 0.5
        bin_edges = np.linspace(left, right, bins + 1, dtype=float)
    else:
        raise TypeError("bins must be either int or list[float|int]")

    # 若 lower_data 为空，直接 counts 全为0（长度为 len(bin_edges)-1）
    if len(lower_data) == 0:
        counts = np.zeros(len(bin_edges) - 1, dtype=int)
    else:
        # 使用 np.digitize 构造左闭右开区间 [edge_i, edge_{i+1})
        # 但 np.digitize 的索引是 1..N_edges-1
        indices = np.digitize(lower_data, bin_edges, right=False)  # right=False => left-closed
        counts = np.zeros(len(bin_edges) - 1, dtype=int)
        for idx in indices:
            # idx 属于 1..len(bin_edges)-1 对应 counts[idx-1]
            if 1 <= idx <= counts.size:
                counts[idx - 1] += 1
            # idx == 0 表示 value < bin_edges[0]（理论上不应发生，除非数据小于第一个边界）
            elif idx == 0:
                # 将其放到第一个桶（可选策略）
                counts[0] += 1
            # idx > counts.size 表示 value >= bin_edges[-1]（但我们提前把大于等于 upper_limit 分离了）
            else:
                # 忽略或统计为溢出（这里忽略）
                pass

    # 构造标签：所有常规 bin 都显示为 [left, right)；当 upper_limit 为 None，保留最后一个区间右闭（可选）
    bin_labels = []
    n_bins = len(bin_edges) - 1
    for i in range(n_bins):
        left, right = bin_edges[i], bin_edges[i + 1]
        # 格式化数值，尽量显示整数如果是整数
        def fmt(x):
            return f"{int(x)}" if float(x).is_integer() else f"{x:.2f}"
        left_s, right_s = fmt(left), fmt(right)

        # 默认左闭右开
        if upper_limit is None and i == n_bins - 1:
            # 如果没有 upper_limit，保留最后一个 bin 右闭（和 np.histogram 保持一致）
            label = fr"$[{left_s},\, {right_s}]$"
        else:
            label = fr"$[{left_s},\, {right_s})$"
        bin_labels.append(label)

    # 如果有 upper_limit，则追加一个 [upper_limit, +∞) 并把上界及以上的数据计入
    if upper_limit is not None:
        upper_count = len(upper_data)
        counts = np.append(counts, upper_count)
        # 格式化 upper_limit
        upper_s = f"{int(upper_limit)}" if float(upper_limit).is_integer() else f"{upper_limit:.2f}"
        bin_labels.append(fr"$[{upper_s},\, +\infty)$")

    # 如果 bins 本来就是整数边界的列表，则强制 x 轴整数
    if isinstance(bins, (list, np.ndarray)) and all(float(b).is_integer() for b in bin_edges):
        fig_xinteger = True

    # 绘图
    _, ax = plt.subplots(figsize=fig_figsize)
    y = np.arange(len(bin_labels))
    bars = ax.barh(y, counts, height=fig_barheight, color=fig_color, alpha=0.85, edgecolor="black")

    ax.set_ylim(-0.5, len(bin_labels) - 0.5)
    ax.set_xlim(0, max(counts) * 1.18 if max(counts) > 0 else 1)

    # 标注频数
    max_c = max(counts) if len(counts) > 0 else 0
    for i, bar in enumerate(bars):
        value = int(counts[i])
        ax.text(bar.get_width() + (max_c * 0.01 if max_c > 0 else 0.1),
                bar.get_y() + bar.get_height() / 2,
                f"{value}", va="center", ha="left", fontsize=10)

    # 坐标轴与标签
    ax.set_yticks(y)
    ax.set_yticklabels(bin_labels, fontsize=config_figure["size"]["usual_fontsize"])  # type: ignore
    ax.set_ylabel(legends["y"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')
    ax.set_xlabel(legends["x"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')
    ax.tick_params(axis='x', labelsize=config_figure["size"]["usual_fontsize"])

    if fig_xinteger:
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    # 外观
    ax.grid(axis="x", linestyle="--", alpha=0.6)
    ax.set_axisbelow(True)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    if title:
        ax.set_title(title, fontsize=config_figure["size"]["axis_fontsize"], pad=10)

    # 保存
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
    if_freq_sort: bool = True,         # ✅ 是否排序
    is_int_data: bool = False,     # ✅ 是否为整数数据
    req_sort: list | None = None
) -> None:
    """
    绘制垂直柱状图，支持可选排序。
    """

    common_configuration(config_figure)

    # 统计频数
    data_count = Counter(data)

    # ✅ 排序逻辑
    if req_sort is not None and not if_freq_sort:
        # 如果提供了 req_sort，按 req_sort 的顺序排列 keys
        sorted_items = sorted(
            data_count.items(),
            key=lambda x: req_sort.index(x[0]) if x[0] in req_sort else len(req_sort)
        )
    elif if_freq_sort:
        if is_int_data:
            # 如果是整数列表，按数值大小升序排列
            sorted_items = sorted(data_count.items(), key=lambda x: x[0])
        else:
            # 否则按频数升序 + 名称逆序排列
            sorted_items = sorted(
                data_count.items(),
                key=lambda x: (x[1], -ord(str(x[0])[0].lower())),  
                reverse=False
            )
    else:
        # 不排序，保持原始出现顺序
        sorted_items = list(data_count.items())

    data_vals = [item[0] for item in sorted_items]
    counts = [item[1] for item in sorted_items]

    # 绘制 Bar Chart
    _, ax = plt.subplots(figsize=fig_figsize)
    x = np.arange(len(data_vals))
    bars = ax.bar(x, counts, width=fig_barwidth, color=fig_color, alpha=0.85, edgecolor="black")

    # 设置坐标轴范围
    ax.set_ylim(0, max(counts) * 1.18)
    ax.set_xlim(-0.5, len(data_vals) - 0.5)

    # 柱子顶部显示频次
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

    # 设置 x 轴
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

    # 保存图像
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
    fig_scatteralpha: float = 0.5,     # Transparency for scatters
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
    # --- （1）x轴只显示整数 & 自动简化显示（1k, 1M 等） ---
    def format_large_ticks(x, pos):
 
        if abs(x) >= 1_000_000:
            if fig_xinteger:
                # 正式模式：只允许整数 M
                return f"{x/1_000_000:.0f}M"
            else:
                # 非整数模式：允许小数 M，避免 1M 1M
                return f"{x/1_000_000:.2f}M".rstrip('0').rstrip('.')

        elif abs(x) >= 1_000:
            return f"{x/1_000:.0f}K"

        else:
            if fig_xinteger and abs(x - round(x)) < 1e-6:
                return f"{int(round(x))}"
            return f"{x:.2f}"
        
    """绘制带数据散点与统计标注的水平箱线图"""
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

 

    # --- 绘制散点 ---
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

    # --- 坐标轴标签 ---
    ax.set_xlabel(legends["x"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')
    ax.set_ylabel(legends["y"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')

    # --- ✅ 如果 no_ytick 为 True，则隐藏 y 轴刻度与标签 ---
    if no_ytick:
        ax.set_yticks([])                      # 移除刻度位置
        ax.set_yticklabels([])                 # 移除刻度标签
        ax.tick_params(axis='y', length=0)     # 移除刻度线

    # --- （1）x轴只显示整数 ---
    ax.xaxis.set_major_formatter(FuncFormatter(format_large_ticks))

    if fig_xinteger:
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))

    # --- （3）添加灰色网格 ---
    ax.grid(True, color="#E0E0E0", linestyle="--", linewidth=0.8, axis="x")
    ax.set_axisbelow(True)

    # --- 自动获取 boxplot whisker ---
    # matplotlib boxplot 对象
    box_dict = ax.artists  # 每个箱体
    whiskers = ax.lines    # whiskers 存在 lines 中，注意索引规则

    for i, vals in enumerate(data):
        vals = np.asarray(vals)
        n = len(vals)
        # 中位数
        q2 = np.percentile(vals, 50)

        # 获取 whisker
        lower_whisker = whiskers[2*i].get_xdata()[1]  # type: ignore # 第 i 个箱子的下 whisker
        upper_whisker = whiskers[2*i+1].get_xdata()[1]  # type: ignore # 第 i 个箱子的上 whisker

        min_v, max_v, median = lower_whisker, upper_whisker, q2
        y_pos = i

        if samplesize_name is not None:
            if len(data) == 1:
                ax.set_title(f"{samplesize_name} = {n}", fontsize=config_figure["size"]["axis_fontsize"])
            else:
                ax.text(
                    max_v + (max_v - min_v) * 0.05, y_pos, # type: ignore
                    f"{samplesize_name} = {n}",
                    va='center', ha='left', fontsize=8, color='black', zorder=5
                )

        # --- 控制显示数据格式（与坐标轴分离）---
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

        # --- 中位数 ---
        ax.scatter(median, y_pos, color='red', marker='o', s=30,
                   zorder=5, label='Median' if i == 0 else "")
        ax.annotate(
            annotated_data["median"], (median, y_pos), xytext=fig_median_offset, # type: ignore
            textcoords='offset points',
            fontsize=config_figure["size"]["usual_fontsize"],
            color='red', va='center', fontweight='bold'
        )

        # --- 最大值（upper whisker） ---
        ax.scatter(max_v, y_pos, color='#8E44AD', marker='>',
                   s=fig_extremesize, zorder=5, label='Upper whisker' if i == 0 else "")
        ax.annotate(
            annotated_data["maximum"], (max_v, y_pos), xytext=fig_max_offset, # type: ignore
            textcoords='offset points',
            fontsize=config_figure["size"]["usual_fontsize"],
            color='#8E44AD', va='bottom', fontweight='bold'
        )

        # --- 最小值（lower whisker） ---
        ax.scatter(min_v, y_pos, color='#16A085', marker='<',
                   s=fig_extremesize, zorder=5, label='Lower whisker' if i == 0 else "")
        ax.annotate(
            annotated_data["minimum"], (min_v, y_pos), xytext=(-20, -2), # type: ignore
            textcoords='offset points',
            fontsize=config_figure["size"]["usual_fontsize"],
            color='#16A085', va='top', fontweight='bold'
        )

    # --- 保存图或图例 ---
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
                frameon=True,  # ✅ 必须为 True，否则不会生成边框
                fontsize=config_figure["size"]["axis_fontsize"],
                handlelength=1.2,
                columnspacing=0.8
            )

            # ✅ 设置边框样式
            frame = leg.get_frame()
            frame.set_edgecolor('black')   # 黑色边框
            frame.set_linewidth(0.8)       # 边框线宽
            frame.set_facecolor('white')   # 可选：背景为白色
            frame.set_alpha(1.0)           # 可选：不透明
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

    # 应用通用配置（例如字体、样式等）
    common_configuration(config_figure)

    # 构造数据
    req_data = from_memberships(memberships, data=values)

    # ✅ 直接在 UpSet 内部定义 figsize
    upset = UpSet(
        req_data,
        show_counts=True, # type: ignore
        sort_by="cardinality",
        facecolor=fig_color
    )

    # 绘制 UpSet 图
    upset.plot(fig=plt.figure(figsize=fig_figsize))
    fig = plt.gcf()  # 获取当前 figure
    fig.set_size_inches(*fig_figsize)  # ✅ 之后再调整大小 

    # 通过调整 subplot 参数，让左右子图更紧凑
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
    ellipse: float | None= None,               # 圆→椭圆变换系数
    label_offset: dict | None = None            # 新增：标签偏移配置
):
    # 通用配置
    common_configuration(config_figure)

    plt.figure(figsize=fig_figsize)

    # pastel 颜色
    colors = cm.Pastel1.colors  # type: ignore
    colors = [colors[i % len(colors)] for i in range(2)]

    # 绘制 Venn
    v = venn2(subsets=counts, set_labels=labels)

    # 设置颜色
    if v.get_patch_by_id("10"):
        v.get_patch_by_id("10").set_color(colors[0])
        v.get_patch_by_id("10").set_alpha(0.8)
    if v.get_patch_by_id("01"):
        v.get_patch_by_id("01").set_color(colors[1])
        v.get_patch_by_id("01").set_alpha(0.8)
    if v.get_patch_by_id("11"):
        v.get_patch_by_id("11").set_alpha(0.6)

    # === 标签加粗 ===
    for region in ["10", "01", "11"]:
        label = v.get_label_by_id(region)
        if label:
            label.set_fontweight("bold")

    # 外侧集合名称
    for side in ["A", "B"]:
        label = v.get_label_by_id(side)
        if label:
            label.set_fontweight("bold")

    # === 椭圆支持 ===
    if ellipse is not None:
        for region in ["10", "01", "11"]:
            patch = v.get_patch_by_id(region)
            if patch is not None:
                trans = Affine2D().scale(ellipse, 1.0) + plt.gca().transData
                patch.set_transform(trans)

    # === 标签偏移功能 ===
    if label_offset is None:
        label_offset = {}

    for key, offset in label_offset.items():
        label = v.get_label_by_id(key)
        if label:
            x, y = label.get_position()
            dx, dy = offset
            label.set_position((x + dx, y + dy))

    # 保存
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
    将二维字典转换为热力图并保存为图片(如 .png/.jpg/.pdf).
    data_dict: dict[row][col] = value(字符串，但会尝试转换为数字)
    """
 
    common_configuration(config_figure)  # 假设你有自己的配置函数
   

    # 行
    rows = sorted(data_dict.keys())

    # 所有列名
    col_set = set()
    for r in rows:
        col_set.update(data_dict[r].keys())
    
    # x 轴列顺序：按 desired_order 排序，只保留存在于数据中的列
    cols = [c for c in desired_order if c in col_set]

    # 构建 DataFrame
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

    # 绘制热力图
    plt.figure(figsize=fig_figsize)
    ax = sns.heatmap(
        df,
        cmap=cmap,
        annot=annot,
        fmt=".0f",
        linewidths=1,          # 单元格边框宽度
        linecolor="black",     # 网格颜色
        annot_kws={
            "fontsize": config_figure["size"]["usual_fontsize"],
            "fontweight": "bold"   # 这里设置加粗
        },
        cbar_kws={"shrink": 0.8}  # colorbar 缩放
    )

    # 确保 x 轴和 y 轴 tick 对齐单元格中心
    ax.set_xticks(np.arange(len(cols)) + 0.5)
    ax.set_yticks(np.arange(len(rows)) + 0.5)
    ax.set_xticklabels(cols, rotation=30, fontsize=config_figure["size"]["usual_fontsize"], ha='right')
    ax.set_yticklabels(rows, rotation=0, fontsize=config_figure["size"]["usual_fontsize"])

    ax.set_xlabel(legends["x"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')
    ax.set_ylabel(legends["y"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')

    # 移除多余的 minor ticks
    ax.tick_params(which='minor', length=0)

    # 坐标轴样式
    ax.tick_params(axis="x", labelrotation=30)
    ax.tick_params(axis="y", labelrotation=0)

 

    # 保存文件
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format='pdf', bbox_inches='tight')
 
    print(f"Heatmap saved to {save_path}")


if __name__ == "__main__":
    # 生成示例数据
    data = [
        np.random.normal(0, 10, 100),   # 组1
        # np.random.normal(5, 2, 100),   # 组2
        # np.random.normal(10, 1.5, 100) # 组3
    ]

 