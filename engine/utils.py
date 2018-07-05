import calendar
import json
import os
import random
import re
import logging
import editdistance
import pandas as pd
import math
import requests

from django.utils.safestring import SafeData, SafeText, mark_safe
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.utils import timezone
from django.http import HttpResponse
from django.utils.encoding import smart_str
from rest_framework.authentication import (BasicAuthentication,
                                           SessionAuthentication)
from rest_framework.response import Response
from django.shortcuts import render, get_object_or_404
from rest_framework.views import APIView
from django.core.mail import EmailMultiAlternatives
from django.views import generic
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator

from .constants import *
from .models import *
from .apis import *

logger = logging.getLogger('my_logger')


def write_file(data):
    f = open("logger.txt", "a+")
    f.write(data + "\n")
    f.close()


def find_most_similar_intent(sentence):
    sentence = do_pre_processing(sentence, "web", "eng")
    intents = Intent.objects.filter(misc=False)
    temp_dict = {}
    for intent in intents:
        if len(intent.name) < THIRTY:
            score = intent.get_intent_score(sentence)
            temp_dict[intent.name] = score
    lists = sorted(temp_dict, key=temp_dict.get, reverse=True)
    vall = min(RECOMMENDATION_LIST_SIZE, len(lists))
    return lists[:vall]


def call_cancel_button(fbid):
    post_message_url = Config.objects.all(
    )[0].facebook_endpoint_url + "/cancelbutton/"
    data = {
        "user_id": fbid
    }
    response = requests.post(post_message_url, data)
    return response


def call_update_user(fbid):

    post_message_url = Config.objects.all(
    )[0].facebook_endpoint_url + "/updateuser/"
    data = {
        "user_id": fbid
    }
    response = requests.post(post_message_url, data)
    return response


def call_query(fbid, message, clicked, pipe):
    print("calling query", fbid, message, pipe)
    post_message_url = Config.objects.all(
    )[0].facebook_endpoint_url + "/query/"
    data = {
        "user_id": fbid,
        "message": message,
        "channel": "facebook",
        "language": "eng",
        "clicked": "true",
        "pipe": pipe,
    }
    response = requests.get(post_message_url, data)
    print("response")
    return response


def call_query_googlehome(fbid, message, clicked, pipe):
    print("calling query", fbid, message, pipe)
    post_message_url = Config.objects.all(
    )[0].facebook_endpoint_url + "/query/"
    data = {
        "user_id": fbid,
        "message": message,
        "channel": "googlehome",
        "language": "eng",
        "clicked": "true",
        "pipe": pipe,
    }
    response = requests.get(post_message_url, data)
    print("response")
    return response


def call_query_alexa(fbid, message, clicked, pipe):

    post_message_url = Config.objects.all(
    )[0].facebook_endpoint_url + "/query/"
    data = {
        "user_id": fbid,
        "message": message,
        "channel": "web",
        "language": "eng",
        "clicked": "true",
        "pipe": pipe,
    }
    response = requests.post(post_message_url, data)
    return response


def generate_recommended_queries_data(fbid, text, recommended_queries):
    if len(recommended_queries) > 0:
        button_list = []
        for query in recommended_queries:
            temp_dict = {}
            temp_dict["type"] = "postback"
            temp_dict["title"] = query
            temp_dict["payload"] = "interest rate"
            button_list.append(temp_dict)
        response_dict = {"recipient": {"id": fbid},
                         "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": text,
                    "buttons": button_list[:3]
                }
            }
        }
        }
        return response_dict


def generate_facebook_data(fbid, text, choices):
    list_choices = []
    if len(choices) <= 11:
        for choice in choices:
            choice_dict = {}
            choice_dict["content_type"] = "text"
            choice_dict["title"] = choice
            choice_dict["payload"] = choice
            list_choices.append(choice_dict)
    response_dict = {"recipient": {"id": fbid},
                     "message": {
        "text": text,
    },
    }
    if len(list_choices) > 0:
        response_dict["message"]["quick_replies"] = list_choices
    return response_dict


def process_facebook_message(fbid, receieved_message, flag):

    if receieved_message.lower().strip() == GET_STARTED:
        response = call_update_user(fbid)
        json_data = json.loads(response.text)
        try:
            user_pipe = UserPipe.objects.get(user_id=fbid)
            user_pipe.pipe = ""
            user_pipe.save()
        except:
            pass
        post_facebook_message(fbid, json_data["response"], [])
        post_facebook_recommendations(fbid, RECOMMENDATIONS_TEXT, json_data[
            "recommended_queries"])
    elif receieved_message.lower().strip() == CANCEL or receieved_message.lower().strip() == HOME:
        try:
            user_pipe = UserPipe.objects.get(user_id=fbid)
            user_pipe.pipe = ""
            user_pipe.save()
        except:
            pass
        response = call_cancel_button(fbid)
        json_data = json.loads(response.text)
        post_facebook_message(fbid, json_data["response"], [])
    else:

        try:
            pipe = UserPipe.objects.get(user_id=fbid).pipe
            pipe = pipe + receieved_message + "|"
        except:
            UserPipe(user_id=fbid,
                     pipe="").save()
            pipe = receieved_message + "|"

        response = call_query(fbid, receieved_message, "a", pipe)

        json_data = json.loads(response.text)
        if 'choices' in json_data:
            choices = json_data["choices"]
        else:
            choices = []
        post_facebook_message(fbid, json_data["response"], choices)
        if 'pipe' in json_data:

            a = UserPipe.objects.get(user_id=fbid)
            a.pipe = json_data["pipe"]
            a.save()
        else:
            a = UserPipe.objects.get(user_id=fbid)
            a.pipe = ""
            a.save()
        if 'recommended_queries' in json_data:
            post_facebook_recommendations(fbid, "Here are some recommendations", json_data[
                "recommended_queries"])


def post_facebook_message(fbid, recevied_message, choices):
    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=EAAWgoujWQhoBANxtjXNdvQZAuvjGhUTRFZBUFN1hbmXQ4EZAmKUoeElJyK5XeXRcDw5uhKTjgFgjaIOZB39iOj6OSiGKhP7iyXZBdCad2aJZABFInAw8wI5kqYfpvn9euPezwW9VyWLKrX18Gz5RMJKlSYnlMtQUhrTUPUfvoAnRuZCJlo4SIbu'
    recevied_message = re.sub(r'<[^>]*?>', '', recevied_message)
    response_msg = json.dumps(generate_facebook_data(
        fbid, recevied_message, choices))
    status = requests.post(post_message_url, headers={
        "Content-Type": "application/json"}, data=response_msg)


def post_facebook_recommendations(fbid, recevied_message, recommended_queries):

    post_message_url = 'https://graph.facebook.com/v2.6/me/messages?access_token=EAAWgoujWQhoBANxtjXNdvQZAuvjGhUTRFZBUFN1hbmXQ4EZAmKUoeElJyK5XeXRcDw5uhKTjgFgjaIOZB39iOj6OSiGKhP7iyXZBdCad2aJZABFInAw8wI5kqYfpvn9euPezwW9VyWLKrX18Gz5RMJKlSYnlMtQUhrTUPUfvoAnRuZCJlo4SIbu'
    recevied_message = re.sub(r'<[^>]*?>', '', recevied_message)
    response_msg = json.dumps(generate_recommended_queries_data(
        fbid, recevied_message, recommended_queries))
    status = requests.post(post_message_url, headers={
        "Content-Type": "application/json"}, data=response_msg)


def get_top_intent_in_entities(entity_top_intent):
    TOP_Y_INTENT = 3
    top_intent_in_entities = {}
    for key, val in entity_top_intent.items():
        list_of_top_intents = val
        sorted_list = sorted(list_of_top_intents.items(), key=lambda x: -x[1])
        new_list_of_top_intents = {}
        for i in range(min(TOP_Y_INTENT, len(sorted_list))):
            new_list_of_top_intents[sorted_list[i][0]] = sorted_list[i][1]
        top_intent_in_entities[key] = new_list_of_top_intents
    return top_intent_in_entities


