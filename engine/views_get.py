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
import datetime
from pprint import pprint

from django.conf import settings
from django.http import HttpResponse
from django.utils.encoding import smart_str
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication)
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

from .utils import *
from .models import *
from .constants import *

logger = logging.getLogger('my_logger')


class CsrfExemptSessionAuthentication(SessionAuthentication):

    def enforce_csrf(self, request):
        return


def Export(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="mixed.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Tests'
    ])
    writer.writerow([
        'Question',
        'Expected Answer',
        'Actual Answer'
    ])
    test_model = reversed(list(TestModel.objects.all()))
    list_intent = []
    for test in test_model:
        intent = Intent.objects.get(pk=test.intent_id)
        test_sentences = test.sentences
        if test_sentences is not None:
            for sentence in test_sentences.splitlines():
                sentence = sentence.strip()
                if sentence != "":
                    intent_recognized = get_intent(
                        do_pre_processing(sentence, "web", "eng"))
                    if intent_recognized is not None:
                        intent_obj = get_object_or_404(
                            Intent, name=intent_recognized[0].name)
                        if intent_obj.pk != intent.pk:
                            try:
                                answer1 = mark_safe(Intent.objects.get(
                                    name=intent.name).tree.answer.group_of_sentences.all()[0].sentence)
                                answer1 = re.sub(r'<[^>]*?>', '', answer1)
                            except:
                                answer1 = mark_safe(Intent.objects.get(
                                    name=intent.name).tree.question_entity_type.question.group_of_sentences.all()[0].sentence)
                                answer1 = re.sub(r'<[^>]*?>', '', answer1)
                            try:
                                answer2 = mark_safe(Intent.objects.get(
                                    name=intent_obj.name).tree.answer.group_of_sentences.all()[0].sentence)
                                answer2 = re.sub(r'<[^>]*?>', '', answer2)
                            except:
                                answer2 = mark_safe(Intent.objects.get(
                                    name=intent_obj.name).tree.question_entity_type.question.group_of_sentences.all()[0].sentence)
                                answer2 = re.sub(r'<[^>]*?>', '', answer2)
                            writer.writerow([
                                smart_str(sentence),
                                smart_str(answer1),
                                smart_str(answer2),
                            ])
                    else:
                        try:
                            answer1 = mark_safe(Intent.objects.get(
                                name=intent.name).tree.answer.group_of_sentences.all()[0].sentence)
                            answer1 = re.sub(r'<[^>]*?>', '', answer1)
                        except:
                            answer1 = mark_safe(Intent.objects.get(
                                name=intent.name).tree.question_entity_type.question.group_of_sentences.all()[0].sentence)
                            answer1 = re.sub(r'<[^>]*?>', '', answer1)
                        writer.writerow([
                            smart_str(sentence),
                            smart_str(answer1),
                            smart_str(UNRECOGNIZED_MESSAGE),
                        ])

    test_model = reversed(list(TestModel.objects.all()))
    list_intent = []
    for test in test_model:
        intent = Intent.objects.get(pk=test.intent_id)
        test_sentences = test.sentences
        if test_sentences is not None:
            for sentence in test_sentences.splitlines():
                sentence = sentence.strip()
                if sentence != "":
                    intent_recognized = get_intent(
                        do_pre_processing(sentence, "web", "eng"))
                    if intent_recognized is not None:
                        intent_obj = get_object_or_404(
                            Intent, name=intent_recognized[0].name)
                        if intent_obj.pk == intent.pk:
                            try:
                                answer1 = mark_safe(Intent.objects.get(
                                    name=intent.name).tree.answer.group_of_sentences.all()[0].sentence)
                                answer1 = re.sub(r'<[^>]*?>', '', answer1)
                            except:
                                try:
                                    answer1 = mark_safe(Intent.objects.get(
                                        name=intent.name).tree.question_entity_type.question.group_of_sentences.all()[0].sentence)
                                    answer1 = re.sub(r'<[^>]*?>', '', answer1)
                                except:
                                    answer1 = ""
                            writer.writerow([
                                smart_str(sentence),
                                smart_str(answer1),
                                smart_str(answer1),
                            ])
    return response


