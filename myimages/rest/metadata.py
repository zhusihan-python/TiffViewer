import io
import json
import pathlib

# from drf_yasg.utils import swagger_auto_schema
# from rest_framework.decorators import action
# from rest_framework.exceptions import Exception, ValidationError
# from rest_framework.request import Request
# from rest_framework.response import Response
from django.http import HttpRequest as Request
from django.http import HttpResponse as Response

from myimages.rest import tilesource
# import params
from myimages.rest.base import LargeImageMixinBase

try:
    import tifftools
    from tifftools.exceptions import TifftoolsError
except ImportError:  # pragma: no cover
    tifftools = None
    TifftoolsError = None

# metadata_summary = 'Returns tile metadata.'
# metadata_parameters = params.BASE
# metadata_internal_summary = 'Returns additional known metadata about the tile source.'
# metadata_internal_parameters = params.BASE
# bands_summary = 'Returns bands information.'
# bands_parameters = params.BASE
# band_summary = 'Returns single band information.'
# band_parameters = params.BASE + [params.band]
# tiffdump_summary = 'Returns tifftools tiffdump JSON. This will raise a `ValidationError` if the image is not a Tiff.'


class MetaDataMixin(LargeImageMixinBase):
    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary=metadata_summary,
    #     manual_parameters=metadata_parameters,
    # )
    # @action(detail=False)
    def metadata(self, request: Request, pk: int = None) -> Response:
        source = self.get_tile_source(request, pk, style=False)
        metadata = tilesource.get_metadata(source)
        return Response(metadata)

    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary=metadata_internal_summary,
    #     manual_parameters=metadata_internal_parameters,
    # )
    # @action(detail=False)
    def metadata_internal(self, request: Request, pk: int = None) -> Response:
        source = self.get_tile_source(request, pk, style=False)
        metadata = tilesource.get_metadata_internal(source)
        return Response(metadata)

    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary=bands_summary,
    #     manual_parameters=bands_parameters,
    # )
    # @action(detail=False)
    def bands(self, request: Request, pk: int = None) -> Response:
        source = self.get_tile_source(request, pk, style=False)
        metadata = source.getBandInformation()
        return Response(metadata)

    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary=bands_summary,
    #     manual_parameters=band_parameters,
    # )
    # @action(detail=False)
    def band(self, request: Request, pk: int = None) -> Response:
        band = int(self.get_query_param(request, 'band', 1))
        source = self.get_tile_source(request, pk, style=False)
        metadata = source.getOneBandInformation(band)
        return Response(metadata)

    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary=tiffdump_summary,
    # )
    # @action(detail=False)
    def tiffdump(self, request: Request, pk: int = None) -> Response:
        if tifftools is None:  # pragma: no cover
            raise Exception('`tifftools` is not installed on the server.')
        source = self.get_tile_source(request, pk, style=False)
        # This will only work for local files (path on disk)
        path = source._getLargeImagePath()
        try:
            if not pathlib.Path(path).exists():
                raise OSError  # pragma: no cover
        except OSError:
            raise Exception(
                'The image path is not local and tifftools will not be able to open this image.'
            )
        output = io.StringIO()
        try:
            tifftools.tiff_dump(path, dest=output, outformat='json')
        except (TifftoolsError, OSError) as e:
            raise Exception(str(e))
        output.seek(0)
        return Response(json.loads(output.read()))


class MetaDataDetailMixin(MetaDataMixin):
    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary=metadata_summary,
    #     manual_parameters=metadata_parameters,
    # )
    # @action(detail=True)
    def metadata(self, request: Request, pk: int = None) -> Response:
        return super().metadata(request, pk)

    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary=metadata_internal_summary,
    #     manual_parameters=metadata_internal_parameters,
    # )
    # @action(detail=True)
    def metadata_internal(self, request: Request, pk: int = None) -> Response:
        return super().metadata_internal(request, pk)

    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary=bands_summary,
    #     manual_parameters=bands_parameters,
    # )
    # @action(detail=True)
    def bands(self, request: Request, pk: int = None) -> Response:
        return super().bands(request, pk)

    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary=bands_summary,
    #     manual_parameters=band_parameters,
    # )
    # @action(detail=True)
    def band(self, request: Request, pk: int = None) -> Response:
        return super().band(request, pk)

    # @swagger_auto_schema(
    #     method='GET',
    #     operation_summary=tiffdump_summary,
    # )
    # @action(detail=True)
    def tiffdump(self, request: Request, pk: int = None) -> Response:
        return super().tiffdump(request, pk)
