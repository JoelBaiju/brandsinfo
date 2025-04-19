from django.http import JsonResponse, HttpResponseBadRequest
from django.http import HttpResponseServerError
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from ..models import Plan_Varients, PhonePeTransaction, Buisnesses
import uuid
import logging
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from brandsinfo import phonepe
from brandsinfo.phonepe import initiate_payment as phonepe_initiate_payment
from rest_framework import status as rest_framework_status
from datetime import timedelta
from django.utils.timezone import now
from communications.ws_notifications import payment_status_update



@api_view(['POST'])
def initiate_payment_view(request):
    if request.method == 'POST':
        try:
            # Get and validate parameters
            bid = request.data.get('bid')  # Changed from POST to data for DRF
            pvid = request.data.get('pvid')
            print(bid, pvid)
            if not bid or not pvid:
                return Response(
                    {'error': 'Both business ID (bid) and plan variant ID (pvid) are required'},
                    status=rest_framework_status.HTTP_400_BAD_REQUEST
                )

            # Get related objects
            try:
                plan_variant = Plan_Varients.objects.get(id=pvid)
                business = Buisnesses.objects.get(id=bid)
            except (Plan_Varients.DoesNotExist, Buisnesses.DoesNotExist):
                return Response(
                    {'error': 'Invalid business or plan variant ID'},
                    status=rest_framework_status.HTTP_400_BAD_REQUEST
                )


            response = phonepe_initiate_payment(int(plan_variant.price))  
            if response['success']:
                print(f"Redirect user to:")
                status = check_payment_status(request,response['order_id'])
                print("Payment status:" ,status)

                with transaction.atomic():
                    PhonePeTransaction.objects.create(
                        order_id=response['order_id'],   
                        user=request.user if request.user.is_authenticated else None,
                        amount=plan_variant.price,
                        buisness=business,
                        plan=plan_variant.plan,
                        plan_variant=plan_variant,
                        expire_at = now() + timedelta(days=int(plan_variant.duration)),
                        payment_url='',
                        status='INITIATED'
                    )
            else:
                return Response(
                    {'error': 'Payment initiation failed', 'details': response},
                    status=rest_framework_status.HTTP_400_BAD_REQUEST
                )

            return Response({
                'redirect_url': response['redirect_url'],
                'success': True,
                'message': 'Payment initiated successfully',
            },status=rest_framework_status.HTTP_200_OK)

        except Exception as e:
            print(str(e))
            # print(response)
            return Response(    
                {'error': 'Internal server error', 'details': str(e),'redirect_url': response['redirect_url']},
                
            )
    
    return Response(
        {'error': 'Only POST method allowed'},
    )
    
   
   
   
   
   
   
   
   
   
import json
   
@api_view(['POST'])   
def payment_callback(request):
    print("\n=== PhonePe Callback Received ===")
    print("Method:", request.method)
    print("Headers:", dict(request.headers))
    print("GET Params:", dict(request.GET))
    print("Body:", request.body.decode('utf-8'))
    # Handle POST request (webhook with JSON payload)
    if request.method == "POST":
        try:
            callback_data = json.loads(request.body.decode('utf-8'))
            print("Callback Data:", callback_data)
            
            if callback_data.get('type') != 'CHECKOUT_ORDER_COMPLETED':
                return JsonResponse({"status": "ignored", "reason": "Not an order completion event"}, status=200)
            
            payload = callback_data.get('payload', {})
            order_id = payload.get('orderId')
            merchant_order_id = payload.get('merchantOrderId')  
            state = payload.get('state')
            
            if not merchant_order_id:
                return HttpResponseBadRequest("Missing merchantOrderId in payload")
            print("merchant_order_id:", merchant_order_id)
            print("order_id:", order_id)
            try:
                txn = PhonePeTransaction.objects.get(order_id=merchant_order_id)
                txn.status = state
                txn.phonepe_order_id = order_id  
                
                payment_details = payload.get('paymentDetails', [{}])[0]
                if payment_details:
                    txn.transaction_id = payment_details.get('transactionId')
                    txn.payment_mode = payment_details.get('paymentMode')
                    txn.amount = payment_details.get('amount')
                
                txn.save()
                
                payment_status_update(merchant_order_id)
                
                return JsonResponse({"status": "success"})
                
            except PhonePeTransaction.DoesNotExist:
                print(f"Transaction not found for order_id: {merchant_order_id}")
                return HttpResponseBadRequest("Transaction not found")
                
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON in callback body")
        except Exception as e:
            print("Callback Processing Error:", str(e))
            return HttpResponseBadRequest("Error processing callback")

    elif request.method == "GET":
       
        return HttpResponseBadRequest("Transaction not found")

    return HttpResponseBadRequest("Invalid request method")
   
   
   
   
   
   
   
   
   
   
   
   
   









def check_payment_status(request, order_id):
    try:
        txn = PhonePeTransaction.objects.get(
            order_id=order_id
        )
        
        status_response = phonepe.check_payment_status(order_id)
        
        # Update our record if status changed
        if status_response['status'] != txn.status:
            txn.status = status_response['status']
            txn.phonepe_response = status_response
            txn.save()
        
        return JsonResponse({
            'order_id': order_id,
            'amount': txn.amount,
            'status': txn.status,
            'user_email': txn.user_email,
            'timestamp': txn.created_at.isoformat(),
            'gateway_response': status_response
        })
        
    except PhonePeTransaction.DoesNotExist:
        return HttpResponseBadRequest({'error': 'Transaction not found'})
    except Exception as e:
        return HttpResponseServerError({'error': str(e)})
    
    
    
    
    
from communications.ws_notifications import new_plan_purchased
    
@api_view(['GET'])
def puchase_plan(request):
    pvid = request.POST.get('pvid')
    bid = request.POST.get('bid')
    plan_varient = Plan_Varients.objects.get(id=3)
    buisness = Buisnesses.objects.get(id=85)
    # if not pvid or not bid:
    #     return Response({'error': 'pvid and bid are required'}, 400)
    new_plan_purchased(buisness)
    return Response({'message': 'Notification sent successfully'}, 200)



















@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pcreds(request):
    response={
        'merchantId': 'SU2504091720243320731397',
        'saltKey': '20435b66-f622-4903-ba22-40bead21262e',
        'saltIndex': '1',
        'appId': '',
        'callbackUrl' : phonepe.PHONEPE_REDIRECT_URL
        
    }
    return Response(response)
