from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.shortcuts import render
from django.urls import reverse
from django.contrib.auth.decorators import login_required
import datetime
import json
from django.core.files import File
import razorpay
import os

from .models import User, Missing, Sighting
from .utils import geocode, decode64ImgFile, formatTime

# Environment variable holding geocoding api key
api_key = "AIzaSyD1hr0O6KuE8L00gPtInroZQH3TikfpnFg"


# Landing page
def index(request):
    return render(request, "sentry/index.html", {
        "home": True
    })

# Map page
@login_required
def sentry(request):
    user = User.objects.get(pk = request.user.id)
    missing_alerts = []
    sighting_alerts = []

    # Populate lists with missing alerts and sightings
    for element in Missing.objects.all():
        missing_alerts.append(element.serialize())
    for element in Sighting.objects.all():
        sighting_alerts.append(element.serialize())
    return render(request, "sentry/sentry.html", {
        "user": user,
        "missings": json.dumps(missing_alerts, cls=DjangoJSONEncoder),
        "sightings": json.dumps(sighting_alerts, cls=DjangoJSONEncoder)
    })

@login_required
def shop(request):
    if request.method == 'POST':
        client = razorpay.Client(auth=("rzp_test_DWstJuR6f2D2C9", "KHIlvWLq4quiRbEc0HvfLf7Z"))

        
        currency = "INR"

        # Create the order
        order = client.order.create({
            'currency': currency,
            'payment_capture': 1  # Auto-capture the payment
        })

        order_id = order['id']

        context = {
            'order_id': order_id,
        }
        return render(request, "shop.html", context)

    return render(request, "shop.html")
# Add new missing alert to database
@login_required
def newMissing(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    else:
        # Retrieve and process data from the request body
        data = json.loads(request.body)
        try:
            latLng = geocode(data.get("location"), api_key)
        except Exception as e:
            return JsonResponse({"error": "Couldn't fetch location's latitude and longitude"}, status=400)
        time = formatTime(data.get("time"))

        # Write data inside the model
        try:
            miss = Missing(
                owner=User.objects.get(pk=request.user.id),
                name=data.get("name"),
                lat=latLng["lat"],
                lng=latLng["lng"],
                missing_time=datetime.datetime(time["year"], time["month"], time["day"]),
                description=data.get("description"),
                contact=data.get("contact"),
            )
        except Exception as e:
            print("Error while writing missing alert data to the database:", str(e))
            return JsonResponse({"error": "An error occurred while writing missing alert data to the database"}, status=500)

        # Create a file with decoded image data and save it inside the model
        image_data = decode64ImgFile(data.get("image"))
        try:
            with open(f"img.{image_data['img_format']}", "wb") as f:
                f.write(image_data['data'])
            miss.image = f.name  # Set the image field to the file path
        except FileNotFoundError:
            pass

        # Delete the file in BASE_DIR
        if os.path.exists(f"img.{image_data['img_format']}"):
            os.remove(f"img.{image_data['img_format']}")

        # Save the new missing alert
        miss.save()
        return JsonResponse({
            "message": "New missing alert posted!",
            "data": data,
            "lat_lng": latLng
        }, status=201)

# Add new Sighting alert to database
@login_required
def newSight(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST request required."}, status=400)
    else:
        # Retrieve and process data from the request body
        data = json.loads(request.body)
        try:
            latLng = geocode(data.get("location"), api_key)
        except Exception as e:
            return JsonResponse({"error": "Couldn't fetch location's latitude and longitude"}, status=400)
        time = formatTime(data.get("time"))

        # Write data inside the model
        try:
            sight = Sighting(
                author=User.objects.get(pk=request.user.id),
                lat=latLng["lat"],
                lng=latLng["lng"],
                sight_time=datetime.datetime(time["year"], time["month"], time["day"]),
                description=data.get("description"),
                contact=data.get("contact"),
            )
        except Exception as e:
            print("Error while writing sight data to the database:", str(e))
            return JsonResponse({"error": "An error occurred while writing sight data to the database"}, status=500)

        # Create a file with decoded image data and save it inside the model
        image_data = decode64ImgFile(data.get("image"))
        try:
            with open(f"img.{image_data['img_format']}", "wb") as f:
                f.write(image_data['data'])
            sight.image = f.name  # Set the image field to the file path

        except FileNotFoundError:
            pass

        # Delete the file in BASE_DIR
        if os.path.exists(f"img.{image_data['img_format']}"):
            os.remove(f"img.{image_data['img_format']}")

        # Save the new sighting
        sight.save()
        return JsonResponse({
            "message": "New sighting alert posted!",
            "data": data,
            "lat_lng": latLng
        }, status=201)


# Login view
def loginView(request):
    # Attempt to sign user in
    email = request.POST["email"]
    password = request.POST["password"]
    user = authenticate(request, username=email ,email=email, password=password)

    # Check if authentication successful
    if user is not None:
        login(request, user)
        return HttpResponseRedirect(reverse("sentry"))
    else:
        return render(request, "sentry/index.html", {
            "message": "Invalid email and/or password."
        })

# Logout view
def logoutView(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

# Register view
def register(request):
    email = request.POST["email"]

    # Ensure password matches confirmation
    password = request.POST["password"]
    confirmation = request.POST["confirmation"]
    if password != confirmation:
        return render(request, "sentry/index.html", {
            "message": "Passwords must match."
        })

    # Attempt to create new user
    try:
        user = User.objects.create_user(email, email, password)
        user.save()
    except IntegrityError:
        return render(request, "sentry/index.html", {
            "message": "Email already used."
        })
    login(request, user)
    return HttpResponseRedirect(reverse("sentry"))
