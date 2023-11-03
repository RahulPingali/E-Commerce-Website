from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from auctions.models import Listing, User, Bid, Comment
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from .models import Listing, Bid, Comment
from django.db.models import Max

def index(request):
    return render(request, "auctions/index.html")


def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "auctions/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "auctions/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "auctions/register.html", {
                "message": "Passwords must match."
            })

        # Attempt to create new user
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "auctions/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "auctions/register.html")
    
def active_listings(request):
    active_listings = Listing.objects.filter(active=True).annotate(highest_bid=Max('bids__amount'))
    closed_listings = Listing.objects.filter(active=False).annotate(highest_bid=Max('bids__amount'))
    return render(request, "auctions/active_listings.html", {"active_listings": active_listings, "closed_listings": closed_listings})


def create_listing(request):
    if request.method == "POST":
        title = request.POST["title"]
        description = request.POST["description"]
        starting_bid = request.POST["starting_bid"]
        image = request.POST["image_url"]
        category = request.POST["category"]
        active = True
        winner = None
        user = request.user
        listing = Listing(user=user, title=title, description=description, starting_bid=starting_bid, image=image, category=category, active=active, winner=winner)
        listing.save()
        return redirect("active_listings")
    else:
        return render(request, "auctions/create_listing.html")

def listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)

    if not listing.active:
        return render(request, "auctions/listing.html", {"listing": listing, "error": "This listing is closed."})

    return render(request, "auctions/listing.html", {"listing": listing})


@login_required
def add_to_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    user = request.user
    if listing not in user.watchlist.all():
        user.watchlist.add(listing)
    return redirect("listing", listing_id=listing_id)

@login_required
def remove_from_watchlist(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    user = request.user
    if listing in user.watchlist.all():
        user.watchlist.remove(listing)
    return redirect("listing", listing_id=listing_id)

@login_required
def place_bid(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if request.method == "POST":
        bid_amount = float(request.POST["bid"])
        if bid_amount < listing.starting_bid:
            return render(request, "auctions/listing.html", {"listing": listing, "error": "Bid amount must be greater than or equal to the starting bid."})
        if listing.bids.filter(amount__gte=bid_amount).exists():
            return render(request, "auctions/listing.html", {"listing": listing, "error": "Bid amount must be greater than the current highest bid."})
        bid = Bid(user=request.user, listing=listing, amount=bid_amount)
        bid.save()
        return redirect("listing", listing_id=listing_id)
    return redirect("listing", listing_id=listing_id)


@login_required
def close_auction(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    print("Debug: Close auction view is executed.")  
    if request.user == listing.user:
        if listing.active:
            listing.active = False
            highest_bid = listing.bids.order_by("-amount").first()
            if highest_bid:
                listing.winner = highest_bid.user
            else:
                listing.winner = None
            listing.save()
    return redirect("listing", listing_id=listing_id)

@login_required
def add_comment(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if request.method == "POST":
        comment_text = request.POST["comment"]
        comment = Comment(user=request.user, listing=listing, comment=comment_text)
        comment.save()
    return redirect("listing", listing_id=listing_id)

def remove_listing(request, listing_id):
    listing = get_object_or_404(Listing, pk=listing_id)
    if request.user == listing.user:
        listing.delete()
    return redirect("active_listings")

def add_bid(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    bid = request.POST["bid"]
    if float(bid) > listing.starting_bid:
        listing.starting_bid = bid
        listing.save()
        return redirect("listing", listing_id=listing_id)
    else:
        return render(request, "auctions/listing.html", {"listing": listing, "error": "Bid must be higher than the current bid."})

def remove_bid(request, listing_id):
    listing = Listing.objects.get(pk=listing_id)
    listing.starting_bid = listing.starting_bid
    listing.save()
    return redirect("listing", listing_id=listing_id)

def categories(request):
    categories = Listing.objects.values_list('category', flat=True).distinct()
    return render(request, "auctions/categories.html", {"categories": categories})

def category(request, category):
    category_listings = Listing.objects.filter(category=category)
    return render(request, "auctions/category_listings.html", {"category_listings": category_listings, "category": category})