from django.urls import path, re_path
from django.conf import settings
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
import apis.views as views

schema_view = get_schema_view(
    openapi.Info(
        title="Swagger API Document of License-Server",
        default_version="v1",
        description="License-Server API 문서 입니다.",
        terms_of_service="https://www.google.com/policies/terms/",
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

urlpatterns = [
    path('api/generator', views.generator, name='라이선스 키 생성'), # 라이선스 키 생성 API
    path('api/activate', views.activate, name='라이선스 키 활성화'), # 라이선스 키 활성화 API
]

if settings.DEBUG:
    urlpatterns += [
        re_path(r'^docs(?P<format>\.json|\.yaml)$', schema_view.without_ui(cache_timeout=0), name="schema-json"),
        re_path(r'^docs/$', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
        re_path(r'^redoc/$', schema_view.with_ui('redoc', cache_timeout=0), name='schema-redoc'),    ]