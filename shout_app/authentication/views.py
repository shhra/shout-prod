from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import View, APIView
from rest_framework.permissions import AllowAny, IsAuthenticated 
from allauth.account.views import ConfirmEmailView
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.shortcuts import redirect

from .serializers import LoginSerializer
from rest_auth.registration.serializers import VerifyEmailSerializer

class LoginAPIView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer 

    def post(self, request):
        data = request.data.get('data')
        serializer = self.serializer_class(data=data['user'])
        serializer.is_valid(raise_exception=True)

        return Response(serializer.validated_data, status=status.HTTP_200_OK)


class VerifyEmailView(APIView, ConfirmEmailView):
    permission_classes = (AllowAny,)
    allowed_methods = ('POST', 'OPTIONS', 'HEAD')

    def get_serializer(self, *args, **kwargs):
        return VerifyEmailSerializer(*args, **kwargs)

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.kwargs['key'] = serializer.validated_data['key']
        confirmation = self.get_object()
        confirmation.confirm(self.request)
        return Response({'detail': ('ok'), 'url':'https://apprester.com'}, status=status.HTTP_200_OK)


class EmailConfirmAPIView(APIView):

    def get(self, request, key):
        return redirect(f"https://apprester.com/#/verify-email/{key}")


