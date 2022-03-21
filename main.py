import re
import requests
import json

BASE_CODE, CHOSUNG, JUNGSUNG = 44032, 588, 28
CHOSUNG_LIST = ['ㄱ', 'ㄲ', 'ㄴ', 'ㄷ', 'ㄸ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅃ', 'ㅅ', 'ㅆ', 'ㅇ', 'ㅈ', 'ㅉ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
JUNGSUNG_LIST = ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ', 'ㅓ', 'ㅔ', 'ㅕ', 'ㅖ', 'ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ', 'ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ',
                 'ㅣ']
JONGSUNG_LIST = [' ', 'ㄱ', 'ㄲ', 'ㄳ', 'ㄴ', 'ㄵ', 'ㄶ', 'ㄷ', 'ㄹ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅁ', 'ㅂ', 'ㅄ', 'ㅅ',
                 'ㅆ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ']
booknum_dict_5_1 = {1: ['ㄱ', 'ㄲ'], 19: ['ㄴ'], 2: ['ㄷ', 'ㄸ'], 29: ['ㄹ'], 3: ['ㅁ'], 4: ['ㅂ', 'ㅃ'], 5: ['ㅅ', 'ㅆ'],
                    6: ['ㅇ'], 7: ['ㅈ', 'ㅉ'], 8: ['ㅊ'], 87: ['ㅋ'], 88: ['ㅌ'], 89: ['ㅍ'], 9: ['ㅎ']}
booknum_dict_5_2 = {2: ['ㅏ'], 3: ['ㅐ', 'ㅑ', 'ㅒ'], 4: ['ㅓ', 'ㅔ', 'ㅕ', 'ㅖ'], 5: ['ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅚ', 'ㅛ'],
                    6: ['ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ'], 7: ['ㅡ', 'ㅢ'], 8: ['ㅣ']}
booknum_dict_5_3 = {2: ['ㅏ', 'ㅐ', 'ㅑ', 'ㅒ'], 3: ['ㅓ', 'ㅔ', 'ㅕ', 'ㅖ'], 4: ['ㅗ', 'ㅘ', 'ㅙ', 'ㅚ', 'ㅛ'],
                    5: ['ㅜ', 'ㅝ', 'ㅞ', 'ㅟ', 'ㅠ', 'ㅡ', 'ㅢ'], 6: ['ㅣ']}


# 자음 모음 분리기
def convert(test_keyword):
    split_keyword_list = list(test_keyword)
    result = list()
    for keyword in split_keyword_list:
        if re.match('.*[ㄱ-ㅎㅏ-ㅣ가-힣]+.*', keyword) is not None:
            char_code = ord(keyword) - BASE_CODE
            char1 = int(char_code / CHOSUNG)
            result.append(CHOSUNG_LIST[char1])
            char2 = int((char_code - (CHOSUNG * char1)) / JUNGSUNG)
            result.append(JUNGSUNG_LIST[char2])
            char3 = int((char_code - (CHOSUNG * char1) - (JUNGSUNG * char2)))
            if char3 == 0:
                result.append('#')
            else:
                result.append(JONGSUNG_LIST[char3])
        else:
            result.append(keyword)
    return "".join(result)


# 도서기호
def book_number(title: str, author: str) -> str:
    first_num, second_num = "0", "0"
    tmp_title = convert(title[0])[0]  # 제목 첫자음
    tmp_author = convert(author[1])  # 저자 2번째 글자 자음모음 분리
    tmp_1 = tmp_author[0]  # 자음
    tmp_2 = tmp_author[1]  # 모음
    # 리재철 제5표
    for k, v in booknum_dict_5_1.items():
        if tmp_1 in v:
            first_num = str(k)
    if first_num != "8":
        for k, v in booknum_dict_5_2.items():
            if tmp_2 in v:
                second_num = str(k)
    else:
        for k, v in booknum_dict_5_3.items():
            if tmp_2 in v:
                second_num = str(k)

    return author[0] + first_num + second_num + tmp_title

# 데이터 파싱
def book_info(isbn: int) -> dict:
    output_data = {}
    result = {}

    isbn = str(isbn)
    data_format = "json"

    seoji_param = {}
    seoji_key = "KEY DATA"
    seoji_param.setdefault('result_style', data_format)
    seoji_param.setdefault('page_no', '1')
    seoji_param.setdefault('page_size', '1')
    seoji_param.setdefault('isbn', isbn)
    seoji_param.setdefault('cert_key', seoji_key)
    url = "https://seoji.nl.go.kr/landingPage/SearchApi.do"
    request_seoji = requests.get(url,params=seoji_param)
    if request_seoji.status_code == 200 :
        try :
            seoji_data = request_seoji.json()
            seoji_data = seoji_data['docs'][0]
            if seoji_data['FORM'] == "전자책" :
                isbn = seoji_data['RELATED_ISBN']
        except :
            print("국립중앙도서관 API 에러 발생")
    else :
        print("국립중앙도서관 API 호출 에러 발생")

    dlib_param = {}
    dlib_key = "KEY DATA"
    dlib_param.setdefault('format', data_format)
    dlib_param.setdefault('isbn13', isbn)
    dlib_param.setdefault('authKey', dlib_key)
    url = "http://dlib.data4library.kr/api/srchDtlList"
    request_dlib = requests.get(url,params=dlib_param)
    if request_dlib.status_code == 200 :
        try : 
            elib_data = request_dlib.json()
            elib_data = elib_data['response']['detail'][0]['book']
        except :
            print("정보나루 API 에러 발생 (종이책 ISBN 가져오기 실패)")
    else :
        print("정보나루 API 호출 에러 발생")

    output_data.update(seoji_data)
    output_data.update(elib_data)
    
    for k,v in output_data.items() :
        if k in ['authors','class_no','class_nm','bookImageURL','isbn','isbn13','description','publisher','bookname','FORM','FORM_DETAIL','EA_ADD_CODE','PUBLISH_PREDATE'] :
            result[k] = v

    return result


if __name__ == '__main__':

    isbn = 9788959165575
    data = book_info(isbn)
    print("입력한 isbn : ",str(isbn))
    print("도서기호:", book_number(title="환한 숨 조해진 소설집", author="조초진"))
    for k,v in data.items() :
        print(k,v)
