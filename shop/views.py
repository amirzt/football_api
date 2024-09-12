import datetime
import json
import threading

import requests
from django.http import HttpResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response

from shop.models import Plan, ZarinpalCode, Transaction, LotteryChance
from shop.serializers import PlanSerializer, AddTransactionSerializer, TransactionSerializer, GetLotteryChanceSerializer
from users.models import CustomUser, Lottery

ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"

CallbackURL = 'https://api.footsoccer.top/api/shop/verify/'
lottery_CallbackURL = 'https://api.footsoccer.top/api/shop/lottery_verify/'


@api_view(['POST'])
@permission_classes([AllowAny])
def get_plans(request):
    if 'special' in request.data:
        plans = Plan.objects.filter(is_available=True)
    else:
        plans = Plan.objects.filter(is_available=True,
                                    is_special=False)
    # user = CustomUser.objects.get(id=request.user.id)

    return Response({
        "plans": PlanSerializer(plans, many=True).data,
        # 'user': CustomUserSerializer(user).data,
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_zarinpal_url(request):
    plan = Plan.objects.get(id=request.data['plan'])

    serializer = AddTransactionSerializer(data=request.data,
                                          context={'user': request.user,
                                                   'plan': plan.id,
                                                   'price': plan.price,
                                                   'gateway': 'zarinpal',
                                                   'gateway_code': ZarinpalCode.objects.last().code,
                                                   'description': 'خرید اشتراک ' + plan.title})
    if serializer.is_valid():
        transaction = serializer.save()
        return Response({
            'purchase_url': '?merchant=' + ZarinpalCode.objects.last().code
                            + "&email=" + CustomUser.objects.get(id=request.user.id).email
                            + "&amount=" + str(int(transaction.price))
                            + "&description=" + 'خرید اشتراک ' + plan.title
                            + "&transaction_id=" + str(transaction.id)
        },
            status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def send_request(request):
    req_data = {
        "merchant_id": request.GET['merchant'],
        "amount": int(request.GET['amount']),
        "callback_url": CallbackURL,
        "description": request.GET['description'],
        "metadata": {"email": request.GET['email']},
    }
    req_header = {"accept": "application/json",
                  "content-type": "application/json'"}
    req = requests.post(url=ZP_API_REQUEST, data=json.dumps(
        req_data), headers=req_header)
    authority = req.json()['data']['authority']

    transaction = Transaction.objects.get(id=request.GET['transaction_id'])
    transaction.gateway_code = authority
    transaction.save()

    if len(req.json()['errors']) == 0:
        return redirect(ZP_API_STARTPAY.format(authority=authority))
    else:
        e_code = req.json()['errors']['code']
        e_message = req.json()['errors']['message']
        return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")


def update_expire_date(params):
    user = CustomUser.objects.get(id=params['user'])

    if user.expire_date < timezone.now():
        user.expire_date = timezone.now() + datetime.timedelta(days=int(params['duration']))
    else:
        user.expire_date += datetime.timedelta(days=int(params['duration']))
    user.save()


def verify(request):
    # t_status = request.GET.get('Status')
    t_authority = request.GET['Authority']

    if request.GET.get('Status') == 'OK':

        transaction = Transaction.objects.get(gateway_code=t_authority)

        req_header = {"accept": "application/json",
                      "content-type": "application/json'"}
        req_data = {
            "merchant_id": ZarinpalCode.objects.last().code,
            "amount": transaction.price,
            "authority": t_authority
        }
        req = requests.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
        if len(req.json()['errors']) == 0:
            t_status = req.json()['data']['code']

            if t_status == 100:
                # save reservation
                transaction.state = 'success'
                transaction.tracking_code = req.json()['data']['ref_id']
                transaction.save()

                # update expire date
                data = {
                    'user': transaction.user.id,
                    'duration': transaction.plan.duration
                }
                thread = threading.Thread(target=update_expire_date,
                                          args=[data])
                thread.setDaemon(True)
                thread.start()
                #
                context = {
                    'tracking_code': transaction.tracking_code
                }
                return render(request, 'success_payment.html', context)
                # return HttpResponse('Transaction success.\nRefID: ' + str(
                #     req.json()['data']['ref_id']
                # ))
            elif t_status == 101:
                context = {
                    'tracking_code': transaction.tracking_code
                }
                return render(request, 'error_payment.html', context)
                # return HttpResponse('Transaction submitted : ' + str(
                #     req.json()['data']['message']
                # ))
            else:
                return render(request, 'error_payment.html')

                # return HttpResponse('Transaction failed.\nStatus: ' + str(
                #     req.json()['data']['message']
                # ))
        else:
            return render(request, 'error_payment.html')

            # e_code = req.json()['errors']['code']
            # e_message = req.json()['errors']['message']
            # return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")
    else:
        return render(request, 'error_payment.html')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def lottery(request):
    user = CustomUser.objects.get(id=request.user.id)
    try:
        lo = LotteryChance.objects.get(user=user,
                                       date=datetime.datetime.today())
        if lo.state == LotteryChance.StateChoices.PENDING or lo.state == LotteryChance.StateChoices.FAILED:
            return Response(status=status.HTTP_402_PAYMENT_REQUIRED)
        elif lo.state == LotteryChance.StateChoices.FINISHED:
            return Response(status=status.HTTP_403_FORBIDDEN)
        else:
            lo.state = LotteryChance.StateChoices.FINISHED
            lo.result = int(request.data['score'])
            lo.save()
            user.score = int(request.data['score']) + user.score
            user.save()
            return Response(status=status.HTTP_200_OK)

    except LotteryChance.DoesNotExist:
        lo = LotteryChance(user=user,
                           date=datetime.datetime.today(),
                           state=LotteryChance.StateChoices.SUCCESS)
        lo.save()
        return Response(status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_chances(request):
    chances = LotteryChance.objects.filter(user_id=request.user.id,
                                           state=LotteryChance.StateChoices.SUCCESS)
    return Response(GetLotteryChanceSerializer(chances, many=True).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_lottery_url(request):
    lottery_chance = LotteryChance(user_id=request.user.id, )
    lottery_chance.save()

    serializer = AddTransactionSerializer(data=request.data,
                                          context={'user': request.user,
                                                   'chance': lottery_chance.id,
                                                   'gateway': 'zarinpal',
                                                   'price': Lottery.objects.filter(active=True).last().price,
                                                   'gateway_code': ZarinpalCode.objects.last().code,
                                                   'plan': Plan.objects.filter().first().id,
                                                   'description': 'خرید گردونه'})
    if serializer.is_valid():
        transaction = serializer.save()
        lottery_chance.transaction = transaction
        lottery_chance.save()
        return Response({
            'purchase_url': '?merchant=' + ZarinpalCode.objects.last().code
                            + "&email=" + CustomUser.objects.get(id=request.user.id).email
                            + "&amount=" + str(int(transaction.price))
                            + "&description=" + 'خرید گردونه'
                            + "&transaction_id=" + str(transaction.id)
        },
            status=status.HTTP_200_OK)
    else:
        return Response(status=status.HTTP_400_BAD_REQUEST)


def send_lottery_request(request):
    req_data = {
        "merchant_id": request.GET['merchant'],
        "amount": int(request.GET['amount']),
        "callback_url": lottery_CallbackURL,
        "description": request.GET['description'],
        "metadata": {"email": request.GET['email']},
    }
    req_header = {"accept": "application/json",
                  "content-type": "application/json'"}
    req = requests.post(url=ZP_API_REQUEST, data=json.dumps(
        req_data), headers=req_header)
    authority = req.json()['data']['authority']

    transaction = Transaction.objects.get(id=request.GET['transaction_id'])
    transaction.gateway_code = authority
    transaction.save()

    if len(req.json()['errors']) == 0:
        return redirect(ZP_API_STARTPAY.format(authority=authority))
    else:
        e_code = req.json()['errors']['code']
        e_message = req.json()['errors']['message']
        return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")


def lottery_verify(request):
    t_authority = request.GET['Authority']

    if request.GET.get('Status') == 'OK':

        transaction = Transaction.objects.get(gateway_code=t_authority)

        req_header = {"accept": "application/json",
                      "content-type": "application/json'"}
        req_data = {
            "merchant_id": ZarinpalCode.objects.last().code,
            "amount": transaction.price,
            "authority": t_authority
        }
        req = requests.post(url=ZP_API_VERIFY, data=json.dumps(req_data), headers=req_header)
        if len(req.json()['errors']) == 0:
            t_status = req.json()['data']['code']

            if t_status == 100:
                # save reservation
                transaction.state = 'success'
                transaction.tracking_code = req.json()['data']['ref_id']
                transaction.save()

                # update expire date
                lottery_chance = LotteryChance.objects.get(transaction=transaction)
                lottery_chance.state = LotteryChance.StateChoices.SUCCESS
                lottery_chance.save()
                #
                context = {
                    'tracking_code': transaction.tracking_code
                }
                return render(request, 'success_payment.html', context)
                # return HttpResponse('Transaction success.\nRefID: ' + str(
                #     req.json()['data']['ref_id']
                # ))
            elif t_status == 101:
                context = {
                    'tracking_code': transaction.tracking_code
                }
                return render(request, 'error_payment.html', context)
                # return HttpResponse('Transaction submitted : ' + str(
                #     req.json()['data']['message']
                # ))
            else:
                return render(request, 'error_payment.html')

                # return HttpResponse('Transaction failed.\nStatus: ' + str(
                #     req.json()['data']['message']
                # ))
        else:
            return render(request, 'error_payment.html')

            # e_code = req.json()['errors']['code']
            # e_message = req.json()['errors']['message']
            # return HttpResponse(f"Error code: {e_code}, Error Message: {e_message}")
    else:
        return render(request, 'error_payment.html')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def use_chance(request):
    lottery_chance = LotteryChance.objects.get(id=request.data['id'])
    lottery_chance.state = LotteryChance.StateChoices.FINISHED
    lottery_chance.result = request.data['result']

    lottery_chance.save()

    user = CustomUser.objects.get(id=request.user.id)
    user.score = user.score + int(lottery_chance.result)
    user.save()
    return Response(status=status.HTTP_200_OK)
