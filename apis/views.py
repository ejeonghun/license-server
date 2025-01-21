from django.http import HttpResponse
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
from apis.helper import hash_key_cryto
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_protect
from .models import License
import random
import string
from django.db.models import Q
import pandas as pd
import openpyxl

@swagger_auto_schema(
    method='post',
    operation_summary="라이선스 키 생성",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['id', 'password'],
        properties={
            'id': openapi.Schema(type=openapi.TYPE_STRING, description="관리자 아이디"),
            'password': openapi.Schema(type=openapi.TYPE_STRING, description="관리자 비밀번호"),
        }
    ),
    responses={
        200: openapi.Response('응답', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='응답 메시지',
                    example='라이선스 키가 생성되었습니다./아이디와 비밀번호는 필수 입력값입니다./관리자 계정만 접근 가능합니다.'
                ),
                'license_key': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='생성된 라이선스 키',
                    example='xxxx-xxxx-xxxx-xxxx-xxxx'
                ),
                'result': openapi.Schema(
                    type=openapi.TYPE_INTEGER, 
                    description='결과 코드 (0: 성공, -1: 실패)',
                    example=0
                )
            }
        )),
        500: '서버 오류'
    }
)
@api_view(['post'])
def generator(request): # 라이선스 키 생성 API
    id = request.data.get('id')
    password = request.data.get('password')

    if not id or not password:
        return Response({"message": "아이디와 비밀번호는 필수 입력값입니다.", "result": -1}, 
                      status=status.HTTP_200_OK)

    user = authenticate(username=id, password=password)
    if user is None or not user.is_superuser:
        return Response({"message": "관리자 계정만 접근 가능합니다.", "result": -1}, 
                      status=status.HTTP_200_OK)

    def generate_license_key():
        return '-'.join([''.join(random.choices(string.ascii_lowercase + string.digits, k=4)) 
                        for _ in range(5)])

    while True:
        license_key = generate_license_key()
        try:
            if License.objects.filter(license_key=license_key).exists(): # 중복된 라이선스 키가 있는 경우 다시 생성
                continue
            License.objects.create(license_key=license_key)
            return Response({
                "message": "라이선스 키가 생성되었습니다.",
                'license_key': license_key, 
                "result": 0
            }, status=status.HTTP_200_OK)
        except IntegrityError:
            continue
        except Exception as e:
            return Response({
                'message': str(e), 
                "result": -1
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



@swagger_auto_schema(
    method='post',
    operation_summary="라이선스 키 활성화",
    operation_description="""제공된 라이선스 키를 활성화하고 사용자 정보를 등록합니다.
                            result :  0 : 라이선스 키 활성화 성공
                                      1 : 필수 입력값 누락
                                      2 : 이미 활성화된 라이선스 키
                                      3 : 라이선스 키가 존재하지 않음
                                      4 : 이미 등록된 기기
                            """,
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['license_key', 'hash_key', 'user_name', 'email', 'company'],
        properties={
            'license_key': openapi.Schema(type=openapi.TYPE_STRING, description="활성화할 라이선스 키", example='xxxx-xxxx-xxxx-xxxx-xxxx'),
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
                'result': openapi.Schema(type=openapi.TYPE_STRING)
            }
        )),
        500: '서버 오류'
    }
)
@api_view(['post'])
def activate(request): # 라이선스 키 활성화 API
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
            "result": 1
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
        return Response({'message': '해당 라이선스 키가 존재하지 않습니다.', "result": 3}, status=status.HTTP_200_OK) 

    if license.is_activation:
        return Response({'message': '이미 활성화된 라이선스 키입니다.', "result" : 2}, status=status.HTTP_200_OK)

    # 해시키 중복 검사
    hashed_key = hash_key_cryto(hash_key)
    if License.objects.filter(hash_key=hashed_key).exists():
        return Response({'message': '이미 등록된 기기입니다.', "result" : 4}, status=status.HTTP_200_OK)

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

    return Response({'message': '라이선스 키가 성공적으로 활성화되었습니다.', "result": 0}, status=status.HTTP_200_OK)


