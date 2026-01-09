import math
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from .presets import NORTH_ARROW_STYLES, SCALE_BAR_STYLES, GRID_STYLES


class MapComponent:
    def __init__(self, ax):
        self.ax = ax

class NorthArrow(MapComponent):
    def draw(self, location='top-right', size=0.08, style_name='nice',
             font_size=None, font_family=None):
        """
        Args:
            location:
                - str: 'top-right', 'top-left', 'bottom-right', 'bottom-left'
                - tuple: (x, y) 相对坐标, 范围 0.0~1.0。例如 (0.5, 0.5) 为正中心。
        """
        style = NORTH_ARROW_STYLES.get(style_name, NORTH_ARROW_STYLES['nice'])

        if isinstance(location, (list, tuple)):
            cx, cy = location[0], location[1]
        else:
            # 预设字符串坐标
            pad = 0.03
            loc_map = {
                'top-right': (1 - pad, 1 - pad), 'top-left': (pad, 1 - pad),
                'bottom-right': (1 - pad, pad), 'bottom-left': (pad, pad)
            }
            cx, cy = loc_map.get(location, (0.95, 0.95))

        bbox = self.ax.get_window_extent().transformed(self.ax.figure.dpi_scale_trans.inverted())
        ax_aspect = bbox.width / bbox.height
        h = size
        w = size * style['width_factor'] / ax_aspect

        if style['type'] == 'split':
            self._draw_split_arrow(cx, cy, w, h, style)
        elif style['type'] == 'solid':
            self._draw_solid_arrow(cx, cy, w, h, style)
        elif style['type'] == 'arrow_line':
            self._draw_simple_line_arrow(cx, cy, w, h, style)

        final_font = font_family if font_family else style.get('font_family', 'Arial')
        final_size = font_size if font_size is not None else size * 150 * style.get('font_scale', 1.0)
        y_offset = h * style.get('pad_factor', 0.1)

        self.ax.text(cx, cy + h / 2 + y_offset, "N", transform=self.ax.transAxes, ha='center', va='bottom',
                     fontsize=final_size, fontweight=style.get('font_weight', 'normal'), fontfamily=final_font,
                     color=style.get('text_color', 'black'), zorder=30)

    def _draw_split_arrow(self, cx, cy, w, h, style):
        top, bottom_wing, bottom_center = cy + h / 2, cy - h / 2, cy - h / 4
        left_x, right_x = cx - w / 2, cx + w / 2
        p_left = mpatches.Polygon([[cx, top], [left_x, bottom_wing], [cx, bottom_center]], transform=self.ax.transAxes,
                                  facecolor=style['facecolor_left'], edgecolor=style['edgecolor'],
                                  linewidth=style['linewidth'], zorder=30, clip_on=False)
        p_right = mpatches.Polygon([[cx, top], [right_x, bottom_wing], [cx, bottom_center]],
                                   transform=self.ax.transAxes, facecolor=style['facecolor_right'],
                                   edgecolor=style['edgecolor'], linewidth=style['linewidth'], zorder=30, clip_on=False)
        self.ax.add_patch(p_left);
        self.ax.add_patch(p_right)

    def _draw_solid_arrow(self, cx, cy, w, h, style):
        top, bottom, left_x, right_x = cy + h / 2, cy - h / 2, cx - w / 2, cx + w / 2
        poly = mpatches.Polygon([[cx, top], [left_x, bottom], [right_x, bottom]], transform=self.ax.transAxes,
                                facecolor=style['facecolor'], edgecolor=style['edgecolor'], zorder=30, clip_on=False)
        self.ax.add_patch(poly)

    def _draw_simple_line_arrow(self, cx, cy, w, h, style):
        top, bottom = cy + h / 2, cy - h / 2
        self.ax.plot([cx, cx], [bottom, top], transform=self.ax.transAxes, color=style['color'],
                     linewidth=style['linewidth'], zorder=30, clip_on=False)
        self.ax.plot([cx, cx - w / 2], [top, top - h * 0.25], transform=self.ax.transAxes, color=style['color'],
                     linewidth=style['linewidth'], zorder=30, clip_on=False)
        self.ax.plot([cx, cx + w / 2], [top, top - h * 0.25], transform=self.ax.transAxes, color=style['color'],
                     linewidth=style['linewidth'], zorder=30, clip_on=False)


