from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.dto.response.ClusterResponseSchemas import ClusterResponse, MarkerResponse
from app.services import cluster_sido, cluster_gungu, cluster_dongmyeon, cluster_marker

router = APIRouter()

@router.get("/sido",
            response_model= ClusterResponse,
            summary= "시/도 단위 클러스터링",
            description= """
                지도에서 남서쪽, 북동쪽 위도/경도를 기준으로 단위 클러스터 결과값을 제공
                response schema 참고 바람 \n
                카테고리 파라미터 추가 (필수 아님) (예: 감성/하이틴/캐릭터/복고/팝업/인기)
            """)
def get_sido_cluster(db: Session = Depends(get_db),
                     sw_lat: float = Query(35.0000, description="남서 위도"),
                     sw_lng: float = Query(127.0000, description="남서 경도"),
                     ne_lat: float = Query(37.5100, description="북동 위도"),
                     ne_lng: float = Query(127.5000, description="북동 경도"),
                     category: str = Query(None, description="필터할 카테고리 이름 (예: 복고)")):
    return cluster_sido.cluster(db, sw_lat, sw_lng, ne_lat, ne_lng, category)

@router.get("/gungu",
            response_model= ClusterResponse,
            summary= "군/구 단위 클러스터링",
            description= """
                지도에서 남서쪽, 북동쪽 위도/경도를 기준으로 단위 클러스터 결과값을 제공
                response schema 참고 바람 \n
                카테고리 파라미터 추가 (필수 아님) (예: 감성/하이틴/캐릭터/복고/팝업/인기)
            """)
def get_gungu_cluster(db: Session = Depends(get_db),
                      sw_lat: float = Query(35.861, description= "남서 위도"),
                      sw_lng: float = Query(128.591, description= "남서 경도"),
                      ne_lat: float = Query(35.876, description= "북동 위도"),
                      ne_lng: float = Query(128.609, description= "북동 경도"),
                      category: str = Query(None, description="필터할 카테고리 이름 (예: 복고)")):
    return cluster_gungu.cluster(db, sw_lat, sw_lng, ne_lat, ne_lng, category)

@router.get("/dongmyeon",
            response_model= ClusterResponse,
            summary="동/면 단위 클러스터링",
            description="""
                지도에서 남서쪽, 북동쪽 위도/경도를 기준으로 단위 클러스터 결과값을 제공
                response schema 참고 바람 \n
                카테고리 파라미터 추가 (필수 아님) (예: 감성/하이틴/캐릭터/복고/팝업/인기)
            """)
def get_dongmyeon_cluster(db: Session = Depends(get_db),
                          sw_lat: float = Query(35.861, description="남서 위도"),
                          sw_lng: float = Query(128.591, description="남서 경도"),
                          ne_lat: float = Query(35.876, description="북동 위도"),
                          ne_lng: float = Query(128.609, description="북동 경도"),
                          category: str = Query(None, description="필터할 카테고리 이름 (예: 복고)")):
    return cluster_dongmyeon.cluster(db, sw_lat, sw_lng, ne_lat, ne_lng, category)


@router.get(
    "/marker",
    response_model=MarkerResponse,
    summary="마커 단위 매장 데이터",
    description="""
        지도에서 남서쪽, 북동쪽 위도/경도를 기준으로 실제 매장 데이터를 마커 단위로 반환 \n
        기본 위경도는 '대구 중구' 기준 \n
        카테고리 파라미터 추가 (필수 아님) (예: 감성/하이틴/캐릭터/복고/팝업/인기)
    """)
def get_marker_data(db: Session = Depends(get_db),
                    sw_lat: float = Query(35.861, description="남서 위도"),
                    sw_lng: float = Query(128.591, description="남서 경도"),
                    ne_lat: float = Query(35.876, description="북동 위도"),
                    ne_lng: float = Query(128.609, description="북동 경도"),
                    category: str = Query(None, description="필터할 카테고리 이름 (예: 복고)")):
    return cluster_marker.get_filtered_markers(db, sw_lat, sw_lng, ne_lat, ne_lng, category)