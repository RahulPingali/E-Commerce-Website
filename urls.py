from django.urls import path
from .views import index, login_view, logout_view, register, active_listings, create_listing, listing, remove_listing, add_bid, remove_bid, add_comment, add_to_watchlist, remove_from_watchlist, place_bid, close_auction, categories

urlpatterns = [
    path("", index, name="index"),
    path("login", login_view, name="login"),
    path("logout", logout_view, name="logout"),
    path("register", register, name="register"),
    path("active_listings", active_listings, name="active_listings"),
    path("create_listing", create_listing, name="create_listing"),
    path("listing/<int:listing_id>", listing, name="listing"),
    path("listing/<int:listing_id>/remove_listing", remove_listing, name="remove_listing"),
    path("listing/<int:listing_id>/add_bid", add_bid, name="add_bid"),
    path("listing/<int:listing_id>/remove_bid", remove_bid, name="remove_bid"),
    path("listing/<int:listing_id>/add_comment", add_comment, name="add_comment"),
    path("listing/<int:listing_id>/add_to_watchlist", add_to_watchlist, name="add_to_watchlist"),
    path("listing/<int:listing_id>/remove_from_watchlist", remove_from_watchlist, name="remove_from_watchlist"),
    path("listing/<int:listing_id>/place_bid", place_bid, name="place_bid"),
    path("listing/<int:listing_id>/close_auction", close_auction, name="close_auction"),
    path("categories", categories, name="categories")
]