def get_top_entities_in_intent(intent_top_entity):
    TOP_Y_ENTITIES = 3
    top_entities_in_intent = {}
    for key, val in intent_top_entity.items():
        list_of_top_entities = val
        sorted_list = sorted(list_of_top_entities.items(), key=lambda x: -x[1])
        new_list_of_top_entities = {}
        for i in range(min(TOP_Y_ENTITIES, len(sorted_list))):
            new_list_of_top_entities[sorted_list[i][0]] = sorted_list[i][1]
        top_entities_in_intent[key] = new_list_of_top_entities
    return top_entities_in_intent


def get_entity_top_intent(analytics, entity_count_name):
    entity_top_intent = {}
    for analytic_obj in analytics:
        if analytic_obj.entity is not None:
            if analytic_obj.entity.choice_name not in entity_top_intent and analytic_obj.entity.choice_name in entity_count_name:
                entity_top_intent[analytic_obj.entity.choice_name] = {}
    for analytic_obj in analytics:
        if analytic_obj.time is not None:
            if analytic_obj.entity is not None and analytic_obj.entity.choice_name in entity_top_intent:
                temp_dict = entity_top_intent[
                    analytic_obj.entity.choice_name]
                if analytic_obj.intent is not None:
                    if analytic_obj.intent.name not in temp_dict:
                        temp_dict[analytic_obj.intent.name] = 1
                    else:
                        temp_dict[analytic_obj.intent.name] += 1
                entity_top_intent[
                    analytic_obj.entity.choice_name] = temp_dict
    return entity_top_intent


def get_intent_top_entity(analytics):
    intent_top_entity = {}
    for analytic_obj in analytics:
        if analytic_obj.time is not None:
            if analytic_obj.intent is not None:
                if analytic_obj.intent.name not in intent_top_entity:
                    intent_top_entity[analytic_obj.intent.name] = {}
                temp_dict = intent_top_entity[analytic_obj.intent.name]
                if analytic_obj.entity is not None:
                    if analytic_obj.entity.choice_name not in temp_dict:
                        temp_dict[analytic_obj.entity.choice_name] = 1
                    else:
                        temp_dict[analytic_obj.entity.choice_name] += 1
                intent_top_entity[analytic_obj.intent.name] = temp_dict
    new_intent_top_entity = {}
    order_score = {}
    for key, val in intent_top_entity.items():
        if val:
            tot_val = sum(val.values())
            order_score[key] = tot_val
    sorted_intent = sorted(order_score.items(), key=lambda x: -x[1])
    sorted_intent = sorted_intent[-5:]
    new_intent_top_entity = dict((x, y) for x, y in sorted_intent)
    for i in sorted_intent:
        new_intent_top_entity[i[0]] = intent_top_entity[i[0]]
    return new_intent_top_entity


def get_total_unique_users(total_unique_users, unique_users, current_choice):
    for user in unique_users:
        t = user.time
        if current_choice == "0":
            total_unique_users[t.strftime('%d/%m/%Y')] += 1
        elif current_choice == "1":
            total_unique_users[calendar.month_name[t.month]] += 1
        else:
            total_unique_users[t.year] += 1
    return total_unique_users


def get_entity_count_and_entity_count_name(analytics):
    entity_count = {}
    for analytic_obj in analytics:
        if analytic_obj.time is not None:
            if analytic_obj.entity is not None:
                if analytic_obj.entity.choice_name not in entity_count:
                    entity_count[analytic_obj.entity.choice_name] = 1
                else:
                    entity_count[analytic_obj.entity.choice_name] += 1
    entity_count = sorted(entity_count.items(), key=lambda x: x[1])
    list = entity_count[-5:]
    entity_count_name = []
    entity_count = {}
    for key, val in list:
        entity_count[key] = val
        entity_count_name.append(key)
    return entity_count, entity_count_name


def get_final_average_dict(dict_user_cnt, dict_message_cnt, final_average_dict):
    for key, elem in final_average_dict.items():
        users = dict_user_cnt[key]
        messages = dict_message_cnt[key]
        if users != 0:
            average = messages / users
        else:
            average = 0
        final_average_dict[key] = average
    return final_average_dict


def get_dict_cnt(queries, current_choice, dict_message_cnt, dict_user_cnt):
    try:
        dict_user = {}
        for query in queries:
            if query.time is not None:
                t = query.time
                if current_choice == "0":
                    dict_message_cnt[t.strftime('%d/%m/%Y')] += 1
                    if query.user.user_id not in dict_user:
                        dict_user[query.user.user_id] = 1
                        dict_user_cnt[t.strftime('%d/%m/%Y')] += 1
                elif current_choice == "1":
                    dict_message_cnt[calendar.month_name[t.month]] += 1
                    if query.user.user_id not in dict_user:
                        dict_user[query.user.user_id] = 1
                        dict_user_cnt[calendar.month_name[t.month]] += 1
                else:
                    dict_message_cnt[t.year] += 1
                    if query.user.user_id not in dict_user:
                        dict_user[query.user.user_id] = 1
                        dict_user_cnt[t.year] += 1
    except Exception as e:
        logger.error(
            "class: GetAnalysisAPIView, method: post error %s", str(e))
    return dict_user_cnt, dict_message_cnt


def create_blank_dict(value, choice, start_date):
    dict = {}
    if choice == "0":
        current_date = start_date
        for i in range(value + 1):
            t = current_date.strftime('%d/%m/%Y')
            dict[t] = 0
            current_date += timedelta(days=1)
    elif choice == "1":
        current_month = start_date.month - 1
        for i in range(value + 1):
            current_month += 1
            if current_month == 13:
                current_month = 1
            dict[calendar.month_name[current_month]] = 0
    else:
        current_year = start_date.year
        for i in range(value + 1):
            dict[current_year] = 0
            current_year += 1
    return dict


