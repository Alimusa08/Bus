from django.contrib.auth import login, logout
from rest_framework.decorators import api_view, authentication_classes
from rest_framework.response import Response
from .models import CustomUser, OTP
import random
from .authintications import CsrfExemptSessionAuthentication
import string
from django.views.decorators.csrf import csrf_exempt

@api_view(['POST'])
def register(request):
    phone = request.data.get('phone')
    name = request.data.get('name', '')

    if not phone:
        return Response({"error": "Phone is required"}, status=400)

    try:
        user, created = CustomUser.objects.get_or_create(phone=phone, defaults={'name': name})
        if created:
            otp = OTP(user=user)
            otp.save()
            send_sms(phone, otp.code)  
            return Response({"message": f"OTP sent to {phone}"}, status=201)
        else:
            return Response({"error": "User already exists, please login"}, status=400)
    except Exception as e:
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def login_user(request):
    phone = request.data.get('phone')
    otp_code = request.data.get('otp')

    if not phone or not otp_code:
        return Response({"error": "Phone and OTP are required"}, status=400)

    try:
        user = CustomUser.objects.get(phone=phone)
        otp = OTP.objects.filter(user=user, code=otp_code).latest('created_at')
        # OTP is valid; set a random password
        random_password = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        user.set_password(random_password)
        user.save()
        # Delete OTP after use
        # Log in the user
        login(request._request, user)
        request._request.session.set_expiry(315360000)  
        return Response({"message": "Login successful"}, status=200)
    except (CustomUser.DoesNotExist, OTP.DoesNotExist):
        return Response({"error": "Invalid phone or OTP"}, status=401)

@api_view(['POST'])
def send_otp(request):
    phone = request.data.get('phone')

    if not phone:
        return Response({"error": "Phone is required"}, status=400)

    try:
        user = CustomUser.objects.get(phone=phone)
        if user.password:  
            user.set_password(None)
            user.save()
        otp = OTP(user=user)
        otp.save()
        send_sms(phone, otp.code)  
        return Response({"message": f"OTP sent to {phone}"}, status=200)
    except CustomUser.DoesNotExist:
        return Response({"error": "User does not exist, please register"}, status=404)

@api_view(['POST'])
@authentication_classes([CsrfExemptSessionAuthentication])
def logout_user(request):
    user = request.user
    if user.is_authenticated:
        user.set_password(None)  # clean password
        user.save()
        logout(request._request)
        return Response({"message": "Logged out"}, status=200)
    return Response({"error": "Not logged in"}, status=401)

def send_sms(phone, otp):
    # Mock SMS for development
    with open('otp_log.txt', 'a') as f:
        f.write(f"OTP {otp} sent to {phone}\n")
        
@api_view(['GET'])
def check_user(request):
    if request.user.is_authenticated:
        return Response({"phone": request.user.phone})
    return Response({"error": "Not authenticated"}, status=401)