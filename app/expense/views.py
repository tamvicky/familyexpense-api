from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import viewsets, mixins, status,\
                           authentication, permissions
from django.db.models import Q
from django.db.models import Sum

from core.models import Category, UserProfile, ExpenseRecord
from expense import serializers


class CategoryViewSet(viewsets.ModelViewSet):
    """Manage category in the databases"""
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = Category.objects.all()

    def get_queryset(self):
        """
        Return categories which is public or belongs to authenticated
        user & family
        """
        userprofile = UserProfile.objects.get(user=self.request.user)
        return self.queryset.filter(Q(isPublic=True) |
                                    Q(user=self.request.user) |
                                    Q(family=userprofile.family))

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return serializers.CateogryListSerializer
        else:
            return serializers.CateogryCreateSerializer

    def perform_create(self, serializer):
        """Create a new category"""
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Update category"""
        serializer.save()


class RecordViewSet(viewsets.ModelViewSet):
    """Manage expense record in the databases"""
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ExpenseRecord.objects.all()

    def get_queryset(self):
        """
        Retrieve the expense records for the authenticated user
        Query Params:
            - type: personal | family | all (default)
            - date_range: start_date,end_date in yyyy-mm-dd format
            - year: int
            - month: int
            - day: int
            - category: category_id
        """
        queryset = self.queryset

        # filter by type
        type = self.request.query_params.get('type')
        if type == 'personal':
            queryset = queryset.filter(user=self.request.user)\
                        .filter(family__isnull=True)
        elif type == 'family':
            userprofile = UserProfile.objects.get(user=self.request.user)
            queryset = queryset.filter(family=userprofile.family)
        else:
            queryset = queryset.filter(user=self.request.user)

        # filter by date range
        date_range = self.request.query_params.get('date_range')
        if date_range:
            dates = date_range.split(",")
            if (len(dates) == 2):
                queryset = queryset.filter(date__range=dates)

        # filter by day/month/year
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        day = self.request.query_params.get('day')

        if day and month and year:
            queryset = queryset.filter(date__year=year,
                                       date__month=month,
                                       date__day=day)
        elif month and year:
            queryset = queryset.filter(date__year=year,
                                       date__month=month)
        elif year:
            queryset = queryset.filter(date__year=year)

        # filter by day/month/year
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        return queryset.order_by('-date', '-id')

    def get_serializer_class(self):
        if self.action == 'upload_image':
            return serializers.RecordImageSerializer
        elif self.request.method == 'GET':
            return serializers.ExpenseRecordListSerializer
        else:
            return serializers.ExpenseRecordDetailsSerializer

    def perform_create(self, serializer):
        """Create a new record"""
        serializer.is_valid(raise_exception=True)
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        """Update record"""
        serializer.is_valid(raise_exception=True)
        serializer.save()

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a record"""
        record = self.get_object()
        serializer = self.get_serializer(
            record,
            data=request.data
        )

        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class RecordSummaryViewSet(viewsets.GenericViewSet,
                           mixins.ListModelMixin,):
    """Expense Record summary in the databases"""
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    queryset = ExpenseRecord.objects.all()
    serializer_class = serializers.ExpenseRecordSummarySerializer

    def get_queryset(self):
        """
        Retrieve the expense records for the authenticated user
        Query Params:
            - type: personal | family | all (default)
            - date_range: start_date,end_date in yyyy-mm-dd format
            - year: int
            - month: int
            - day: int
            - category: category_id
        """
        queryset = self.queryset

        # filter by type
        type = self.request.query_params.get('type')
        if type == 'personal':
            queryset = queryset.filter(user=self.request.user)\
                        .filter(family__isnull=True)
        elif type == 'family':
            userprofile = UserProfile.objects.get(user=self.request.user)
            queryset = queryset.filter(family=userprofile.family)
        else:
            queryset = queryset.filter(user=self.request.user)

        # filter by date range
        date_range = self.request.query_params.get('date_range')
        if date_range:
            dates = date_range.split(",")
            if (len(dates) == 2):
                queryset = queryset.filter(date__range=dates)

        # filter by day/month/year
        year = self.request.query_params.get('year')
        month = self.request.query_params.get('month')
        day = self.request.query_params.get('day')

        if day and month and year:
            queryset = queryset.filter(date__year=year,
                                       date__month=month,
                                       date__day=day)
        elif month and year:
            queryset = queryset.filter(date__year=year,
                                       date__month=month)
        elif year:
            queryset = queryset.filter(date__year=year)

        # filter by day/month/year
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)

        queryset = queryset.values(
            'category__id',
            'category__name').annotate(total_amount=Sum('amount'))
        return queryset.order_by('category__id')
