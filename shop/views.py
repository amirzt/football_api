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

from shop.models import Plan, ZarinpalCode, Transaction
from shop.serializers import PlanSerializer, AddTransactionSerializer, TransactionSerializer
from users.models import CustomUser

ZP_API_REQUEST = "https://api.zarinpal.com/pg/v4/payment/request.json"
ZP_API_VERIFY = "https://api.zarinpal.com/pg/v4/payment/verify.json"
ZP_API_STARTPAY = "https://www.zarinpal.com/pg/StartPay/{authority}"

CallbackURL = 'https://api.myscard.ir/api/shop/verify/'


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
                            + "&phone=" + CustomUser.objects.get(id=request.user.id).phone
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
        "metadata": {"phone": request.GET['phone'], "email": ''},
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

