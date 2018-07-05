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
import socket

from pprint import pprint
from bs4 import BeautifulSoup

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

from .models import *
from .constants import *


def parse_user_id(response):
    soup = BeautifulSoup(response)
    userids = soup.findAll("bayuserid")

    if len(userids) < 0 or len(userids) == 0:
        return "-5"       # Error Code 5, User Not Found

    if len(userids) == 1:
        # print("".join(userids[0].strings))
        return "".join(userids[0].strings)

    if len(userids) > 1:
        return "-5"       # Error Code 6, Multiple Users Returned


def parse_otp_send(response):
    soup = BeautifulSoup(response)
    actcode = soup.findAll("actcode")

    if len(actcode) < 0 or len(actcode) == 0:
        return "-5"       # Error Code 5, User Not Found

    if len(actcode) == 1:
        return "".join(actcode[0].strings)

    if len(actcode) > 1:
        return "-5"       # Error Code 6, Multiple Users Returned

def parse_ticket_number(response):
    soup = BeautifulSoup(response)
    ticket = soup.findAll("ticket")
    
    if len(ticket) < 0 or len(ticket) == 0:
        return "-5"       # Error Code 5, User Not Found

    if len(ticket) == 1:
        return "".join(ticket[0].strings)

    if len(ticket) > 1:
        return "-5"       # Error Code 6, Multiple Users Returned

def parse_payee_payment_billers(response):
    
    soup = BeautifulSoup(response)

    AddDataPvt125 = soup.findAll("adddatapvt125")
    AddDataPvt126 = soup.findAll("adddatapvt126")
    AddDataPvt127 = soup.findAll("adddatapvt127")
    value = "".join(AddDataPvt125[0].strings)
    
    if(len(AddDataPvt126)==1):
        value += "".join(AddDataPvt126[0].strings)

    if(len(AddDataPvt127)==1):
        value += "".join(AddDataPvt127[0].strings)
    
    #value = value.strip(" ")
    number_of_records = int(value[1:3])
    print(number_of_records)
    more_flag = value[0]
    
    list_of_payee_list_id = []
    list_of_consumer_code = []
    list_of_nick_name = []

    for i in range(number_of_records):
        time_stamp = value[136*i+3:136*i+8]
        payee_list_id = value[136*i+8:136*i+20]
        payee_id = value[136*i+20:136*i+32]
        payee_nick_name = value[136*i+32:136*i+72]
        consumer_code = value[136*i+72:136*i+136]
        payee_type = value[136*i+136]
        payment_type = value[136*i+137]
        status_flag = value[136*i+138]
        if(payee_id[-3:]=='254' or payee_id[-3:]=='783'):
            list_of_payee_list_id.append(payee_list_id)
            list_of_consumer_code.append(consumer_code)
            list_of_nick_name.append(payee_nick_name)

    print(more_flag, list_of_payee_list_id, list_of_consumer_code, list_of_nick_name)

    return (more_flag, list_of_payee_list_id, list_of_consumer_code, list_of_nick_name)


def parse_payee_ids_amount(response, type_of_payee):
    soup = BeautifulSoup(response)
    print(soup)
    instanceamts = soup.findAll("instanceamt")
    payeenames = soup.findAll("payeename")
    consumerids = soup.findAll("consumerid")
    payee_ids = soup.findAll("payeeid")

    payee_name_list = []
    for i in range(len(payeenames)):
        temp = "".join(payeenames[i].strings)
        temp = temp.lstrip('0')
        temp2 = "".join(instanceamts[i].strings).strip()
        temp3 = "".join(consumerids[i].strings).strip()
        temp4 = "".join(payee_ids[i].strings).strip()
        print(temp)
        temp_tuple = (temp, temp2, temp3, temp4, type_of_payee)
        payee_name_list.append(temp_tuple)
    print(payee_name_list)
    return payee_name_list


def parse_payee_ids(response):
    soup = BeautifulSoup(response)
    print(soup)
    payee_ids = soup.findAll("payeeid")
    print(payee_ids)
    payee_id_list = []
    for payee in payee_ids:
        temp = "".join(payee.strings)
        print(temp)
        payee_id_list.append(temp)
    print(payee_id_list)
    return payee_id_list


def parse_last_transactions(response):
    soup = BeautifulSoup(response)
    TransactionDesc = soup.findAll("transactiondescription")
    AmountSpentWithdrawn = soup.findAll("amount")

    if len(TransactionDesc) < 0 or len(TransactionDesc) == 0:
        return []
    
    global_list = []
    for i in range(len(TransactionDesc)):
        desc = TransactionDesc[i]
        amt = AmountSpentWithdrawn[i]
        amount = "".join(amt.strings)
        desc = "".join(desc.strings)
        amount = amount.strip()

        if amount != "":
            amount = str(float(amount) / 100)
        
        temp_tuple = (desc, amount)
        global_list.append(temp_tuple)

    return global_list


def parse_account_numbers(response):
    response = response[response.find(
        "<PvtDataField125") + 1:response.find("</PvtDataField125>")]
    soup = BeautifulSoup(response)

    fsids = soup.findAll("fsid")
    account_numbers = soup.findAll("accnum")

    linked_account_numbers = []

    if len(fsids) < 0 or len(fsids) == 0:
        return "-5"       # Error Code 5, No Account Number

    for i in range(len(fsids)):
        fsid = fsids[i]
        accnum = account_numbers[i]
        accnum_text = "".join(accnum.strings)

        fsid_text = "".join(fsid.strings)

        if(fsid_text == "2") and accnum_text[4:6] == "01":
            linked_account_numbers.append(accnum_text)

    return linked_account_numbers


