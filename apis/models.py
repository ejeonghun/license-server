from django.db import models

class License(models.Model):
    license_key = models.CharField(max_length=24, primary_key=True)             # 숫자와 소문자로 구성된 라이센스 키
    hash_key = models.CharField(max_length=100)                                 # 해시키(MB ID를 해싱하여 사용)
    is_activation = models.BooleanField(default=False)                          # 활성화 여부
    activation_date = models.DateTimeField(null=True, blank=True)               # 활성화 일자
    user_name = models.CharField(max_length=100, null=True, blank=True)         # 관리자 이름
    email = models.EmailField(null=True, blank=True)                            # 이메일
    company = models.CharField(max_length=100, null=True, blank=True)           # 병원 또는 사업장 명 