@swagger_auto_schema(
    method='post',
    operation_summary="라이선스 해시키 확인",
    request_body=openapi.Schema(
        type=openapi.TYPE_OBJECT,
        required=['hash_key'],
        properties={
            'hash_key': openapi.Schema(
                type=openapi.TYPE_STRING, 
                description="기기 고유 식별자"
            ),
        }
    ),
    responses={
        200: openapi.Response('응답', openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'message': openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='응답 메시지',
                    example='이 기기는 이미 활성화 됨/이 기기는 활성화 되지 않음/필수 입력값 누락'
                ),
                'result': openapi.Schema(
                    type=openapi.TYPE_INTEGER, 
                    description='결과 코드 (0: 성공, 1: 실패)',
                    example=0
                ),
                "hash_key": openapi.Schema(
                    type=openapi.TYPE_STRING, 
                    description='활성화 여부 확인 한 해시 키',
                    example='string'
                )
            }
        )),
        500: '서버 오류'
    }
)
@api_view(['post']) # 해시 키로 기기 활성화 여부 조회 API
def license(request):
    hash_key = request.data.get('hash_key')

    if not hash_key:
        return Response({'message': '필수 입력값 누락', "result": -1}, status=status.HTTP_200_OK)
    
    hashed_key = hash_key_cryto(hash_key)

    try:
        license = License.objects.filter(hash_key=hashed_key).exists()
        if license:
            return Response({'message': '이 기기는 이미 활성화 됨', "hash_key": hash_key, "result": 0}, status=status.HTTP_200_OK)
        else:
            return Response({'message': '이 기기는 활성화 되지 않음',"hash_key": hash_key , "result": 1}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'message': str(e), "result": -1}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# View 로그인 로직
@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('dashboard')
        else:
            messages.error(request, '아이디, 비밀번호를 확인해주세요.')
            
    return render(request, 'login.html')

# View 로그아웃 로직
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# View 페이지에서 사용되는 대시보드 로직
@login_required
def dashboard(request):
    if not request.user.is_superuser:
        return redirect('login')
    
    licenses = License.objects.all()
    
    # 검색 처리
    search_query = request.GET.get('search', '')
    if search_query:
        licenses = licenses.filter(
            Q(license_key__icontains=search_query) |
            Q(user_name__icontains=search_query) |
            Q(company__icontains=search_query)
        )
    
    # 정렬 처리
    sort = request.GET.get('sort', '')
    if sort == 'activation':
        licenses = licenses.filter(is_activation=True).order_by('-activation_date')
    elif sort == 'inactive':
        licenses = licenses.filter(is_activation=False).order_by('-activation_date')
    else:
        licenses = licenses.order_by('-activation_date')
    
    return render(request, 'dashboard.html', {'licenses': licenses})


# View 페이지에서 사용되는 라이선스 생성 로직 
@login_required
def create_license(request):
    if request.method == 'POST':
        def generate_license_key():
            return '-'.join([''.join(random.choices(string.ascii_lowercase + string.digits, k=4)) for _ in range(5)])

        try:
            while True:
                license_key = generate_license_key()
                try:
                    if License.objects.filter(license_key=license_key).exists(): # 중복된 라이선스 키가 있는 경우 다시 생성
                        continue
                    License.objects.create(
                        license_key=license_key,
                        hash_key='',  # 초기에는 빈 값
                        is_activation=False
                    )
                    messages.success(request, '라이센스가 성공적으로 생성되었습니다. 생성된 라이센스 키: ' + license_key)
                    break
                except:
                    continue
        except Exception as e:
            messages.error(request, f'라이센스 생성 중 오류가 발생했습니다: {str(e)}')

    return redirect('dashboard')



# views.py
@login_required
def delete_licenses(request):
    if request.method == 'POST':
        license_keys = request.POST.getlist('license_keys[]')
        if license_keys:
            try:
                deleted_count = License.objects.filter(license_key__in=license_keys).delete()[0]
                messages.success(request, f'{deleted_count}개의 라이선스가 삭제되었습니다.')
            except Exception as e:
                messages.error(request, f'라이선스 삭제 중 오류가 발생했습니다: {str(e)}')
    return redirect('dashboard')




@login_required
def excel_download(request):    
    licenses = License.objects.all()
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(['라이선스 키', '해시 키', '사용자 이름', '이메일', '회사', '활성화 여부', '활성화 날짜'])
    
    for license in licenses:
        ws.append([
            license.license_key,
            license.hash_key,
            license.user_name,
            license.email,
            license.company,
            '활성화' if license.is_activation else '비활성화',
            license.activation_date.strftime('%Y-%m-%d %H:%M:%S') if license.activation_date else ''
        ])

    # 컬럼 너비 자동 조절
    for column in ws.columns:
        max_length = 0
        column_letter = column[0].column_letter
        
        for cell in column:
            try:
                if len(str(cell.value)) > max_length:
                    max_length = len(str(cell.value))
            except:
                pass
                
        adjusted_width = (max_length + 2) * 1.2
        ws.column_dimensions[column_letter].width = adjusted_width
    
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=licenses.xlsx'
    wb.save(response)
    
    return response
