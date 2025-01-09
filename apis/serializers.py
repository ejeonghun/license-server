from rest_framework import serializers

class UserActivateSerializer(serializers.Serializer):
    license_key = serializers.CharField(max_length=24)
    hash_key = serializers.CharField()
    user_name = serializers.CharField(max_length=100, required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    company = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def validate(self, data):
        # 모든 필드가 비어 있는 경우 에러 반환
        if not any([data.get('user_name'), data.get('email'), data.get('company')]):
            raise serializers.ValidationError({'error': '모든 항목을 채워주세요.'})
        return data

    def is_valid(self, raise_exception=False):
        # 기본 유효성 검사를 진행
        valid = super().is_valid(raise_exception=False)

        if not valid:
            # 유효성 검사 실패 시 커스텀 에러 메시지 반환
            raise serializers.ValidationError({'error': '이메일 형식 확인 필요'})

        return valid