import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import PatchCollection, LineCollection
from matplotlib.path import Path
import numpy as np
from osgeo import osr, ogr
from .core import RasterData, VectorData
from .utils import GeoTransformer
from .components import NorthArrow, ScaleBar, Graticule
from .axes import add_styled_colorbar


class Map:
    """
    Mapborn 主绘图类。

    提供类似于 plt.show() 的极简体验，同时具备地理绘图所需的坐标转换和组件支持。
    支持自动识别栅格 (GeoTIFF) 和矢量 (Shapefile) 数据作为底图。
    """

    def __init__(self, filepath, figsize=(10, 10), nodata=None):
        """
        初始化地图对象。

        Args:
            filepath (str): 数据路径。
                - 若为栅格 (.tif)，将作为底图并渲染。
                - 若为矢量 (.shp)，将作为底图并绘制轮廓。
            figsize (tuple): 画布大小 (宽, 高)，单位英寸。默认 (10, 10)。
            nodata (float): 强制指定的 NoData 值。若为 None 则尝试自动读取。
        """
        self.fig, self.ax = plt.subplots(figsize=figsize)
        self.base_data = None
        self.data_type = None
        self._image_handle = None
        self.transformer = None

        try:
            self.base_data = RasterData(filepath, nodata=nodata)
            self.data_type = 'raster'
        except Exception:
            try:
                self.base_data = VectorData(filepath)
                self.data_type = 'vector'
            except Exception:
                raise ValueError(f"无法识别文件格式或打开失败: {filepath}")

        self.transformer = GeoTransformer(self.base_data.crs)
        self._render_base_map()

        xmin, xmax, ymin, ymax = self.base_data.extent
        self.ax.set_xlim(xmin, xmax)
        self.ax.set_ylim(ymin, ymax)
        self.ax.set_aspect('equal')
        self.ax.axis('off')

    def _render_base_map(self):
        if self.data_type == 'raster':
            self._image_handle = self.ax.imshow(
                self.base_data.data, extent=self.base_data.extent,
                cmap='terrain', interpolation='nearest'
            )
        elif self.data_type == 'vector':
            self._plot_vector_layer(self.base_data, facecolor='#eeeeee', edgecolor='black')

    def set_title(self, title, fontsize=16, fontfamily=None):
        """
        设置地图标题。

        Args:
            title (str): 标题文本。
            fontsize (int): 字体大小。
            fontfamily (str): 字体名称 (如 'Arial', 'SimHei')。
        """
        kwargs = {'fontsize': fontsize}
        if fontfamily:
            kwargs['fontfamily'] = fontfamily
        self.ax.set_title(title, **kwargs)

    def set_cmap(self, cmap_name):
        """
        设置栅格数据的色带 (仅对栅格底图有效)。

        Args:
            cmap_name (str): Matplotlib 色带名称。
                常用: 'viridis', 'plasma', 'terrain', 'gray', 'RdYlBu', 'Spectral'。
        """
        if self._image_handle:
            self._image_handle.set_cmap(cmap_name)

    def set_clim(self, vmin=None, vmax=None):
        """
        设置色带的数据显示范围 (仅对栅格底图有效)。

        Args:
            vmin (float): 最小值。
            vmax (float): 最大值。
        """
        if self._image_handle:
            self._image_handle.set_clim(vmin=vmin, vmax=vmax)

    def add_north_arrow(self, location='top-right', style='nice', size=0.08,
                        font_size=None, font_family=None):
        """
        添加指北针组件。

        Args:
            location (str/tuple): 组件位置。
                - 字符串: 'top-right', 'top-left', 'bottom-right', 'bottom-left'。
                - 元组: (x, y) 相对坐标 (0.0~1.0)。
            style (str): 指北针样式。
                - 'nice': 黑白分体样式 (默认)。
                - 'simpleB': 黑色实心箭头。
                - 'simpleW': 白色实心箭头。
                - 'arrow_line': 线条样式。
            size (float): 指北针高度占画布高度的比例 (默认 0.08)。
            font_size (float): 'N' 标签字体大小。
            font_family (str): 字体名称。
        """
        arrow = NorthArrow(self.ax)
        arrow.draw(location=location, size=size, style_name=style,
                   font_size=font_size, font_family=font_family)

    def add_scale_bar(self, location='bottom-left', unit='km', style='blocks',
                      font_size=None, font_family=None):
        """
        添加比例尺组件。
        会自动根据底图坐标系计算真实地理距离。

        Args:
            location (str/tuple): 组件位置 (同上)。
            unit (str): 距离单位。
                - 'km': 千米 (默认)。
                - 'm': 米。
            style (str): 比例尺样式。
                - 'blocks': 黑白方块交替 (默认)。
                - 'line-black': 黑色线段。
                - 'line-white': 白色线段。
        """
        bar = ScaleBar(self.ax)
        bar.draw(self.base_data.crs, self.base_data.extent, location=location, unit=unit,
                 style_name=style, font_size=font_size, font_family=font_family)

    def add_grid(self, style='default', interval=None, font_size=None, font_family=None,
                 label_sides=['bottom', 'left'], label_rotation=0,
                 padding=0.01):
        """
        添加经纬网 (Graticule) 及坐标标注。

        Args:
            style (str): 网格样式 (目前仅支持 'default')。
            interval (float/tuple): 网格经纬度间隔。None 表示自动计算。
            font_size (float): 标注字体大小。
            label_sides (list/str): 显示标注的方向。
                - 列表: ['bottom', 'left'] (默认)。
                - 字符串: 'all' (显示四周)。
            label_rotation (float/dict): 标注旋转角度。
            padding (float): 标注距离图廓的间距 (相对画布比例，默认 0.01)。
        """
        grid = Graticule(self.ax)
        grid.draw(self.transformer, self.base_data.extent, style_name=style,
                  interval=interval, font_size=font_size, font_family=font_family,
                  label_sides=label_sides, label_rotation=label_rotation,
                  padding=padding)

    def add_colorbar(self, location='right', width="5%", pad="2%", extend='neither',
                     label="", label_size=12, tick_size=10, color='black',
                     font_family='Arial'):
        """
        添加色带 (Colorbar)。
        需确保底图为栅格数据。

        Args:
            location (str): 位置 ('right', 'left', 'bottom', 'top')。
            width (str): 色带宽度/高度 (如 "5%")。
            pad (str/float): 距离主图的间距 (如 "2%" 或 0.1)。
            extend (str): 尖角样式 ('neither', 'both', 'min', 'max')。
            label (str): 色带标签文本 (如单位)。
            color (str): 文本和边框颜色。
        """
        if self._image_handle is None:
            print("警告: 当前未绘制栅格数据，无法添加色带。")
            return

        add_styled_colorbar(
            fig=self.fig,
            mappable=self._image_handle,
            ax=self.ax,
            location=location,
            width=width,
            pad=pad,
            extend=extend,
            label=label,
            label_size=label_size,
            tick_size=tick_size,
            color=color,
            font_family=font_family
        )

    def add_vector(self, filepath, **kwargs):
        """
        叠加额外的矢量图层。

        Args:
            filepath (str): 矢量文件路径 (.shp 等)。
            **kwargs: Matplotlib 绘图参数。
                - facecolor (fc): 填充色 (如 'none')。
                - edgecolor (ec): 边框色 (如 'red')。
                - linewidth (lw): 线宽。
                - alpha: 透明度。
        """
        vector = VectorData(filepath)
        target_crs = self.base_data.crs
        source_crs = vector.crs

        coord_trans = None
        if not source_crs.IsSame(target_crs):
            coord_trans = osr.CoordinateTransformation(source_crs, target_crs)

        self._plot_vector_layer(vector, transform=coord_trans, **kwargs)

    def _plot_vector_layer(self, vector_obj, transform=None, **kwargs):
        layer = vector_obj.layer
        patches = []
        lines = []
        points = []

        for feature in layer:
            geom = feature.GetGeometryRef()
            if not geom: continue
            if transform:
                geom = geom.Clone()
                geom.Transform(transform)
            self._parse_geometry(geom, patches, lines, points)

        if patches:
            poly_kwargs = {k: v for k, v in kwargs.items() if k not in []}
            collection = PatchCollection(patches, match_original=False, **kwargs)
            self.ax.add_collection(collection)

        if lines:
            lc = LineCollection(lines, **kwargs)
            self.ax.add_collection(lc)

        if points:
            xs, ys = zip(*points)
            self.ax.scatter(xs, ys, **kwargs)

    def _parse_geometry(self, geom, patches_list, lines_list, points_list):
        gt = geom.GetGeometryType()

        if gt == ogr.wkbPoint or gt == ogr.wkbPoint25D:
            points_list.append((geom.GetX(), geom.GetY()))

        elif gt == ogr.wkbLineString or gt == ogr.wkbLineString25D:
            pts = geom.GetPoints()
            lines_list.append([p[:2] for p in pts])

        elif gt == ogr.wkbPolygon or gt == ogr.wkbPolygon25D:
            ring_codes = []
            ring_verts = []
            for i in range(geom.GetGeometryCount()):
                ring = geom.GetGeometryRef(i)
                pts = ring.GetPoints()
                if not pts: continue
                vert = [p[:2] for p in pts]
                ring_verts.extend(vert)
                codes = [Path.MOVETO] + [Path.LINETO] * (len(vert) - 2) + [Path.CLOSEPOLY]
                ring_codes.extend(codes)
            if ring_verts:
                path = Path(ring_verts, ring_codes)
                patches_list.append(mpatches.PathPatch(path))

        elif gt in [ogr.wkbMultiPolygon, ogr.wkbMultiLineString, ogr.wkbMultiPoint, ogr.wkbGeometryCollection,
                    ogr.wkbMultiPolygon25D, ogr.wkbMultiLineString25D, ogr.wkbMultiPoint25D,
                    ogr.wkbGeometryCollection25D]:
            for i in range(geom.GetGeometryCount()):
                sub_geom = geom.GetGeometryRef(i)
                self._parse_geometry(sub_geom, patches_list, lines_list, points_list)

    def show(self):
        """显示交互式绘图窗口。"""
        plt.show()

    def save(self, path, dpi=300):
        """
        保存地图为图片。

        Args:
            path (str): 输出路径 (如 'map.png', 'map.pdf')。
            dpi (int): 分辨率，默认 300。
        """
        self.fig.savefig(path, dpi=dpi, bbox_inches='tight', pad_inches=0.1)

    def __del__(self):
        if hasattr(self, 'base_data') and self.base_data:
            self.base_data.close()