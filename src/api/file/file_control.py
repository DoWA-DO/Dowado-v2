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
router = APIRouter(prefix="/file", tags=["프로필 이미지 업로드 API"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR,'static/')
IMG_DIR = os.path.join(STATIC_DIR,'images/')
SERVER_IMG_DIR = os.path.join('http://localhost:8000/','static/','images/')
     
# 이미지 저장 폴더 생성 (없는 경우)
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)
    
@router.post('/upload')
async def upload_board(in_files: List[UploadFile] = File(...)):
    file_urls=[]
    for file in in_files:
        currentTime = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        saved_file_name = ''.join([currentTime,secrets.token_hex(16)])
        print(saved_file_name)
        file_location = os.path.join(IMG_DIR,saved_file_name)
        with open(file_location, "wb+") as file_object:
            file_object.write(file.file.read())
        file_urls.append(SERVER_IMG_DIR+saved_file_name)
    result={'fileUrls' : file_urls}
    logger.info(f"{file_urls}에 이미지 업로드가 완료되었습니다.")
    return result

@router.get('/images/{file_name}')
def get_image(file_name:str):
    return FileResponse(''.join([IMG_DIR,file_name]))