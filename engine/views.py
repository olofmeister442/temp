#!/usr/bin/python
# -*- coding: utf-8 -*-
import calendar
import csv
import logging
import random
from datetime import date, timedelta
import editdistance
import xmltodict
import pandas as pd
import math
import requests
import json
import uuid
import datetime
from pprint import pprint
from random import randint

from django.conf import settings
from django.http import HttpResponse
from django.utils.encoding import smart_str
from rest_framework.authentication import BasicAuthentication, \
    SessionAuthentication
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from django.core.mail import EmailMultiAlternatives
from django.utils.safestring import SafeData, SafeText, mark_safe
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, HttpResponse, get_object_or_404, HttpResponseRedirect
from oauth2_provider.models import Application, Grant, AccessToken

from utils import *
from models import *
from constants import *
from apis import *
from OpenAuthApp.models import *

logger = logging.getLogger('my_logger')


def write_file(data):
    f = open("logger.txt", "a+")
    f.write(data + "\n")
    f.close()


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def Export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="mixed.csv"'
    writer = csv.writer(response)
    writer.writerow(['Tests'])
    writer.writerow(['Question', 'Expected Answer', 'Actual Answer'])
    test_model = reversed(list(TestModel.objects.all()))
    list_intent = []
    for test in test_model:
        intent = Intent.objects.get(pk=test.intent_id)
        test_sentences = test.sentences
        if test_sentences is not None:
            for sentence in test_sentences.splitlines():
                sentence = sentence.strip()
                if sentence != '':
                    intent_recognized = \
                        get_intent(do_pre_processing(sentence, 'web',
                                                     'eng'))
                    if intent_recognized is not None:
                        intent_obj = get_object_or_404(Intent,
                                                       name=intent_recognized[0].name)
                        if intent_obj.pk != intent.pk:
                            try:
                                answer1 = \
                                    mark_safe(Intent.objects.get(
                                        name=intent.name).tree.answer.group_of_sentences.all()[0].sentence)
                                answer1 = re.sub(r'<[^>]*?>', '',
                                                 answer1)
                            except:
                                answer1 = \
                                    mark_safe(Intent.objects.get(
                                        name=intent.name).tree.question_entity_type.question.group_of_sentences.all()[0].sentence)
                                answer1 = re.sub(r'<[^>]*?>', '',
                                                 answer1)
                            try:
                                answer2 = \
                                    mark_safe(Intent.objects.get(
                                        name=intent_obj.name).tree.answer.group_of_sentences.all()[0].sentence)
                                answer2 = re.sub(r'<[^>]*?>', '',
                                                 answer2)
                            except:
                                answer2 = \
                                    mark_safe(Intent.objects.get(
                                        name=intent_obj.name).tree.question_entity_type.question.group_of_sentences.all()[0].sentence)
                                answer2 = re.sub(r'<[^>]*?>', '',
                                                 answer2)
                            writer.writerow([smart_str(sentence),
                                             smart_str(answer1),
                                             smart_str(answer2)])
                    else:
                        try:
                            answer1 = \
                                mark_safe(Intent.objects.get(
                                    name=intent.name).tree.answer.group_of_sentences.all()[0].sentence)
                            answer1 = re.sub(r'<[^>]*?>', '', answer1)
                        except:
                            answer1 = \
                                mark_safe(Intent.objects.get(
                                    name=intent.name).tree.question_entity_type.question.group_of_sentences.all()[0].sentence)
                            answer1 = re.sub(r'<[^>]*?>', '', answer1)
                        writer.writerow([smart_str(sentence),
                                         smart_str(answer1),
                                         smart_str(UNRECOGNIZED_MESSAGE)])

    test_model = reversed(list(TestModel.objects.all()))
    list_intent = []
    for test in test_model:
        intent = Intent.objects.get(pk=test.intent_id)
        test_sentences = test.sentences
        if test_sentences is not None:
            for sentence in test_sentences.splitlines():
                sentence = sentence.strip()
                if sentence != '':
                    intent_recognized = \
                        get_intent(do_pre_processing(sentence, 'web',
                                                     'eng'))
                    if intent_recognized is not None:
                        intent_obj = get_object_or_404(Intent,
                                                       name=intent_recognized[0].name)
                        if intent_obj.pk == intent.pk:
                            try:
                                answer1 = \
                                    mark_safe(Intent.objects.get(
                                        name=intent.name).tree.answer.group_of_sentences.all()[0].sentence)
                                answer1 = re.sub(r'<[^>]*?>', '',
                                                 answer1)
                            except:
                                try:
                                    answer1 = \
                                        mark_safe(Intent.objects.get(
                                            name=intent.name).tree.question_entity_type.question.group_of_sentences.all()[0].sentence)
                                    answer1 = re.sub(r'<[^>]*?>', '',
                                                     answer1)
                                except:
                                    answer1 = ''
                            writer.writerow([smart_str(sentence),
                                             smart_str(answer1),
                                             smart_str(answer1)])
    return response


