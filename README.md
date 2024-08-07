# Memento AI 과제 - URL 단축 서비스

## 프로젝트 설명

각 API에 대한 설명과 상태 코드별 Response를 Swagger에 작성해 두었습니다.

보너스 기능으로 URL 만료 기능, 통계 기능, 테스트 코드를 포함하여 만들었습니다.

추가로 만료된 단축 URL을 일괄적으로 삭제하는 스케줄러를 추가해 두었습니다.

부가 기능: 트랜잭션, CommonResponse, CustomException과 ResponseType, MongoDB Replica Set, Docker

### DB 채택 이유

DB는 MongoDB를 채택했습니다.

- **복잡하지 않은 프로젝트 구조.**
    - 데이터 간에 많은 연관 관계가 필요한 경우 MySQL이나 PostgreSQL을 채택했을 것입니다.
- **분산 네트워크 지원.**
    - MySQL이나 PostgreSQL도 마스터 슬레이브 전략을 통해 분산 DB 구현이 가능하지만 설정이 복잡해집니다.
    - 반드시 RDB를 채택해야 하는 순간이 아니므로 NoSQL인 MongoDB를 채택했습니다.
- **영구적인 저장.**
    - 같은 NoSQL인 Redis와 고민했으나 기본적으로 만료되지 않는 URL을 제공하는 서비스이기 때문에 메모리에 데이터를 저장해 분실 가능성이 있는 Redis는 사용하지 않았습니다.

## 프로젝트 실행 방법

루트 디렉토리에서 다음 명령어를 실행합니다.

```sh
docker-compose up -d
```

만약 인식 안될시 docker ps를 통해 fastapi서버 컨테이너 ID 사용

```sh
docker exec -i [컨테이너 ID] pytest
```