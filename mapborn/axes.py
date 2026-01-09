import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1 import make_axes_locatable


def add_styled_colorbar(fig, mappable, ax=None, location='right',
                        width="5%", pad="2%", extend='both', label="",
                        label_size=12, tick_size=10, color='black',
                        font_family='SimHei'):
    """
    独立封装的色带添加函数，包含位置、大小、颜色及字体样式的完整控制。

    参数:
    fig : Figure 对象
    mappable : 绘图对象 (imshow/contourf result)
    ax : 依附的主坐标轴
    location : 位置 ('right', 'left', 'bottom', 'top')
    width : 色带宽度/高度 (如 "5%")
    pad : 色带与图的间距 (如 "2%")
    extend : 尖角设置 ('neither', 'both', 'min', 'max')
    label : 色带标签文本
    label_size : 标签字体大小
    tick_size : 刻度数值字体大小
    color : 整体颜色风格 (边框、刻度、文字颜色)
    font_family : 字体样式 (如 'Times New Roman', 'Arial', 'SimHei')
    """

    orientation = 'vertical' if location in ['right', 'left'] else 'horizontal'

    divider = make_axes_locatable(ax)
    cax = divider.append_axes(location, size=width, pad=pad)

    cbar = fig.colorbar(
        mappable,
        cax=cax,
        orientation=orientation,
        extend=extend,
        label=label
    )

    cbar.set_label(label, size=label_size, color=color, family=font_family)

    # 设置刻度大小和颜色
    cbar.ax.tick_params(labelsize=tick_size, color=color, labelcolor=color)

    # tick_params 无法直接设置 family，需要遍历设置
    if orientation == 'horizontal':
        tick_labels = cbar.ax.get_xticklabels()
    else:
        tick_labels = cbar.ax.get_yticklabels()

    for tl in tick_labels:
        tl.set_family(font_family)


    cbar.outline.set_edgecolor(color)
    cbar.outline.set_linewidth(0.8)

    return cbar