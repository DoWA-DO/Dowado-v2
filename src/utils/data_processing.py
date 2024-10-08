from kiwipiepy import Kiwi


kiwi = Kiwi()

pred_label_decoding = {0: '운동 관련직', 1: '무용 관련직', 2: '안전 관련직', 3: '일반운전 관련직', 4: '기능직', 5: '의복제조 관련직', 6: '조리 관련직', 7: '이미용 관련직', 8: '기타 게임·오락·스포츠 관련직', 9: '고급 운전 관련직', 10: '공학 기술직', 11: '공학 전문직', 12: '음악 관련직', 13: '악기 관련직', 14: '연기 관련직', 15: '웹·게임·애니메이션 관련직', 16: '미술 및 공예 관련직', 17: '기타 특수 예술직', 18: '사회서비스직', 19: '인문계 교육 관련직', 20: '이공계 교육 관련직', 21: '의료관련 전문직', 22: 'IT관련전문직', 23: '금융 및 경영 관련직', 24: '인문 및 사회과학 관련직', 25: '회계 관련직', 26: '언어 관련 전문직', 27: '작가 관련직', 28: '교육관련 서비스직', 29: '기획서비스직', 30: '매니지먼트 관련직', 31: '보건의료 관련 서비스직', 32: '사무 관련직', 33: '영업관련 서비스직', 34: '일반 서비스직', 35: '디자인 관련직', 36: '영상 관련직', 37: '예술기획 관련직', 38: '자연친화 관련직', 39: '농생명산업 관련직', 40: '환경관련 전문직', 41: '법률 및 사회활동 관련직', 42: '이학 전문직'}

def preprocess_text_kiwi(text):
    ''' Kiwi 전처리 '''
    result = kiwi.analyze(text)
    tokens = []
    for sentence in result:
        for word, pos, _, _ in sentence[0]:
            # 명사와 동사 등 주요 품사를 추출
            if pos in ['NNG', 'NNP', 'VV', 'VA']:
                tokens.append(word)
    return ' '.join(tokens)


def label_decoding(text):
    decoded_labels = [pred_label_decoding[p] for p in text]
    return decoded_labels
