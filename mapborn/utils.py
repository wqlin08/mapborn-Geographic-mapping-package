from osgeo import osr


class GeoTransformer:
    def __init__(self, source_crs):
        self.source_crs = source_crs
        self.source_crs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

        self.target_crs = osr.SpatialReference()
        self.target_crs.ImportFromEPSG(4326)  # WGS84
        self.target_crs.SetAxisMappingStrategy(osr.OAMS_TRADITIONAL_GIS_ORDER)

        self._to_wgs84 = osr.CoordinateTransformation(self.source_crs, self.target_crs)
        self._to_source = osr.CoordinateTransformation(self.target_crs, self.source_crs)

    def transform_point(self, x, y):
        """Source -> WGS84 (Lon, Lat)"""
        res = self._to_wgs84.TransformPoint(x, y)
        return res[0], res[1]

    def transform_point_inverse(self, lon, lat):
        """WGS84 (Lon, Lat) -> Source (X, Y)"""
        res = self._to_source.TransformPoint(lon, lat)
        return res[0], res[1]

    def get_wgs84_bounds(self, extent):
        """获取 Extent 对应的经纬度范围 [min_lon, max_lon, min_lat, max_lat]"""
        xmin, xmax, ymin, ymax = extent
        # 采样四个角点
        corners = [
            self.transform_point(xmin, ymin),
            self.transform_point(xmin, ymax),
            self.transform_point(xmax, ymin),
            self.transform_point(xmax, ymax)
        ]
        lons = [c[0] for c in corners]
        lats = [c[1] for c in corners]
        return [min(lons), max(lons), min(lats), max(lats)]