class ScaleBar(MapComponent):
    def draw(self, crs, extent, location='bottom-left', unit='km', style_name='blocks',
             font_size=None, font_family=None):
        """
        Args:
            location:
                - str: 'bottom-left', 'bottom-right'
                - tuple: (x, y) 相对坐标, 范围 0.0~1.0。
                         (0,0) 为左下角, (0.5, 0.5) 为中心。
                         注意：这是比例尺左下角锚点的位置。
        """
        style = SCALE_BAR_STYLES.get(style_name, SCALE_BAR_STYLES['blocks'])
        bar_width_map_units, label_text = self._calculate_scale_params(crs, extent, unit)

        final_font = font_family if font_family else style.get('font_family', 'Arial')
        final_size = font_size if font_size is not None else style['font_size']

        xmin, xmax, ymin, ymax = extent
        map_width = xmax - xmin
        map_height = ymax - ymin

        if isinstance(location, (list, tuple)):
            rel_x, rel_y = location[0], location[1]
            sx = xmin + rel_x * map_width
            sy = ymin + rel_y * map_height
        else:
            pad_x, pad_y = map_width * 0.05, map_height * 0.05
            if location == 'bottom-left':
                sx, sy = xmin + pad_x, ymin + pad_y
            elif location == 'bottom-right':
                sx, sy = xmax - pad_x - bar_width_map_units, ymin + pad_y
            else:
                sx, sy = xmin + pad_x, ymin + pad_y

        if style['type'] == 'blocks':
            self._draw_blocks(sx, sy, bar_width_map_units, extent, style, label_text, final_size, final_font)
        elif style['type'] == 'line':
            self._draw_line(sx, sy, bar_width_map_units, extent, style, label_text, final_size, final_font)

    def _draw_blocks(self, sx, sy, width, extent, style, label, f_size, f_fam):
        height = (extent[3] - extent[2]) * style['height_ratio']
        self.ax.add_patch(
            mpatches.Rectangle((sx, sy), width / 2, height, facecolor=style['color_1'], edgecolor=style['edgecolor'],
                               linewidth=style['linewidth'], zorder=20))
        self.ax.add_patch(mpatches.Rectangle((sx + width / 2, sy), width / 2, height, facecolor=style['color_2'],
                                             edgecolor=style['edgecolor'], linewidth=style['linewidth'], zorder=20))
        self.ax.text(sx + width / 2, sy + height + (extent[3] - extent[2]) * style['text_pad'], label, ha='center',
                     va='bottom', fontsize=f_size, fontweight=style.get('font_weight', 'normal'), fontfamily=f_fam,
                     color='black', zorder=20)

    def _draw_line(self, sx, sy, width, extent, style, label, f_size, f_fam):
        tick_h = (extent[3] - extent[2]) * style['tick_height_ratio']
        c, lw = style['color'], style['linewidth']
        self.ax.plot([sx, sx + width], [sy, sy], color=c, linewidth=lw, zorder=20)
        self.ax.plot([sx, sx], [sy, sy + tick_h], color=c, linewidth=lw, zorder=20)
        self.ax.plot([sx + width, sx + width], [sy, sy + tick_h], color=c, linewidth=lw, zorder=20)
        self.ax.plot([sx + width / 2, sx + width / 2], [sy, sy + tick_h * 0.6], color=c, linewidth=lw, zorder=20)
        t = self.ax.text(sx + width / 2, sy + tick_h + (extent[3] - extent[2]) * style['text_pad'], label, ha='center',
                         va='bottom', fontsize=f_size, fontweight=style.get('font_weight', 'normal'), fontfamily=f_fam,
                         color=c, zorder=20)
        if 'white' in str(c):
            import matplotlib.patheffects as pe
            t.set_path_effects([pe.withStroke(linewidth=2, foreground='black')])

    def _calculate_scale_params(self, crs, extent, unit):
        xmin, xmax, ymin, ymax = extent
        meters_per_unit = 111320 * math.cos(math.radians((ymin + ymax) / 2)) if crs.IsGeographic() else (
                    crs.GetLinearUnits() or 1.0)
        target_width_m = (xmax - xmin) * meters_per_unit * 0.2
        magnitude = 10 ** math.floor(math.log10(target_width_m))
        lead = target_width_m / magnitude
        val = 1 if lead < 2 else (2 if lead < 5 else 5)
        rounded_m = val * magnitude
        return rounded_m / meters_per_unit, f"{int(rounded_m / 1000)} km" if unit == 'km' else f"{int(rounded_m)} m"