def FailedExport(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="failed.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Question',
        'Expected Answer',
        'Actual Answer'
    ])
    test_model = reversed(list(TestModel.objects.all()))
    list_intent = []
    for test in test_model:
        try:
            intent = Intent.objects.get(pk=test.intent_id)
            test_sentences = test.sentences
            if test_sentences is not None:
                for sentence in test_sentences.splitlines():
                    sentence = sentence.strip()
                    if sentence != "":
                        intent_recognized = get_intent(
                            do_pre_processing(sentence, "web", "eng"))

                        if intent_recognized is not None:
                            intent_obj = get_object_or_404(
                                Intent, name=intent_recognized[0].name)
                            if intent_obj.pk != intent.pk:
                                try:
                                    answer1 = mark_safe(Intent.objects.get(
                                        name=intent.name).tree.answer.group_of_sentences.all()[0].sentence)
                                    answer1 = re.sub(r'<[^>]*?>', '', answer1)
                                except:
                                    answer1 = mark_safe(Intent.objects.get(
                                        name=intent.name).tree.question_entity_type.question.group_of_sentences.all()[0].sentence)
                                    answer1 = re.sub(r'<[^>]*?>', '', answer1)
                                try:
                                    answer2 = mark_safe(Intent.objects.get(
                                        name=intent_obj.name).tree.answer.group_of_sentences.all()[0].sentence)
                                    answer2 = re.sub(r'<[^>]*?>', '', answer2)
                                except:
                                    answer2 = mark_safe(Intent.objects.get(
                                        name=intent_obj.name).tree.question_entity_type.question.group_of_sentences.all()[0].sentence)
                                    answer2 = re.sub(r'<[^>]*?>', '', answer2)
                                writer.writerow([
                                    smart_str(sentence),
                                    smart_str(answer1),
                                    smart_str(answer2),
                                ])
                        else:
                            try:
                                answer1 = mark_safe(Intent.objects.get(
                                    name=intent.name).tree.answer.group_of_sentences.all()[0].sentence)
                                answer1 = re.sub(r'<[^>]*?>', '', answer1)
                            except:
                                answer1 = mark_safe(Intent.objects.get(
                                    name=intent.name).tree.question_entity_type.question.group_of_sentences.all()[0].sentence)
                                answer1 = re.sub(r'<[^>]*?>', '', answer1)
                            writer.writerow([
                                smart_str(sentence),
                                smart_str(answer1),
                                smart_str(UNRECOGNIZED_MESSAGE),
                            ])
        except Exception as e:
            pass
    return response


def PassedExport(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="passed.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Question',
        'Expected Answer',
        'Actual Answer'
    ])
    test_model = reversed(list(TestModel.objects.all()))
    list_intent = []
    for test in test_model:
        try:
            intent = Intent.objects.get(pk=test.intent_id)
            test_sentences = test.sentences
            if test_sentences is not None:
                for sentence in test_sentences.splitlines():
                    sentence = sentence.strip()
                    if sentence != "":
                        intent_recognized = get_intent(
                            do_pre_processing(sentence, "web", "eng"))
                        if intent_recognized is not None:
                            intent_obj = get_object_or_404(
                                Intent, name=intent_recognized[0].name)
                            if intent_obj.pk == intent.pk:
                                try:
                                    answer1 = mark_safe(Intent.objects.get(
                                        name=intent.name).tree.answer.group_of_sentences.all()[0].sentence)
                                    answer1 = re.sub(r'<[^>]*?>', '', answer1)
                                except:
                                    answer1 = mark_safe(Intent.objects.get(
                                        name=intent.name).tree.question_entity_type.question.group_of_sentences.all()[0].sentence)
                                    answer1 = re.sub(r'<[^>]*?>', '', answer1)
                                writer.writerow([
                                    smart_str(sentence),
                                    smart_str(answer1),
                                    smart_str(answer1),
                                ])
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
        temp_dict["intent"] = intent.name
        temp_dict["id"] = intent.pk
        try:
            count = 0
            for sentence in TestModel.objects.get(name=intent.name).sentences.splitlines():
                if sentence.strip() != "":
                    count = count + 1
            temp_dict["count"] = count
        except:
            temp_dict["count"] = "0"
        items.append(temp_dict)
    return render_to_response('engine/chatbot_test.html', {'intents': items},)


def RunTests(request):
    return render(request, 'engine/uat.html', {})


def Index(request):
    if request.user_agent.is_mobile:
        return render(request, 'engine/index1.html', {})
    else:
        return render(request, 'engine/index.html', {})


class SendPPCAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request):
        try:
            data = request.data

            policy_number = data.get('policy_number').strip()
            financial_year = data.get('fin_year').strip()
            financial_year = financial_year.replace("=", "-")
            url = Config.objects.all()[0].url_customer_id
            headers = {'content-type': 'text/xml'}
            body = """<?xml version="1.0" encoding="utf-8"?>
                    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                      <soap:Body>
                        <getPPC_EasyAccess_mail xmlns="http://tempuri.org/">
                          <strPolicyNumber>""" + policy_number + """</strPolicyNumber>
                          <strFinYear>""" + financial_year + """</strFinYear>
                        </getPPC_EasyAccess_mail>
                      </soap:Body>
                    </soap:Envelope>
                    """
            response = requests.post(url, data=body, headers=headers)
            content = str(response.content)
            content = content[content.find(
                "<getPPC_EasyAccess_mailResult>") + 30:content.find("</getPPC_EasyAccess_mailResult>")]
            content = content.replace("&lt;", "<")
            content = content.replace("&gt;", ">")
            content = content.replace(r"\r", "")
            content = content.replace(r"\n", "")
            answer = content.strip()
            if answer == "0":
                data = {}
                temp_dict = {}
                temp_dict["flag"] = ""
                data["answer"] = temp_dict
            else:
                data = {}
                temp_dict = {}
                temp_dict["flag"] = "temp"
                data["answer"] = temp_dict
            return Response(data=data)
        except:
            data = {}
            temp_dict = {}
            temp_dict["flag"] = ""
            temp_dict["answer"] = ""
            data["answer"] = temp_dict
            return Response(data=data)


class GetAllPolicyDtlsAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request):
        try:
            data = request.data
            policy_number = data.get('policy_number').strip()
            dob = data.get('dob').strip()
            url = Config.objects.all()[0].url_customer_id
            headers = {'content-type': 'text/xml'}
            body = """<?xml version="1.0" encoding="utf-8"?>
                    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                      <soap:Body>
                        <getCustomer_ID xmlns="http://tempuri.org/">
                          <strPolicyNo>""" + policy_number + """</strPolicyNo>
                          <strDOB>""" + dob + """</strDOB>
                        </getCustomer_ID>
                      </soap:Body>
                    </soap:Envelope>
                    """
            response = requests.post(url, data=body, headers=headers)
            content = str(response.content)
            content = content[content.find(
                "<getCustomer_IDResult>") + 22:content.find("</getCustomer_IDResult>")]
            content = content.replace("&lt;", "<")
            content = content.replace("&gt;", ">")
            content = content.replace(r"\r", "")
            content = content.replace(r"\n", "")
            answer = content
            dictt = xmltodict.parse(answer)
            answer = json.loads(json.dumps(dictt))
            customer_id = answer["PolicyDetails"]["Table"]["PL_PERSON_ID"]
            body = """<?xml version="1.0" encoding="utf-8"?>
                    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                      <soap:Body>
                        <showAllPolicyDtls xmlns="http://tempuri.org/">
                          <strCustId>""" + customer_id + """</strCustId>
                        </showAllPolicyDtls>
                      </soap:Body>
                    </soap:Envelope>
                    """
            response = requests.post(url, data=body, headers=headers)
            content = str(response.content)
            content = content[content.find(
                "<showAllPolicyDtlsResult>") + 25:content.find("</showAllPolicyDtlsResult>")]
            content = content.replace("&lt;", "<")
            content = content.replace("&gt;", ">")
            content = content.replace(r"\r", "")
            content = content.replace(r"\n", "")
            answer = content
            answer = answer.replace("'", '')
            answer = answer.replace("\\", '')
            answer = answer.replace(" xml:space=preserve", '')

            data = {}

            temp_dict = {}
            temp_dict["answer"] = answer
            temp_dict["flag"] = "temp"
            data["answer"] = temp_dict
            return Response(data=data)
        except Exception as e:
            data = {}
            temp_dict = {}
            temp_dict["flag"] = ""
            temp_dict["answer"] = ""
            data["answer"] = temp_dict
            return Response(data=data)


class GetPolicyDtlsAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request):
        try:
            data = request.data
            policy_number = data.get('policy_number').strip()
            dob = data.get('dob').strip()
            url = Config.objects.all()[0].url_customer_id
            headers = {'content-type': 'text/xml'}
            body = """<?xml version="1.0" encoding="utf-8"?>
                    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                      <soap:Body>
                        <getCustomer_ID xmlns="http://tempuri.org/">
                          <strPolicyNo>""" + policy_number + """</strPolicyNo>
                          <strDOB>""" + dob + """</strDOB>
                        </getCustomer_ID>
                      </soap:Body>
                    </soap:Envelope>
                    """
            response = requests.post(url, data=body, headers=headers)
            content = str(response.content)
            content = content[content.find(
                "<getCustomer_IDResult>") + 22:content.find("</getCustomer_IDResult>")]
            content = content.replace("&lt;", "<")
            content = content.replace("&gt;", ">")
            content = content.replace(r"\r", "")
            content = content.replace(r"\n", "")
            answer = content
            dictt = xmltodict.parse(answer)
            answer = json.loads(json.dumps(dictt))
            customer_id = answer["PolicyDetails"]["Table"]["PL_PERSON_ID"]
            body = """<?xml version="1.0" encoding="utf-8"?>
                    <soap:Envelope xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/">
                      <soap:Body>
                        <showPolicyDtls xmlns="http://tempuri.org/">
                          <strPolicyNumber>""" + policy_number + """</strPolicyNumber>
                          <userId>""" + customer_id + """</userId>
                        </showPolicyDtls>
                      </soap:Body>
                    </soap:Envelope>
                    """
            response = requests.post(url, data=body, headers=headers)
            content = str(response.content)
            content = content[content.find(
                "<showPolicyDtlsResult>") + 22:content.find("</showPolicyDtlsResult>")]
            content = content.replace("&lt;", "<")
            content = content.replace("&gt;", ">")
            content = content.replace(r"\r", "")
            content = content.replace(r"\n", "")
            answer = content

            data = {}

            temp_dict = {}
            temp_dict["answer"] = answer
            temp_dict["flag"] = "temp"
            data["answer"] = temp_dict
            return Response(data=data)
        except Exception as e:
            data = {}
            temp_dict = {}
            temp_dict["flag"] = ""
            temp_dict["answer"] = ""
            data["answer"] = temp_dict
            return Response(data=data)


class IToSAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request):
        data = request.data
        intent_id = data.get('intent_id')
        intent = Intent.objects.get(pk=intent_id)
        return Response(data={"answer": intent.tree.answer.group_of_sentences.all()[0].pk})
        pass


class TestChatbotMapperAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request):
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
                        temp_dict["wordmapper_keyword"] = keyword
                        temp_dict["intent"] = smart_str(intent.name)
                        temp_dict["intent_keyword_remove"] = smart_str(
                            ','.join(keyword_set))
                        list_mapper.append(temp_dict)
        return Response(data={"mappers": list_mapper})


class TestIntentAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request):
        test_model = reversed(list(TestModel.objects.all()))
        list_intent = []
        for test in test_model:
            intent = Intent.objects.get(pk=test.intent_id)
            test_sentences = test.sentences
            if test_sentences is not None:
                for sentence in test_sentences.splitlines():
                    sentence = sentence.strip()
                    if sentence != "":
                        intent_recognized = get_intent(
                            do_pre_processing(sentence, "web", "eng"))
                        if intent_recognized is not None:
                            intent_obj = get_object_or_404(
                                Intent, name=intent_recognized[0].name)
                            if intent_obj.pk != intent.pk:
                                temp_dict = {}
                                temp_dict["sentence"] = smart_str(sentence)
                                temp_dict["intent"] = smart_str(intent.name)
                                temp_dict["intent_recognized"] = smart_str(
                                    intent_obj.name)
                                temp_dict["level1"] = intent.level
                                temp_dict["level2"] = intent_obj.level
                                temp_dict["id1"] = intent.pk
                                temp_dict["id2"] = intent_obj.pk
                                list_intent.append(temp_dict)
                        else:
                            temp_dict = {}
                            temp_dict["sentence"] = smart_str(sentence)
                            temp_dict["intent"] = smart_str(test.name)
                            temp_dict["intent_recognized"] = ""
                            temp_dict["level1"] = intent.level
                            temp_dict["level2"] = ""
                            temp_dict["id1"] = intent.pk
                            list_intent.append(temp_dict)
        return Response(data={"intents": list_intent})


class TestChatbotIntentAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request):
        intents = Intent.objects.all()
        list_intent = []
        count = 0
        for intent in intents:
            count = count + 1
            test_sentences = intent.test_sentences
            for sentence in test_sentences.splitlines():
                sentence = sentence.strip()
                intent_recognized = get_intent(
                    do_pre_processing(sentence, "web", "eng"))
                if intent_recognized is not None:
                    intent_obj = get_object_or_404(
                        Intent, name=intent_recognized[0].name)
                    if intent_obj.pk != intent.pk:
                        temp_dict = {}
                        temp_dict["sentence"] = smart_str(sentence)
                        temp_dict["intent"] = smart_str(intent.name)
                        temp_dict["intent_recognized"] = smart_str(
                            intent_obj.name)
                        temp_dict["level1"] = intent.level
                        temp_dict["level2"] = intent_obj.level
                        list_intent.append(temp_dict)
                else:
                    temp_dict = {}
                    temp_dict["sentence"] = smart_str(sentence)
                    temp_dict["intent"] = smart_str(intent.name)
                    temp_dict["intent_recognized"] = ""
                    temp_dict["level1"] = intent.level
                    temp_dict["level2"] = ""
                    list_intent.append(temp_dict)
        return Response(data={"intents": list_intent})


