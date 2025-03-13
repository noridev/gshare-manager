from dataclasses import dataclass
import os
import yaml
from typing import Dict, Any, Optional

@dataclass
class Config:
    # Proxmox android 사용량 감시
    ## Proxmox API 호스트
    PROXMOX_HOST: str
    ## Proxmox 노드 이름
    NODE_NAME: str
    ## android VM ID
    VM_ID: str
    ## API 토큰 ID
    TOKEN_ID: str
    ## API 토큰 시크릿
    SECRET: str
    ## CPU 사용량 임계치(%)
    CPU_THRESHOLD: float
    ## 체크 간격(초)
    CHECK_INTERVAL: int
    ## 체크 횟수
    THRESHOLD_COUNT: int
    
    # 폴더용량 감시
    ## 감시폴더 마운트 경로
    MOUNT_PATH: str
    ## 폴더 용량 확인 시간 초과(초)
    GET_FOLDER_SIZE_TIMEOUT: int
    ## macrodroid 종료 웹훅 URL
    SHUTDOWN_WEBHOOK_URL: str
    
    # SMB 설정
    ## SMB 공유 이름
    SMB_SHARE_NAME: str
    ## SMB 사용자 이름
    SMB_USERNAME: str
    ## SMB 비밀번호
    SMB_PASSWORD: str
    ## SMB 설명
    SMB_COMMENT: str
    ## SMB 게스트 허용 여부
    SMB_GUEST_OK: bool
    ## SMB 읽기 전용 여부
    SMB_READ_ONLY: bool
    ## SMB 링크 디렉토리
    SMB_LINKS_DIR: str
    
    # 로그 시간대
    TIMEZONE: str = 'Asia/Seoul'
    
    ## SMB 포트
    SMB_PORT: int = 445
    
    # 로그 레벨 설정
    LOG_LEVEL: str = 'INFO'

    # NFS 설정
    ## NFS 공유 경로
    NFS_PATH: Optional[str] = None

    @classmethod
    def load_config(cls) -> 'Config':
        """설정 파일에서 설정 로드"""
        # Docker 환경을 가정하고 설정 파일 경로 고정
        config_path = '/config/config.yaml'
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r', encoding='utf-8') as f:
                    yaml_config = yaml.safe_load(f)
                print(f"설정 파일 로드 완료: {config_path}")
            else:
                raise ValueError("설정 파일을 찾을 수 없습니다.")
        except Exception as e:
            print(f"설정 파일 로드 실패: {e}")
            raise ValueError("YAML 설정 파일을 로드할 수 없습니다.")

        # 필수 필드 확인
        required_fields = [
            'proxmox', 'mount', 'smb', 'timezone',
            'credentials'
        ]
        
        for field in required_fields:
            if field not in yaml_config:
                yaml_config[field] = {}
        
        if 'cpu' not in yaml_config['proxmox']:
            yaml_config['proxmox']['cpu'] = {}
            
        if 'credentials' not in yaml_config:
            yaml_config['credentials'] = {}

        # YAML 설정에서 값 추출
        config_dict = {
            'PROXMOX_HOST': yaml_config['credentials'].get('proxmox_host', ''),
            'NODE_NAME': yaml_config['proxmox'].get('node_name', ''),
            'VM_ID': yaml_config['proxmox'].get('vm_id', ''),
            'TOKEN_ID': yaml_config['credentials'].get('token_id', ''),
            'SECRET': yaml_config['credentials'].get('secret', ''),
            'CPU_THRESHOLD': yaml_config['proxmox']['cpu'].get('threshold', 10.0),
            'CHECK_INTERVAL': yaml_config['proxmox']['cpu'].get('check_interval', 60),
            'THRESHOLD_COUNT': yaml_config['proxmox']['cpu'].get('threshold_count', 3),
            'MOUNT_PATH': yaml_config['mount'].get('path', '/mnt/gshare'),
            'GET_FOLDER_SIZE_TIMEOUT': yaml_config['mount'].get('folder_size_timeout', 30),
            'SHUTDOWN_WEBHOOK_URL': yaml_config['credentials'].get('shutdown_webhook_url', ''),
            'SMB_SHARE_NAME': yaml_config['smb'].get('share_name', 'gshare'),
            'SMB_USERNAME': yaml_config['credentials'].get('smb_username', ''),
            'SMB_PASSWORD': yaml_config['credentials'].get('smb_password', ''),
            'SMB_COMMENT': yaml_config['smb'].get('comment', 'GShare SMB 공유'),
            'SMB_GUEST_OK': yaml_config['smb'].get('guest_ok', False),
            'SMB_READ_ONLY': yaml_config['smb'].get('read_only', True),
            'SMB_LINKS_DIR': yaml_config['smb'].get('links_dir', '/mnt/gshare_links'),
            'SMB_PORT': yaml_config['smb'].get('port', 445),
            'TIMEZONE': yaml_config.get('timezone', 'Asia/Seoul'),
            'LOG_LEVEL': yaml_config.get('log_level', 'INFO')
        }

        # NFS 설정 추가
        if 'nfs' in yaml_config and 'path' in yaml_config['nfs']:
            config_dict['NFS_PATH'] = yaml_config['nfs']['path']
            
        # 로그 레벨 로드 및 환경 변수 설정
        log_level = yaml_config.get('log_level', 'INFO')
        os.environ['LOG_LEVEL'] = log_level

        return cls(**config_dict)

    @staticmethod
    def update_yaml_config(config_dict: Dict[str, Any]) -> None:
        """YAML 설정 파일 업데이트"""
        # Docker 환경을 가정하고 설정 파일 경로 고정
        yaml_path = '/config/config.yaml'
        
        try:
            if os.path.exists(yaml_path):
                with open(yaml_path, 'r', encoding='utf-8') as f:
                    yaml_config = yaml.safe_load(f)
                if yaml_config is None:
                    yaml_config = {}
            else:
                # 설정 파일이 없으면 기본 구조 생성
                yaml_config = {
                    'proxmox': {'cpu': {}},
                    'mount': {},
                    'smb': {},
                    'credentials': {},
                    'nfs': {},
                    'timezone': 'Asia/Seoul',
                    'log_level': 'INFO'
                }
        except Exception:
            # 파일을 읽을 수 없는 경우 기본 구조 생성
            yaml_config = {
                'proxmox': {'cpu': {}},
                'mount': {},
                'smb': {},
                'credentials': {},
                'nfs': {},
                'timezone': 'Asia/Seoul',
                'log_level': 'INFO'
            }

        # 일반 설정 업데이트
        if 'NODE_NAME' in config_dict:
            yaml_config['proxmox']['node_name'] = config_dict['NODE_NAME']
        if 'VM_ID' in config_dict:
            yaml_config['proxmox']['vm_id'] = config_dict['VM_ID']
        if 'CPU_THRESHOLD' in config_dict:
            yaml_config['proxmox']['cpu']['threshold'] = float(config_dict['CPU_THRESHOLD'])
        if 'CHECK_INTERVAL' in config_dict:
            yaml_config['proxmox']['cpu']['check_interval'] = int(config_dict['CHECK_INTERVAL'])
        if 'THRESHOLD_COUNT' in config_dict:
            yaml_config['proxmox']['cpu']['threshold_count'] = int(config_dict['THRESHOLD_COUNT'])
        if 'MOUNT_PATH' in config_dict:
            yaml_config['mount']['path'] = config_dict['MOUNT_PATH']
        if 'GET_FOLDER_SIZE_TIMEOUT' in config_dict:
            yaml_config['mount']['folder_size_timeout'] = int(config_dict['GET_FOLDER_SIZE_TIMEOUT'])
        if 'SMB_SHARE_NAME' in config_dict:
            yaml_config['smb']['share_name'] = config_dict['SMB_SHARE_NAME']
        if 'SMB_COMMENT' in config_dict:
            yaml_config['smb']['comment'] = config_dict['SMB_COMMENT']
        if 'SMB_GUEST_OK' in config_dict:
            yaml_config['smb']['guest_ok'] = config_dict['SMB_GUEST_OK'] == 'yes'
        if 'SMB_READ_ONLY' in config_dict:
            yaml_config['smb']['read_only'] = config_dict['SMB_READ_ONLY'] == 'yes'
        if 'SMB_LINKS_DIR' in config_dict:
            yaml_config['smb']['links_dir'] = config_dict['SMB_LINKS_DIR']
        if 'SMB_PORT' in config_dict:
            yaml_config['smb']['port'] = int(config_dict['SMB_PORT'])
        if 'TIMEZONE' in config_dict:
            yaml_config['timezone'] = config_dict['TIMEZONE']
        # 로그 레벨 업데이트
        if 'LOG_LEVEL' in config_dict:
            yaml_config['log_level'] = config_dict['LOG_LEVEL']
        
        # 민감한 정보(자격 증명) 업데이트
        if 'PROXMOX_HOST' in config_dict:
            yaml_config['credentials']['proxmox_host'] = config_dict['PROXMOX_HOST']
        if 'TOKEN_ID' in config_dict:
            yaml_config['credentials']['token_id'] = config_dict['TOKEN_ID']
        if 'SECRET' in config_dict:
            yaml_config['credentials']['secret'] = config_dict['SECRET']
        if 'SHUTDOWN_WEBHOOK_URL' in config_dict:
            yaml_config['credentials']['shutdown_webhook_url'] = config_dict['SHUTDOWN_WEBHOOK_URL']
        if 'SMB_USERNAME' in config_dict:
            yaml_config['credentials']['smb_username'] = config_dict['SMB_USERNAME']
        if 'SMB_PASSWORD' in config_dict:
            yaml_config['credentials']['smb_password'] = config_dict['SMB_PASSWORD']
        
        # NFS 설정 저장
        if 'NFS_PATH' in config_dict:
            yaml_config['nfs']['path'] = config_dict['NFS_PATH']

        # 설정 저장
        os.makedirs(os.path.dirname(yaml_path), exist_ok=True)
        with open(yaml_path, 'w', encoding='utf-8') as f:
            yaml.dump(yaml_config, f, allow_unicode=True, default_flow_style=False)

    @staticmethod
    def load_template_config() -> Dict[str, Any]:
        """템플릿 설정 파일 로드"""
        template_path = '/config/config.yaml.template'
        
        try:
            if os.path.exists(template_path):
                with open(template_path, 'r', encoding='utf-8') as f:
                    yaml_config = yaml.safe_load(f)
                
                print(f"템플릿 설정 파일 로드 완료: {template_path}")
                
                # 기본 구조 확인 및 설정
                if yaml_config is None:
                    yaml_config = {}
                
                # credentials 섹션이 없으면 빈 딕셔너리 추가
                if 'credentials' not in yaml_config:
                    yaml_config['credentials'] = {}
                
                # 필요한 항목이 없으면 빈 값 추가
                for section in ['proxmox', 'mount', 'smb', 'nfs']:
                    if section not in yaml_config:
                        yaml_config[section] = {}
                
                if 'cpu' not in yaml_config.get('proxmox', {}):
                    yaml_config['proxmox']['cpu'] = {}
                
                return yaml_config
        except Exception as e:
            print(f"템플릿 설정 파일 로드 실패: {e}")
        
        # 템플릿 파일이 없으면 기본 설정 반환
        return {
            'proxmox': {'node_name': '', 'vm_id': '', 'cpu': {'threshold': 10.0, 'check_interval': 60, 'threshold_count': 3}},
            'mount': {'path': '/mnt/gshare', 'folder_size_timeout': 30},
            'smb': {'share_name': 'gshare', 'comment': 'GShare SMB 공유', 'guest_ok': False, 'read_only': True, 'links_dir': '/mnt/gshare_links', 'port': 445},
            'nfs': {'path': ''},
            'credentials': {'proxmox_host': '', 'token_id': '', 'secret': '', 'shutdown_webhook_url': '', 'smb_username': '', 'smb_password': ''},
            'timezone': 'Asia/Seoul'
        }

    def __post_init__(self):
        # 초기화 시 설정 유효성 검사
        if not all([
            self.PROXMOX_HOST,
            self.TOKEN_ID,
            self.SECRET,
            self.SHUTDOWN_WEBHOOK_URL,
            self.SMB_USERNAME,
            self.SMB_PASSWORD
        ]):
            raise ValueError("필수 설정값이 누락되었습니다.")