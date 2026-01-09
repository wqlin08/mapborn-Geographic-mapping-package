import sys
import numpy as np
from osgeo import gdal, osr, ogr
gdal.UseExceptions()
ogr.UseExceptions()


class RasterData:
    """
    栅格数据封装类。
    """

    def __init__(self, filepath, nodata=None):
        self.filepath = filepath
        self._dataset = None
        self._array = None
        self._geotransform = None
        self._projection = None
        self._user_nodata = nodata
        self._file_nodata = None
        self._final_nodata = None

        self._load_data()

    def _load_data(self):
        try:
            self._dataset = gdal.Open(self.filepath, gdal.GA_ReadOnly)
        except RuntimeError as e:
            raise FileNotFoundError(f"无法打开栅格文件: {self.filepath}\nGDAL错误: {str(e)}")

        proj_wkt = self._dataset.GetProjectionRef()
        if not proj_wkt:
            # 尝试从 GCPs 获取
            if self._dataset.GetGCPCount() > 0:
                proj_wkt = self._dataset.GetGCPProjection()

        if not proj_wkt:
            raise ValueError(f"输入栅格缺失坐标系信息 (CRS)。\n文件: {self.filepath}")

        self._projection = osr.SpatialReference()
        self._projection.ImportFromWkt(proj_wkt)

        self._geotransform = self._dataset.GetGeoTransform()
        band = self._dataset.GetRasterBand(1)
        raw_array = band.ReadAsArray()

        self._file_nodata = band.GetNoDataValue()
        self._final_nodata = self._user_nodata if self._user_nodata is not None else self._file_nodata

        if self._final_nodata is not None:
            if np.issubdtype(raw_array.dtype, np.floating):
                self._array = np.ma.masked_values(raw_array, self._final_nodata, copy=False)
                self._array = np.ma.masked_invalid(self._array)
            else:
                self._array = np.ma.masked_equal(raw_array, self._final_nodata, copy=False)
        else:
            self._array = np.ma.array(raw_array)

    @property
    def data(self):
        return self._array

    @property
    def extent(self):
        """[xmin, xmax, ymin, ymax]"""
        gt = self._geotransform
        rows, cols = self._array.shape
        xmin = gt[0]
        xmax = gt[0] + (cols * gt[1])
        ymax = gt[3]
        ymin = gt[3] + (rows * gt[5])
        return [xmin, xmax, ymin, ymax]

    @property
    def crs(self):
        return self._projection

    def close(self):
        self._dataset = None


class VectorData:
    """
    矢量数据封装类
    """

    def __init__(self, filepath):
        self.filepath = filepath
        self._ds = None
        self._layer = None
        self._crs = None
        self._extent = None
        self._load_data()

    def _load_data(self):
        try:
            self._ds = ogr.Open(self.filepath)
        except RuntimeError as e:
            raise FileNotFoundError(f"无法打开矢量文件: {self.filepath}\n错误: {str(e)}")

        if self._ds is None:
            raise FileNotFoundError(f"无法打开矢量文件 (返回 None): {self.filepath}")

        self._layer = self._ds.GetLayer()

        self._crs = self._layer.GetSpatialRef()
        if not self._crs:
            raise ValueError(f"输入矢量缺失坐标系信息 (CRS)。\n文件: {self.filepath}")

        self._extent = self._layer.GetExtent()

    @property
    def layer(self):
        """返回 OGR Layer 对象"""
        self._layer.ResetReading()
        return self._layer

    @property
    def crs(self):
        return self._crs

    @property
    def extent(self):
        """[xmin, xmax, ymin, ymax]"""
        return [self._extent[0], self._extent[1], self._extent[2], self._extent[3]]

    def close(self):
        self._ds = None