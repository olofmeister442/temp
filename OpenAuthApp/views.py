from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.authentication import SessionAuthentication, BasicAuthentication

from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse, get_object_or_404, HttpResponseRedirect
from django.contrib.auth.models import User

from oauth2_provider.views.generic import ProtectedResourceView

from models import *
from oauth2_provider.models import Application, Grant, AccessToken

import os

import json
from django.http import HttpResponse
from oauth2_provider.decorators import protected_resource
import datetime
import requests
from engine.parsers import *

def write_file(data):
    f= open("logger.txt","a+")
    f.write(data+"\n")
    f.close()

"""
def get_user(request):
    user = request.
    return HttpResponse(
        json.dumps({
            'username': user.username, 
            'email': user.email}),
        content_type='application/json')

class get_userAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        data = request.data
        access_token = data.get('acces_token')
        print("Acces token is", access_token)

        return Response(data={})
"""


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


class ApiEndpoint(ProtectedResourceView):

    def get(self, request, *args, **kwargs):
        return HttpResponse('Hello, OAuth2!')


class get_userAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        data = request.data
        print(data)
        access_token = data.get('access_token')
        print("Acces token is", access_token)
        print("all ", AccessToken.objects.filter(
            token=access_token)[0].user.username)
        return Response(data={'name': AccessToken.objects.filter(token=access_token)[0].user.username})


@login_required(login_url='/login/')  # redirect when user is not logged in
def Home(request):

    return render(request, 'OpenAuthApp/home.html')


@login_required(login_url='/login/')  # redirect when user is not logged in
def Pin(request):
    return render(request, 'OpenAuthApp/pin.html')


@login_required(login_url='/login/')  # redirect when user is not logged in
def Otp(request):
    try:
        request.session.set_expiry(60*4)            
    except:
        print("No Session Obtained.")
    return render(request, 'OpenAuthApp/otp-grid.html')


def RedirectHome(request):

    return HttpResponseRedirect('/home/')


def Login(request):
    client_id = request.GET.get('client_id')

    #Match With Alexa or Something
    return render(request, 'OpenAuthApp/login.html')


@login_required(login_url='/login/')
def Logout(request):
    logout(request)
    return HttpResponseRedirect('/login/')


class get_grant_codeAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:

            data = request.data
            app_name = data['app_name']

            app = Application.objects.filter(name=app_name)[0]

            grant = Grant.objects.filter(Application=app)[0]

            grant_code = grant.code

            response['status'] = 200
            response['grant_code'] = grant_code

        except Exception as e:
            print("Error get_grant_codeAPI", str(e))

        return Response(data=response)


class LoginSubmitAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):

        response = {}
        response['status'] = 500
        try:
            data = request.data

            reg_mob_no = data['reg_mob_no']
            otp = data['otp']
            #unique1 = data['unique1']
            #unique2 = data['unique2']			
            # Call api to check if user exists
            headers = {'content-type':'text/xml', 'SOAPAction':''}
            url = "http://10.50.81.32:9001/OTPEngine/services/OTPWebService?wsdl"
            #body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ws="http://ws.otp.icicibank.com">
            #           <soapenv:Header/>
            #           <soapenv:Body>
            #              <ws:otpService>
            #                 <ws:input>
            #        <![CDATA[<REQUEST>   <ACTCODE/>   <CHANNEL>5</CHANNEL>   <APPLICATION_NAME>67</APPLICATION_NAME>   <FIELD1>"""+unique1+"""</FIELD1>   <FIELD2>"""+unique2+"""</FIELD2>   <FIELD3>SWOPNA</FIELD3>   <AMOUNT>0.0</AMOUNT>   <TRANSACTION_CODE>127</TRANSACTION_CODE>   <VALIDITY>0</VALIDITY>   <DELIVERY_MODE>SMS</DELIVERY_MODE>   <DELIVERY_ADDRESS>"""+reg_mob_no+"""</DELIVERY_ADDRESS>   <MANAGED_BY/>   <ACTION>V</ACTION>   <OTP>"""+otp+"""</OTP>   <VALIDITY_GIVEN/> </REQUEST>]]> 
            #        </ws:input>
            #              </ws:otpService>
            #           </soapenv:Body>
            #        </soapenv:Envelope>"""
            #print(body)		
            #response = requests.post(url, data=body, headers=headers, timeout=7)
            #print(response.text)
            #response.text = response.text.replace("&gt;",">")
            #response.text = response.text.replace("&lt;","<")			
            #acct = parse_otp_send(response.text)
            #print(acct)			
            #acct = "000"
            #if (acct != "000"):
            #    return Response(data=response)
            ########### After verification ###############

            # If user exist continue
            user = CustomUser.objects.filter(username=reg_mob_no)
            print(reg_mob_no)
            print(user, "UISER")
            if(len(user)) == 0:
                user = CustomUser.objects.create_user(username=reg_mob_no,
                                                      password=otp)                      
            else:
                user = user[0]

            login(request, user)

            response['status'] = 200

        except Exception as e:
            print("Error LoginSubmitAPI", str(e))

        return Response(data=response)

class StoreParamsAPI(APIView):

    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request, *args, **kwargs):
        response = {}
        response['status'] = 500
        try:
            data = request.data
            print(request.session.get_expiry_age(), type(request.session.get_expiry_age()),"SESSION OBJECt")
            request.session.set_expiry(60*4)            
            print(request.session.get_expiry_age(), type(request.session.get_expiry_age()),"SESSION OBJECt")
            try:
                write_file("AA")
                mpin = data.get('mpin')
                write_file(mpin)
                user = CustomUser.objects.get(username=request.user.username)                
                write_file(mpin)  
                user_params = json.dumps(json.loads(data.get('user_params')))                
                write_file(mpin)  
                user.user_params = user_params
                write_file(mpin)  
                print("MPIN IS: ", mpin)
                user.set_password(mpin)
                write_file(mpin)  
                user.save()
                login(request, user)                #VERY IMPORTANT
                request.session.set_expiry(30)
            except Exception as e:
                print(str(e))                

            response['status'] = 200
        except Exception as e:
            print("Error StoreParamsAPI", str(e))

        return Response(data=response)

LoginSubmit = LoginSubmitAPI.as_view()
get_grant_code = get_grant_codeAPI.as_view()
StoreParams = StoreParamsAPI.as_view()