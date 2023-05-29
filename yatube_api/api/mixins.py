from rest_framework import mixins, viewsets


class CreateListFollowViewSet(mixins.CreateModelMixin,
                              mixins.ListModelMixin,
                              viewsets.GenericViewSet):
    pass
