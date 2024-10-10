"""
파일 업로드(프로필 사진 업로드) 관련 API 라우터
"""
import datetime
import logging
import os
import secrets
from typing import List
from fastapi import APIRouter, File, UploadFile
from fastapi.responses import FileResponse


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/file", tags=["파일 업로드 API"])

BASE_DIR = f'data/'
IMG_DIR = os.path.join(BASE_DIR,'profile/')
SERVER_IMG_DIR = os.path.join('http://localhost:8000/','static/','images/')
     
# 이미지 저장 폴더 생성 (없는 경우)
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)
    
@router.post(
    '/upload',
    summary="🔵 프로필이미지 업로드 엔드포인트",
    description="- 이미지 업로드 후, 로그아웃하고 재로그인하면 잘되는지 검증필요함.\n- 서버단에서 업로드는 정상확인"
)
async def upload_board(in_files: List[UploadFile] = File(...)):
    file_urls=[]
    for profileimg in in_files:
        saved_file_name = profileimg.filename # 업로드 파일명
        file_location = os.path.join(IMG_DIR, saved_file_name)
        
        # 파일 이름 중복 방지: 파일이 이미 있으면 숫자를 추가하여 저장
        base_name, extension = os.path.splitext(saved_file_name)
        counter = 1
        while os.path.exists(file_location):
            saved_file_name = f"{base_name}_{counter}{extension}"
            file_location = os.path.join(IMG_DIR, saved_file_name)
            counter += 1
        
        with open(file_location, "wb+") as file_object:
            file_object.write(profileimg.file.read())
        
        file_urls.append(SERVER_IMG_DIR + saved_file_name)
        
    result={'fileUrls' : file_urls}
    logger.info(f"{file_urls}에 이미지 업로드가 완료되었습니다.")
    return result


@router.get(
    '/images/{file_name}',
    summary="🔵 업로드한 파일 서버에서 다시 불러오는 엔드포인트",
    description="- 파일명에 확장자 포함시켜야 함."
)
def get_image(file_name:str):
    return FileResponse(''.join([IMG_DIR,file_name]))