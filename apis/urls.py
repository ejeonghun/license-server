from django.urls import path, re_path
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
import apis.views as views
from django.views.generic import RedirectView
from .custom.permissions import IsAllowedIP

schema_view = get_schema_view(
    openapi.Info(
        title="Swagger API Document of License-Server",
        default_version="v1",
        description="License-Server API 문서 입니다.",
        terms_of_service="https://www.google.com/policies/terms/",
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(IsAllowedIP,),  # 허용된 IP주소만 접근 가능
)

urlpatterns = [
    path('', views.login_view, name='login'),                                           # View 로그인 로직
    path('logout/', views.logout_view, name='logout'),                                  # View 로그아웃 로직
    path('dashboard/', views.dashboard, name='dashboard'),                              # View 대시보드 로직
    path('create-license/', views.create_license, name='create_license'),               # View 라이선스 생성 로직
    path('download', views.excel_download, name='라이선스 다운로드'),                             # View 엑셀 다운로드 로직
    path('delete', views.delete_licenses, name='delete_licenses'),                                    # View 라이선스 삭제 로직

    path('api/generator', views.generator, name='라이선스 키 생성'),                        # 라이선스 키 생성 API
    path('api/activate', views.activate, name='라이선스 키 활성화'),                        # 라이선스 키 활성화 API
    path('api/license', views.license, name='해시 키 활성화 여부 조회'),                     # 해시 키로 활성화 여부 조회 API
    
]
urlpatterns += [ # 스웨거
        re_path(r'^docs(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name="schema-json"),
        re_path(r'^docs/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),    ]