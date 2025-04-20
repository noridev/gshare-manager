# GShare Manager

GShare Manager는 Proxmox 환경에서 Android VM을 효율적으로 관리하기 위한 자동화 도구입니다. NAS 등의 공유 폴더를 모니터링하다가 파일 변경이 감지되면 VM을 자동으로 시작하고, VM의 사용량이 감소하면 자동으로 종료하는 기능을 제공합니다.

## 주요 기능

- NAS로부터 NFS로 폴더를 공유받아 개별 폴더의 수정 시간 모니터링
- 최근 수정 감지 시 자동 Android VM 시작 및 해당 폴더만 SMB 공유 시작
- VM CPU 사용량 모니터링하여 Idle상태 시 자동 종료 웹훅 전송 및 SMB 공유 중단
- 상태 모니터링 웹 인터페이스

## 사전 준비사항

- Proxmox에 설치된 Android VM (구글포토, Macrodroid 설치)
- Proxmox API token, secret 준비, 권한은 androidVM에 대해서만 주면 됩니다. (아래 예시)
- ![예시](https://github.com/user-attachments/assets/b38d3cdc-65c4-4762-bb57-2dd20b6279ca)

- Macrodroid에서 `/shutdown` 엔드포인트로 웹훅 수신 시 VM이 종료되도록 설정. 웹훅주소 (예: http://192.168.1.9:8080/shutdown)
- ![스크린샷 2025-03-18 114622](https://github.com/user-attachments/assets/5ac321a8-090d-48f0-b371-fd025c6d422f)


## 설치 방법
### 자동 설치
- proxmox node shell에 입력
- `bash -c "$(wget -qLO - https://raw.githubusercontent.com/noridev/gshare-manager/refs/heads/main/lxc_update.sh)"`
- proxmox community script로 만들었습니다. apline linux CT에 docker환경으로 설치됩니다.

### 수동 설치
- SMB포트(445) 사용이 가능한 도커환경
- 본 저장소를 clone후 `git clone -b docker https://github.com/noridev/gshare-manager.git`
- `cd gshare-manager && docker compse up -d --build`

## 설치 후
1. Android VM에 설치된 Macrodroid에서
   - 부팅후 `su --mount-master -c mount -t cifs //{도커호스트주소}/gshare /mnt/runtime/default/emulated/0/DCIM/1 -o username={SMB유저},password={SMB비번},ro,iocharset=utf8` 스크립트 실행으로 마운트 시키는 자동화
   - ![스크린샷 2025-03-18 114451](https://github.com/user-attachments/assets/4d30918f-ac22-4129-912d-a1b0bd85602b)


2. 모니터링할 NAS 폴더를 도커호스트에 NFS 공유하기
   ![NFS 설정 예시](/docs/img/nfs.png)
4. 안내되는 주소로 (예: 192.168.1.10:5000) 접속하여 초기설정을 완료하면 모니터링이 시작됩니다.


## 업데이트

도커 호스트 쉘에서 root계정으로 `update`실행 (아마 안될겁니다)
안되면 아래 커맨드 직접 실행행
```
cd /opt/gshare-manager
git pull
docker compose down
docker compose up -d --build
```

## 라이선스

MIT License
