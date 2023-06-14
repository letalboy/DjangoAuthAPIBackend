from django.shortcuts import render

# Create your views here.

from .serializers import UserSerializer

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.exceptions import APIException, AuthenticationFailed

from .authentication import create_access_token, decode_access_token
from .authentication import create_refresh_token, decode_refresh_token

from .models import User

class RegistryUser(APIView):

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
class UserLogin(APIView):

    def post (self, request):

        user = User.objects.filter(email=request.data['email']).first()

        if not user:
            raise APIException('Invalid Credentials')
        
        if not user.check_password(request.data['password']):
            raise APIException('Invalid Credentials')
        
        access_token = create_access_token(user.id)
        refresh_token = create_refresh_token(user.id)

        response = Response()
        response.set_cookie(key='refreshToken', value=refresh_token, httponly=False, samesite=None)

        response.data = {
            'token':access_token
        }

        return response
    
from rest_framework.authentication import get_authorization_header

class GetUser (APIView):
    def get (self, request):
        
        auth = get_authorization_header(request).split()

        if auth and len(auth) == 2:

            token = auth[1].decode('utf-8')

            id = decode_access_token(token)

            user = User.objects.filter(pk=id).first()

            return Response(UserSerializer(user).data)
        
        return AuthenticationFailed('unauthenticated')
    
    
class Refresh (APIView):

    def post(self, request):


        refresh_token = request.COOKIES.get('refreshToken')
        # print(refresh_token)


        id = decode_refresh_token(refresh_token)

        # print (id)

        access_token = create_access_token(id)

        return Response (
            {
                'token': access_token
            }
        )

class UserLogout (APIView):
    def post(self, request):

        response = Response()
        response.delete_cookie(key='refreshToken')
        response.date = {
            'message':'success'
        }

        return response
    
