from django.urls import path, include
from rest_framework.routers import DefaultRouter
from airport.views import (AirportViewSet,
                           RouteViewSet,
                           CrewViewSet,
                           AirplaneTypeViewSet,
                           AirplaneViewSet,
                           FlightViewSet,
                           OrderViewSet,
                           TicketViewSet)

router = DefaultRouter()

router.register("airports", AirportViewSet)
router.register("routes", RouteViewSet)
router.register("crews", CrewViewSet)
router.register("airplane_types", AirplaneTypeViewSet)
router.register("airplanes", AirplaneViewSet)
router.register("flights", FlightViewSet)
router.register("orders", OrderViewSet, basename="orders")
router.register("tickets", TicketViewSet)


urlpatterns = [
    path("", include(router.urls))
]


app_name = "airport"