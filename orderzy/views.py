from django.shortcuts import render
from restaurant.models import Restaurant
from django.contrib.gis.geos import GEOSGeometry
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.functions import Distance


def is_valid_coordinate(value):
    try:
        val = float(value)
        return True
    except ValueError:
        return False

def get_or_set_current_location(request):
    if 'lat' in request.session and 'lng' in request.session:
        lat = request.session['lat']
        lng = request.session['lng']
        # Validate the coordinates
        if is_valid_coordinate(lat) and is_valid_coordinate(lng):
            return float(lng), float(lat)
        else:
            return None
    elif 'lat' in request.GET and 'lng' in request.GET:
        lat = request.GET.get('lat')
        lng = request.GET.get('lng')
        # Validate the coordinates
        if is_valid_coordinate(lat) and is_valid_coordinate(lng):
            request.session['lat'] = lat
            request.session['lng'] = lng
            return float(lng), float(lat)
        else:
            return None
    else:
        return None


def home(request):
    if get_or_set_current_location(request) is not None:
       
        # pnt = GEOSGeometry('POINT(%s %s)' % (get_or_set_current_location(request)))
        lng, lat = get_or_set_current_location(request)
        pnt = GEOSGeometry(f'POINT({lng} {lat})')

        restaurants = Restaurant.objects.filter(user_profile__location__distance_lte=(pnt, D(km=1000))).annotate(distance=Distance("user_profile__location", pnt)).order_by("distance")

        for r in restaurants:
            r.kms = round(r.distance.km,1)
    else:
        
        restaurants = Restaurant.objects.filter(is_approved=True, user__is_active=True)[:8]
        
    context = {
        'restaurants':restaurants
    }
    return render(request, 'home.html',context)

def base(request):
    return render(request, 'base.html')