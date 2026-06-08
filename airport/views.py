from django.shortcuts import render
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
from airport.serializers import (
    AirportSerializer,
    RouteSerializer,
    CrewSerializer,
    AirplaneSerializer,
    AirplaneTypeSerializer,
    FlightSerializer,
    OrderSerializer,
    TicketSerializer
)


class AirportViewSet(ModelViewSet):
    serializer_class = AirportSerializer
    queryset = Airport.objects.all()


class RouteViewSet(ModelViewSet):
    serializer_class = RouteSerializer
    queryset = Route.objects.select_related("source", "destination")


class CrewViewSet(ModelViewSet):
    serializer_class = CrewSerializer
    queryset = Crew.objects.all()


class AirplaneTypeViewSet(ModelViewSet):
    serializer_class = AirplaneTypeSerializer
    queryset = AirplaneType.objects.all()


class AirplaneViewSet(ModelViewSet):
    serializer_class = AirplaneSerializer
    queryset = Airplane.objects.select_related("airplane_type")


class FlightViewSet(ModelViewSet):
    serializer_class = FlightSerializer
    queryset = Flight.objects.select_related("route", "airplane")


class OrderViewSet(ModelViewSet):
    serializer_class = OrderSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user.id).select_related("user")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TicketViewSet(ModelViewSet):
    serializer_class = TicketSerializer
    queryset = Ticket.objects.select_related("flight", "order")