def parse_credit_card_numbers(response):
    response = response[response.find(
        "<PvtDataField125") + 1:response.find("</PvtDataField125>")]
    print(response)
    soup = BeautifulSoup(response)

    fsids = soup.findAll("fsid")
    account_numbers = soup.findAll("accnum")

    linked_credit_card_numbers = []

    if len(fsids) < 0 or len(fsids) == 0:
        return "-5"       # Error Code 5, No Account Number

    for i in range(len(fsids)):
        fsid = fsids[i]
        accnum = account_numbers[i]

        fsid_text = "".join(fsid.strings)
        accnum_text = "".join(accnum.strings)

        if(fsid_text == "3"):
            linked_credit_card_numbers.append(accnum_text)

    return linked_credit_card_numbers


def parse_account_balance(response):
    soup = BeautifulSoup(response)

    available_balance = soup.findAll("availbal")
    fd_balance = soup.findAll("ffdbal")
    effective_balance = soup.findAll("usrdefbal")

    if len(available_balance) < 0 or len(available_balance) == 0:
        return "-5"       # Error Code 5, No Account Number

    if len(available_balance) > 1:
        return "-5"       # Error Code 6, Multiple Users Returned

    if len(fd_balance) < 0 or len(fd_balance) == 0:
        return "-5"       # Error Code 5, No Account Number

    if len(fd_balance) > 1:
        return "-5"       # Error Code 6, Multiple Users Returned

    if len(effective_balance) < 0 or len(effective_balance) == 0:
        return "-5"       # Error Code 5, No Account Number

    if len(effective_balance) > 1:
        return "-5"       # Error Code 6, Multiple Users Returned

    #return ("".join(available_balance[0].strings), "".join(fd_balance[0].strings), "".join(effective_balance[0].strings))
    return ("".join(available_balance[0].strings), "".join(fd_balance[0].strings), "".join(effective_balance[0].strings)) 



def parse_cc_date_amount(response):
    soup = BeautifulSoup(response)

    tad = soup.findAll("closingbalance")
    if len(tad) < 0 or len(tad) == 0:
        return ("-5", "-5")       # Error Code 5, No Tad

    if len(tad) > 1:
        return ("-5", "-5")       # Error Code 6, Multiple Tad Returned

    due_amount = "".join(tad[0].strings)
    due_date = soup.findAll("printduedate")
    if len(due_date) < 0 or len(due_date) == 0:
        return ("-5", "-5")       # Error Code 5, No Due date

    if len(due_date) > 1:
        return ("-5", "-5")       # Error Code 6, Multiple Due Date Returned

    due_date = "".join(due_date[0].strings)
    return (due_date, due_amount)


def parse_pay_creditcard_bill(response):
    soup = BeautifulSoup(response)

    actcode = soup.findAll("actcode")

    if len(actcode) < 0 or len(actcode) == 0:
        return "-5"       # Error Code 5, No Tad

    if len(actcode) > 1:
        return "-5"       # Error Code 6, Multiple Tad Returned

    act_code = "".join(actcode[0].strings)

    return act_code


def parse_recharge_mobile(response):
    soup = BeautifulSoup(response)
    actcode = soup.findAll("actcode")

    if len(actcode) < 0 or len(actcode) == 0:
        return "-5"       # Error Code 5, No Tad

    if len(actcode) > 1:
        return "-5"       # Error Code 6, Multiple Tad Returned

    act_code = "".join(actcode[0].strings)

    return act_code

def parse_account_number_value(response):

    soup = BeautifulSoup(response)
    account_number_value = soup.findAll("Value")
    account_number_value  = account_number_value[0].split('|')[0]

    return account_number_value 


def parse_presentment_payees(response):

    soup = BeautifulSoup(response)

    schedule_id_list = []
    instance_amt_list = []
    payee_id_list = []
    payee_name_list = []


    soup_list_of_schedule_id = soup.findAll("scheduleid")
    soup_list_of_payee_id = soup.findAll("payeeid")
    soup_list_of_payee_name = soup.findAll("payeename")
    soup_list_of_instance_amt = soup.findAll("instanceamt")

    schedule_id_list = ["".join(soup_list_of_schedule_id[i].strings) for i in range(len(soup_list_of_schedule_id))]
    instance_amt_list = ["".join(soup_list_of_instance_amt[i].strings) for i in range(len(soup_list_of_instance_amt))]
    payee_id_list = ["".join(soup_list_of_payee_id[i].strings) for i in range(len(soup_list_of_payee_id))]
    payee_name_list = ["".join(soup_list_of_payee_name[i].strings) for i in range(len(soup_list_of_payee_name))]

    print(schedule_id_list, "SSSSSS")
    print(instance_amt_list, "SSSSSS")
    print(payee_id_list, "SSSSSS")
    print(payee_name_list, "SSSSSS")

    return (schedule_id_list, instance_amt_list, payee_id_list, payee_name_list)

def parse_payment_biller_success(response):

    soup = BeautifulSoup(response)
    soup_act_code = soup.findAll("actcode")
    act_code = "".join(soup_act_code[0].strings)
    return act_code


def parse_presentment_biller_sucess(response):

    soup = BeautifulSoup(response)
    soup_act_code = soup.findAll("actcode")
    act_code = "".join(soup_act_code[0].strings)
    return act_code