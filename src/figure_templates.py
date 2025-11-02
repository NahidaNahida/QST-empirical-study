from collections import Counter
from typing import Literal
import matplotlib.pyplot as plt
from matplotlib import cm
import os
import numpy as np

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

def line_chart(
    data: list, 
    legends: dict[Literal["x", "y"], str], 
    save_path: str,
    config_figure: dict,
    temporal_config: dict = {
        "offset": 0.7,          # Offset above the data point for the label
        "figsize": (3.5, 2.25),
        "ylim": [0, 25],         # y-axis display range
    }
) -> None:
    common_configuration(config_figure)

    # Count the frequency of each value
    data_count = Counter(data)

    # Sort the values in ascending order
    data_vals = sorted(data_count.keys())
    counts = [data_count[y] for y in data_vals]

    # Plot the line chart
    plt.figure(figsize=temporal_config["figsize"])
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
            y + temporal_config["offset"], 
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
    plt.ylim(temporal_config["ylim"])

    # Save the figure to the specified path
    # Ensure the directory exists
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format='pdf', bbox_inches='tight')
    print(f"The line chart has been saved to {save_path}")


def pie_chart(
    data: list[str],
    save_path: str,
    config_figure: dict,
    temporal_config: dict = {
        "figsize": (3, 3),
        "explode": None,
        "autopct": "%1.1f%%",
        "startangle": 90,
        "offset": 0.25,
    }
) -> None:
    """
    Draw a pie chart from the data, showing percentages with counts.
    """
    common_configuration(config_figure)

    # Count the frequency of each category
    data_count = Counter(data)
    labels = list(data_count.keys())
    sizes = list(data_count.values())

    if temporal_config["explode"] is None:
        temporal_config["explode"] = [0] * len(labels)

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
    _, ax = plt.subplots(figsize=temporal_config["figsize"])
    wedges, _, autotexts = ax.pie( # type: ignore
        sizes,
        labels=None,  # 不使用默认 labels
        autopct=autopct_with_count,
        startangle=temporal_config["startangle"],
        explode=temporal_config["explode"],
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
            x, y - temporal_config["offset"],  # 微调 y 轴，让 label 在百分比上方
            labels[i],
            ha='center',
            va='bottom',
            fontweight='bold',
            fontsize=config_figure["size"]["usual_fontsize"]
        )

    plt.axis('equal')

    # Save the figure
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format='pdf', bbox_inches='tight')
    print(f"The pie chart has been saved to {save_path}")

def horizontal_bar_chart(
    data: list[str],
    legends: dict[Literal["x", "y"], str], 
    save_path: str,
    config_figure: dict,
    temporal_config: dict = {
        "figsize": (3.5, 2.25),
        "bar_height": 0.25,
        "color": "#B7B5B7F8"
    }
) -> None:
    common_configuration(config_figure)

    # Count the frequency of each value
    data_count = Counter(data)

    # Sort by frequency (ascending), then by name alphabetically
    sorted_items = sorted(
        data_count.items(),
        key=lambda x: (x[1], -ord(x[0][0].lower())),  # 二级排序：频数 → 名称, 按频数升序，首字母逆序  
        reverse=False
    )

    data_vals = [item[0] for item in sorted_items]   # 按频数（及字母顺序）排序后的值
    counts = [item[1] for item in sorted_items]      # 对应的频数

    # 绘制 Bar Chart
    fig, ax = plt.subplots(figsize=temporal_config["figsize"])

    y = np.arange(len(data_vals))
    bar_height = temporal_config["bar_height"]

    bars = ax.barh(y, counts, height=bar_height, color=temporal_config["color"], alpha=0.85, edgecolor="black")
    ax.set_ylim(-0.5, len(data_vals)-0.5)  # 紧凑排列
    ax.set_xlim(0, max(counts)*1.18)  # 让右边留出 15% 空间

    # 在每个柱子顶部显示频次
    for i, bar in enumerate(bars):
        value = counts[i]
        #text_str = f"{value}\n({percent:.1f}%)"
        ax.text(bar.get_width() + max(counts)*0.01, bar.get_y() + bar.get_height()/2,
                f"{value}", va="center", ha="left", fontsize=10)

    # 设置 y 轴
    ax.set_yticks(y)
    ax.set_yticklabels(data_vals, fontsize=config_figure["size"]["usual_fontsize"])
    ax.set_ylabel(legends["y"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')

    # x 轴
    ax.set_xlabel(legends["x"], fontsize=config_figure["size"]["axis_fontsize"], fontweight='bold')
    ax.tick_params(axis='x', labelsize=config_figure["size"]["usual_fontsize"])  # 只调整刻度字体大小

    # 网格线
    ax.grid(axis="x", linestyle="--", alpha=0.6)
    ax.set_axisbelow(True)  # ✅ 确保网格线在柱子下方

    # 去掉边框
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Save the figure
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, format='pdf', bbox_inches='tight')
    print(f"The horizontal bar chart has been saved to {save_path}")