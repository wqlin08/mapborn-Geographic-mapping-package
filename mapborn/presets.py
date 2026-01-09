"""
presets.py
存储绘图组件的样式配置。
"""

# --- 指北针样式 ---
NORTH_ARROW_STYLES = {
    'nice': {
        'type': 'split',
        'facecolor_left': 'black',
        'facecolor_right': 'white',
        'edgecolor': 'black',
        'linewidth': 0.5,
        'text_color': 'black',
        'font_family': 'Arial',
        'font_size': 12,
        'font_weight': 'normal',
        'pad_factor': 0.1,
        'width_factor': 0.6,
        'font_scale': 1.0
    },
    'simpleB': {
        'type': 'solid',
        'facecolor': 'black',
        'edgecolor': 'none',
        'text_color': 'black',
        'font_family': 'Arial',
        'font_size': 14,
        'font_weight': 'normal',
        'pad_factor': 0.1,
        'width_factor': 0.7,
        'font_scale': 1.2
    },
    'simpleW': {
        'type': 'solid',
        'facecolor': 'white',
        'edgecolor': 'none',
        'text_color': 'black',
        'font_family': 'Arial',
        'font_size': 14,
        'font_weight': 'normal',
        'pad_factor': 0.1,
        'width_factor': 0.7,
        'font_scale': 1.2
    }
}


# --- 比例尺样式 ---
SCALE_BAR_STYLES = {
    'blocks': {
        'type': 'blocks',
        'color_1': 'black',
        'color_2': 'white',
        'edgecolor': 'black',
        'linewidth': 0.8,
        'font_family': 'Arial',
        'font_size': 9,
        'font_weight': 'normal',
        'height_ratio': 0.012,
        'text_pad': 0.015
    },
    'line-black': {
        'type': 'line',
        'color': 'black',
        'linewidth': 1.5,
        'tick_height_ratio': 0.01,
        'font_family': 'Arial',
        'font_size': 9,
        'font_weight': 'normal',
        'text_pad': 0.01
    },
    'line-white': {
        'type': 'line',
        'color': 'white',
        'linewidth': 1.5,
        'tick_height_ratio': 0.01,
        'font_family': 'Arial',
        'font_size': 9,
        'font_weight': 'normal',
        'text_pad': 0.01
    }
}

# --- 经纬网样式 ---
GRID_STYLES = {
    'default': {
        'color': '#333333',
        'linestyle': '--',
        'linewidth': 0.4,
        'alpha': 0.6,
        'font_family': 'Arial',
        'label_size': 7,
        'font_weight': 'normal',
        'label_color': 'black',
        'density': 4
    }
}
