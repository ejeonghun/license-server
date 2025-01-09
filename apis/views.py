from django.forms import ValidationError
from django.shortcuts import render
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
import random
import string
from django.db import IntegrityError
from apis.models import License
from django.utils import timezone
from apis.serializers import UserActivateSerializer
from apis.helper import hash_key_cryto, is_hash_key_valid
from django.db import transaction


@swagger_auto_schema(
    method='post',
    operation_summary="라이선스 키 생성",
    responses={
        200: openapi.Response('성공', openapi.Schema(type=openapi.TYPE_OBJECT, properties={
            'license_key': openapi.Schema(type=openapi.TYPE_STRING, example='xxxx-xxxx-xxxx-xxxx-xxxx')
        })),
        500: '서버 오류'
    }
)
@api_view(['post'])
def generator(request):
    def generate_license_key():
        """라이선스 키를 생성하는 함수"""
        return '-'.join([''.join(random.choices(string.ascii_lowercase + string.digits, k=4)) for _ in range(5)])

    while True:
        license_key = generate_license_key()

        # 중복 체크 및 DB에 삽입
        try:
            License.objects.create(license_key=license_key) # DB에 라이선스 키 삽입 및 중복 체크
            return Response({"message": "라이선스 키가 생성되었습니다.",'license_key': license_key, "success": "true"}, status=status.HTTP_200_OK)
        except IntegrityError:
            # 중복된 키가 발생하면 다시 생성
            continue
        except Exception as e:
            return Response({'message': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@swagger_auto_schema(
    method='post',
    operation_summary="라이선스 키 활성화",
    operation_description="제공된 라이선스 키를 활성화하고 사용자 정보를 등록합니다.",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['license_key', 'hash_key', 'user_name', 'email', 'company'],
        properties={
            'license_key': openapi.Schema(type=openapi.TYPE_STRING, description="활성화할 라이선스 키"),
            'hash_key': openapi.Schema(type=openapi.TYPE_STRING, description="기기 고유 식별자"),
            'user_name': openapi.Schema(type=openapi.TYPE_STRING, description="사용자 이름"),
            'email': openapi.Schema(type=openapi.TYPE_STRING, description="사용자 이메일"),
            'company': openapi.Schema(type=openapi.TYPE_STRING, description="회사 또는 기관 이름")
        }
    ),
    responses={
        200: openapi.Response('성공', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(type=openapi.TYPE_STRING, example='라이선스 키가 성공적으로 활성화되었습니다.'),
                'success': openapi.Schema(type=openapi.TYPE_STRING, example='true/false')
            }
        )),
        500: '서버 오류'
    }
)
@api_view(['post'])
def activate(request):
    serializer = UserActivateSerializer(data=request.data)

    # 유효성 검사 수행
    if not serializer.is_valid():
        # 오류 메시지 생성
        error_messages = []
        for field, errors in serializer.errors.items():
            for error in errors:
                error_messages.append(f"{field}: {error}")

        return Response({
            "message": ", ".join(error_messages),
            "success": False
        }, status=status.HTTP_200_OK)  # 200 응답 코드로 반환

    license_key = serializer.validated_data['license_key']
    hash_key = serializer.validated_data['hash_key']
    user_name = serializer.validated_data['user_name']
    email = serializer.validated_data['email']
    company = serializer.validated_data['company']

    # 라이선스 키로 검색
    try:
        license = License.objects.get(license_key=license_key)
    except License.DoesNotExist:
        return Response({'message': '해당 라이선스 키가 존재하지 않습니다.', "success": False}, status=status.HTTP_200_OK)

    if license.is_activation:
        return Response({'message': '이미 활성화된 라이선스 키입니다.', "success": False}, status=status.HTTP_200_OK)

    # 해시키 중복 검사
    hashed_key = hash_key_cryto(hash_key)
    if License.objects.filter(hash_key=hashed_key).exists():
        return Response({'message': '이미 등록된 기기입니다.', "success": False}, status=status.HTTP_200_OK)

    # 활성화 처리
    license.__dict__.update({
        'hash_key': hashed_key,
        'user_name': user_name,
        'email': email,
        'company': company,
        'is_activation': True,
        'activation_date': timezone.now()  # 현재 시간 기록
    })
    license.save()

    return Response({'message': '라이선스 키가 성공적으로 활성화되었습니다.', "success": True}, status=status.HTTP_200_OK)


