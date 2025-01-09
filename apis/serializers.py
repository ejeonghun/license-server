from rest_framework import serializers

class UserActivateSerializer(serializers.Serializer):
    license_key = serializers.CharField(max_length=24)
    hash_key = serializers.CharField()
    user_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    company = serializers.CharField(max_length=100, required=False, allow_blank=True)

    # def validate(self, data):
    #     # 모든 필드가 비어 있는 경우 에러 반환
    #     if not any([data.get('user_name'), data.get('email'), data.get('company')]):
    #         raise serializers.ValidationError({'message': '모든 항목을 채워주세요.', 'success': "false"})
    #     return data
    def validate(self, attrs):
        errors = {}
        if not attrs.get('license_key'):
            errors['license_key'] = "라이선스 키는 필수 입력값입니다."
        if not attrs.get('hash_key'):
            errors['hash_key'] = "해시 키는 필수 입력값입니다."
        if not attrs.get('user_name'):
            errors['user_name'] = "관리자 이름은 필수 입력값입니다."
        if not attrs.get('email'):
            errors['email'] = "이메일은 필수 입력값입니다."
        if not attrs.get('company'):
            errors['company'] = "병원 또는 사업장 명은 필수 입력값입니다."

        if errors:
            raise serializers.ValidationError(errors)

        return attrs

    def is_valid(self, raise_exception=False):
        # 기본 유효성 검사를 진행
        try:
            valid = super().is_valid(raise_exception=False)

            if not valid:
                # 유효성 검사 실패 시 커스텀 에러 메시지 반환
                self._validated_data = {'message': '이메일 형식 확인 필요', "success": "false"}
                return False
            return valid
        except Exception as e:
            self._validated_data = {'message': str(e), "success": "false"}
            return True