from django.http import HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
# from drf_yasg.utils import swagger_auto_schema
# from rest_framework.decorators import action
# from rest_framework.exceptions import ValidationError
# from rest_framework.request import Request
# from rest_framework.response import Response
from django.http import HttpRequest as Request
from django.http import HttpResponse as Response

from myimages.rest import tilesource
from myimages.rest import utilities
# from myimages.rest import params
from myimages.rest.base import CACHE_TIMEOUT, LargeImageMixinBase

# thumbnail_summary = 'Returns thumbnail of full image.'
# thumbnail_parameters = params.BASE + params.THUMBNAIL + params.STYLE
# region_summary = 'Returns region tile binary.'
# region_parameters = params.BASE + params.REGION
# pixel_summary = 'Returns single pixel.'
# pixel_parameters = params.BASE + [params.left, params.top] + params.STYLE
# histogram_summary = 'Returns histogram'
# histogram_parameters = params.BASE + params.HISTOGRAM


class DataMixin(LargeImageMixinBase):
    @method_decorator(cache_page(CACHE_TIMEOUT))
    def thumbnail(self, request: Request, pk: int = None, format: str = None) -> HttpResponse:
        encoding = tilesource.format_to_encoding(format)
        width = int(self.get_query_param(request, 'max_width', 256))
        height = int(self.get_query_param(request, 'max_height', 256))
        source = self.get_tile_source(request, pk, encoding=encoding)
        thumb_data, mime_type = source.getThumbnail(encoding=encoding, width=width, height=height)
        return HttpResponse(thumb_data, content_type=mime_type)

    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary=thumbnail_summary,
    #     manual_parameters=thumbnail_parameters,
    # )
    # @action(detail=False, url_path='thumbnail.png')
    def thumbnail_png(self, request: Request, pk: int = None) -> HttpResponse:
        return self.thumbnail(request, pk, format='png')

    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary=thumbnail_summary,
    #     manual_parameters=thumbnail_parameters,
    # )
    # @action(detail=False, url_path='thumbnail.jpeg')
    def thumbnail_jpeg(self, request: Request, pk: int = None) -> HttpResponse:
        return self.thumbnail(request, pk, format='jpeg')

    def region(self, request: Request, pk: int = None, format: str = None) -> HttpResponse:
        """Return the region tile binary from world coordinates in given EPSG.

        Note
        ----
        Use the `units` query parameter to inidicate the projection of the given
        coordinates. This can be different than the `projection` parameter used
        to open the tile source. `units` defaults to `EPSG:4326` for geospatial
        images, otherwise, must use `pixels`.

        """
        source = self.get_tile_source(request, pk)
        units = self.get_query_param(request, 'units')
        encoding = tilesource.format_to_encoding(format)
        left = float(self.get_query_param(request, 'left'))
        right = float(self.get_query_param(request, 'right'))
        top = float(self.get_query_param(request, 'top'))
        bottom = float(self.get_query_param(request, 'bottom'))
        path, mime_type = tilesource.get_region(
            source,
            left,
            right,
            bottom,
            top,
            units,
            encoding,
        )
        if not path:
            raise Exception(
                'No output generated, check that the bounds of your ROI overlap source imagery and that your `projection` and `units` are correct.'
            )
        tile_binary = open(path, 'rb')
        return HttpResponse(tile_binary, content_type=mime_type)

    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary=region_summary,
    #     manual_parameters=region_parameters,
    # )
    # @action(detail=False, url_path=r'region.tif')
    def region_tif(self, request: Request, pk: int = None) -> HttpResponse:
        return self.region(request, pk, format='tif')

    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary=region_summary,
    #     manual_parameters=region_parameters + params.STYLE,
    # )
    # @action(detail=False, url_path=r'region.png')
    def region_png(self, request: Request, pk: int = None) -> HttpResponse:
        return self.region(request, pk, format='png')

    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary=region_summary,
    #     manual_parameters=region_parameters + params.STYLE,
    # )
    # @action(detail=False, url_path=r'region.jpeg')
    def region_jpeg(self, request: Request, pk: int = None) -> HttpResponse:
        return self.region(request, pk, format='jpeg')

    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary=pixel_summary,
    #     manual_parameters=pixel_parameters,
    # )
    # @action(detail=False)
    def pixel(self, request: Request, pk: int = None) -> Response:
        left = int(self.get_query_param(request, 'left'))
        top = int(self.get_query_param(request, 'top'))
        source = self.get_tile_source(request, pk)
        metadata = source.getPixel(region={'left': left, 'top': top, 'units': 'pixels'})
        return Response(metadata)

    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary=histogram_summary,
    #     manual_parameters=histogram_parameters,
    # )
    # @action(detail=False)
    def histogram(self, request: Request, pk: int = None) -> Response:
        only_min_max = not utilities.param_nully(self.get_query_param(request, 'onlyMinMax', False))
        density = not utilities.param_nully(self.get_query_param(request, 'density', False))
        kwargs = dict(
            onlyMinMax=only_min_max,
            bins=int(self.get_query_param(request, 'bins', 256)),
            density=density,
            format=self.get_query_param(request, 'format'),
        )
        source = self.get_tile_source(request, pk, style=False)
        result = source.histogram(**kwargs)
        if 'histogram' in result:
            result = result['histogram']
            for entry in result:
                for key in {'bin_edges', 'hist', 'range'}:
                    if key in entry:
                        entry[key] = [float(val) for val in list(entry[key])]
                for key in {'min', 'max', 'samples'}:
                    if key in entry:
                        entry[key] = float(entry[key])
        return Response(result)


class DataDetailMixin(DataMixin):
    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary=thumbnail_summary,
    #     manual_parameters=thumbnail_parameters,
    # )
    # @action(detail=True, url_path='thumbnail.png')
    def thumbnail_png(self, request: Request, pk: int = None) -> HttpResponse:
        return super().thumbnail_png(request, pk)

    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary=thumbnail_summary,
    #     manual_parameters=thumbnail_parameters,
    # )
    # @action(detail=True, url_path='thumbnail.jpeg')
    def thumbnail_jpeg(self, request: Request, pk: int = None) -> HttpResponse:
        return super().thumbnail_jpeg(request, pk)

    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary=region_summary,
    #     manual_parameters=region_parameters,
    # )
    # @action(detail=True, url_path=r'region.tif')
    def region_tif(self, request: Request, pk: int = None) -> HttpResponse:
        return super().region_tif(request, pk)

    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary=region_summary,
    #     manual_parameters=region_parameters + params.STYLE,
    # )
    # @action(detail=True, url_path=r'region.png')
    def region_png(self, request: Request, pk: int = None) -> HttpResponse:
        return super().region_png(request, pk)

    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary=region_summary,
    #     manual_parameters=region_parameters + params.STYLE,
    # )
    # @action(detail=True, url_path=r'region.jpeg')
    def region_jpeg(self, request: Request, pk: int = None) -> HttpResponse:
        return super().region_jpeg(request, pk)

    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary=pixel_summary,
    #     manual_parameters=pixel_parameters,
    # )
    # @action(detail=True)
    def pixel(self, request: Request, pk: int = None) -> Response:
        return super().pixel(request, pk)

    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary=histogram_summary,
    #     manual_parameters=histogram_parameters,
    # )
    # @action(detail=True)
    def histogram(self, request: Request, pk: int = None) -> Response:
        return super().histogram(request, pk)
