<p align="center">
  <a href="https://aivle.kt.co.kr/home/main/indexMain">
    <img alt="DoWADO Logo" src="asset/img/dowado_logo.png" width="60" style="border-radius: 50%;" />
  </a>
</p>
<h1 align="center">
    DoWA:DO-Web-Server
</h1>

🌟 AIVLE School 5기 빅프로젝트 Team31 'AI 기반 교원 업무 어시스턴트'


## 개발 환경 세팅하기

참고) 본 개발 빌드는 Docker Postgres, redis 이미지를 사용하는 버전입니다.

### 사전 준비

- `python` 버전 관리 목적 `pyenv` 설치
- `python` 패키지 관리 목적 `poetry` 설치
- Docker Descktop 설치
- Dbeaver 설치

### 개발 빌드

1. 가상 환경 생성

   ```shell
   python -m venv .venv
   ```

2. 의존성 설치
   모듈 호환 에러 날 경우 개발 OS 차이 때문이니 poetry.toml 파일 참고해서 우선은 수동으로 설치해주세요.
   추후, window에도 호환되게 수정해두겠습니다.

   ```shell
   poetry install
   ```

3. PostgreSQL 이미지 다운로드

   - 윈도우 CMD를 관리자 모드로 실행하여 도커가 설치되었는지 확인
     ```
     docker -v
     ```
   - 도커 이미지 다운 + 컨테이너 생성
     ```
     docker-compose up -d
     ```
   - 설치했던 도커 데스크톱에서 container가 정상적으로 실행되는지 확인한다.

4. 이후 DBeaver에 접속해서 Docker에서 실행되는 PostgreSQL과 연결

   - 좌측 최상단 콘센트모양(+) 를 클릭
   - Connect to a databse 창이 뜨면 PostgreSQL 아이콘 클릭 후 `다음` 클릭
   - URL 칸에 `jdbc:postgresql://localhost:5432/postgres` 적혀있는지 확인 후
   - 각 칸에 DB정보를 기입한다.
     - Host -> localhost
     - Port -> 5432
     - Database -> postgres
     - Username -> dowado
     - Password -> 1234
   - 이후 좌측 최하단 Test Connection 을 클릭해서 정상적으로 DB서버에 접속되었는지 확인한다.

5. VScode에서 Uvicorn 서버 실행
   ```
   uvicorn src.main:app --reload
   ```
   서버 실행 이후 DBeaver 에서 postgres 를 우클릭하여 검증/재연결 을 눌러서 정상 연결되고 있는지 확인한 후,
   public -> table -> user 을 클릭해서 user테이블이 정상적으로 생성되었는지 확인한다.

6. 이후 `http://127.0.0.1:8000/docs`에 접속하여 API 테스트를 해볼 수 있는 Swagger 페이지에 접속한다. <br>

    각 CRUD 기능이 구현된 example API 를 동작시켜보며 정삭작동하는지 확인한다.

7. 이후 다시 실행할 때에는 다음과 같은 순서로 서버를 실행할 수 있다.

    - `Docker Desktop` 을 열고, Containers 탭을 클릭한 뒤 `postgres-dowado` 컨테이너를 실행한다. + redis 컨테이너 실행
    - `dbeaver`을 열고 좌측 `Database Navigator`에서 `postgres_dowado` 를 우클릭한 후 `Edit-Connection`을 클릭한다.
    - 새로운 창이 열리면 좌측 하단의 `Test Connection`을 눌러서 정상적으로 연결되었는지 확인한다.
    - 이후 fastapi 서버를 실행하면 끝.





(중요) 실행전에 models/model, models/tokenizer 디렉토리 만들고 코드 추가 필요(문의)