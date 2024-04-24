from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from . models import *
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db.models import Count


def index(request):
    all_group = BloodGroup.objects.annotate(total=Count('donor'))
    return render(request, "index.html", {'all_group':all_group})

def donors_list(request, myid):
    blood_groups = BloodGroup.objects.filter(id=myid).first()
    donor = Donor.objects.filter(blood_group=blood_groups)
    return render(request, "donors_list.html", {'donor':donor})

def donors_details(request, myid):
    details = Donor.objects.filter(id=myid)[0]
    return render(request, "donors_details.html", {'details':details})

def request_blood(request):
    if request.method == "POST":
        name = request.POST['name']
        email = request.POST['email']
        phone = request.POST['phone']
        state = request.POST['state']
        city = request.POST['city']
        address = request.POST['address']
        blood_group = request.POST['blood_group']
        date = request.POST['date']
        blood_requests = RequestBlood.objects.create(name=name, email=email, phone=phone, state=state, city=city, address=address, blood_group=BloodGroup.objects.get(name=blood_group), date=date)
        blood_requests.save()
        return render(request, "index.html")
    return render(request, "request_blood.html")

def see_all_request(request):
    requests = RequestBlood.objects.all()
    return render(request, "see_all_request.html", {'requests':requests})

def become_donor(request):
    if request.method=="POST":   
        username = request.POST['username']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        email = request.POST['email']
        phone = request.POST['phone']
        state = request.POST['state']
        city = request.POST['city']
        address = request.POST['address']
        gender = request.POST['gender']
        blood_group = request.POST['blood_group']
        date = request.POST['date']
        image = request.FILES['image']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('/signup')

        user = User.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name, password=password)
        donors = Donor.objects.create(donor=user, phone=phone, state=state, city=city, address=address, gender=gender, blood_group=BloodGroup.objects.get(name=blood_group), date_of_birth=date, image=image)
        user.save()
        donors.save()
        return render(request, "index.html")
    return render(request, "become_donor.html")

def Login(request):
    if request.user.is_authenticated:
        return redirect("/")
    else:
        if request.method == "POST":
            username = request.POST['username']
            password = request.POST['password']
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect("/profile")
            else:
                thank = True
                return render(request, "user_login.html", {"thank":thank})
    return render(request, "login.html")

def Logout(request):
    logout(request)
    return redirect('/')

@login_required(login_url = '/login')
def profile(request):
    donor_profile = Donor.objects.get(donor=request.user)
    return render(request, "profile.html", {'donor_profile':donor_profile})


@login_required(login_url = '/login')
def change_status(request):
    donor_profile = Donor.objects.get(donor=request.user)
    if donor_profile.ready_to_donate:
        donor_profile.ready_to_donate = False
        donor_profile.save()
    else:
        donor_profile.ready_to_donate = True
        donor_profile.save()
    return redirect('/profile')
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Donor

@login_required(login_url='/login')
def edit_profile(request):
    donor_profile = get_object_or_404(Donor, donor=request.user)
    print("Donor profile:", donor_profile)  # Debug information

    if request.method == "POST":
        # Get the updated profile information from the form
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        state = request.POST.get('state')
        city = request.POST.get('city')
        address = request.POST.get('address')
        image = request.FILES.get('image')

        # Update the donor profile with the new information
        donor_profile.donor.email = email
        donor_profile.phone = phone
        donor_profile.state = state
        donor_profile.city = city
        donor_profile.address = address
        
        # If a new image is provided, update the profile picture
        if image:
            donor_profile.image = image
        
        # Save the changes to the donor profile
        donor_profile.donor.save()
        donor_profile.save()

        # Redirect to the profile page with a success message
        messages.success(request, 'Profile updated successfully.')
        return redirect('/profile')

    # If the request method is GET, render the edit profile form
    return render(request, "edit_profile.html", {'donor_profile': donor_profile})

def why(request):
    return render(request,"why.html")
def about_us(request):
    return render(request,"aboutus.html")


# from django.contrib.gis.geos import Point
# from django.contrib.gis.db.models.functions import Distance
from django.http import JsonResponse
from .utils import calcdistance


def list_nearest_donors(request):
    return render(request,'list_nearest_donors.html')
def nearest_donors(request):
    if request.method == 'GET':
        # Assuming the user's latitude and longitude are passed as GET parameters
        user_latitude = request.GET.get('latitude')
        user_longitude = request.GET.get('longitude')
        # user_latitude= 27.7958429
        # user_longitude = 87.295600

        if user_latitude and user_longitude:
            # user_location = Point(float(user_longitude), float(user_latitude), srid=4326)  # Assuming WGS84 coordinate system

            # Query to find nearest donors
            # nearest_donors = Donor.objects.annotate(
            #     distance=Distance('location', user_location)
            # ).order_by('distance')[:10]  # Get the 10 nearest donors
            donors = Donor.objects.filter(ready_to_donate=True)
            nearest_donors_list = []
            for donor in donors: 
                if donor.latitude and donor.longitude:
                    distance = round(calcdistance(user_latitude,user_longitude,donor.latitude,donor.longitude),2)
                else:
                    donor.latitude = 27.7958429
                    donor.longitude = 87.295000
                    distance = round(calcdistance(user_latitude,user_longitude,donor.latitude,donor.longitude),2)
                    print(distance)
                donor_data = {}
                donor_data['name'] = donor.donor.get_full_name()
                donor_data['blood_group'] =donor.blood_group.name
                donor_data['distance'] = distance
                donor_data['latitude'] = donor.latitude
                donor_data['longitude'] = donor.longitude
                nearest_donors_list.append(donor_data)

            sorted_donor_list = sorted(nearest_donors_list, key=lambda x: float(x['distance']))[:10]

            # Serialize the queryset to JSON
            # donors_data = [
            #     {
            #         'id': donor.id,
            #         'username': donor.donor.username if donor.donor else "Anonymous",
            #         'distance': donor.distance.km
            #     }
            #     for donor in nearest_donors
            # ]
            return JsonResponse({'nearest_donors': sorted_donor_list})
            # return JsonResponse({'nearest_donors': nearest_donors_list})
        else:
            return JsonResponse({'error': 'Latitude and longitude parameters are required.'}, status=400)
    else:
        return JsonResponse({'error': 'Only GET method is allowed.'}, status=405)
    
def set_location(request):
    
    if request.method == 'POST':
        donor = request.user.donor
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        donor.latitude = latitude
        donor.longitude = longitude
        donor.save()
        return redirect('profile')
        

def current_location(request):
    return render(request,'current_location.html')