def return_choice(date1, date2):
    delta = date2 - date1
    days = delta.days
    years, remainder = divmod(days, 365)
    months = years * 12 + (remainder // 30)
    if days > 0:
        if (years > 0):
            return (years, "2")
        elif (months > 0):
            return (months, "1")
        else:
            return (days, "0")
    return (days, "-1")


def initial_base_response():
    list_temp = []
    response_1 = Config.objects.all()[0].base_response_1
    if response_1 is not None:
        if response_1:
            list_temp.append(response_1)
    response_2 = Config.objects.all()[0].base_response_2
    if response_2 is not None:
        if response_2:
            list_temp.append(response_2)
    response_3 = Config.objects.all()[0].base_response_3
    if response_3 is not None:
        if response_3:
            list_temp.append(response_3)
    response_4 = Config.objects.all()[0].base_response_4
    if response_4 is not None:
        if response_4:
            list_temp.append(response_4)
    response_5 = Config.objects.all()[0].base_response_5
    if response_5 is not None:
        if response_5:
            list_temp.append(response_5)
    return list_temp


def process_message_with_pipe(tree, message, user_id, channel, language, clicked, pipe_temp, alexa_id, device_id, access_token):
    return match_choices_final_a(tree, message, user_id, channel, language, clicked, pipe_temp, alexa_id, device_id, access_token)


def process_message_without_pipe(tree, message, user_id, channel, language, clicked, pipe_temp, alexa_id, device_id, access_token):
    return match_choices_final_a(tree, message, user_id, channel, language, clicked, pipe_temp, access_token)


def change_number_to_text(tree, message):
    try:
        for number_mapper in tree.number_mapper.all():
            if preprocess_question(message.lower().strip()) == number_mapper.number:
                return number_mapper.values
        return message
    except Exception as e:
        return message


def autocorrect_web_eng(message, channel, language):
    try:
        logger.info("Entered autocorrect()")
        words_in_dict = list(
            AutoCorrectWordList.objects.all().values_list('word', flat=True))
        final_message = ''
        for index, elem in enumerate(message.split()):
            if elem in words_in_dict:
                final_message += elem + " "
            else:
                list_of_probable_words = []
                for word in words_in_dict:
                    if (editdistance.eval(word, elem) <= 1):
                        list_of_probable_words.append(word)

                if len(list_of_probable_words) > 0:
                    final_message += random.choice(
                        list_of_probable_words) + " "
                else:
                    final_message += elem + " "
        return final_message
    except Exception as e:

        logger.error("Error in autocorrect() %s", str(e))


def autocorrect(message, channel, language):
    if channel == "web" and language == "eng":
        return autocorrect_web_eng(message, channel, language)
    elif channel == "android" and language == "eng":
        return autocorrect_web_eng(message, channel, language)
    elif channel == "alexa" and language == "eng":
        return autocorrect_web_eng(message, channel, language)
    else:
        return message


def remove_stopwords(message):
    try:
        logger.info("Entered remove_stopwords()")
        STOP_WORDS = set(STOPWORDS)
        list_t = []
        value = str(Config.objects.all()[0].custom_stop_word)
        for val in value.split(","):
            list_t.append(val)
        set_custom_stop_words = set(list_t)
        message = ' '.join(
            [i for i in message.lower().split() if i not in STOP_WORDS])
        message = ' '.join([i for i in message.lower().split()
                            if i not in set_custom_stop_words])
        return message
    except Exception as e:
        logger.error("Error in remove_stopwords %s", str(e))


def recommendations(intent, entity):
    try:
        logger.info("Entered recommendations")
        intent_obj = intent
        entity_obj = entity
        if intent is not None and entity is not None:
            with_same_entity = Recommendation.objects.filter(
                entity=entity_obj).exclude(intent=intent_obj)
            if with_same_entity.count() == 0:
                with_same_entity = Recommendation.objects.filter(
                    entity=entity_obj.parent)
            with_same_intent = Recommendation.objects.filter(
                intent=intent_obj).exclude(entity=entity_obj)
            list_with_same_entity = list(set(with_same_entity))
            list_with_same_intent = list(set(with_same_intent))
            if len(list_with_same_entity) > 3:
                list_random = random.sample(list_with_same_entity, 3)
            else:
                list_random = random.sample(
                    list_with_same_entity, len(list_with_same_entity))
                more_needed_values = 3 - len(list_random)
                if len(list_with_same_intent) > more_needed_values:
                    list_temp = random.sample(
                        list_with_same_intent, more_needed_values)
                    list_random.extend(list_temp)
                else:
                    list_temp = random.sample(
                        list_with_same_intent, len(list_with_same_intent))
                    list_random.extend(list_temp)
            list_query_name = []
            for elem in list_random:
                list_query_name.append(elem.query_name)
            return (list_query_name)
        elif entity is not None:
            objects = Recommendation.objects.filter(entity=entity_obj)
            list_temp = []
            for object in objects:
                list_temp.append(object.query_name)
            list_random = random.sample(list_temp, min(3, len(list_temp)))
            return (list_random)
        elif intent is not None:
            objects = Recommendation.objects.filter(intent=intent_obj)
            list_temp = []
            for object in objects:
                list_temp.append(object.query_name)
            list_random = random.sample(list_temp, min(3, len(list_temp)))
            return (list_random)
        return []
    except Exception as e:
        logger.error("Error in recommendations %s", str(e))
        return []


def recur_entities(current_choice, user_id):
    try:
        logger.info("Entered recur_entities")
        parent = current_choice.parent
        for entity_type in parent.entity_choices.all():
            val_to_save = entity_type.name
            Data(entity_name=val_to_save,
                 entity_value=parent.entity_name,
                 user=Profile.objects.get(user_id=user_id)).save()
        recur_entities(parent, user_id)
    except Exception as e:
        logger.error("Error from: recur_entities() %s", str(e))


def recur_entity_tree(entities, user_id):
    try:
        logger.info("Entered recur_entity_tree")
        for entity in entities:
            current_entity = Entities.objects.get(
                entity_name=entity.entity_name)
            recur_entities(current_entity, user_id)
    except Exception as e:
        logger.error("Error from: recur_entity_tree() %s", str(e))


def increment_querycnt(message, channel):
    try:
        query_cnt = QueryCnt.objects.get(query=message)
        cnt = query_cnt.count
        cnt = cnt + 1
        QueryCnt.objects.filter(query=message).update(count=cnt)
        current_query = query_cnt.pk
        return current_query
    except Exception as e:
        try:
            channel = Channel.objects.get(name="web")
        except:
            channel = Channel(name="web")
            channel.save()
        try:
            language = Language.objects.get(name="eng")
        except:
            language = Language(name="eng")
            language.save()
        query = QueryCnt(query=message,
                         channel=channel,
                         language=language,
                         count=0)
        query.save()
        logger.error("function: increment_quer_cnt %s", str(e))
        return query.pk


def add_entities_in_user(entities, intent_objects, query_id, user_id, pipe):
    try:
        user = Profile.objects.get(user_id=user_id)
        user.tree = intent_objects.tree
        pipe += intent_objects.name + "|"
        if entities is not None:
            for entity in entities:
                for entity_type in entity.entity_choices.all():
                    logger.info("Entity Name: %s", entity_type.name)
                    val_to_save = entity_type.name
                    print("VAAAAAAAAAAAAAL: ", entity.entity_name)
                    Data(entity_name=val_to_save,
                         entity_value=entity.entity_name,
                         user=user).save()
        user.current_intent = intent_objects
        user.current_query = query_id
        user.save()
        return pipe
    except Profile.DoesNotExist:
        logger.error("No matching profile found")


def create_choice_list(entity_type):
    try:
        choices = entity_type.choices.all()
        choice_list = []
        for choice in choices:
            choice_list.append(choice.entity_name)
        return choice_list
    except Exception as e:
        logger.error("Error in: create_choice_list() %s", str(e))


def get_recommendation_list_from_entities(entities):
    try:
        recommendation_list = []
        for entity in entities:
            temp_list = recommendations(intent=None, entity=entity)
            recommendation_list.extend(temp_list)
        return recommendation_list
    except Exception as e:
        logger.error(
            "Error in: get_recommendation_list_from_entities() %s", str(e))


def get_recommendation_list_json(recommendation_list):
    try:
        json = {}
        boolean = True
        if (len(recommendation_list) > 0):
            json["recommended_queries"] = recommendation_list
            message = str(Config.objects.all()[
                0].recommended_queries_statement)
            json["response"] = message
        else:
            message = str(Config.objects.all()[0].question_not_recognized)
            json["response"] = message
            boolean = False
        json["is_typable"] = "true"
        return (json, boolean)
    except Exception as e:
        logger.error("Error in: get_recommendation_list_json() %s", str(e))


def remove_nonalphanumeric(message):
    pattern = re.compile('[^a-z.@/,A-Z0-9_ ]+', re.UNICODE)
    pattern1 = re.compile("\s\s+", re.UNICODE)
    message = pattern.sub('', message)
    message = pattern1.sub(' ', message)
    message = message.strip()
    message = message.lower()
    return message


def parse_json(current_answer, file, user_id):
    if (file != "999abc999" and file is not None):
        try:
            current_answer = current_answer.replace("<p>", "")
            current_answer = current_answer.replace("</p>", "")
            current_answer = current_answer.replace("&nbsp;", " ")
            df = pd.read_csv(file.file)
            string = ""
            flag_start = False
            word = ""
            flag_colon_start = False
            list = []
            list_to_find = []
            flag_start_2 = False
            for words in current_answer.split():
                if words == ")}":
                    flag_start_2 = False
                elif flag_start_2 == True:
                    list_to_find.append(words)
                elif words == "{(":
                    flag_start_2 = True
                elif words == "]}":
                    flag_start = False
                elif flag_start == True:
                    if flag_colon_start == True:
                        list_t = []
                        list_t.append(word)
                        list_t.append(words)
                        list.append(list_t)
                        flag_colon_start = False
                    if words == ":":
                        flag_colon_start = True
                    if flag_colon_start == False:
                        word = words
                elif words == "{[":
                    flag_start = True
                else:
                    string += words + " "
            for stuff in list:
                str1 = str(stuff[0])
                str2 = str(stuff[1])
                df[str1] = df[str1].astype(str)
                df[str1] = df[str1].str.lower()
                df = df.loc[df[str1] == str2.lower()]
            dict_temp = {}
            if(len(list_to_find) > 0):
                for stuff in list_to_find:
                    if stuff == "respone_code":
                        if math.isnan(df.iloc[0][stuff]):
                            dict_temp[stuff] = "NaN"
                        else:
                            dict_temp[stuff] = int(df.iloc[0][stuff])
                    else:
                        dict_temp[stuff] = df.iloc[0][stuff]
            return (string, dict_temp)
        except:
            message = str(Config.objects.get(
                name="entry_not_present_in_database").value)
            return (message, {})
    else:
        return (current_answer, {})


def replace_values(sentence, dict_temp):
    string = ""
    for words in sentence.split():
        if words in dict_temp:
            string += str(dict_temp[words]) + " "
        else:
            string += words + " "
    return string


def replace_if_statement(sentence):
    string = ""
    sentence = sentence.replace('<p>', '')
    sentence = sentence.replace('</p>', '')
    string_answer_1 = ""
    string_answer_2 = ""
    condition = ""
    start_flag = False
    start_flag_2 = False
    start_flag_3 = False
    final_flag = False
    for words in sentence.split():
        if words == "}}}":
            start_flag = False
        if start_flag == True:
            string_answer_1 += words + " "
        if words == "{{{":
            start_flag = True
        if words == "}}}}":
            start_flag_2 = False
        if start_flag_2 == True:
            string_answer_2 += words + " "
        if words == "{{{{":
            start_flag_2 = True
        if words == "))}":
            start_flag_3 = False
            final_flag = True
        if start_flag_3 == True:
            condition += words + " "
        if words == "{((":
            start_flag_3 = True
    condition = condition.replace(" ", "")

    if final_flag == True:
        if condition != "nan" and condition != "":
            return string_answer_1
        else:
            return string_answer_2
    else:
        return sentence


def parse_pool(rere, temp, ans):
    try:
        for wor in temp.split(","):
            ans = ans[wor]
        if type(ans) is dict:
            temp_list = []
            temp_list.append(ans)
            ans = temp_list
        string_final = ""
        for objj in ans:
            for word in rere.split():
                if '///' in word:
                    string_final += objj[word[3:]] + " "
                else:
                    string_final += word + " "
            string_final += '<br>'
        return string_final
    except Exception as e:

        pass


def parse_api(message, user_id, alexa_id, device_id, access_token):
    if '{*' in message:
        try:
            message = message.replace("<p>", "")
            message = message.replace("</p>", "")
            message = message.replace("&nbsp;", " ")
            string = ""
            final_string = ""
            flag_api = False
            for words in message.split():
                if words == "*}":
                    flag_api = False
                elif flag_api == True:
                    string += words + " "
                elif words == "{*":
                    flag_api = True
                else:
                    final_string += words + " "
            list = string.split(',')
            dict = {}
            temp_dict = {}
            for val in list:
                key, pair = val.split('[')
                print(key, pair)
                if(key == "url"):
                    dict["url"] = pair
                if(key == "type"):
                    dict["type"] = pair
                if(key == "data"):
                    pair = pair[1:]
                    pair = pair[:-1]
                    temp_list = pair.split(';')
                    for item in temp_list:
                        keey, valuee = item.split("-")
                        temp_dict[keey] = valuee
                    temp_dict["access_token"] = "AICaLJPkjryiSYerAEouwSMwPudInp"
                    temp_dict["access_token"] = access_token
                    temp_dict["user_id"] = user_id
                    temp_dict["alexa_id"] = alexa_id
                    temp_dict["device_id"] = device_id
                    dict["data"] = temp_dict
                if(key == "output"):
                    pair = pair[1:]
                    pair = pair[:-1]
                    list = pair.split(';')
                    dict["output"] = list
            if(dict["type"] == "GET"):
                answer = requests.get(dict["url"], dict["data"])
            elif(dict["type"] == "POST"):
                answer = requests.post(dict["url"], dict["data"])

            answer = json.loads(answer.text)

            answer = answer["answer"]

            try:
                success = answer["success"]
                message = answer["message"]
            except:
                success = "true"

            if success == "false":
                return (message, success)

            try:
                ans = answer["answer"]
                dictt = xmltodict.parse(ans)
                ans = json.loads(json.dumps(dictt))
                answer.pop('answer', None)
                z = answer.copy()
                z.update(ans)

            except Exception as e:
                z = answer

                pass
            answer = z

            flag_t = False
            temp = ""
            final_string_a = ""
            for words in final_string.split():

                if words == "}+":
                    flag_t = False
                    word = temp.split(",")
                    ans = answer

                    for wor in word:
                        try:
                            ans = ans[wor]
                        except:
                            ans = ans[int(wor)]
                    final_string_a += str(ans) + " "
                elif flag_t == True:
                    temp = words
                elif words == "+{":
                    flag_t = True
                else:
                    final_string_a += words + " "
            flag_f = False
            temp = ""
            flag_p = False
            final_string_b = ""
            poool = ""
            for words in final_string_a.split():
                if words == "}}":
                    flag_p = False
                    final_string_b += parse_pool(poool, temp, answer) + " "
                elif flag_p == True:
                    poool += words + " "
                elif words == "){{":
                    flag_p = True
                    flag_f = False
                elif flag_f == True:
                    temp = words
                elif words == "for(":
                    flag_f = True
                else:
                    final_string_b += words + " "
            return (final_string_b, "true")
        except Exception as e:
            print("EEEEEEEEEXCCCCCCCCEPTION: ", str(e))
            pos_1 = message.find('{*')
            pos_2 = message.find('*}')
            #print("Check ", message[pos_1:pos_2])
            message = message.replace(message[pos_1:pos_2], '')
            #print("Message after replacing is ", message)
            return (message[:-3], "true")
    else:
        return (message, "true")


def do_api_call(tree, message, user_id, alexa_id, device_id, access_token):
    print(message)
    if '{*' in message:
        try:
            message = parse_is_typable(message, user_id)
        except:
            pass
        try:
            message = message.replace("<p>", "")
            message = message.replace("</p>", "")
            message = message.replace("&nbsp;", " ")
            string = ""
            final_string = ""
            flag_api = False
            for words in message.split():
                if words == "*}":
                    flag_api = False
                elif flag_api == True:
                    string += words + " "
                elif words == "{*":
                    flag_api = True
                else:
                    final_string += words + " "
            list = string.split(',')
            dict = {}
            temp_dict = {}
            for val in list:
                key, pair = val.split('[')
                if(key == "url"):
                    dict["url"] = pair
                if(key == "type"):
                    dict["type"] = pair
                if(key == "data"):
                    pair = pair[1:]
                    pair = pair[:-1]
                    temp_list = pair.split(';')
                    for item in temp_list:
                        keey, valuee = item.split("-")
                        temp_dict[keey] = valuee
                    temp_dict["access_token"] = "AICaLJPkjryiSYerAEouwSMwPudInp"
                    temp_dict["access_token"] = access_token
                    temp_dict["user_id"] = user_id
                    temp_dict["alexa_id"] = alexa_id
                    temp_dict["device_id"] = device_id
                    temp_dict["user_id"] = user_id
                    dict["data"] = temp_dict
                if(key == "output"):
                    pair = pair[1:]
                    pair = pair[:-1]
                    list = pair.split(';')
                    dict["output"] = list
            print(dict[
                  "data"], "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
            if(dict["type"] == "GET"):
                answer = requests.get(dict["url"], dict["data"])
            elif(dict["type"] == "POST"):
                answer = requests.post(dict["url"], dict["data"])

            answer = json.loads(answer.text)
            print("Answer is: ", answer)
            write_file(str(answer))
            list_t = answer["numbers"]
            try:
                success = answer["success"]
                message = answer["message"]
            except:
                write_file("GOES HERE2")
                success = "true"
            print("Succes: ", success)
            if success == "false":
                print("QUIT TREE")
                write_file("GOES HERE")
                return (message, "quittree")

            # for i in range(len(list_t)):
            #    list_t[i] = list_t[i].replace("@","-")
            if(len(list_t) == 1):
                if(isinstance(list_t[0], basestring)):
                    Data(
                        user=Profile.objects.get(user_id=user_id),
                        entity_name=tree.question_entity_type.entity_group.name,
                        entity_value=list_t[0]
                    ).save()
                    return (message, "nexttree")
                else:
                    if len(list_t[0]) == 2:
                        vall = list_t[0][1]
                        vall = "@".join(vall)
                        Data(
                            user=Profile.objects.get(user_id=user_id),
                            entity_name=tree.question_entity_type.entity_group.name,
                            entity_value=vall
                        ).save()
                        return (message, "nexttree")
                    elif len(list_t[0]) == 5:
                        vall = [list_t[0][1]]
                        Data(
                            user=Profile.objects.get(user_id=user_id),
                            entity_name=tree.question_entity_type.entity_group.name,
                            entity_value=",".join(vall)
                        ).save()
                        return (message, "nexttree")                        
                    else:
                        Data(
                            user=Profile.objects.get(user_id=user_id),
                            entity_name=tree.question_entity_type.entity_group.name,
                            entity_value=",".join(list_t[0])
                        ).save()
                        return (message, "nexttree")
            else:
                cnt = 0
                message = ""
                for data in list_t:
                    if(isinstance(data, basestring)):
                        cnt = cnt + 1
                        ApiMapper(
                            user_id=user_id,
                            number=str(cnt),
                            choice_name=data
                        ).save()
                        message = message + "Speak " + \
                            str(cnt) + " for " + data + ". "
                    else:
                        if len(data) == 2:
                            vall = data[1]
                            vall = "@".join(vall)
                            cnt = cnt + 1
                            ApiMapper(
                                user_id=user_id,
                                number=str(cnt),
                                choice_name=vall
                            ).save()
                            message = message + "Speak " + \
                                str(cnt) + " for " + \
                                data[0] + " having number " + vall + " . "
                        elif len(data) == 5:
                            vall = [data[1]]
                            cnt = cnt + 1
                            ApiMapper(
                                user_id=user_id,
                                number=str(cnt),
                                choice_name=",".join(vall)
                            ).save()
                            message = message + "Speak " + \
                                str(cnt) + " for " + \
                                data[0] + " having denomination " + data[1] + " and a validty of " + data[2] + " . "
                        else:
                            cnt = cnt + 1
                            ApiMapper(
                                user_id=user_id,
                                number=str(cnt),
                                choice_name=",".join(data)
                            ).save()
                            message = message + "Speak " + \
                                str(cnt) + " for " + \
                                data[0] + " having amount " + data[1] + " . "
                print(message)
                return (message, "showmessage")
        except Exception as e:
            print(str(e))
            return (message, "1")
    else:
        print("ELSE")
        return (message, "1")


def parse_is_typable(current_answer, user_id):
    try:
        current_answer = current_answer.replace("<p>", "")
        current_answer = current_answer.replace("</p>", "")
        current_answer = current_answer.replace("&nbsp;", " ")
        flag_what = False
        string = ""
        for words in current_answer.split():
            if words == "/}":
                flag_what = False
            elif flag_what == True:
                variable_name = words
                print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
                obj = Data.objects.filter(entity_name=variable_name,
                                          user__user_id=user_id)
                count = obj.count()
                needed_obj = obj[count - 1]
                value = needed_obj.entity_value
                if value:
                    string += value + " "
            elif words == "{/":
                flag_what = True
            else:
                string += words + " "
        return string
    except:
        return "Corresponding entry is not present  "


def check_velocity_a(name, amount):
    velocity_amount = VelocityChanges.objects.get(
        velocity_name=name).velocity_amount

    if(int(amount) > int(velocity_amount)):
        return False
    else:
        return True


def parse_custom(success, current_answer, user_id):
    try:
        current_answer = current_answer.replace("<p>", "")
        current_answer = current_answer.replace("</p>", "")
        current_answer = current_answer.replace("&nbsp;", " ")
        flag_what = False
        string = ""
        for words in current_answer.split():
            if words == "**1":
                amount = Data.objects.filter(user=Profile.objects.get(
                    user_id=user_id), entity_name="Amount")[0].entity_value
                flag = check_velocity_a("Recharge", amount)
                if not flag:
                    message = "Velocty amount string"
                    return (message, "false")
            else:
                string += words + " "
        return (string, success)
    except Exception as e:
        print(str(e))
        return ("Corresponding entry is not ", success)


def parse_sentence(current_answer, file, user_id, alexa_id, device_id, access_token):
    sentence = current_answer
    sentence = parse_is_typable(sentence, user_id)
    (sentence, dict_temp) = parse_json(sentence, file, user_id)
    sentence = replace_values(sentence, dict_temp)
    (sentence, success) = parse_api(sentence,
                                    user_id, alexa_id, device_id, access_token)
    (sentence, success) = parse_custom(success, sentence, user_id)
    print("SAAAAAAAAAAAA", sentence, success)
# sentence = replace_if_statement(sentence
#sentence = parse_custom(sentence, user_id)
    return (sentence.strip(), success)


def match_choices_final(tree, message, user_id, channel, language, clicked, pipe):
    try:

        json = {}
        clear_data_from_model(user_id)
        pipe_array = pipe.split("|")
        pipe_temp = ""
        for val in pipe_array[:len(pipe_array) - 1]:
            json = match_choices_final_a(Profile.objects.get(
                user_id=user_id).tree, val, user_id, channel, language, clicked, pipe_temp)
            try:
                pipe_temp = json["pipe"]
            except:
                logger.info("no pipe")
            reset_re_question(user_id)
        clear_data_from_model(user_id)
        reset_user(user_id)
        return json
    except Profile.DoesNotExist:
        logger.error("No matching profile found")

def save_to_it_log(alexa_id, device_id, access_token, initial_message, json):
    chatbot_answer = ""
    try:
        chatbot_answer = json["response"]
    except Exception as e:
        logger.error("function: match_choices_final No response %s", str(e))

    try:
        mobile_number = AccessToken.objects.filter(token=access_token)[0].user.username
    except:
        mobile_number = ""

    Logs_IT(query=initial_message,           
           icici_user_id="",
           chatbot_answer=chatbot_answer,
           request_packets_fired="",
           response_packets_fired="",
           access_token=access_token,
           alexa_id=alexa_id,
           device_id=device_id).save()


def save_to_business_log(access_token, initial_message, json):
    chatbot_answer = ""
    try:
        chatbot_answer = json["response"]
    except Exception as e:
        logger.error("function: match_choices_final No response %s", str(e))

    try:
        mobile_number = AccessToken.objects.filter(token=access_token)[0].user.username
    except:
        mobile_number = ""

    Logs_B(query=initial_message,
           mobile_number=mobile_number,
           icici_user_id="",
           chatbot_answer=chatbot_answer,
           ).save()

def save_to_log(clicked, channel, language, initial_message, user_id, answer_succesful, json):
    chatbot_answer = ""
    try:
        chatbot_answer = json["response"]
    except Exception as e:
        logger.error("function: match_choices_final No response %s", str(e))
    if clicked == "1":
        clicked = True
    else:
        clicked = False
    try:
        channel = Channel.objects.get(name=channel)
    except:
        channel = Channel(name=channel)
        channel.save()
    try:
        language = Language.objects.get(name=language)
    except:
        language = Language(name=language)
        language.save()
    Log(query=initial_message,
        user=Profile.objects.get(user_id=user_id),
        channel=channel,
        answer_succesfull=answer_succesful,
        chatbot_answer=chatbot_answer,
        language=language,
        clicked=clicked).save()


def run_all_datavalidators(message, user_id, alexa_id, device_id, access_token):
    dv = DataValidators.objects.filter(run_at_start=True)
    print(dv)
    for validator in dv:
        print(validator)
        d = {}
        exec(str(validator.function), d)
        if d['f'](message, alexa_id, device_id, access_token) is not None:
            print(validator.entity_group, "a")
            print(d['f'](message, alexa_id, device_id, access_token), "a")
            Data(user=Profile.objects.get(user_id=user_id), entity_name=validator.entity_group,
                 entity_value=d['f'](message, alexa_id, device_id, access_token)).save()


def match_choices_final_a(tree, message, user_id, channel, language, clicked, pipe_temp, alexa_id, device_id, access_token):
    # print("TF")
    json = {}
    answer_succesful = True
    initial_message = message

    if tree is None:
        write_file(channel)
        write_file(language)
        write_file("No Tree")
        message = do_pre_processing(message, channel, language)
        #print("TF: ", message)
        write_file("After pre processing: " + message)
        entities = get_entity(message)
        intent = get_intent(message)
        write_file(str(intent))
        logger.info("Intent is : %s", intent)
        logger.info("Entities is : %s", entities)
        print("Intent are: ", intent)
        print("Entities are: ", entities)
        recur_entity_tree(entities, user_id)
        current_query = increment_querycnt(message, channel)
        run_all_datavalidators(message, user_id, alexa_id,
                               device_id, access_token)
        write_file("Goood")
        if intent is not None:
            intent_obj = get_object_or_404(Intent, name=intent[0].name)
            pipe_temp = add_entities_in_user(
                entities, intent_obj, current_query, user_id, pipe_temp)
            print("Okay")
            write_file("Okay")
            json = process_any_tree_with_stages_new(
                intent_obj.tree, entities, user_id, "false", channel, message, "true", pipe_temp, alexa_id, device_id, access_token)
            write_file(str(json) + " Check json")
        else:
            recommendation_list = find_most_similar_intent(message)
            if len(recommendation_list) == 0:
                if entities is not None:
                    recommendation_list = get_recommendation_list_from_entities(
                        entities)
                    (json, value) = get_recommendation_list_json(
                        recommendation_list)
                    answer_succesful = value
                    if(value == False):
                        json["recommended_queries"] = get_random()
                else:
                    answer_succesful = False
                    json["is_typable"] = "true"
                    message = str(Config.objects.all()[
                        0].question_not_recognized)
                    json["response"] = message
            else:
                message = str(Config.objects.all()[0].question_not_recognized)
                json["response"] = message
                json["recommended_queries"] = recommendation_list
                json["is_typable"] = "true"
    else:
        message = do_pre_processing(message, channel, language)
        print("AFTER PRE: ", message)
        intent = get_intent(message)
        print("Intent in else: ", intent)
        if intent is not None:
            entities = get_entity(message)
            recur_entity_tree(entities, user_id)
            current_query = increment_querycnt(message, channel)
            intent_obj = get_object_or_404(Intent, name=intent[0].name)
            pipe_temp = add_entities_in_user(
                entities, intent_obj, current_query, user_id, pipe_temp)
            json = process_any_tree_with_stages_new(
                intent_obj.tree, entities, user_id, "false", channel, message, "true", pipe_temp, alexa_id, device_id, access_token)
        else:
            message = message.lower()
            message = remove_nonalphanumeric(message)
            entities = get_entity(message)
            json = process_any_tree_with_stages_new(
                tree, entities, user_id, "false", channel, message, "false", pipe_temp, alexa_id, device_id, access_token)
    save_to_log(clicked, channel, language, initial_message,
                user_id, answer_succesful, json)
    save_to_business_log(access_token, initial_message, json)
    save_to_it_log(alexa_id, device_id, access_token, initial_message, json)
    return json


def validate_number(message, tree, user_id):
    print("GGGGGGGGG")
    mappers = ApiMapper.objects.filter(user_id=user_id).order_by('-pk')
    print(mappers)
    for mapper in mappers:
        print(mapper.number, mapper.choice_name)
        print(message)
        if mapper.number in message:
            print("YUS")
            try:
                s = mapper.choice_name.split(",")[4]
                write_file(s + "CCCCCCCCCC")
                if (s == "P"):
                    Data(user=Profile.objects.get(user_id=user_id),
                         entity_value=mapper.choice_name.split(",")[1],
                         entity_name="AmountBill"
                         ).save()  # Save something
            except:
                pass
            print("Saving Data", mapper.choice_name)
            Data(user=Profile.objects.get(user_id=user_id),
                 entity_value=mapper.choice_name,
                 entity_name=tree.question_entity_type.entity_group.name).save()
            return


def process_any_tree_with_stages_new(tree, entities, user_id, flag, channel, message, what, pipe_temp, alexa_id, device_id, access_token):
    try:
        logger.info("Entered process_any_tree_with_stages_new")
        current_user = Profile.objects.get(user_id=user_id)
        current_stage = current_user.stage
        print("Current stage", current_stage)
        write_file("Current stage: " + current_stage)
        if current_stage == "pre":
            if tree.question_entity_type is not None and tree.question_entity_type.entity_group.is_typable_special:
                write_file("Super special")
                data_present = is_data_present(tree, user_id)
                print(data_present)
                if data_present[0]:
                    print("Well woo")
                    (tree, pipe_temp) = return_next_tree(
                        tree, user_id, pipe_temp)
                    print("Tree", tree)
                    user = Profile.objects.get(user_id=user_id)
                    user.tree = tree
                    user.stage = "post"
                    user.save()
                    return create_data_stages(tree, user_id, channel, pipe_temp, alexa_id, device_id, access_token)
                else:
                    print("WOHOO")
                    write_file("WOHOO")
                    (message, choice) = do_api_call(tree, get_question(
                        tree, channel), user_id, alexa_id, device_id, access_token)
                    print(message, choice)
                    write_file(message + "Message")
                    write_file(choice + " Choice")
                    if choice == "quittree":
                        json = {}
                        json["is_typable"] = "true"
                        message = message.replace("@", "-")
                        json["response"] = message
                        json["is_answer"] = "true"
                        json["pipe"] = pipe_temp
                        clear_data_from_model(user_id)
                        reset_user(user_id)
                        return json
                    if choice == "showmessage":
                        json = {}
                        json["is_typable"] = "true"
                        message = message.replace("@", "-")
                        json["response"] = message
                        json["is_answer"] = "false"
                        json["pipe"] = pipe_temp
                        user = Profile.objects.get(user_id=user_id)
                        user.stage = "post"
                        user.save()
                        return json
                    if choice == "nexttree":
                        print("Well woo")
                        (tree, pipe_temp) = return_next_tree(
                            tree, user_id, pipe_temp)
                        print("Tree", tree)
                        user = Profile.objects.get(user_id=user_id)
                        user.tree = tree
                        user.stage = "post"
                        user.save()
                        return create_data_stages(tree, user_id, channel, pipe_temp, alexa_id, device_id, access_token)
            else:
                (tree, pipe_temp) = return_next_tree(tree, user_id, pipe_temp)
                print("Tree", tree)
                user = Profile.objects.get(user_id=user_id)
                user.tree = tree
                user.stage = "post"
                user.save()
                return create_data_stages(tree, user_id, channel, pipe_temp, alexa_id, device_id, access_token)
        else:
            if tree.question_entity_type.entity_group.is_typable_special:
                print("WELL WELL WELL")
                validate_number(message, tree, user_id)
                (tree, pipe_temp) = return_next_tree(tree, user_id, pipe_temp)
                user = Profile.objects.get(user_id=user_id)
                user.tree = tree
                user.stage = "pre"
                user.save()
                return process_any_tree_with_stages_new(tree, entities, user_id, flag, channel, message, what, pipe_temp, alexa_id, device_id, access_token)
            else:
                to_delete = ""
                if tree.question_entity_type.entity_group.multi:
                    to_delete = tree.question_entity_type.name
                validate_choice_and_save_from_response(tree, entities, user_id)
                validate_data_and_save_from_response(
                    message, tree, user_id, channel, alexa_id, device_id, access_token)
                (tree, pipe_temp) = return_next_tree(tree, user_id, pipe_temp)
                user = Profile.objects.get(user_id=user_id)
                user.tree = tree
                user.stage = "pre"
                user.save()
                if to_delete != "":
                    Data.objects.filter(entity_name=to_delete,
                                        user=user).delete()
                return process_any_tree_with_stages_new(tree, entities, user_id, flag, channel, message, what, pipe_temp, alexa_id, device_id, access_token)
    except Exception as e:
        print(str(e))
        logger.error(
            "Error process_any_tree_with_stages_new %s", str(e))


def get_random():
    try:
        logger.info("Entered get_random")
        objects = Recommendation.objects.all()
        list_temp = []
        for object in objects:
            list_temp.append(object.query_name)
        list_random = random.sample(list_temp, min(3, len(list_temp)))
        return (list_random)
    except Exception as e:
        logger.error("Error get_random %s", str(e))


def reset_re_question(user_id):
    try:
        user = Profile.objects.get(user_id=user_id)
        user.re_question = False
        user.save()
    except Profile.DoesNotExist:
        pass


def create_data_stages(tree, user_id, channel, pipe_temp, alexa_id, device_id, access_token):
    try:
        logger.info("Entered create_data_stages")
        """if tree.question_entity_type is not None and tree.question_entity_type.entity_group.is_typable_special:
            (message, choice) = do_api_call(tree, get_question(
                tree, channel), user_id, alexa_id, device_id, access_token)
            if choice == "quittree":
                json = {}
                json["is_typable"] = "true"
                message = message.replace("@", "-")
                json["response"] = message
                json["is_answer"] = "true"
                json["pipe"] = pipe_temp
                clear_data_from_model(user_id)
                reset_user(user_id)
                return json
            if choice == "showmessage":
                json = {}
                json["is_typable"] = "true"
                message = message.replace("@", "-")
                json["response"] = message
                json["is_answer"] = "false"
                json["pipe"] = pipe_temp
                user = Profile.objects.get(user_id=user_id)
                user.stage = "post"
                user.save()
                return json
            if choice == "nexttree":
                (tree, pipe_temp) = return_next_tree(tree, user_id, pipe_temp)
                user = Profile.objects.get(user_id=user_id)
                user.tree = tree
                user.stage = "post"
                user.save()
                return create_data_stages(tree, user_id, channel, pipe_temp, alexa_id, device_id, access_token)"""
        if tree.question_entity_type is not None:
            json = create_data_flow(
                tree, user_id, channel, pipe_temp, alexa_id, device_id, access_token)
        else:
            json = create_data_answer(
                tree, channel, user_id, alexa_id, device_id, access_token)
        return json
    except Exception as e:
        logger.error(
            "function: error_data_stages Error from create_data %s", str(e))


def validate_data_and_save_from_response(message, tree, user_id, channel, alexa_id, device_id, access_token):
    try:
        logger.info("Entered validate_data_and_save_from_response")
        entity_type = tree.question_entity_type.entity_group

        dataValidator = DataValidators.objects.get(
            entity_group=entity_type, channel__name=channel)

        # print(dataValidator.function)

        d = {}
        exec(str(dataValidator.function), d)
        user_t = Profile.objects.get(user_id=user_id)
        if d['f'](message, alexa_id, device_id, access_token) is not None:
            logger.info("Value Is: %s", d['f'](
                message, alexa_id, device_id, access_token))
            print("TOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
            print("Name", entity_type.name)
            print("Value", d['f'](message, alexa_id, device_id, access_token))
            Data(entity_name=entity_type.name,
                 entity_value=d['f'](message, alexa_id,
                                     device_id, access_token),
                 user=user_t).save()
            return True
        else:
            user_t.re_question = True
            user_t.save()
            return False
    except DataValidators.DoesNotExist:
        logger.error("No matching extracter found")
    except Exception as e:
        logger.error("Error saveValueFromMessage %s", str(e))


def validate_choice_and_save_from_response(tree, entities, user_id):
    try:
        logger.info("Entered validate_choice_and_save_from_response")
        if tree.question_entity_type.entity_group.is_clickable:
            if entities is not None:
                entity_type = tree.question_entity_type.entity_group
                logger.info("Inside SaveEntity")
                for entity in entities:
                    entity_value = entity.entity_name
                    logger.info("Entity Type: %s", entity_type.name)
                    logger.info("Choice Value %s", entity_value)
                    Data(entity_name=entity_type.name,
                         entity_value=entity_value,
                         user=Profile.objects.get(user_id=user_id)).save()
    except Exception as e:
        logger.error(
            "Error Entered validate_choice_and_save_from_response %s", str(e))


def return_next_tree(tree, user_id, pipe_temp):
    try:
        logger.info("Entered return_next_tree")
        print("Return next tree", tree)
        data_present = is_data_present(tree, user_id)
        print(data_present)
        if data_present[0]:
            count = provide_mapper_count(tree)
            if count == 1:
                pipe_temp += data_present[1][0].entity_value + "|"
                return return_next_tree(get_next_tree_typable(tree), user_id, pipe_temp)
            else:
                mappers = tree.mapper.all()
                for mapper in mappers:
                    for data in data_present[1]:
                        choice = data.entity_value
                        if (choice == mapper.entity.entity_name):
                            pipe_temp += mapper.entity.entity_name + "|"
                            if tree.question_entity_type.entity_group.is_primary:
                                user = Profile.objects.get(user_id=user_id)
                                user.current_entity = mapper.entity
                                user.save()
                            if tree.name == "main.EmployeeId.null.EmployeeName.No.Reenter.null.Tree" and choice == "No":
                                user = Profile.objects.get(user_id=user_id)
                                Data.objects.filter(
                                    user=user, entity_name="Reenter").delete()
                                print("Deleted")
                                # time.sleep(4)
                            return return_next_tree(mapper.next_tree, user_id, pipe_temp)
            return (tree, pipe_temp)
        else:
            return (tree, pipe_temp)
    except Exception as e:
        logger.error("Error return_next_tree %s", str(e))
        return (tree, pipe_temp)


def get_question(tree, channel):
    for choice in tree.question_entity_type.question.group_of_sentences.all():
        if choice.channel.name == channel:
            return choice.sentence


def get_question_id(tree, channel):
    for choice in tree.question_entity_type.question.group_of_sentences.all():
        if choice.channel.name == channel:
            return choice.pk


def get_question_file(tree, channel):
    for choice in tree.question_entity_type.question.group_of_sentences.all():
        if choice.channel.name == channel:
            file = "999abc999"
            if choice.file is not None:
                file = choice.file
    return file


def get_re_question(tree, channel):
    for choice in tree.question_entity_type.re_question.group_of_sentences.all():
        if choice.channel.name == channel:
            return choice.sentence


def get_re_question_file(tree, channel):
    for choice in tree.question_entity_type.re_question.group_of_sentences.all():
        if choice.channel.name == channel:
            file = "999abc999"
            if choice.file is not None:
                file = choice.file
    return file


def create_data_flow(tree, user_id, channel, pipe_temp, alexa_id, device_id, access_token):
    try:
        print("COOOOOOOOOOOL")
        logger.info("Entered create_data_flow")
        json = {}
        if tree.question_entity_type.entity_group.is_typable:
            json["is_typable"] = "true"
        if tree.question_entity_type.entity_group.is_clickable:
            json["is_clickable"] = "true"
        if tree.question_entity_type.entity_group.is_date:
            json["is_date"] = True
        if tree.question_entity_type.entity_group.is_checkbox:
            json["is_checkbox"] = True
        (json["response"], success) = parse_sentence(get_question(
            tree, channel), get_question_file(tree, channel), user_id, alexa_id, device_id, access_token)
        print("COOOOOOOOOOOL")
        json["response_id"] = get_question_id(tree, channel)
        print("COOOOOOOOOOOL")
        if Profile.objects.get(user_id=user_id).re_question:
            print("COOOOOOOOOOOL")
            if tree.question_entity_type.re_question is not None:

                (json["response"], success) = parse_sentence(get_re_question(
                    tree, channel), get_re_question_file(tree, channel), user_id, alexa_id, device_id, access_token)
        print("COOOOOOOOOOOL")
        if success == "true":
            json["choices"] = create_choice_list(
                tree.question_entity_type.entity_group)
        else:
            json["choices"] = []
            json["is_clickable"] = "false"
        print("COOOOOOOOOOOL")
        if success == "true":
            json["is_answer"] = "false"
        else:
            json["is_answer"] = "true"
            clear_data_from_model(user_id)
            reset_user(user_id)
        json["pipe"] = pipe_temp
        print("COOOOOOOOOOOL")
        json["response"] = json["response"].replace("@", "-")
        print("CCCCCCCCCCCCCC: ", json)
        return json
        print("CCCCCCCCCCCCCC: ", json)
    except Exception as e:
        print("Error create_data_flow() %s", str(e))
        logger.error("Error create_data_flow() %s", str(e))


def get_answer(tree, channel):
    for choice in tree.answer.group_of_sentences.all():
        if choice.channel.name == channel:
            return choice.sentence


def get_file(tree, channel):
    for choice in tree.answer.group_of_sentences.all():
        if choice.channel.name == channel:
            file = "999abc999"
            if choice.file is not None:
                file = choice.file
    return file


def save_analytics(user):
    try:
        AnalyticCount(intent=user.current_intent,
                      entity=user.current_entity).save()
    except Exception as e:
        logger.error("Error in save_analytics %s", str(e))


def create_upvote_downvote_links(user):
    upvote_link = "/queryfeedback/" + user.current_query + "/" + user.user_id + "/like"
    downvote_link = "/queryfeedback/" + \
        user.current_query + "/" + user.user_id + "/dislike"
    return (upvote_link, downvote_link)


def get_recommendations(user):
    return recommendations(user.current_intent, user.current_entity)


def reset_user(user_id):
    try:
        user = Profile.objects.get(user_id=user_id)
        user.tree = None
        user.current_intent = None
        user.current_entity = None
        user.re_question = False
        user.stage = "pre"
        user.save()
        print("Okay")
    # except Profile.DoesNotExist:
    #    logger.error("No matching profile found")
    except Exception as e:
        print("This is retarded ", str(e))


def clear_data_from_model(user_id):
    try:
        data = Data.objects.filter(user__user_id=user_id)
        for value in data:
            if not EntityGroup.objects.get(name=value.entity_name).is_persistent:
                Data.objects.filter(user__user_id=user_id,
                                    entity_name=value.entity_name).delete()
        ApiMapper.objects.filter(user_id=user_id).delete()
    except Data.DoesNotExist:
        logger.error("No matching data found")


def create_data_answer(tree, channel, user_id, alexa_id, device_id, access_token):
    try:
        logger.info("Entered create_data_answer")
        json = {}
        user = Profile.objects.get(user_id=user_id)
        save_analytics(user)
        json["is_typable"] = "true"
        (json["response"], success) = parse_sentence(get_answer(
            tree, channel), get_file(tree, channel), user_id, alexa_id, device_id, access_token)
        (upvote_link, downvote_link) = create_upvote_downvote_links(user)
        json["upvote_link"] = upvote_link
        json["downvote_link"] = downvote_link
        json["is_answer"] = "true"
        json["recommended_queries"] = get_recommendations(user)
        json["response"] = json["response"].replace("@", "-")
        print(json)
        clear_data_from_model(user_id)
        reset_user(user_id)
        return json
    except Profile.DoesNotExist:
        print(str(e))
        logger.error("No matching profile found")
    except Exception as e:
        print(str(e))
        logger.error("Error create_data_answer() %s", str(e))


def is_data_present(tree, user_id):
    data = Data.objects.filter(entity_name=tree.question_entity_type.entity_group.name,
                               user__user_id=user_id)
    # print(data[0].entity_value)
    if data.count() > 0:
        return (True, data)
    else:
        return (False, "")


def send_mail(email_id, html_content):

    html_content = html_content
    from_email = 'allincall1221@gmail.com'
    text_content = ''
    msg = EmailMultiAlternatives(
        "PPC Details", text_content, from_email, [email_id])
    msg.attach_alternative(html_content, "text/html")
    msg.send()


def provide_mapper_count(tree):
    return tree.mapper.all().count()


def get_next_tree_typable(tree):
    return tree.mapper.all()[0].next_tree


def do_pre_processing(message, channel, language):
    try:
        logger.info("Entered do_pre_processing")
        write_file(message + " 1")
        message = message.lower()
        write_file(message + " 2")
        message = remove_nonalphanumeric(message)
        write_file(message + " 3")
        message = remove_stopwords(message)
        write_file(message + " 4")
        #message = autocorrect(message, channel, language)

        message = remove_nonalphanumeric(message)
        write_file(message + " 5")
        message = preprocess_question(message)
        write_file(message + " 6")
        if '.com' not in message:
            message = message.replace(".", "")
        write_file(message + " 7")
        logger.info("After Preprocessing: %s", message)
        return message
    except Exception as e:
        logger.error("Error do_pre_processing Error %s", str(e))
        write_file(str(e) + " 8")


def config_logger():
    try:
        log_file_name = 'EasyChatLog.log'
        logging_level = logging.INFO
        formatter = logging.Formatter(
            '%(asctime)s %(name)s %(levelname)s %(message)s')
        handler = logging.handlers.TimedRotatingFileHandler(
            log_file_name, when='midnight', backupCount=2000)
        handler.setFormatter(formatter)
        logger = logging.getLogger('my_logger')
        logger.addHandler(handler)
        logger.setLevel(logging_level)
        logger.propagate = False
    except Exception as e:
        logger.error("Error config_logger %s", str(e))


def get_entity(question):
    entities = Entities.objects.all().order_by('-level')
    list = []
    for entity in entities:
        if entity.is_this_entity(question):
            list.append(entity)
    if list:
        return list
    return UNIDENTIFIED_ENTITY


def get_intent(message):
    message = message.lower()
    intents = Intent.objects.all().order_by('-level')
    list = []
    for intent in intents:
        if intent.is_this_intent(message):
            list.append(intent)
    if list:
        return list
    return UNIDENTIFIED_INTENT


def preprocess_question(question):
    words = set()
    WORD_MAP = {}
    word_mappers = WordMapper.objects.all()
    for word_mapper in word_mappers:
        for similar_word in word_mapper.get_similar_words():
            WORD_MAP[similar_word] = word_mapper.keyword
    for word in WORD_MAP:
        if word != '':
            words.add(word)
        if WORD_MAP[word] != '':
            words.add(WORD_MAP[word])
    modified_question = ''
    for word in question.split(' '):
        replacement = word
        if word in WORD_MAP:
            replacement = WORD_MAP[word]
        modified_question += replacement + ' '
    return re.sub(' +', ' ', modified_question).strip().lower()
