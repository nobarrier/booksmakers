from django.core.management.base import BaseCommand
from apps.catalog.models import Category
from django.utils.text import slugify

CATEGORY_STRUCTURE = {
    "아두이노": {
        "개발 보드": ["정품 보드", "호환 보드", "입문용 키트"],
        "쉴드/모듈": ["통신 쉴드", "모터 드라이버 쉴드", "디스플레이 쉴드"],
        "구성 부품": [
            "전자부품",
            "전기부품",
            "센서",
            "RLC",
            "DISPLAY",
            "POWER",
            "커넥터",
            "와이어",
        ],
    },
    "라즈베리 파이": {
        "컴퓨팅 보드": ["Pi 5", "Pi 4", "Pi 3", "Pi Zero", "Pi Pico"],
        "전용 액세서리": ["케이스", "방열판/팬", "전원 어댑터", "SD 카드"],
        "확장 모듈": [
            "카메라 모듈",
            "터치 디스플레이",
            "오디오 모듈",
            "커넥터",
            "와이어",
        ],
    },
    "MCU / 개발 보드": {
        "브랜드별 보드": [
            "Digilent",
            "AVR",
            "ARM",
            "STM",
            "PIC",
            "8051",
            "RENESAS",
            "WIZNET",
        ],
        "AI / 고성능 보드": ["NVIDIA Jetson", "기타 MCU"],
        "평가/디버깅": [
            "MCU/DSP 평가기판",
            "FPGA 평가기판",
            "완성기판/프로그래머",
            "데모기판/키트",
            "부속품",
        ],
    },
    "통신 / 네트워크": {
        "무선 통신": ["블루투스/BLE", "Wi-Fi", "Zigbee", "LoRa", "RF 모듈"],
        "유선 통신": ["USB", "RS-232", "RS-485/422", "CAN 통신", "이더넷"],
        "기타 통신": ["GPS/GNSS", "NFC/RFID", "무선 충전", "적외선 통신", "안테나"],
    },
    "전원 / 배터리": {
        "변환 장치": ["AC/DC 컨버터", "DC/DC 컨버터", "레귤레이터", "인버터"],
        "배터리": ["리튬 폴리머", "리튬 이온", "니켈수소", "건전지", "리튬 충전기"],
        "전원 부품": ["트랜스포머", "스위칭 파워 서플라이", "태양광 모듈"],
    },
    "전자/전기 부품": {
        "수동 소자": ["저항", "콘덴서", "인덕터", "크리스탈/오실레이터"],
        "능동 소자": ["다이오드", "트랜지스터", "FET", "IC (집적 회로)"],
        "연결/보호": ["퓨즈", "서지 보호기", "릴레이", "스위치"],
    },
    "로봇 / 기계 / 모터": {
        "모터/구동": ["DC 모터", "서보 모터", "스텝 모터", "기어드 모터"],
        "기구부": ["RC 자동차 프레임", "드론 프레임", "로봇 팔 키트"],
        "기계 부속": ["기어", "풀리/벨트", "베어링", "볼트/너트"],
    },
    "계측기 / 공구": {
        "측정 도구": ["멀티미터", "오실로스코프", "파워 서플라이", "로직 분석기"],
        "작업 공구": ["인두기", "납/플럭스", "핀셋/니퍼", "드라이버 세트"],
    },
    "교육 / 도서": {
        "학습 키트": ["코딩 교육", "과학 상자", "DIY 프로젝트"],
        "기술 서적": ["아두이노/파이 가이드", "임베디드 이론", "데이터시트"],
    },
}


class Command(BaseCommand):
    help = "Seed category tree"

    def handle(self, *args, **kwargs):
        for level1, level2_dict in CATEGORY_STRUCTURE.items():

            parent1, _ = Category.objects.get_or_create(
                name=level1,
                defaults={"slug": slugify(level1, allow_unicode=True)},
            )

            for level2, level3_list in level2_dict.items():

                parent2, _ = Category.objects.get_or_create(
                    name=level2,
                    parent=parent1,
                    defaults={
                        "slug": f"{parent1.slug}-{slugify(level2, allow_unicode=True)}"
                    },
                )

                for level3 in level3_list:
                    Category.objects.get_or_create(
                        name=level3,
                        parent=parent2,
                        defaults={
                            "slug": f"{parent2.slug}-{slugify(level3, allow_unicode=True)}"
                        },
                    )

        self.stdout.write(self.style.SUCCESS("카테고리 생성 완료"))
