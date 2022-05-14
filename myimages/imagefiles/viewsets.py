# from rest_framework import mixins, viewsets
from django.views import View
from myimages.rest import LargeImageFileDetailMixin
from myimages.imagefiles import models


class ImageFileDetailViewSet(
    # mixins.ListModelMixin,
    # viewsets.GenericViewSet,
    LargeImageFileDetailMixin,
    View
):
    queryset = models.ImageFile.objects.all()
    serializer_class = models.ImageFileSerializer

    # for `django-large-image`: the name of the image FileField on your model
    FILE_FIELD_NAME = 'file'
