from django.db import transaction
from rest_framework import serializers
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


class AirportSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airport
        fields = ["name", "closest_big_city"]


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(slug_field="name", read_only=True)
    destination = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Route
        fields = ["source", "destination", "distance"]


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["first_name", "last_name"]


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ["name"]


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True
    )

    class Meta:
        model = Airplane
        fields = [
            "name",
            "rows",
            "seats_in_row",
            "airplane_type"
        ]


class FlightSerializer(serializers.ModelSerializer):
    route = RouteSerializer()
    airplane = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True
    )

    class Meta:
        model = Flight
        fields = [
            "route",
            "airplane",
            "departure_time",
            "arrival_time"
        ]


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            "row",
            "seat",
            "flight",
            "order"
        ]

class TicketReadSerializer(TicketSerializer):
    flight = FlightSerializer(read_only=True)


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            "row",
            "seat",
            "flight",
        ]


class OrderReadSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    tickets = TicketReadSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "created_at",
            "user",
            "tickets",
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    tickets = TicketCreateSerializer(many=True)

    class Meta:
        model = Order
        fields = ["tickets"]

    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
        return order