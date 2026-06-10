from logging import raiseExceptions

from django.db.models.sql import query
from django.shortcuts import render
from django.views.generic import detail
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

import user
from airport.models import (
    Airport,
    Route,
    Crew,
    AirplaneType,
    Airplane,
    Flight,
    Order,
    Ticket
)
from airport.permission import IsAdminOrReadOnly
from airport.serializers import (
    AirportSerializer,
    RouteSerializer,
    CrewSerializer,
    AirplaneSerializer,
    AirplaneTypeSerializer,
    FlightSerializer,
    TicketSerializer, OrderCreateSerializer, OrderReadSerializer, FlightListSerializer,
    FlightDetailSerializer, AirplaneImageSerializer, TicketDetailSerializer, TicketListSerializer
)


class AirportViewSet(ModelViewSet):
    serializer_class = AirportSerializer
    queryset = Airport.objects.all()
    permission_classes = [IsAdminOrReadOnly]

class RouteViewSet(ModelViewSet):
    serializer_class = RouteSerializer
    queryset = Route.objects.select_related("source", "destination")
    permission_classes = [IsAdminOrReadOnly]

class CrewViewSet(ModelViewSet):
    serializer_class = CrewSerializer
    queryset = Crew.objects.all()
    permission_classes = [IsAdminOrReadOnly]


class AirplaneTypeViewSet(ModelViewSet):
    serializer_class = AirplaneTypeSerializer
    queryset = AirplaneType.objects.all()
    permission_classes = [IsAdminOrReadOnly]


class AirplaneViewSet(ModelViewSet):
    serializer_class = AirplaneSerializer
    queryset = Airplane.objects.select_related("airplane_type")
    permission_classes = [IsAdminOrReadOnly]

    @staticmethod
    def get_int_param(ids):
        return [int(number) for number in ids.split(",")]

    def get_queryset(self):
        name = self.request.query_params.get("name")
        airplane_type = self.request.query_params.get("airplane_type")
        
        queryset = self.queryset

        if name:
            queryset = queryset.filter(
                name__icontains=name
            )
        if airplane_type:
            queryset = queryset.filter(
                airplane_type__name__icontains=airplane_type
            )
        return queryset

    def get_serializer_class(self):
        if self.action == "upload_image":
            return AirplaneImageSerializer
        return AirplaneSerializer

    @action(
        methods=["POST"],
        detail=True,
        url_path="upload-image"
    )
    def upload_image(self, request, pk):
        airplane = self.get_object()
        serializer = self.get_serializer(
            airplane,
            data=request.data,
            partial=True
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)



class FlightViewSet(ModelViewSet):
    serializer_class = FlightSerializer
    queryset = Flight.objects.select_related("route", "airplane")
    permission_classes = [IsAdminOrReadOnly]

    @staticmethod
    def get_int_param(ids):
        return [int(number) for number in ids.split(",")]

    def get_queryset(self):
        source = self.request.query_params.get("source")
        destination = self.request.query_params.get("destination")
        airplane = self.request.query_params.get("airplane")
        date = self.request.query_params.get("date")

        queryset = self.queryset

        if source:
            ids_source = self.get_int_param(source)
            queryset = queryset.filter(
                route__source__id__in=ids_source
            ).distinct()
        if destination:
            ids_destination = self.get_int_param(destination)
            queryset = queryset.filter(
                route__destination__id__in=ids_destination
            ).distinct()
        if airplane:
            ids_airplane = self.get_int_param(airplane)
            queryset = queryset.filter(
                airplane__id__in=ids_airplane
            ).distinct()
        if date:
            queryset = queryset.filter(
                departure_time__date=date
            ).distinct()
        return queryset

    def get_serializer_class(self):
        if self.action == "list":
            return FlightListSerializer
        if self.action == "retrieve":
            return FlightDetailSerializer
        return FlightSerializer


class OrderPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"
    max_page_size = 100


class OrderViewSet(ModelViewSet):
    pagination_class = OrderPagination

    def get_queryset(self):
        return (
            Order.objects
            .filter(user=self.request.user.id)
            .select_related("user")
            .prefetch_related(
                "tickets__flight__route__source",
                "tickets__flight__route__destination",
                "tickets__flight__airplane"
            )
        )

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return OrderReadSerializer
        return OrderCreateSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketViewSet(ModelViewSet):
    serializer_class = TicketSerializer
    queryset = Ticket.objects.select_related("flight", "order")

    def get_serializer_class(self):
        if self.action == "list":
            return TicketListSerializer
        if self.action == "retrieve":
            return TicketDetailSerializer
        return TicketSerializer