def TestChatbot(request):
    return render(request, 'engine/testing.html', {})


def Iframe(request):
    return render(request, 'engine/chatbox.html', {})


def Analytics(request):
    return render(request, 'engine/analytics.html')


class CancelAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request):
        data = request.GET
        response_json = {}
        response_json["is_typable"] = "true"
        user_id = data.get('user_id', False)
        clear_data_from_model(user_id)
        reset_user(user_id)
        response_json["response"] = Config.objects.all()[0].initial_message
        response_json["recommended_queries"] = initial_base_response()
        return Response(data=response_json)


class QueryFeedbackLikeAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args, **kwargs):
        data = self.kwargs
        user_id = data["user_id"]
        query_id = data["query_id"]
        try:
            fdback = QueryFeedbackCounter.objects.filter(user__user_id=user_id,
                                                         query__pk=query_id).get()
            fdback.like_cnt = 1
            if fdback.dislike_cnt == 1:
                fdback.dislike_cnt = 0
            fdback.save()
        except Exception as e:
            user = Profile.objects.get(user_id=user_id)
            QueryFeedbackCounter(user=user,
                                 like_cnt=1,
                                 query_id=query_id).save()
            logger.error(
                "class: QueryFeedbackLikeAPIView, method: get %s", str(e))
        return Response(data={})


class QueryFeedbackDislikeAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request, *args, **kwargs):
        data = self.kwargs
        user_id = data["user_id"]
        query_id = data["query_id"]
        try:
            fdback = QueryFeedbackCounter.objects.filter(user__user_id=user_id,
                                                         query__pk=query_id).get()
            fdback.dislike_cnt = 1
            if fdback.like_cnt == 1:
                fdback.like_cnt = 0
            fdback.save()
        except Exception as e:
            user = Profile.objects.get(user_id=user_id)
            QueryFeedbackCounter(user=user,
                                 dislike_cnt=1,
                                 query_id=query_id).save()
            logger.error(
                "class: QueryFeedbackDislikeAPIView, method: get %s", str(e))
        return Response(data={})


class QueryAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request):
        data = request.GET
        message = data.get('message', False)
        user_id = data.get('user_id', False)
        channel = data.get('channel', False)
        language = data.get('language', False)
        clicked = data.get('clicked', False)
        pipe = data.get('pipe', False)
        message = message.lower()
        if message.lower().strip() == "home" or message.lower().strip() == "cancel":
            if channel == "whatsapp":
                response_json = {}
                response_json["show_menu_fast"] = "1"
                clear_data_from_model(user_id)
                reset_user(user_id)
                #user = Profile.objects.get(user_id=user_id)
                #user.tree = Tree.objects.get(name="sbi life main tree.Tree")
                #user.save()
                return Response(data=response_json)
        user = Profile.objects.get(user_id=user_id)
        current_tree = user.tree
        if channel.lower() == "whatsapp":
            message = change_number_to_text(current_tree, message)
        if channel.lower() == "alexa" or channel.lower() == "whatsapp":
            pipe = message + "|"
            response_json = process_message_without_pipe(
                current_tree, message, user_id, channel, language, clicked, pipe)
        else:
            response_json = process_message_with_pipe(
                current_tree, message, user_id, channel, language, clicked, pipe)
        if channel.lower() == "whatsapp" and 'is_answer' in response_json:
            if response_json["is_answer"] == "true" and channel.lower() == "whatsapp":
                response_json["show_menu"] = "1"
                clear_data_from_model(user_id)
                reset_user(user_id)
                #user = Profile.objects.get(user_id=user_id)
                #user.tree = Tree.objects.get(name="sbi life main tree.Tree")
                #user.save()
        return Response(data=response_json)


class UpdateUserAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request):
        data = request.GET
        try:
            Profile.objects.get(user_id=data.get('user_id'))
        except:
            dict2 = {}
            dict2['user_id'] = data.get('user_id')
            Profile.objects.create(**dict2)
        response_json = {}
        response_json["is_typable"] = TRUE
        response_json["response"] = Config.objects.all()[0].initial_message
        list_temp = initial_base_response()
        response_json["recommended_queries"] = list_temp
        logger.info(response_json)
        #a = Profile.objects.get(user_id=data.get('user_id'))
        #a.tree = Tree.objects.get(name="main.Tree")
        #a.save()
        return Response(data=response_json)


def Report(request, from_date, to_date):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sia_report.csv"'
    writer = csv.writer(response)
    writer.writerow([
        'Message Text',
        'Answered (Yes or No)',
        'user_id',
        'chatbot_answer',
        'language',
        'channel',
        'time',
        'clicked'
    ])
    from_date = from_date.split("/")
    to_date = to_date.split("/")
    start_date = date(int(from_date[2]), int(from_date[1]), int(from_date[0]))
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
                clicked
            ])
    return response


class GetPcIdAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request):
        data = request.GET
        pc_id = data.get('pcid')
        try:
            UniqueUsers.objects.filter(user_id=pc_id).get()
        except Exception as e:
            p = UniqueUsers(user_id=pc_id)
            p.save()
        return Response(data={})


def ChatTesting(request, *args, **kwargs):
    return render(request, 'engine/chat_testing.html', {})


class SaveSentencesAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request):
        data = request.GET
        intent_id = data.get('intent_id')
        sentences = data.get('sentences')
        try:
            test_model = TestModel.objects.get(intent_id=intent_id)
            test_model.sentences = sentences
            test_model.save()
            return Response(data={})
        except:
            intent_name = Intent.objects.get(id=intent_id).name
            TestModel(intent_id=intent_id,
                      name=intent_name,
                      sentences=sentences).save()
            return Response(data=data)
        pass


class GetSentencesAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request):
        data = request.GET
        intent_id = data.get('intent_id')
        try:
            test_model = TestModel.objects.get(intent_id=intent_id)
            name = test_model.name
            sentences = test_model.sentences
            data = {}
            data["name"] = name
            data["sentences"] = sentences
            try:
                data["answer"] = Intent.objects.get(
                    name=name).tree.answer.group_of_sentences.all()[0].sentence
            except:
                data["answer"] = NESTED_QUESTION
            if sentences is None:
                sentences = ""
            return Response(data=data)
        except:
            intent_name = Intent.objects.get(id=intent_id).name
            TestModel(intent_id=intent_id,
                      name=intent_name).save()
            data = {
            }
            data["name"] = intent_name
            data["sentences"] = ""
            try:
                data["answer"] = Intent.objects.get(
                    name=intent_name).tree.answer.group_of_sentences.all()[0].sentence
            except:
                data["answer"] = NESTED_QUESTION
            return Response(data=data)


class SubmitQueriesAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request):
        data = request.GET
        intent = data.get('intent')
        sentences = data.get('sentences')
        final_dict = {}
        final_dict["intent"] = intent
        answer_list = []
        for sentence in sentences.splitlines():
            intent = Intent.objects.get(name=intent)
            sentence2 = do_pre_processing(sentence, "web", "eng")
            intent2 = get_intent(sentence2)
            if intent2 is not None:
                intent_obj = get_object_or_404(Intent, name=intent2[0].name)
                if intent_obj.pk == intent.pk:
                    temp_dict = {}
                    temp_dict["sentence"] = sentence
                    temp_dict["verdict"] = PASS
                    answer_list.append(temp_dict)
                else:
                    temp_dict = {}
                    temp_dict["sentence"] = sentence
                    temp_dict["verdict"] = FAIL
                    answer_list.append(temp_dict)
            else:
                temp_dict = {}
                temp_dict["sentence"] = sentence
                temp_dict["verdict"] = FAIL
                answer_list.append(temp_dict)
        final_dict["answer"] = answer_list
        return Response(data=final_dict)


class GetAnalysisAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request):
        try:
            data = request.GET
            from_date = data.get('from_date').split("/")
            to_date = data.get('to_date').split("/")
            start_date = date(int(from_date[2]),
                              int(from_date[1]),
                              int(from_date[0]))
            end_date = date(int(to_date[2]),
                            int(to_date[1]),
                            int(to_date[0]))
            choices = return_choice(start_date, end_date)
            current_choice = choices[1]
            value = choices[0]
            dict_count = create_blank_dict(value,
                                           current_choice,
                                           start_date)
            answered_count = create_blank_dict(value,
                                               current_choice,
                                               start_date)
            unanswered_count = create_blank_dict(value,
                                                 current_choice,
                                                 start_date)
            platform_dict = {}
            answered_messages = []
            unanswered_messages = []
            total_message = []
            dict_user_cnt = create_blank_dict(value,
                                              current_choice,
                                              start_date)
            dict_message_cnt = create_blank_dict(value,
                                                 current_choice,
                                                 start_date)
            final_average_dict = create_blank_dict(value,
                                                   current_choice,
                                                   start_date)
            total_unique_users = create_blank_dict(value,
                                                   current_choice,
                                                   start_date)
            queries = Log.objects.filter(
                time__range=(start_date, end_date))
            analytics = AnalyticCount.objects.filter(
                time__range=(start_date, end_date))
            unique_users = UniqueUsers.objects.filter(
                time__range=(start_date, end_date))
            list_insights_1 = {}
            clicked_vs_typed = {}
            try:
                for query in queries:
                    if query.time is not None:
                        total_message.append(
                            query.query + " " + query.user.user_id)
                        if query.answer_succesfull == True:
                            answered_messages.append(
                                query.query + " " + query.user.user_id)
                        else:
                            unanswered_messages.append(
                                query.query + " " + query.user.user_id)
                        current_platform = query.channel.name
                        if current_platform != "False":
                            if current_platform not in platform_dict:
                                platform_dict[current_platform] = 1
                            else:
                                platform_dict[current_platform] += 1
                        clicked = query.clicked
                        if clicked == True:
                            if "clicked" not in clicked_vs_typed:
                                clicked_vs_typed["clicked"] = 1
                            else:
                                clicked_vs_typed["clicked"] += 1
                        else:
                            if "typed" not in clicked_vs_typed:
                                clicked_vs_typed["typed"] = 1
                            else:
                                clicked_vs_typed["typed"] += 1
                        t = query.time
                        if current_choice == "0":
                            dict_count[t.strftime('%d/%m/%Y')] += 1
                            if query.answer_succesfull == True:
                                answered_count[t.strftime('%d/%m/%Y')] += 1
                            else:
                                unanswered_count[t.strftime('%d/%m/%Y')] += 1
                        elif current_choice == "1":
                            dict_count[calendar.month_name[t.month]] += 1
                            if query.answer_succesfull == True:
                                answered_count[
                                    calendar.month_name[t.month]] += 1
                            else:
                                unanswered_count[
                                    calendar.month_name[t.month]] += 1
                        else:
                            dict_count[t.year] += 1
                            if query.answer_succesfull == True:
                                answered_count[t.year] += 1
                            else:
                                unanswered_count[t.year] += 1
                        list_insights_1["total_messages"] = dict_count
                        list_insights_1["answered_messages"] = answered_count
                        list_insights_1[
                            "unanswered_messages"] = unanswered_count
            except Exception as e:
                logger.error(
                    "class: GetAnalysisAPIView, method: post ERROr %s", str(e))
            dict_user_cnt, dict_message_cnt = get_dict_cnt(queries,
                                                           current_choice,
                                                           dict_message_cnt,
                                                           dict_user_cnt)
            final_average_dict = get_final_average_dict(dict_user_cnt,
                                                        dict_message_cnt,
                                                        final_average_dict)
            (entity_count,
             entity_count_name) = get_entity_count_and_entity_count_name(analytics)
            entity_top_intent = get_entity_top_intent(
                analytics, entity_count_name)
            top_intent_in_entities = get_top_intent_in_entities(
                entity_top_intent)
            intent_top_entity = get_intent_top_entity(analytics)
            top_entities_in_intent = get_top_entities_in_intent(
                intent_top_entity)
            total_unique_users = get_total_unique_users(total_unique_users,
                                                        unique_users,
                                                        current_choice)
            final_dict = {}
            final_dict["list_insights_1"] = list_insights_1
            final_dict["platform_dict"] = platform_dict
            final_dict["average_session_time"] = final_average_dict
            final_dict["clicked_vs_typed"] = clicked_vs_typed
            final_dict["top_products"] = entity_count
            final_dict["top_intent_in_entities"] = top_intent_in_entities
            final_dict["top_entities_in_intent"] = top_entities_in_intent
            final_dict["total_unique_users"] = total_unique_users
            final_dict["answered_messages"] = answered_messages
            final_dict["unanswered_messages"] = unanswered_messages
            final_dict["total_messages"] = total_message
            return Response(data=final_dict)
        except Exception as e:
            return Response(data={})


class saveLeadDataAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request):
        try:
            data = request.GET
            name = data.get('name').strip()
            email = data.get('email').strip()
            contact = data.get('contact').strip()
            try:
                Leads.objects.get(name=name,
                                  email_id=email,
                                  contact=contact)
            except:
                Leads(name=name,
                      email_id=email,
                      contact=contact).save()
            data = {}
            data["answer"] = ""
            return Response(data=data)
        except:
            return Response(data=data)
            pass


class GetPPCAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def get(self, request):
        try:
            data = request.GET
            policy_number = data.get('policy_number').strip()
            dob = data.get('dob').strip()
            email = data.get('email').strip()
            url = Config.objects.all()[0].url_customer_id
            headers = {'content-type': 'text/xml'}
            body = """<?xml version="1.0" encoding="utf-8"?>
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
            content = content[content.find(
                "<getCustomer_IDResult>") + 22:content.find("</getCustomer_IDResult>")]
            content = content.replace("&lt;", "<")
            content = content.replace("&gt;", ">")
            content = content.replace(r"\r", "")
            content = content.replace(r"\n", "")
            answer = content
            dictt = xmltodict.parse(answer)
            answer = json.loads(json.dumps(dictt))
            customer_id = answer["PolicyDetails"]["Table"]["PL_PERSON_ID"]
            body = """<?xml version="1.0" encoding="utf-8"?>
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
            content = content[content.find(
                "<getPPCResult>") + 14:content.find("</getPPCResult>")]
            content = content.replace("&lt;", "<")
            content = content.replace("&gt;", ">")
            content = content.replace(r"\r", "")
            content = content.replace(r"\n", "")
            answer = content
            dictt = xmltodict.parse(answer)
            answer = json.loads(json.dumps(dictt))

            send_mail(email, '<h5>The below are the following details: </h5><br><div>Product Name - ' + answer['NewDataSet']['Table1']['PRODUCT_NAME'] + '<br>Product Type - ' + answer[
                      'NewDataSet']['Table1']['PROD_TYPE'] + '<br> Policy Number - ' + answer['NewDataSet']['Table1']['POLICY_NUMBER'] + '</div>')
            data = {}

            data["flag"] = "temp"
            return Response(data=data)
        except Exception as e:
            data = {}
            data["flag"] = ""

            return Response(data=data)
try:
    SERVER_PROTOCOL = Config.objects.all()[0].facebook_server_protocol
    SERVER_IP = Config.objects.all()[0].facebook_server_ip
    SERVER_PORT = Config.objects.all()[0].facebook_server_port
except:
    pass

from pprint import pprint
class FacebookAPIView(generic.View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request, *args, **kwargs):
        return generic.View.dispatch(self, request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        return HttpResponse(self.request.GET['hub.challenge'])

    def post(self, request, *args, **kwargs):
        incoming_message = json.loads(self.request.body.decode('utf-8'))
        pprint(incoming_message)
        try:
            for entry in incoming_message['entry']:
                for message in entry['messaging']:
                    if 'postback' in message:
                        process_facebook_message(message['sender']['id'], message[
                                                 'postback']['title'], ONE)
                    if 'message' in message:

                        if 'quick_reply' in message['message']:
                            process_facebook_message(message['sender']['id'], message[
                                                     'message']['quick_reply']['payload'], TWO)
                        else:
                            process_facebook_message(message['sender']['id'], message[
                                                     'message']['text'], THREE)
        except:
            pass
        return HttpResponse()

class DeleteEntriesAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

    def post(self, request):
        data = request.data
        user_id = data.get('user_id')
        print("User id is: ", user_id)
        user = Profile.objects.get(user_id=user_id)
        print("User is: ", user)
        try:
            data = Data.objects.filter(user=user, entity_name="LeaveType").delete()
        except:
            pass
        try:
            data = Data.objects.filter(user=user, entity_name="Reenter").delete()
        except:
            pass
        #print("Data is: ", data)
        return Response(data={})

class AlexaAPIView(APIView):
    authentication_classes = (
        CsrfExemptSessionAuthentication, BasicAuthentication)

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
        answer = response["response"]
        try:
            choices = response['choices']
            if len(choices) > 0:
                for choice in choices:
                    answer += choice + COMMA
        except:
            pass
        answer = re.sub(r'<[^>]*?>', '', answer)
        return Response(data={"response": answer})

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
DeleteEntries = DeleteEntriesAPIView.as_view()