class Graticule(MapComponent):
    """
    经纬网绘制组件。
    已更新：支持 padding 参数调整标签距离。
    """

    def draw(self, transformer, extent, style_name='default',
             interval=None, font_size=None, font_family=None,
             label_sides=['bottom', 'left'],
             label_rotation=0,
             padding=0.01):
        """
        Args:
            padding (float): 标签距离图廓的间距，相对于地图长宽的比例。
                             例如 0.02 表示 2% 的间距。
        """
        style = GRID_STYLES.get(style_name, GRID_STYLES['default'])
        lon_min, lon_max, lat_min, lat_max = transformer.get_wgs84_bounds(extent)

        final_font = font_family if font_family else style.get('font_family', 'Arial')
        final_size = font_size if font_size is not None else style['label_size']

        if label_sides == 'all' or (isinstance(label_sides, (list, tuple)) and 'all' in label_sides):
            sides = ['top', 'bottom', 'left', 'right']
        elif isinstance(label_sides, str):
            sides = [label_sides]
        else:
            sides = label_sides

        rots = {'top': 0, 'bottom': 0, 'left': 0, 'right': 0}
        if isinstance(label_rotation, (int, float)):
            rots = {k: label_rotation for k in rots}
        elif isinstance(label_rotation, dict):
            rots.update(label_rotation)

        width_span = extent[1] - extent[0]
        height_span = extent[3] - extent[2]
        pad_x = width_span * padding
        pad_y = height_span * padding

        if interval is not None:
            if isinstance(interval, (list, tuple)):
                lon_step, lat_step = interval[0], interval[1]
            else:
                lon_step = lat_step = interval
        else:
            def get_step(span, n=style.get('density', 4)):
                raw = span / n
                if raw == 0: return 1
                mag = 10 ** math.floor(math.log10(raw))
                lead = raw / mag
                if lead < 2: return 1 * mag
                elif lead < 5: return 2 * mag
                else: return 5 * mag

            lon_step = get_step(lon_max - lon_min)
            lat_step = get_step(lat_max - lat_min)

        def get_precision(step):
            if step >= 1: return 0
            return max(0, -int(math.floor(math.log10(step))))

        lon_precision = get_precision(lon_step)
        lat_precision = get_precision(lat_step)

        lons = np.arange(math.floor(lon_min / lon_step) * lon_step, lon_max + lon_step, lon_step)
        lats = np.arange(math.floor(lat_min / lat_step) * lat_step, lat_max + lat_step, lat_step)

        for lon in lons:
            if lon < lon_min or lon > lon_max: continue
            lat_samples = np.linspace(lat_min, lat_max, 50)
            line_points = [transformer.transform_point_inverse(lon, lat) for lat in lat_samples]
            xs, ys = zip(*line_points)

            self.ax.plot(xs, ys, color=style['color'], linestyle=style['linestyle'],
                         linewidth=style['linewidth'], alpha=style['alpha'], zorder=5)

            valid_x = xs[len(xs) // 2]
            if extent[0] < valid_x < extent[1]:
                text_str = self._format_lon(lon, lon_precision)

                if 'bottom' in sides:
                    self.ax.text(
                        valid_x, extent[2] - pad_y, text_str,
                        ha='center', va='top',
                        fontsize=final_size, fontfamily=final_font,
                        fontweight=style.get('font_weight', 'normal'),
                        color=style['label_color'], zorder=5,
                        rotation=rots['bottom']
                    )

                if 'top' in sides:
                    self.ax.text(
                        valid_x, extent[3] + pad_y, text_str,
                        ha='center', va='bottom',
                        fontsize=final_size, fontfamily=final_font,
                        fontweight=style.get('font_weight', 'normal'),
                        color=style['label_color'], zorder=5,
                        rotation=rots['top']
                    )

        for lat in lats:
            if lat < lat_min or lat > lat_max: continue
            lon_samples = np.linspace(lon_min, lon_max, 50)
            line_points = [transformer.transform_point_inverse(lon, lat) for lon in lon_samples]
            xs, ys = zip(*line_points)

            self.ax.plot(xs, ys, color=style['color'], linestyle=style['linestyle'],
                         linewidth=style['linewidth'], alpha=style['alpha'], zorder=5)

            valid_y = ys[len(ys) // 2]
            if extent[2] < valid_y < extent[3]:
                text_str = self._format_lat(lat, lat_precision)

                if 'left' in sides:
                    self.ax.text(
                        extent[0] - pad_x, valid_y, text_str,
                        ha='right', va='center',
                        fontsize=final_size, fontfamily=final_font,
                        fontweight=style.get('font_weight', 'normal'),
                        color=style['label_color'], zorder=5,
                        rotation=rots['left']
                    )

                if 'right' in sides:
                    self.ax.text(
                        extent[1] + pad_x, valid_y, text_str,
                        ha='left', va='center',
                        fontsize=final_size, fontfamily=final_font,
                        fontweight=style.get('font_weight', 'normal'),
                        color=style['label_color'], zorder=5,
                        rotation=rots['right']
                    )

    def _format_lon(self, val, precision):
        abs_val = abs(val)
        suffix = "E" if val >= 0 else "W"
        if np.isclose(val, 0): return "0°"
        if abs_val.is_integer(): return f"{int(abs_val)}°{suffix}"
        return f"{{:.{precision}f}}°{{}}".format(abs_val, suffix)

    def _format_lat(self, val, precision):
        abs_val = abs(val)
        suffix = "N" if val >= 0 else "S"
        if np.isclose(val, 0): return "0°"
        if abs_val.is_integer(): return f"{int(abs_val)}°{suffix}"
        return f"{{:.{precision}f}}°{{}}".format(abs_val, suffix)