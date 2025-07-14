from django.shortcuts import render
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.decorators import api_view, authentication_classes, permission_classe
# Create your views here.

# @authentication_classes([JWTAuthentication])
# @permission_classes([IsAuthenticatedOrReadOnly])