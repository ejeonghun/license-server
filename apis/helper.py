import hashlib

def hash_key_cryto(board_id):
    """ 메인보드 ID를 해시하는 함수 - SHA256 """
    return hashlib.sha256(board_id.encode()).hexdigest()

def is_hash_key_valid(input_hash, stored_hash):
    """ 입력된 메인보드 ID가 저장된 해시와 동일한지 검증하는 함수 """
    return hash_key_cryto(input_hash) == stored_hash