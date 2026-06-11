from zoneinfo import available_timezones

from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

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
        fields = ["id", "name", "closest_big_city"]


class RouteSerializer(serializers.ModelSerializer):
    source = serializers.SlugRelatedField(slug_field="name", read_only=True)
    destination = serializers.SlugRelatedField(slug_field="name", read_only=True)

    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]


class CrewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name"]


class AirplaneTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = AirplaneType
        fields = ["id", "name"]


class AirplaneSerializer(serializers.ModelSerializer):
    airplane_type = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True
    )

    class Meta:
        model = Airplane
        fields = [
            "id",
            "name",
            "rows",
            "seats_in_row",
            "airplane_type",
            "image",
            "capacity"
        ]


class AirplaneImageUploadSerializer(serializers.ModelSerializer):
    image = serializers.ImageField()

    class Meta:
        model = Airplane
        fields = ["image"]


class AirplaneImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Airplane
        fields = ["id", "image"]


class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time"
        ]


class FlightListSerializer(FlightSerializer):
    source = serializers.CharField(
        source="route.source.name",
        read_only=True
    )
    destination = serializers.CharField(
        source="route.destination.name",
        read_only=True
    )
    airplane = serializers.SlugRelatedField(
        slug_field="name",
        read_only=True
    )

    airplane_image = serializers.ImageField(
        source="airplane.image",
        read_only=True
    )

    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = [
            "id",
            "source",
            "destination",
            "airplane",
            "airplane_image",
            "departure_time",
            "arrival_time",
            "tickets_available"
        ]

class TicketSeatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ticket
        fields = ["id", "row", "seat"]


class FlightDetailSerializer(FlightSerializer):
    route = RouteSerializer(read_only=True)
    airplane = AirplaneSerializer(read_only=True)
    taken_places = TicketSeatSerializer(
        source="tickets",
        many=True,
        read_only=True
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Flight
        fields = [
            "id",
            "route",
            "airplane",
            "departure_time",
            "arrival_time",
            "taken_places",
            "tickets_available"
        ]


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            "id",
            "row",
            "seat",
            "flight",
            "order"
        ]


class TicketListSerializer(serializers.ModelSerializer):
    flight = FlightListSerializer(read_only=True)
    order = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "row",
            "seat",
            "flight",
            "order",
        ]


class TicketDetailSerializer(serializers.ModelSerializer):
    flight = FlightSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "row",
            "seat",
            "flight"
        ]


class TicketCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        fields = [
            "id",
            "row",
            "seat",
            "flight",
        ]

    def validate(self, attrs):
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["flight"].airplane,
            ValidationError
        )

        if Ticket.objects.filter(
            row = attrs["row"],
            seat = attrs["seat"],
            flight = attrs["flight"]
        ).exists():
            raise serializers.ValidationError(
                "This seat is already taken for this flight."
            )
        return attrs





class OrderReadSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    tickets = TicketDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "created_at",
            "user",
            "tickets",
        ]


class OrderCreateSerializer(serializers.ModelSerializer):
    tickets = TicketCreateSerializer(many=True, allow_empty=False)

    class Meta:
        model = Order
        fields = [
            "id",
            "tickets",
            "created_at"
        ]
        read_only_fields = [
            "id",
            "created_at"
        ]

    def validate(self, attrs):
        tickets = attrs["tickets"]

        seen_tickets = set()

        for ticket in tickets:
            key = (
                ticket["row"],
                ticket["seat"],
                ticket["flight"].id
            )

            if key in seen_tickets:
                raise serializers.ValidationError(
                    "Data for ticket must be unique."
                )

            seen_tickets.add(key)

        return attrs


    def create(self, validated_data):
        with transaction.atomic():
            tickets_data = validated_data.pop("tickets")
            order = Order.objects.create(**validated_data)
            for ticket_data in tickets_data:
                Ticket.objects.create(order=order, **ticket_data)
        return order