def FailedExport(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = \
        'attachment; filename="failed.csv"'
    writer = csv.writer(response)
    writer.writerow(['Question', 'Expected Answer', 'Actual Answer'])
    test_model = reversed(list(TestModel.objects.all()))
    list_intent = []
    for test in test_model:
        try:
            intent = Intent.objects.get(pk=test.intent_id)
            test_sentences = test.sentences
            if test_sentences is not None:
                for sentence in test_sentences.splitlines():
                    sentence = sentence.strip()
                    if sentence != '':
                        intent_recognized = \
                            get_intent(do_pre_processing(
                                sentence, 'web', 'eng'))

                        if intent_recognized is not None:
                            intent_obj = get_object_or_404(Intent,
                                                           name=intent_recognized[0].name)
                            if intent_obj.pk != intent.pk:
                                try:
                                    answer1 = \
                                        mark_safe(Intent.objects.get(
                                            name=intent.name).tree.answer.group_of_sentences.all()[0].sentence)
                                    answer1 = re.sub(r'<[^>]*?>', '',
                                                     answer1)
                                except:
                                    answer1 = \
                                        mark_safe(Intent.objects.get(
                                            name=intent.name).tree.question_entity_type.question.group_of_sentences.all()[0].sentence)
                                    answer1 = re.sub(r'<[^>]*?>', '',
                                                     answer1)
                                try:
                                    answer2 = \
                                        mark_safe(Intent.objects.get(
                                            name=intent_obj.name).tree.answer.group_of_sentences.all()[0].sentence)
                                    answer2 = re.sub(r'<[^>]*?>', '',
                                                     answer2)
                                except:
                                    answer2 = \
                                        mark_safe(Intent.objects.get(
                                            name=intent_obj.name).tree.question_entity_type.question.group_of_sentences.all()[0].sentence)
                                    answer2 = re.sub(r'<[^>]*?>', '',
                                                     answer2)
                                writer.writerow([smart_str(sentence),
                                                 smart_str(answer1),
                                                 smart_str(answer2)])
                        else:
                            try:
                                answer1 = \
                                    mark_safe(Intent.objects.get(
                                        name=intent.name).tree.answer.group_of_sentences.all()[0].sentence)
                                answer1 = re.sub(r'<[^>]*?>', '',
                                                 answer1)
                            except:
                                answer1 = \
                                    mark_safe(Intent.objects.get(
                                        name=intent.name).tree.question_entity_type.question.group_of_sentences.all()[0].sentence)
                                answer1 = re.sub(r'<[^>]*?>', '',
                                                 answer1)
                            writer.writerow([smart_str(sentence),
                                             smart_str(answer1),
                                             smart_str(UNRECOGNIZED_MESSAGE)])
        except Exception, e:
            pass
    return response


def PassedExport(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = \
        'attachment; filename="passed.csv"'
    writer = csv.writer(response)
    writer.writerow(['Question', 'Expected Answer', 'Actual Answer'])
    test_model = reversed(list(TestModel.objects.all()))
    list_intent = []
    for test in test_model:
        try:
            intent = Intent.objects.get(pk=test.intent_id)
            test_sentences = test.sentences
            if test_sentences is not None:
                for sentence in test_sentences.splitlines():
                    sentence = sentence.strip()
                    if sentence != '':
                        intent_recognized = \
                            get_intent(do_pre_processing(
                                sentence, 'web', 'eng'))
                        if intent_recognized is not None:
                            intent_obj = get_object_or_404(Intent,
                                                           name=intent_recognized[0].name)
                            if intent_obj.pk == intent.pk:
                                try:
                                    answer1 = \
                                        mark_safe(Intent.objects.get(
                                            name=intent.name).tree.answer.group_of_sentences.all()[0].sentence)
                                    answer1 = re.sub(r'<[^>]*?>', '',
                                                     answer1)
                                except:
                                    answer1 = \
                                        mark_safe(Intent.objects.get(
                                            name=intent.name).tree.question_entity_type.question.group_of_sentences.all()[0].sentence)
                                    answer1 = re.sub(r'<[^>]*?>', '',
                                                     answer1)
                                writer.writerow([smart_str(sentence),
                                                 smart_str(answer1),
                                                 smart_str(answer1)])
        except:
            pass
    return response


def ChatbotTest(request):
    item = Intent.objects.all()
    form = request.POST
    if request.method == 'POST':
        pass
    items = []
    for intent in item:
        temp_dict = {}
        temp_dict['intent'] = intent.name
        temp_dict['id'] = intent.pk
        try:
            count = 0
            for sentence in \
                    TestModel.objects.get(name=intent.name).sentences.splitlines():
                if sentence.strip() != '':
                    count = count + 1
            temp_dict['count'] = count
        except:
            temp_dict['count'] = '0'
        items.append(temp_dict)
    return render_to_response('engine/chatbot_test.html',
                              {'intents': items})


def RunTests(request):
    return render(request, 'engine/uat.html', {})


def Index(request):
    if request.user_agent.is_mobile:
        return render(request, 'engine/index1.html', {})
    else:
        return render(request, 'engine/index.html', {})


class SendPPCAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def post(self, request):
        try:
            data = request.data

            policy_number = data.get('policy_number').strip()
            financial_year = data.get('fin_year').strip()
            financial_year = financial_year.replace('=', '-')
            url = Config.objects.all()[0].url_customer_id
            headers = {'content-type': 'text/xml'}
            body = \
                    """<?xml version="1.0" encoding="utf-8"?>
					<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
					  <soap:Body>
						<getPPC_EasyAccess_mail xmlns="http://tempuri.org/">
						  <strPolicyNumber>""" \
                    + policy_number \
                    + """</strPolicyNumber>
						  <strFinYear>""" \
                    + financial_year \
                    + """</strFinYear>
						</getPPC_EasyAccess_mail>
					  </soap:Body>
					</soap:Envelope>
					"""
            response = requests.post(url, data=body, headers=headers)
            content = str(response.content)
            content = \
                content[content.find('<getPPC_EasyAccess_mailResult>')
                        + 30:content.find('</getPPC_EasyAccess_mailResult>')]
            content = content.replace('&lt;', '<')
            content = content.replace('&gt;', '>')
            content = content.replace(r"\r", '')
            content = content.replace(r"\n", '')
            answer = content.strip()
            if answer == '0':
                data = {}
                temp_dict = {}
                temp_dict['flag'] = ''
                data['answer'] = temp_dict
            else:
                data = {}
                temp_dict = {}
                temp_dict['flag'] = 'temp'
                data['answer'] = temp_dict
            return Response(data=data)
        except:
            data = {}
            temp_dict = {}
            temp_dict['flag'] = ''
            temp_dict['answer'] = ''
            data['answer'] = temp_dict
            return Response(data=data)


class GetAllPolicyDtlsAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def post(self, request):
        try:
            data = request.data
            policy_number = data.get('policy_number').strip()
            dob = data.get('dob').strip()
            url = Config.objects.all()[0].url_customer_id
            headers = {'content-type': 'text/xml'}
            body = \
                    """<?xml version="1.0" encoding="utf-8"?>
					<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
					  <soap:Body>
						<getCustomer_ID xmlns="http://tempuri.org/">
						  <strPolicyNo>""" \
                    + policy_number \
                    + """</strPolicyNo>
						  <strDOB>""" \
                    + dob \
                    + """</strDOB>
						</getCustomer_ID>
					  </soap:Body>
					</soap:Envelope>
					"""
            response = requests.post(url, data=body, headers=headers)
            content = str(response.content)
            content = content[content.find('<getCustomer_IDResult>')
                              + 22:content.find('</getCustomer_IDResult>')]
            content = content.replace('&lt;', '<')
            content = content.replace('&gt;', '>')
            content = content.replace(r"\r", '')
            content = content.replace(r"\n", '')
            answer = content
            dictt = xmltodict.parse(answer)
            answer = json.loads(json.dumps(dictt))
            customer_id = answer['PolicyDetails']['Table'
                                                  ]['PL_PERSON_ID']
            body = \
                    """<?xml version="1.0" encoding="utf-8"?>
					<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
					  <soap:Body>
						<showAllPolicyDtls xmlns="http://tempuri.org/">
						  <strCustId>""" \
                    + customer_id \
                    + """</strCustId>
						</showAllPolicyDtls>
					  </soap:Body>
					</soap:Envelope>
					"""
            response = requests.post(url, data=body, headers=headers)
            content = str(response.content)
            content = content[content.find('<showAllPolicyDtlsResult>')
                              + 25:content.find('</showAllPolicyDtlsResult>')]
            content = content.replace('&lt;', '<')
            content = content.replace('&gt;', '>')
            content = content.replace(r"\r", '')
            content = content.replace(r"\n", '')
            answer = content
            answer = answer.replace("'", '')
            answer = answer.replace('\\', '')
            answer = answer.replace(' xml:space=preserve', '')

            data = {}

            temp_dict = {}
            temp_dict['answer'] = answer
            temp_dict['flag'] = 'temp'
            data['answer'] = temp_dict
            return Response(data=data)
        except Exception, e:
            data = {}
            temp_dict = {}
            temp_dict['flag'] = ''
            temp_dict['answer'] = ''
            data['answer'] = temp_dict
            return Response(data=data)


class GetPolicyDtlsAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def post(self, request):
        try:
            data = request.data
            policy_number = data.get('policy_number').strip()
            dob = data.get('dob').strip()
            url = Config.objects.all()[0].url_customer_id
            headers = {'content-type': 'text/xml'}
            body = \
                    """<?xml version="1.0" encoding="utf-8"?>
					<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
					  <soap:Body>
						<getCustomer_ID xmlns="http://tempuri.org/">
						  <strPolicyNo>""" \
                    + policy_number \
                    + """</strPolicyNo>
						  <strDOB>""" \
                    + dob \
                    + """</strDOB>
						</getCustomer_ID>
					  </soap:Body>
					</soap:Envelope>
					"""
            response = requests.post(url, data=body, headers=headers)
            content = str(response.content)
            content = content[content.find('<getCustomer_IDResult>')
                              + 22:content.find('</getCustomer_IDResult>')]
            content = content.replace('&lt;', '<')
            content = content.replace('&gt;', '>')
            content = content.replace(r"\r", '')
            content = content.replace(r"\n", '')
            answer = content
            dictt = xmltodict.parse(answer)
            answer = json.loads(json.dumps(dictt))
            customer_id = answer['PolicyDetails']['Table'
                                                  ]['PL_PERSON_ID']
            body = \
                    """<?xml version="1.0" encoding="utf-8"?>
					<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
					  <soap:Body>
						<showPolicyDtls xmlns="http://tempuri.org/">
						  <strPolicyNumber>""" \
                    + policy_number \
                    + """</strPolicyNumber>
						  <userId>""" \
                    + customer_id \
                    + """</userId>
						</showPolicyDtls>
					  </soap:Body>
					</soap:Envelope>
					"""
            response = requests.post(url, data=body, headers=headers)
            content = str(response.content)
            content = content[content.find('<showPolicyDtlsResult>')
                              + 22:content.find('</showPolicyDtlsResult>')]
            content = content.replace('&lt;', '<')
            content = content.replace('&gt;', '>')
            content = content.replace(r"\r", '')
            content = content.replace(r"\n", '')
            answer = content

            data = {}

            temp_dict = {}
            temp_dict['answer'] = answer
            temp_dict['flag'] = 'temp'
            data['answer'] = temp_dict
            return Response(data=data)
        except Exception, e:
            data = {}
            temp_dict = {}
            temp_dict['flag'] = ''
            temp_dict['answer'] = ''
            data['answer'] = temp_dict
            return Response(data=data)


class IToSAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def post(self, request):
        data = request.data
        intent_id = data.get('intent_id')
        intent = Intent.objects.get(pk=intent_id)
        return Response(data={'answer': intent.tree.answer.group_of_sentences.all()[0].pk})
        pass


class TestChatbotMapperAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def post(self, request):
        intents = Intent.objects.all()
        WORD_MAP = {}
        word_mappers = WordMapper.objects.all()
        for word_mapper in word_mappers:
            for similar_word in word_mapper.get_similar_words():
                WORD_MAP[similar_word] = word_mapper.keyword
        list_mapper = []
        for intent in intents:
            keyword_sets = intent.get_keywords()
            for keyword_set in keyword_sets:
                for keyword in keyword_set:
                    if keyword in WORD_MAP:
                        temp_dict = {}
                        temp_dict['wordmapper_keyword'] = keyword
                        temp_dict['intent'] = smart_str(intent.name)
                        temp_dict['intent_keyword_remove'] = \
                            smart_str(','.join(keyword_set))
                        list_mapper.append(temp_dict)
        return Response(data={'mappers': list_mapper})


class TestIntentAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def post(self, request):
        test_model = reversed(list(TestModel.objects.all()))
        list_intent = []
        for test in test_model:
            intent = Intent.objects.get(pk=test.intent_id)
            test_sentences = test.sentences
            if test_sentences is not None:
                for sentence in test_sentences.splitlines():
                    sentence = sentence.strip()
                    if sentence != '':
                        intent_recognized = \
                            get_intent(do_pre_processing(
                                sentence, 'web', 'eng'))
                        if intent_recognized is not None:
                            intent_obj = get_object_or_404(Intent,
                                                           name=intent_recognized[0].name)
                            if intent_obj.pk != intent.pk:
                                temp_dict = {}
                                temp_dict['sentence'] = \
                                    smart_str(sentence)
                                temp_dict['intent'] = \
                                    smart_str(intent.name)
                                temp_dict['intent_recognized'] = \
                                    smart_str(intent_obj.name)
                                temp_dict['level1'] = intent.level
                                temp_dict['level2'] = intent_obj.level
                                temp_dict['id1'] = intent.pk
                                temp_dict['id2'] = intent_obj.pk
                                list_intent.append(temp_dict)
                        else:
                            temp_dict = {}
                            temp_dict['sentence'] = smart_str(sentence)
                            temp_dict['intent'] = smart_str(test.name)
                            temp_dict['intent_recognized'] = ''
                            temp_dict['level1'] = intent.level
                            temp_dict['level2'] = ''
                            temp_dict['id1'] = intent.pk
                            list_intent.append(temp_dict)
        return Response(data={'intents': list_intent})


class TestChatbotIntentAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def post(self, request):
        intents = Intent.objects.all()
        list_intent = []
        count = 0
        for intent in intents:
            count = count + 1
            test_sentences = intent.test_sentences
            for sentence in test_sentences.splitlines():
                sentence = sentence.strip()
                intent_recognized = \
                    get_intent(do_pre_processing(sentence, 'web', 'eng'
                                                 ))
                if intent_recognized is not None:
                    intent_obj = get_object_or_404(Intent,
                                                   name=intent_recognized[0].name)
                    if intent_obj.pk != intent.pk:
                        temp_dict = {}
                        temp_dict['sentence'] = smart_str(sentence)
                        temp_dict['intent'] = smart_str(intent.name)
                        temp_dict['intent_recognized'] = \
                            smart_str(intent_obj.name)
                        temp_dict['level1'] = intent.level
                        temp_dict['level2'] = intent_obj.level
                        list_intent.append(temp_dict)
                else:
                    temp_dict = {}
                    temp_dict['sentence'] = smart_str(sentence)
                    temp_dict['intent'] = smart_str(intent.name)
                    temp_dict['intent_recognized'] = ''
                    temp_dict['level1'] = intent.level
                    temp_dict['level2'] = ''
                    list_intent.append(temp_dict)
        return Response(data={'intents': list_intent})


def TestChatbot(request):
    return render(request, 'engine/testing.html', {})


def Iframe(request):
    return render(request, 'engine/chatbox.html', {})


def Analytics(request):
    return render(request, 'engine/analytics.html')


class CancelAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def post(self, request):
        data = request.data
        response_json = {}
        response_json['is_typable'] = 'true'
        user_id = data.get('user_id', False)
        clear_data_from_model(user_id)
        reset_user(user_id)
        response_json['response'] = \
            Config.objects.all()[0].initial_message
        response_json['recommended_queries'] = initial_base_response()
        return Response(data=response_json)


class QueryFeedbackLikeAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def post(
            self,
            request,
            *args,
            **kwargs
    ):
        data = self.kwargs
        user_id = data['user_id']
        query_id = data['query_id']
        try:
            fdback = \
                QueryFeedbackCounter.objects.filter(user__user_id=user_id,
                                                    query__pk=query_id).get()
            fdback.like_cnt = 1
            if fdback.dislike_cnt == 1:
                fdback.dislike_cnt = 0
            fdback.save()
        except Exception, e:
            user = Profile.objects.get(user_id=user_id)

            QueryFeedbackCounter(user=user, like_cnt=1,
                                 query_id=query_id).save()
            logger.error(
                'class: QueryFeedbackLikeAPIView, method: get %s', str(e))
        return Response(data={})


class QueryFeedbackDislikeAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def post(
            self,
            request,
            *args,
            **kwargs
    ):
        data = self.kwargs
        user_id = data['user_id']
        query_id = data['query_id']
        try:
            fdback = \
                QueryFeedbackCounter.objects.filter(user__user_id=user_id,
                                                    query__pk=query_id).get()
            fdback.dislike_cnt = 1
            if fdback.like_cnt == 1:
                fdback.like_cnt = 0
            fdback.save()
        except Exception, e:
            user = Profile.objects.get(user_id=user_id)

            QueryFeedbackCounter(user=user, dislike_cnt=1,
                                 query_id=query_id).save()
            logger.error(
                'class: QueryFeedbackDislikeAPIView, method: get %s', str(e))
        return Response(data={})


class QueryAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def post(self, request):
        data = request.data
        print('Data is: ', data)
        message = data.get('message', False)
        user_id = data.get('user_id', False)
        channel = data.get('channel', False)
        language = data.get('language', False)
        clicked = data.get('clicked', False)
        pipe = data.get('pipe', False)

        alexa_id = data.get('alexa_id', '')
        device_id = data.get('device_id', '')
        access_token = data.get('access_token', '')
        write_file("Goes QUERY")
        write_file(message)
        write_file(access_token)

        message = message.lower()
        if message.lower().strip() == 'home' or message.lower().strip() \
                == 'cancel':
            if channel == 'whatsapp':
                response_json = {}
                response_json['show_menu_fast'] = '1'
                clear_data_from_model(user_id)
                reset_user(user_id)

                # user = Profile.objects.get(user_id=user_id)
                # user.tree = Tree.objects.get(name="sbi life main tree.Tree")
                # user.save()

                return Response(data=response_json)
        user = Profile.objects.get(user_id=user_id)
        current_tree = user.tree
        if channel.lower() == 'whatsapp':
            message = change_number_to_text(current_tree, message)
        if channel.lower() == 'alexa' or channel.lower() == 'whatsapp':
            pipe = message + '|'
            response_json = process_message_without_pipe(
                current_tree,
                message,
                user_id,
                channel,
                language,
                clicked,
                pipe,
                alexa_id,
                device_id,
                access_token,
            )
        else:
            response_json = process_message_with_pipe(
                current_tree,
                message,
                user_id,
                channel,
                language,
                clicked,
                pipe,
                alexa_id,
                device_id,
                access_token,
            )
        if channel.lower() == 'whatsapp' and 'is_answer' \
                in response_json:
            if response_json['is_answer'] == 'true' and channel.lower() \
                    == 'whatsapp':
                response_json['show_menu'] = '1'
                clear_data_from_model(user_id)
                reset_user(user_id)

                # user = Profile.objects.get(user_id=user_id)
                # user.tree = Tree.objects.get(name="sbi life main tree.Tree")
                # user.save()

        return Response(data=response_json)


def set_cookie(
        response,
        key,
        value,
        days_expire=7,
):
    if days_expire is None:
        max_age = 365 * 24 * 60 * 60  # one year
    else:
        max_age = days_expire * 24 * 60 * 60
    expires = datetime.datetime.strftime(datetime.datetime.utcnow()
                                         + datetime.timedelta(seconds=max_age),
                                         '%a, %d-%b-%Y %H:%M:%S GMT')
    response.set_cookie(
        key,
        value,
        max_age=max_age,
        expires=expires,
        domain=settings.SESSION_COOKIE_DOMAIN,
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE or None,
    )


class UpdateUserAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def post(self, request):
        data = request.data

        # try:

        user_id = data.get('user_id', None)
        if user_id is None:
            user_id = str(uuid.uuid4())

        # except:
        #    user_id = str(uuid.uuid4())

        try:
            Profile.objects.get(user_id=user_id)
        except:
            dict2 = {}
            dict2['user_id'] = user_id
            Profile.objects.create(**dict2)
        json = {}
        json['is_typable'] = TRUE
        json['response'] = Config.objects.all()[0].initial_message
        list_temp = initial_base_response()
        json['recommended_queries'] = list_temp
        logger.info(json)
        json['user_id'] = user_id

        # a = Profile.objects.get(user_id=data.get('user_id'))
        # a.tree = Tree.objects.get(name="main.Tree")
        # a.save()

        response = Response(data=json)
        set_cookie(response, 'user_id', user_id)
        return response


def Report(request, from_date, to_date):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = \
        'attachment; filename="sia_report.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Message Text',
        'Answered (Yes or No)',
        'user_id',
        'chatbot_answer',
        'language',
        'channel',
        'time',
        'clicked',
    ])
    from_date = from_date.split('/')
    to_date = to_date.split('/')
    start_date = date(int(from_date[2]), int(from_date[1]),
                      int(from_date[0]))
    end_date = date(int(to_date[2]), int(to_date[1]), int(to_date[0]))
    queries = Log.objects.filter(time__range=(start_date, end_date))
    for query in queries:
        if query.time is not None:
            ans = NO
            clicked = NO
            if query.answer_succesfull:
                ans = YES
            if query.clicked:
                clicked = YES
            writer.writerow([
                smart_str(decrypt(offset, query.query)),
                ans,
                smart_str(query.user.user_id),
                smart_str(decrypt(offset, query.chatbot_answer)),
                smart_str(query.language.name),
                smart_str(query.channel.name),
                smart_str(query.time),
                clicked,
            ])
    return response


class GetPcIdAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def post(self, request):
        data = request.data
        if request.COOKIES.get('pc_id') is not None:
            pc_id = request.COOKIES.get('pc_id')
        else:
            pc_id = str(uuid.uuid4())
        try:
            UniqueUsers.objects.filter(user_id=pc_id).get()
        except Exception, e:
            p = UniqueUsers(user_id=pc_id)
            p.save()
        json = {}
        json['pc_id'] = pc_id
        response = Response(data=json)
        set_cookie(response, 'pc_id', pc_id, 10000)
        return response


def ChatTesting(request, *args, **kwargs):
    return render(request, 'engine/chat_testing.html', {})


class SaveSentencesAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def post(self, request):
        data = request.data
        intent_id = data.get('intent_id')
        sentences = data.get('sentences')
        try:
            test_model = TestModel.objects.get(intent_id=intent_id)
            test_model.sentences = sentences
            test_model.save()
            return Response(data={})
        except:
            intent_name = Intent.objects.get(id=intent_id).name

            TestModel(intent_id=intent_id, name=intent_name,
                      sentences=sentences).save()
            return Response(data=data)
        pass


class GetSentencesAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def post(self, request):
        data = request.data
        intent_id = data.get('intent_id')
        try:
            test_model = TestModel.objects.get(intent_id=intent_id)
            name = test_model.name
            sentences = test_model.sentences
            data = {}
            data['name'] = name
            data['sentences'] = sentences
            try:
                data['answer'] = \
                    Intent.objects.get(name=name).tree.answer.group_of_sentences.all()[
                    0].sentence
            except:
                data['answer'] = NESTED_QUESTION
            if sentences is None:
                sentences = ''
            return Response(data=data)
        except:
            intent_name = Intent.objects.get(id=intent_id).name

            TestModel(intent_id=intent_id, name=intent_name).save()
            data = {}
            data['name'] = intent_name
            data['sentences'] = ''
            try:
                data['answer'] = \
                    Intent.objects.get(name=intent_name).tree.answer.group_of_sentences.all()[
                    0].sentence
            except:
                data['answer'] = NESTED_QUESTION
            return Response(data=data)


class SubmitQueriesAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def post(self, request):
        data = request.data
        intent = data.get('intent')
        sentences = data.get('sentences')
        final_dict = {}
        final_dict['intent'] = intent
        answer_list = []
        for sentence in sentences.splitlines():
            intent = Intent.objects.get(name=intent)
            sentence2 = do_pre_processing(sentence, 'web', 'eng')
            intent2 = get_intent(sentence2)
            if intent2 is not None:
                intent_obj = get_object_or_404(Intent,
                                               name=intent2[0].name)
                if intent_obj.pk == intent.pk:
                    temp_dict = {}
                    temp_dict['sentence'] = sentence
                    temp_dict['verdict'] = PASS
                    answer_list.append(temp_dict)
                else:
                    temp_dict = {}
                    temp_dict['sentence'] = sentence
                    temp_dict['verdict'] = FAIL
                    answer_list.append(temp_dict)
            else:
                temp_dict = {}
                temp_dict['sentence'] = sentence
                temp_dict['verdict'] = FAIL
                answer_list.append(temp_dict)
        final_dict['answer'] = answer_list
        return Response(data=final_dict)


class GetAnalysisAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def post(self, request):
        try:
            data = request.data
            from_date = data.get('from_date').split('/')
            to_date = data.get('to_date').split('/')
            start_date = date(int(from_date[2]), int(from_date[1]),
                              int(from_date[0]))
            end_date = date(int(to_date[2]), int(to_date[1]),
                            int(to_date[0]))
            choices = return_choice(start_date, end_date)
            current_choice = choices[1]
            value = choices[0]
            dict_count = create_blank_dict(value, current_choice,
                                           start_date)
            answered_count = create_blank_dict(value, current_choice,
                                               start_date)
            unanswered_count = create_blank_dict(value, current_choice,
                                                 start_date)
            platform_dict = {}
            answered_messages = []
            unanswered_messages = []
            total_message = []
            dict_user_cnt = create_blank_dict(value, current_choice,
                                              start_date)
            dict_message_cnt = create_blank_dict(value, current_choice,
                                                 start_date)
            final_average_dict = create_blank_dict(value,
                                                   current_choice, start_date)
            total_unique_users = create_blank_dict(value,
                                                   current_choice, start_date)
            queries = Log.objects.filter(time__range=(start_date,
                                                      end_date))
            analytics = \
                AnalyticCount.objects.filter(time__range=(start_date,
                                                          end_date))
            unique_users = \
                UniqueUsers.objects.filter(time__range=(start_date,
                                                        end_date))
            list_insights_1 = {}
            clicked_vs_typed = {}
            try:
                for query in queries:
                    if query.time is not None:
                        total_message.append(query.query + ' '
                                             + query.user.user_id)
                        if query.answer_succesfull == True:
                            answered_messages.append(query.query + ' '
                                                     + query.user.user_id)
                        else:
                            unanswered_messages.append(query.query + ' '
                                                       + query.user.user_id)
                        current_platform = query.channel.name
                        if current_platform != 'False':
                            if current_platform not in platform_dict:
                                platform_dict[current_platform] = 1
                            else:
                                platform_dict[current_platform] += 1
                        clicked = query.clicked
                        if clicked == True:
                            if 'clicked' not in clicked_vs_typed:
                                clicked_vs_typed['clicked'] = 1
                            else:
                                clicked_vs_typed['clicked'] += 1
                        else:
                            if 'typed' not in clicked_vs_typed:
                                clicked_vs_typed['typed'] = 1
                            else:
                                clicked_vs_typed['typed'] += 1
                        t = query.time
                        if current_choice == '0':
                            dict_count[t.strftime('%d/%m/%Y')] += 1
                            if query.answer_succesfull == True:
                                answered_count[t.strftime('%d/%m/%Y'
                                                          )] += 1
                            else:
                                unanswered_count[t.strftime('%d/%m/%Y'
                                                            )] += 1
                        elif current_choice == '1':
                            dict_count[calendar.month_name[t.month]] += \
                                1
                            if query.answer_succesfull == True:

                                answered_count[calendar.month_name[t.month]] += \
                                    1
                            else:

                                unanswered_count[calendar.month_name[t.month]] += \
                                    1
                        else:
                            dict_count[t.year] += 1
                            if query.answer_succesfull == True:
                                answered_count[t.year] += 1
                            else:
                                unanswered_count[t.year] += 1
                        list_insights_1['total_messages'] = dict_count
                        list_insights_1['answered_messages'] = \
                            answered_count

                        list_insights_1['unanswered_messages'] = \
                            unanswered_count
            except Exception, e:
                logger.error(
                    'class: GetAnalysisAPIView, method: post ERROr %s', str(e))
            (dict_user_cnt, dict_message_cnt) = get_dict_cnt(queries,
                                                             current_choice, dict_message_cnt, dict_user_cnt)
            final_average_dict = get_final_average_dict(dict_user_cnt,
                                                        dict_message_cnt, final_average_dict)

            (entity_count, entity_count_name) = \
                get_entity_count_and_entity_count_name(analytics)
            entity_top_intent = get_entity_top_intent(analytics,
                                                      entity_count_name)
            top_intent_in_entities = \
                get_top_intent_in_entities(entity_top_intent)
            intent_top_entity = get_intent_top_entity(analytics)
            top_entities_in_intent = \
                get_top_entities_in_intent(intent_top_entity)
            total_unique_users = \
                get_total_unique_users(total_unique_users,
                                       unique_users, current_choice)
            final_dict = {}
            final_dict['list_insights_1'] = list_insights_1
            final_dict['platform_dict'] = platform_dict
            final_dict['average_session_time'] = final_average_dict
            final_dict['clicked_vs_typed'] = clicked_vs_typed
            final_dict['top_products'] = entity_count
            final_dict['top_intent_in_entities'] = \
                top_intent_in_entities
            final_dict['top_entities_in_intent'] = \
                top_entities_in_intent
            final_dict['total_unique_users'] = total_unique_users
            final_dict['answered_messages'] = answered_messages
            final_dict['unanswered_messages'] = unanswered_messages
            final_dict['total_messages'] = total_message
            return Response(data=final_dict)
        except Exception, e:
            return Response(data={})


class saveLeadDataAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def post(self, request):
        try:
            data = request.data
            name = data.get('name').strip()
            email = data.get('email').strip()
            contact = data.get('contact').strip()
            try:
                Leads.objects.get(name=name, email_id=email,
                                  contact=contact)
            except:

                Leads(name=name, email_id=email, contact=contact).save()
            data = {}
            data['answer'] = ''
            return Response(data=data)
        except:
            return Response(data=data)
            pass


class GetPPCAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def post(self, request):
        try:
            data = request.data
            policy_number = data.get('policy_number').strip()
            dob = data.get('dob').strip()
            email = data.get('email').strip()
            url = Config.objects.all()[0].url_customer_id
            headers = {'content-type': 'text/xml'}
            body = \
                    """<?xml version="1.0" encoding="utf-8"?>
					<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
					  <soap:Body>
						<getCustomer_ID xmlns="http://tempuri.org/">
						  <strPolicyNo>123456789</strPolicyNo>
						  <strDOB>01/01/1980</strDOB>
						</getCustomer_ID>
					  </soap:Body>
					</soap:Envelope>
					"""
            response = requests.post(url, data=body, headers=headers)
            content = str(response.content)
            content = content[content.find('<getCustomer_IDResult>')
                              + 22:content.find('</getCustomer_IDResult>')]
            content = content.replace('&lt;', '<')
            content = content.replace('&gt;', '>')
            content = content.replace(r"\r", '')
            content = content.replace(r"\n", '')
            answer = content
            dictt = xmltodict.parse(answer)
            answer = json.loads(json.dumps(dictt))
            customer_id = answer['PolicyDetails']['Table'
                                                  ]['PL_PERSON_ID']
            body = \
                    """<?xml version="1.0" encoding="utf-8"?>
					<soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
					  <soap:Body>
						<getPPC xmlns="http://tempuri.org/">
						  <strPolicyNumber>123456789</strPolicyNumber>
						  <strFinYear>2016-2017</strFinYear>
						</getPPC>
					  </soap:Body>
					</soap:Envelope>"""
            response = requests.post(url, data=body, headers=headers)
            content = str(response.content)
            content = content[content.find('<getPPCResult>')
                              + 14:content.find('</getPPCResult>')]
            content = content.replace('&lt;', '<')
            content = content.replace('&gt;', '>')
            content = content.replace(r"\r", '')
            content = content.replace(r"\n", '')
            answer = content
            dictt = xmltodict.parse(answer)
            answer = json.loads(json.dumps(dictt))

            send_mail(email,
                      '<h5>The below are the following details: </h5><br><div>Product Name - '
                      + answer['NewDataSet']['Table1']['PRODUCT_NAME']
                      + '<br>Product Type - ' + answer['NewDataSet'
                                                       ]['Table1']['PROD_TYPE'] + '<br> Policy Number - '
                      + answer['NewDataSet']['Table1']['POLICY_NUMBER'
                                                       ] + '</div>')
            data = {}

            data['flag'] = 'temp'
            return Response(data=data)
        except Exception, e:
            data = {}
            data['flag'] = ''

            return Response(data=data)


try:
    SERVER_PROTOCOL = Config.objects.all()[0].facebook_server_protocol
    SERVER_IP = Config.objects.all()[0].facebook_server_ip
    SERVER_PORT = Config.objects.all()[0].facebook_server_port
except:
    pass


class FacebookAPIView(generic.View):

    @method_decorator(csrf_exempt)
    def dispatch(
            self,
            request,
            *args,
            **kwargs
    ):
        return generic.View.dispatch(self, request, *args, **kwargs)

    def get(
            self,
            request,
            *args,
            **kwargs
    ):
        return HttpResponse(self.request.GET['hub.challenge'])

    def post(
            self,
            request,
            *args,
            **kwargs
    ):
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        pprint(incoming_message)
        try:
            for entry in incoming_message['entry']:
                for message in entry['messaging']:
                    if 'postback' in message:
                        process_facebook_message(message['sender']['id'
                                                                   ], message['postback']['title'], ONE)
                    if 'message' in message:

                        if 'quick_reply' in message['message']:
                            process_facebook_message(message['sender'
                                                             ]['id'], message['message'
                                                                              ]['quick_reply']['payload'], TWO)
                        else:
                            process_facebook_message(message['sender'
                                                             ]['id'], message['message']['text'
                                                                                         ], THREE)
        except:
            pass
        return HttpResponse()


def get_user_from_access_token(access_token):
    try:
        return AccessToken.objects.filter(token=access_token)[0].user
    except:
        return None


class DeleteEntriesAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        print('User id is: ', user_id)
        user = Profile.objects.get(user_id=user_id)
        print('User is: ', user)
        try:
            data = Data.objects.filter(user=user,
                                       entity_name='LeaveType').delete()
        except:
            pass
        try:
            data = Data.objects.filter(user=user, entity_name='Reenter'
                                       ).delete()
        except:
            pass

        # print("Data is: ", data)

        return Response(data={})


class GoogleHomeAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        message = data.get('message')
        channel = data.get('channel')
        language = data.get('language')
        clicked = data.get('clicked')
        pipe = data.get('pipe')
        call_update_user(user_id)
        response = call_query_googlehome(user_id, message, clicked,
                                         pipe)
        response = json.loads(response.text)
        answer = response['response']
        try:
            choices = response['choices']
            if len(choices) > 0:
                for choice in choices:
                    answer += choice + COMMA
        except:
            pass
        answer = re.sub(r'<[^>]*?>', '', answer)
        return Response(data={'response': answer})


class ElecBillAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def get(self, request):
        data = {}
        data['numbers'] = ['Mahanagar Connection',
                           'Vivanagar Connection']
        return Response(data=data)


class GasBillAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def get(self, request):
        data = {}
        data['numbers'] = ['Himannagar Connection', 'Kalol Connection']
        return Response(data=data)


class AlexaAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        message = data.get('message')
        channel = data.get('channel')
        language = data.get('language')
        clicked = data.get('clicked')
        pipe = data.get('pipe')

        call_update_user(user_id)

        response = call_query_alexa(user_id, message, clicked, pipe)
        response = json.loads(response.text)
        answer = response['response']
        try:
            choices = response['choices']
            if len(choices) > 0:
                for choice in choices:
                    answer += choice + COMMA
        except:
            pass
        answer = re.sub(r'<[^>]*?>', '', answer)
        return Response(data={'response': answer})


###########

class CreditCardNumbersAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def get(self, request):
        data = request.GET
        user_id = data.get('user_id')
        alexa_id = data.get('alexa_id')
        device_id = data.get('device_id')
        access_token = data.get('access_token')

        write_file(access_token)
        if Config.objects.all()[0].prod:
            mobile_number = get_user_from_access_token(access_token).username
        else:
            mobile_number = CustomUser.objects.get(
                username="8169392028").username
        print("The mobile number is: ", mobile_number)
        write_file(mobile_number)
        # mobile_number = '7990801839'  # Currently Testing
        response = get_credit_card_numbers(mobile_number)
        write_file(str(response))
        if len(response) == 0:
            data = {}
            data["numbers"] = ""
            data["success"] = "false"
            data["message"] = "You have no credit cards registered"
            return Response(data=data)
        data = {}
        data['numbers'] = response
        return Response(data=data)


def random_with_N_digits(n):
    range_start = 10 ** (n - 1)
    range_end = 10 ** n - 1
    return str(randint(range_start, range_end))


class GetOTPAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def post(self, request):

        mobile_number = request.data.get('mob_no')
        user_id = get_user_id(mobile_number)

        if user_id == "-5" or len(user_id) == 0:
            data = {}
            data['success'] = '0'
            return Response(data=data)
        headers = {'content-type': 'text/xml', 'SOAPAction': ''}
        url = \
            'http://10.50.81.32:9001/OTPEngine/services/OTPWebService?wsdl'
        unique1 = random_with_N_digits(5)
        unique2 = random_with_N_digits(6)
        body = \
            """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ws="http://ws.otp.icicibank.com">
   <soapenv:Header/>
   <soapenv:Body>
	  <ws:otpService>
		 <ws:input><![CDATA[<REQUEST><ACTCODE/><CHANNEL>5</CHANNEL><APPLICATION_NAME>67</APPLICATION_NAME><FIELD1>""" \
                + unique1 + """</FIELD1><FIELD2>""" + unique2 \
                + """</FIELD2><FIELD3>SWOPNA</FIELD3><AMOUNT>0.0</AMOUNT><TRANSACTION_CODE>127</TRANSACTION_CODE><VALIDITY>0</VALIDITY><DELIVERY_MODE>SMS</DELIVERY_MODE><DELIVERY_ADDRESS>""" \
                + mobile_number \
                + """</DELIVERY_ADDRESS><MANAGED_BY/><ACTION>C</ACTION><OTP/><VALIDITY_GIVEN/></REQUEST>]]>  
</ws:input>
	  </ws:otpService>
   </soapenv:Body>
</soapenv:Envelope>"""
        print body
        response = requests.post(url, data=body, headers=headers)
        print response.text

        # Parsing now the response.

        response = response.text
        response = response.replace('&lt;', '<')
        response = response.replace('&gt;', '>')

        actcode = parse_otp_send(response)
        print('Act code is: ', actcode)
        data = {}
        if actcode == '000':
            data['success'] = '1'
        else:
            data['success'] = '0'
        print('data is: ', data)
        data['unique1'] = unique1
        data['unique2'] = unique2
        print('data is: ', data)
        return Response(data=data)


class VerifyGridAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request):
        data = request.data

        val1 = data.get('val1')
        val2 = data.get('val2')
        val3 = data.get('val3')

        char1 = data.get('char1')
        char2 = data.get('char2')
        char3 = data.get('char3')

        value_string = "0A1B2C3D4E5F6G7H8I9J1K2L3M4N5O6P"

        index_1 = value_string.find(char1)
        index_2 = value_string.find(char2)
        index_3 = value_string.find(char3)

        #access_token = data.get('access_token')
        mobile_number = request.user.username
        logger.error("MOb %s", mobile_number)
        user = CustomUser.objects.get(username=mobile_number)
        user_params = json.loads(user.user_params)
        account_number = user_params["default_account"]
        # account_number = request.user.user_params some parsing and try if
        # current user is super user or what.

        response = get_grid_response(mobile_number, account_number, val1, val2, val3, str(
            index_1), str(index_1 + 1), str(index_2), str(index_2 + 1), str(index_3), str(index_3 + 1))

        data = {}
        data["success"] = response
        return Response(data=data)


class VerifyMPINAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request):
        data = request.GET
        message = data.get('message')
        alexa_id = data.get('alexa_id')
        device_id = data.get('device_id')
        access_token = data.get('access_token')
        if Config.objects.all()[0].prod:
            user = get_user_from_access_token(access_token)
        else:
            user = CustomUser.objects.get(username="8169392028")
        user = CustomUser.objects.get(username=user)
        user_params = json.loads(user.user_params)
        #user = CustomUser.objects.get(username="12312311")
        print(user)
        success = False
        try:
            if (message.strip() == user_params["mpin"].strip()):
                success = True
                print(success)
        except:
            pass

        data = {}
        if success:
            data["response"] = "Verified"
        else:
            data["response"] = None
        return Response(data=data)


class SendOTPTreeAPIView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def get(self, request):
        data = request.GET
        message = data.get('message').strip()
        alexa_id = data.get('alexa_id')
        device_id = data.get('device_id')
        access_token = data.get('access_token')
        if Config.objects.all()[0].prod:
            reg_mob_no = get_user_from_access_token(access_token).username
        else:
            reg_mob_no = CustomUser.objects.get(username="8169392028").username
        user = CustomUser.objects.get(username=reg_mob_no)

        url = \
            'http://10.50.81.32:9001/OTPEngine/services/OTPWebService?wsdl'
        unique1 = random_with_N_digits(5)
        unique2 = random_with_N_digits(6)
        body = \
            """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ws="http://ws.otp.icicibank.com">
   <soapenv:Header/>
   <soapenv:Body>
	  <ws:otpService>
		 <ws:input><![CDATA[<REQUEST><ACTCODE/><CHANNEL>5</CHANNEL><APPLICATION_NAME>67</APPLICATION_NAME><FIELD1>""" \
                + unique1 + """</FIELD1><FIELD2>""" + unique2 \
                + """</FIELD2><FIELD3>SWOPNA</FIELD3><AMOUNT>0.0</AMOUNT><TRANSACTION_CODE>128</TRANSACTION_CODE><VALIDITY>0</VALIDITY><DELIVERY_MODE>SMS</DELIVERY_MODE><DELIVERY_ADDRESS>""" \
                + reg_mob_no \
                + """</DELIVERY_ADDRESS><MANAGED_BY/><ACTION>C</ACTION><OTP/><VALIDITY_GIVEN/></REQUEST>]]>  
</ws:input>
	  </ws:otpService>
   </soapenv:Body>
</soapenv:Envelope>"""
        print body
        response = requests.post(url, data=body, headers=headers)
        print response.text

        # Parsing now the response.

        response = response.text
        response = response.replace('&lt;', '<')
        response = response.replace('&gt;', '>')

        actcode = parse_otp_send(response)
        print('Act code is: ', actcode)
        data = {}
        if actcode == '000':
            user.unique1 = unique1
            user.unique2 = unique2
            user.save()
        else:
            pass
        return Response(data=data)


class VerifyOTPAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def get(self, request):
        data = request.GET
        message = data.get('message').strip()
        alexa_id = data.get('alexa_id')
        device_id = data.get('device_id')
        access_token = data.get('access_token')
        if Config.objects.all()[0].prod:
            reg_mob_no = get_user_from_access_token(access_token).username
        else:
            reg_mob_no = CustomUser.objects.get(username="8169392028").username
        user = CustomUser.objects.get(username=reg_mob_no)

        unique1 = user.unique1
        unique2 = user.unique2
        headers = {'content-type': 'text/xml', 'SOAPAction': ''}
        url = "http://10.50.81.32:9001/OTPEngine/services/OTPWebService?wsdl"
        body = """<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:ws="http://ws.otp.icicibank.com">
				   <soapenv:Header/>
				   <soapenv:Body>
					  <ws:otpService>
						 <ws:input>
				<![CDATA[<REQUEST>   <ACTCODE/>   <CHANNEL>5</CHANNEL>   <APPLICATION_NAME>67</APPLICATION_NAME>   <FIELD1>""" + unique1 + """</FIELD1>   <FIELD2>""" + unique2 + """</FIELD2>   <FIELD3>SWOPNA</FIELD3>   <AMOUNT>0.0</AMOUNT>   <TRANSACTION_CODE>128</TRANSACTION_CODE>   <VALIDITY>0</VALIDITY>   <DELIVERY_MODE>SMS</DELIVERY_MODE>   <DELIVERY_ADDRESS>""" + reg_mob_no + """</DELIVERY_ADDRESS>   <MANAGED_BY/>   <ACTION>V</ACTION>   <OTP>""" + otp + """</OTP>   <VALIDITY_GIVEN/> </REQUEST>]]> 
				</ws:input>
					  </ws:otpService>
				   </soapenv:Body>
				</soapenv:Envelope>"""
        print(body)
        response = requests.post(url, data=body, headers=headers, timeout=7)
        print(response.text)
        response.text = response.text.replace("&gt;", ">")
        response.text = response.text.replace("&lt;", "<")
        acct = parse_otp_send(response.text)
        # print(acct)
        #acct = "000"
        data = {}
        if (acct != "000"):
            #    return Response(data=response)
            data['response'] = None
        else:
            data['response'] = '1'
        return Response(data=data)


class AccountNumbersOauthAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def post(self, request):
        mobile_number = request.user.username
        print 'YOOOO111'
        response = get_account_numbers_original(mobile_number)
        print 'Okay'
        data = {}
        data['numbers'] = response
        return Response(data=data)


class GetListOfPayeesAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def get(self, request):
        data = request.GET
        user_id = data.get('user_id')
        alexa_id = data.get('alexa_id')
        device_id = data.get('device_id')
        access_token = data.get('access_token')
        type_of_connection = data.get('typeconn')
        print(type_of_connection)
        # mobile_number = get_user_from_access_token(access_token).username
        # Remove comment when production
        if Config.objects.all()[0].prod:
            mobile_number = get_user_from_access_token(access_token).username
        else:
            mobile_number = CustomUser.objects.get(
                username="8169392028").username
        print("The mobile number is: ", mobile_number)
        # mobile_number = '7032770360'  # Currently Testing
        print 'YOOOO'
        response = get_list_of_payees(mobile_number, type_of_connection)
        write_file(str(response) + "AAA")
        if len(response) == 0:
            data = {}
            data["numbers"] = ""
            data["success"] = "false"
            data["message"] = "You have no payees registered"
            return Response(data=data)
        if response == "-5":
            data = {}
            data["numbers"] = ""
            data["success"] = "false"
            data["message"] = "You have no payees registered"
            return Response(data=data)
        print 'Okay'
        data = {}
        data['numbers'] = response
        return Response(data=data)


class GetListOfConnectionAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def get(self, request):
        write_file("AAA")

        data = request.GET
        user_id = data.get('user_id')
        write_file("AAA")

        alexa_id = data.get('alexa_id')
        device_id = data.get('device_id')
        write_file("AAA")

        access_token = data.get('access_token')
        write_file("AAA")
        # mobile_number = get_user_from_access_token(access_token).username
        # Remove comment when production
        if Config.objects.all()[0].prod:
            mobile_number = get_user_from_access_token(access_token).username
        else:
            mobile_number = CustomUser.objects.get(
                username="8169392028").username

        print("The mobile number is: ", mobile_number)
        # mobile_number = '7032770360'  # Currently Testing
        print 'YOOOO'
        response = get_list_of_connections(mobile_number)
        write_file(str(response))
        if len(response) == 0:
            data = {}
            data["numbers"] = ""
            data["success"] = "false"
            data["message"] = "You have no payees registered"
            return Response(data=data)
        if response == "-5":
            data = {}
            data["numbers"] = ""
            data["success"] = "false"
            data["message"] = "You have no payees registered"
            return Response(data=data)
        print 'Okay'
        data = {}
        data['numbers'] = response
        return Response(data=data)

class TopupValuesAPIView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def get(self, request):
        data = request.GET

        user_id = data.get('user_id', None)
        alexa_id = data.get('alexa_id', None)
        device_id = data.get('device_id', None)
        access_token = data.get('access_token', None)
        amount = data.get('amt', None)
        plan = data.get('plan', None)
        print(access_token, amount)
        if amount is not None:
            amount = amount.strip()
        if plan is not None:
            plan = plan.strip()
        print(plan)
        # mobile_number = get_user_from_access_token(access_token).username
        # Remove comment when production
        if Config.objects.all()[0].prod:
            mobile_number = get_user_from_access_token(access_token).username
        else:
            mobile_number = CustomUser.objects.get(
                username="8169392028").username
        print("The mobile number is: ", mobile_number)
        # mobile_number = '7032770360'  # Currently Testing
        print 'YOOOO'
        response = get_different_topup_plans(mobile_number, plan)
        if response == "-5":
            data = {}
            data["numbers"] = ""
            data["success"] = "false"
            data["message"] = "You have no topups registered"
        if len(response) == 0:
            data = {}
            data["numbers"] = ""
            data["success"] = "false"
            data["message"] = "You have no topups registered"
            return Response(data=data)
        print 'Okay'

        try:
            if Config.objects.all()[0].prod:
                user = get_user_from_access_token(access_token).username
                user = CustomUser.objects.get(username=user)
                print(user)
            else:
                user = CustomUser.objects.get(username="8169392028")
            user_params = json.loads(user.user_params)
            print(user_params)
            mpin_recharge_limit = user_params["mpin_recharge_limit"]
            mpin_bill_limit = user_params["mpin_bill_limit"]

            if amount is not None:
                if int(amount) < int(mpin_recharge_limit):
                    choice = '1'
                else:
                    choice = '2'
            else:
                if int(amt) < int(mpin_bill_limit):
                    choice = '1'
                else:
                    choice = '2'
            if choice == '1':
                Data(entity_name='Decision3', entity_value='Less than MPIN',
                     user=Profile.objects.get(user_id=user_id)).save()
            else:
                Data(entity_name='Decision3',
                     entity_value='Greater than MPIN',
                     user=Profile.objects.get(user_id=user_id)).save()
        except:
            pass

        data = {}
        data['numbers'] = response
        return Response(data=data)

class TopupListAPIView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def get(self, request):
        data = request.GET

        user_id = data.get('user_id', None)
        alexa_id = data.get('alexa_id', None)
        device_id = data.get('device_id', None)
        access_token = data.get('access_token', None)
        amount = data.get('amt', None)
        print(access_token, amount)
        if amount is not None:
            amount = amount.strip()
        # mobile_number = get_user_from_access_token(access_token).username
        # Remove comment when production
        if Config.objects.all()[0].prod:
            mobile_number = get_user_from_access_token(access_token).username
        else:
            mobile_number = CustomUser.objects.get(
                username="8169392028").username
        print("The mobile number is: ", mobile_number)
        # mobile_number = '7032770360'  # Currently Testing
        print 'YOOOO'
        response = get_topup_list(mobile_number)
        if response == "-5":
            data = {}
            data["numbers"] = ""
            data["success"] = "false"
            data["message"] = "You have no topups registered"
        if len(response) == 0:
            data = {}
            data["numbers"] = ""
            data["success"] = "false"
            data["message"] = "You have no topups registered"
            return Response(data=data)
        print 'Okay'
        data = {}
        data['numbers'] = response
        return Response(data=data)

class AccountNumbersAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def get(self, request):
        data = request.GET

        user_id = data.get('user_id', None)
        alexa_id = data.get('alexa_id', None)
        device_id = data.get('device_id', None)
        access_token = data.get('access_token', None)
        print(access_token)
        # mobile_number = get_user_from_access_token(access_token).username
        # Remove comment when production
        if Config.objects.all()[0].prod:
            mobile_number = get_user_from_access_token(access_token).username
        else:
            mobile_number = CustomUser.objects.get(
                username="8169392028").username
        print("The mobile number is: ", mobile_number)
        # mobile_number = '7032770360'  # Currently Testing
        print 'YOOOO'
        response = get_account_numbers(mobile_number)
        if response == "-5":
            data = {}
            data["numbers"] = ""
            data["success"] = "false"
            data["message"] = "You have no accounts registered"
        if len(response) == 0:
            data = {}
            data["numbers"] = ""
            data["success"] = "false"
            data["message"] = "You have no accounts registered"
            return Response(data=data)
        print 'Okay'
        data = {}
        data['numbers'] = response
        return Response(data=data)


class AccountNumbersBalanceAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def get(self, request):
        data = request.GET
        user_id = data.get('user_id')
        alexa_id = data.get('alexa_id')
        device_id = data.get('device_id')
        access_token = data.get('access_token')

        account_number = data.get('accnum')
        print('AAAAAAAAAAAAAAA: ', account_number)

        # print("AAAAAAAAAAA: ", data)
        if Config.objects.all()[0].prod:
            mobile_number = get_user_from_access_token(access_token).username
        else:
            mobile_number = CustomUser.objects.get(
                username="8169392028").username
        # Uncomment in prod
        balance = get_balance(account_number, mobile_number)

        if(balance == "-5"):
            data = {}
            temp_data = {}
            temp_data["success"] = "false"
            temp_data["message"] = "Something1"
            data["answer"] = temp_data
            return Response(data=data)

        if(balance == ""):
            data = {}
            temp_data = {}
            temp_data["success"] = "false"
            temp_data["message"] = "Something1"
            data["answer"] = temp_data
            return Response(data=data)

        sign = balance[0]        
        value = balance[0:]

        available_bal = value[0].lstrip('0')
        fd_bal = value[1].lstrip('0')
        effective_bal = value[2].lstrip('0')

        final_data = {}
        data = {}
        data['available_bal'] = available_bal
        data['fd_bal'] = fd_bal
        data['effective_bal'] = effective_bal

        final_data['answer'] = data

        print(final_data)
        
        return Response(data=final_data)


class CreditCardDateAmountAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def get(self, request):
        data = request.GET
        user_id = data.get('user_id')

        alexa_id = data.get('alexa_id')
        device_id = data.get('device_id')
        access_token = data.get('access_token')
        credit_card_num = data.get('creditcardnum')
        print('Credit card num is: ', credit_card_num)
        if Config.objects.all()[0].prod:
            mobile_number = get_user_from_access_token(access_token).username
        else:
            mobile_number = CustomUser.objects.get(
                username="8169392028").username
        (due_date, due_amount) = \
            get_credit_card_details(credit_card_num, mobile_number)

        sign = due_amount[0]
        if sign == "-":
            value = due_amount[1:]
            due_amount = str(float(value) / 100)
        else:
            due_amount = str(float(due_amount) / 100)

        final_data = {}
        data = {}
        data['due_date'] = due_date
        data['due_amount'] = due_amount
        final_data['answer'] = data
        return Response(data=final_data)


class CreditCardBillPayAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def get(self, request):
        data = request.GET
        user_id = data.get('user_id')

        alexa_id = data.get('alexa_id')
        device_id = data.get('device_id')
        access_token = data.get('access_token')
        creditcardnum = data.get('creditcardnum')

        # mobile_number = get_user_from_access_token(access_token).username
        # Remove comment when production
        if Config.objects.all()[0].prod:
            mobile_number = get_user_from_access_token(access_token).username
        else:
            mobile_number = CustomUser.objects.get(
                username="8169392028").username
        print("The mobile number is: ", mobile_number)
        user = CustomUser.objects.get(username=mobile_number)
        # mobile_number = '7032770360'  # Currently Testing
        user_params = json.loads(user.user_params)
        account_number = user_params["default_account"]
        response = pay_credit_card_bill(
            mobile_number, creditcardnum, account_number)

        answer = '000'  # Succesful Payment

        if answer == '000':
            message = \
                'Your credit card bill has been paid successfully.'
        else:
            message = \
                'Well, Sorry seems we have some issue paying your bill.'

        final_data = {}
        data = {}
        data['message'] = message
        final_data['answer'] = data

        return Response(data=final_data)


class RechargeNamesAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def get(self, request):
        data = request.GET
        user_id = data.get('user_id')

        alexa_id = data.get('alexa_id')
        device_id = data.get('device_id')
        access_token = data.get('access_token')

        temp_list = []

        # Get Nick, Number and Pass'
        if Config.objects.all()[0].prod:
            user = get_user_from_access_token(access_token).username
            user = CustomUser.objects.get(username=user)
            print(user)
        else:
            user = CustomUser.objects.get(username="8169392028")
            print(user)

        flag = check_velocity("Recharge", user.username)

        if not flag:
            data = {}
            data["numbers"] = ""
            data["success"] = "false"
            data["message"] = "Velocity Message"
            return Response(data=data)

        user_params = json.loads(user.user_params)
        print(user_params)

        if(user_params["recharge_checked"] == "false"):
            print("WTF M8")
            data = {}
            data["numbers"] = ""
            data["success"] = "false"
            data[
                "message"] = "Sorry, Recharge facility is not enabled on the provided mobile number"
            print("WTF M8")
            return Response(data=data)

        temp_list = []
        if user_params["nick_1"] != "" and user_params["mob_1"] != "":
            temp_tuple = (user_params["nick_1"], user_params["mob_1"])
            temp_list.append(temp_tuple)
        if user_params["nick_2"] != "" and user_params["mob_2"] != "":
            temp_tuple = (user_params["nick_2"], user_params["mob_2"])
            temp_list.append(temp_tuple)
        if user_params["nick_3"] != "" and user_params["mob_3"] != "":
            temp_tuple = (user_params["nick_3"], user_params["mob_3"])
            temp_list.append(temp_tuple)
        if user_params["nick_4"] != "" and user_params["mob_4"] != "":
            temp_tuple = (user_params["nick_4"], user_params["mob_4"])
            temp_list.append(temp_tuple)

        #temp_list = [('Harsh', '7032770360'), ('Aman', '7990801839')]
        final_data = {}
        final_data['numbers'] = temp_list
        return Response(data=final_data)


class PayBill2APIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def get(self, request):
        data = request.GET
        user_id = data.get('user_id')

        alexa_id = data.get('alexa_id')
        device_id = data.get('device_id')
        access_token = data.get('access_token')
        write_file(access_token)
        amount = str(int(data.get('amount').strip()) * 100)
        typepayee = data.get('typepayee').strip()
        write_file(amount)
        write_file(typepayee)
        print('Data: ', data)
        print('Amount is: ', amount)

        if Config.objects.all()[0].prod:
            username = get_user_from_access_token(access_token).username
        else:
            username = CustomUser.objects.get(username="8169392028").username
        print("The mobile number is: ", mobile_number)
        user = CustomUser.objects.get(username=username)
        # mobile_number = '7032770360'  # Currently Testing
        user_params = json.loads(user.user_params)
        write_file(str(user_params))
        account_number = user_params["default_account"]
        write_file(account_number)
        #write_file(amount, mobile_number, account_number)
        consumer_code = typepayee.split(",")[2]
        payee_id = typepayee.split(",")[3]
        response = pay_bill(mobile_number, amount,
                            account_number, consumer_code, payee_id)
        write_file(str(response))
        # answer = "1" # Succesful Recharge

        if response == '000':
            message = 'Thanks, your recharge has been successful.'
        else:
            message = 'Well, Sorry seems we have some issue.'

        final_data = {}
        data = {}
        data['message'] = message
        final_data['answer'] = data

        return Response(data=final_data)


def save_to_velocity_log(name, mobile_number):
    VelocityLogs(velocity_id=name,
                 mobile_number=mobile_number).save()


def check_velocity(name, mobile_number):
    velocity_time = VelocityChanges.objects.get(
        velocity_name=name).velocity_time
    velocity_times = VelocityChanges.objects.get(
        velocity_name=name).velocity_times

    end_date = datetime.datetime.now()
    start_date = datetime.datetime.now() - datetime.timedelta(minutes=int(velocity_time))
    count = VelocityLogs.objects.filter(
        mobile_number=mobile_number, time_created__range=(start_date, end_date)).count()

    print("Count is: ", count)
    if(count >= int(velocity_times)):
        print("FALSE: ")
        return False
    else:
        print("TRUE")
        return True

class TopupActivateAPIView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def get(self, request):
        data = request.GET
        user_id = data.get('user_id')

        alexa_id = data.get('alexa_id')
        device_id = data.get('device_id')
        access_token = data.get('access_token')
        write_file(access_token)
        amount = str(int(data.get('amount').strip()) * 100)
        mobile_number = data.get('mobnum').strip()
        mobile_number = mobile_number.replace("@", "")
        write_file(amount)
        write_file(mobile_number)
        print('Data: ', data)
        print('Amount is: ', amount)

        if Config.objects.all()[0].prod:
            username = get_user_from_access_token(access_token).username
        else:
            username = CustomUser.objects.get(username="8169392028").username
        user = CustomUser.objects.get(username=username)
        user_params = json.loads(user.user_params)
        write_file(str(user_params))
        account_number = user_params["default_account"]
        write_file(account_number)
        #write_file(amount, mobile_number, account_number)
        response = recharge_mobile_topup(mobile_number, amount, account_number)
        write_file(str(response))
        # answer = "1" # Succesful Recharge

        if response == '000':
            save_to_velocity_log("Recharge", username)
            message = 'Thanks, your topup has been activated.'
        else:
            message = 'Well, Sorry seems we have some issue.'

        final_data = {}
        data = {}
        data['message'] = message
        final_data['answer'] = data

        return Response(data=final_data)

class RechargeMobileAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def get(self, request):
        data = request.GET
        user_id = data.get('user_id')

        alexa_id = data.get('alexa_id')
        device_id = data.get('device_id')
        access_token = data.get('access_token')
        write_file(access_token)
        amount = str(int(data.get('amount').strip()) * 100)
        mobile_number = data.get('mobnum').strip()
        mobile_number = mobile_number.replace("@", "")
        write_file(amount)
        write_file(mobile_number)
        print('Data: ', data)
        print('Amount is: ', amount)

        if Config.objects.all()[0].prod:
            username = get_user_from_access_token(access_token).username
        else:
            username = CustomUser.objects.get(username="8169392028").username
        print("The mobile number is: ", mobile_number)
        user = CustomUser.objects.get(username=username)
        # mobile_number = '7032770360'  # Currently Testing
        user_params = json.loads(user.user_params)
        write_file(str(user_params))
        account_number = user_params["default_account"]
        write_file(account_number)
        #write_file(amount, mobile_number, account_number)
        response = recharge_mobile(mobile_number, amount, account_number)
        write_file(str(response))
        # answer = "1" # Succesful Recharge

        if response == '000':
            save_to_velocity_log("Recharge", username)
            message = 'Thanks, your recharge has been successful.'
        else:
            message = 'Well, Sorry seems we have some issue.'

        final_data = {}
        data = {}
        data['message'] = message
        final_data['answer'] = data

        return Response(data=final_data)


class RechargeNameMatchAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def get(self, request):
        data = request.GET

        message = data.get('message')
        alexa_id = data.get('alexa_id')
        device_id = data.get('device_id')
        access_token = data.get('access_token')

        print('Message is: ', message)

        mobile_number = None
        if Config.objects.all()[0].prod:
            user = get_user_from_access_token(access_token).username
            user = CustomUser.objects.get(username=user)
            print(user)
        else:
            user = CustomUser.objects.get(username="8169392028")
            print(user)

        
        print(user.user_params)
        user_params = json.loads(user.user_params)
        print(user_params)
        if(user_params["recharge_checked"] == "false"):
            data = {}
            data["response"] = None
            return Response(data=data)

        nick_list = []
        mob_list = []
        if user_params["nick_1"] != "" and user_params["mob_1"] != "":
            nick_list.append(user_params["nick_1"])
            mob_list.append(user_params["mob_1"])
        if user_params["nick_2"] != "" and user_params["mob_2"] != "":
            nick_list.append(user_params["nick_2"])
            mob_list.append(user_params["mob_2"])
        if user_params["nick_3"] != "" and user_params["mob_3"] != "":
            nick_list.append(user_params["nick_3"])
            mob_list.append(user_params["mob_3"])
        if user_params["nick_4"] != "" and user_params["mob_4"] != "":
            nick_list.append(user_params["nick_4"])
            mob_list.append(user_params["mob_4"])
        for word in message.split(' '):
            for i in range(len(nick_list)):
                if nick_list[i].lower() == word.lower():
                    mobile_number = mob_list[i]
                    mobile_number = "@".join(mobile_number)
        print('Mobile number is: ', mobile_number)
        final_data = {}
        final_data['response'] = mobile_number

        return Response(data=final_data)


class LastTransactionsAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def get(self, request):
        data = request.GET
        user_id = data.get('user_id')

        alexa_id = data.get('alexa_id')
        device_id = data.get('device_id')
        access_token = data.get('access_token')
        credit_card_num = data.get('creditcardnum')

        if Config.objects.all()[0].prod:
            mobile_number = get_user_from_access_token(access_token).username
        else:
            mobile_number = CustomUser.objects.get(
                username="8169392028").username

        last_transactions = get_last_transactions(credit_card_num, mobile_number)

        # message = "Here are the details of your last 2 Transactions. \n 1) Transaction description: INFINITY PAYMENT RECEIVED, THANK YOU, Amount: Rs. 16730.00 \n 2) Transaction description: VELKAR AUTO SERVICE, Amount: Rs. 780.00"
        message = "Here are the details of your last "+str(len(last_transactions))+" transactions. "

        cnt = 0
        for ran_tup in last_transactions:
            desc = ran_tup[0]
            amt = ran_tup[1]
            cnt = cnt + 1
            message = message + str(cnt) + ") Transaction description: "+desc+" . Amount: "+amt+" . " 


        final_data = {}
        data = {}
        data['message'] = message
        final_data['answer'] = data

        return Response(data=final_data)


class SaveChoice2APIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def get(self, request):
        data = request.GET
        print data

        user_id = data.get('user_id')

        alexa_id = data.get('alexa_id')
        device_id = data.get('device_id')
        access_token = data.get('access_token')

        amount = data.get('amount', None)
        amt = data.get('amt', None)

        # Now here fetch the mobile number of the above person.
        # Once you fetch the mobile number, check the bill limit of the guy.
        if Config.objects.all()[0].prod:
            user = get_user_from_access_token(access_token).username
            user = CustomUser.objects.get(username=user)
            print(user)
        else:
            user = CustomUser.objects.get(username="8169392028")
        user_params = json.loads(user.user_params)
        print(user_params)
        mpin_recharge_limit = user_params["mpin_recharge_limit"]
        mpin_bill_limit = user_params["mpin_bill_limit"]

        #mpin_recharge_limit = '1000'
        if amount is not None:
            if int(amount) < int(mpin_recharge_limit):
                choice = '1'
            else:
                choice = '2'
        else:
            if int(amt) < int(mpin_bill_limit):
                choice = '1'
            else:
                choice = '2'

        # If the amount is less than the mpin amount, return 1
        # Else if it's greater than the mpin amount, return 2

        print('CHOICCCCEEEEEEE: ', choice, amount)

        # choice = "1"

        if choice == '1':
            Data(entity_name='Decision2', entity_value='Less than MPIN',
                 user=Profile.objects.get(user_id=user_id)).save()
        else:
            Data(entity_name='Decision2',
                 entity_value='Greater than MPIN',
                 user=Profile.objects.get(user_id=user_id)).save()
        return Response(data={})


class SaveChoiceAPIView(APIView):

    authentication_classes = (CsrfExemptSessionAuthentication,
                              BasicAuthentication)

    def get(self, request):
        data = request.GET
        print data

        user_id = data.get('user_id')

        alexa_id = data.get('alexa_id')
        device_id = data.get('device_id')
        access_token = data.get('access_token')

        amount = data.get('amount', None)
        amt = data.get('amt', None)

        # Now here fetch the mobile number of the above person.
        # Once you fetch the mobile number, check the bill limit of the guy.
        if Config.objects.all()[0].prod:
            user = get_user_from_access_token(access_token).username
        else:
            user = CustomUser.objects.get(username="8169392028").username
        user = CustomUser.objects.get(username=user)
        print(user)
        user_params = json.loads(user.user_params)
        print(user_params)
        mpin_recharge_limit = user_params["mpin_recharge_limit"]

        mpin_bill_limit = '1000'
        #mpin_recharge_limit = '1000'
        if amount is not None:
            if int(amount) < int(mpin_recharge_limit):
                choice = '1'
            else:
                choice = '2'
        else:
            if int(amt) < int(mpin_bill_limit):
                choice = '1'
            else:
                choice = '2'

        # If the amount is less than the mpin amount, return 1
        # Else if it's greater than the mpin amount, return 2

        print('CHOICCCCEEEEEEE: ', choice, amount)

        # choice = "1"

        if choice == '1':
            Data(entity_name='Decision', entity_value='Less than MPIN',
                 user=Profile.objects.get(user_id=user_id)).save()
        else:
            Data(entity_name='Decision',
                 entity_value='Greater than MPIN',
                 user=Profile.objects.get(user_id=user_id)).save()
        return Response(data={})

def Login(request):

   return render(request, 'engine/login.html')



@login_required(login_url='/chat/login/')
def GetBusinessDashboard(request):

   try:

       logs_b_list = Logs_B.objects.all()

       paginator = Paginator(logs_b_list, 10)

       page = request.GET.get('page', 1)

       logs_b_objs = paginator.page(page)

       return render(request, 'engine/dashboard_business.html', {'logs_b_objs': logs_b_objs})

   except Exception as e:
       print("Error GetBusinessDashboard", str(e))

@login_required(login_url='/chat/login/')
def GetITDashboard(request):

   try:

       logs_it_list = Logs_IT.objects.all()

       paginator = Paginator(logs_it_list, 10)

       page = request.GET.get('page', 1)

       logs_it_objs = paginator.page(page)

       return render(request, 'engine/dashboard_IT.html', {'logs_it_objs': logs_it_objs})

   except Exception as e:
       print("Error GetITDashboard", str(e))


class GetLambdaDataAPIView(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,
                             BasicAuthentication)

    def post(self, request, *args, **kwargs):
       response = {}
       response['status'] = 500
       try:           
           response['start'] = "AAAAAA"
           response['end'] = "BBBBBBBBBbbb"
           response['issue'] = "CCCCCCCC"
           response['status'] = 200
           return Response(data=response)
       except Exception as e:
           print("Error LoginSubmitAPI", str(e))

       return Response(data=response)

class LoginSubmitAPI(APIView):

   authentication_classes = (CsrfExemptSessionAuthentication,
                             BasicAuthentication)

   def post(self, request, *args, **kwargs):

       response = {}
       response['status'] = 500
       try:

           print("AAAA")
           data = request.data

           username = data['username']
           password = data['password']

           user = authenticate(username=username, password=password)

           login(request, user)

           response['status'] = 200

           if(len(ITUser.objects.filter(username=username))==1):
               response['type'] = "IT"
           else:
               response['type'] = "Business"


       except Exception as e:
           print("Error LoginSubmitAPI", str(e))

       return Response(data=response)


@login_required(login_url='/chat/login/')
def Logout(request):

   logout(request)
   return HttpResponseRedirect('/chat/login/')
UpdateUser = UpdateUserAPIView.as_view()
Querys = QueryAPIView.as_view()
Cancel = CancelAPIView.as_view()
QueryFeedbackLike = QueryFeedbackLikeAPIView.as_view()
QueryFeedbackDislike = QueryFeedbackDislikeAPIView.as_view()
GetAnalysis = GetAnalysisAPIView.as_view()
GetPcId = GetPcIdAPIView.as_view()
TestChatbotIntent = TestChatbotIntentAPIView.as_view()
TestChatbotMapper = TestChatbotMapperAPIView.as_view()
GetPolicyDtls = GetPolicyDtlsAPIView.as_view()
GetAllPolicyDtls = GetAllPolicyDtlsAPIView.as_view()
SendPPC = SendPPCAPIView.as_view()
IToS = IToSAPIView.as_view()
SubmitQueries = SubmitQueriesAPIView.as_view()
GetSentences = GetSentencesAPIView.as_view()
SaveSentences = SaveSentencesAPIView.as_view()
TestIntent = TestIntentAPIView.as_view()
GetPpc = GetPPCAPIView.as_view()
SaveLeadData = saveLeadDataAPIView.as_view()
FacebookView = FacebookAPIView.as_view()
AlexaView = AlexaAPIView.as_view()
GoogleHomeView = GoogleHomeAPIView.as_view()
DeleteEntries = DeleteEntriesAPIView.as_view()
AccountNumbers = AccountNumbersAPIView.as_view()
ElecBill = ElecBillAPIView.as_view()
GasBill = GasBillAPIView.as_view()
GetBalance = AccountNumbersBalanceAPIView.as_view()
RechargeMobile = RechargeMobileAPIView.as_view()
SaveChoice = SaveChoiceAPIView.as_view()
CreditCardNumbers = CreditCardNumbersAPIView.as_view()
CreditCardDateAmount = CreditCardDateAmountAPIView.as_view()
CreditCardBillPay = CreditCardBillPayAPIView.as_view()
RechargeNameMatch = RechargeNameMatchAPIView.as_view()
RechargeNames = RechargeNamesAPIView.as_view()
LastTransactions = LastTransactionsAPIView.as_view()
AccountNumbersOauth = AccountNumbersOauthAPIView.as_view()
GetOTP = GetOTPAPIView.as_view()
VerifyOTP = VerifyOTPAPIView.as_view()
GetListOfConnection = GetListOfConnectionAPIView.as_view()
GetListOfPayees = GetListOfPayeesAPIView.as_view()
VerifyMPIN = VerifyMPINAPIView.as_view()
VerifyGrid = VerifyGridAPIView.as_view()
SendOTPTree = SendOTPTreeAPIView.as_view()
PayBill2 = PayBill2APIView.as_view()
SaveChoice2 = SaveChoice2APIView.as_view()
GetLambdaData = GetLambdaDataAPIView.as_view()

LoginSubmit = LoginSubmitAPI.as_view()
TopupList = TopupListAPIView.as_view()
TopupValues = TopupValuesAPIView.as_view()
TopupActivate = TopupActivateAPIView.as_view()