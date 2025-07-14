from django.shortcuts import render
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
import requests

from . import serializers
from . import models

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from rest_framework.decorators import api_view, authentication_classes, permission_classes

# Create your views here.
def init_db(request):
    '''
    데이터베이스에 외부 영화 정보 저장
    '''
    url = 'http://43.200.28.219:1313/movies/'
    res = requests.get(url)
    movies = res.json()['movies']
    for movie in movies:
        # movie: 영화 하나
        # json 내 key와 영화 모델의 key 매핑 딕셔너리
        matches = {
            'title_kor': 'title_kor',
            'title_eng': 'title_ori',
            'poster_url': 'poster_url',
            'release_date': 'release_date',
            'rating': 'rate',
            'genre': 'genre',
            'showtime': 'showtime',
            'plot': 'plot',
            'actors': 'actors',

            # 감독을 미리 cast로 넣기 위한 처리
            'director_name': 'name',
            'director_image_url': 'image_url',
        }
        
        # 추가할 데이터 정보 담는 딕셔너리
        data = dict()

        for key in movie.keys():
            if key == 'rating': # float 타입 rating 처리
                data[matches[key]] = float(movie.get(key, ''))
            elif key == 'showtime': # int 타입 showtime 처리
                data[matches[key]] = int(movie.get(key, ''))
            else: # 나머지 데이터 처리
                data[matches[key]] = movie.get(key, '')
        
        director_info = {'character': '감독'}
        
        for key in ('name', 'image_url'):
            director_info[key] = data.pop(key)
        
        casts = [director_info] + data.pop('actors')

        instance = models.Movie.objects.create(**data)

        for cast in casts:
            cast_info = dict()
            cast_info['name'] = cast.get('name', '')
            cast_info['profile_url'] = cast.get('image_url', '')
            cast_info['role'] = cast.get('character', '')
            cast_info['movie_id'] = instance
            models.Cast.objects.create(**cast_info)

class MovieList(generics.ListAPIView):
    '''
    모든 영화 목록을 조회
    '''
    queryset = models.Movie.objects.all()
    serializer_class = serializers.MovieListResponseSerializer

class MovieDetail(generics.RetrieveAPIView):
    '''
    한 영화의 상세 정보를 조회
    '''
    queryset = models.Movie.objects.all()
    serializer_class = serializers.MovieDetailResponseSerializer
    lookup_url_kwarg = 'movie_id'

class MovieSearch(APIView):
    '''
    한국어 제목을 바탕으로 영화 검색. 영화 제목 내 검색어 포함을 기준으로 검색됨
    '''
    def get(self, request):
        keyword = request.query_params.get('title', '')
        movie = models.Movie.objects.filter(title_kor__icontains=keyword)
        serializer = serializers.MovieListResponseSerializer(movie, many=True)
        return Response(serializer.data)


class CommentList(APIView):
    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticatedOrReadOnly])
    def get(self, request, movie_id):
        try:
            movie = models.Movie.objects.get(id=movie_id)
            comment = models.Comment.objects.filter(movie_id=movie)
            serializer = serializers.CommentResponseSerializer(comment, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except models.Movie.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @authentication_classes([JWTAuthentication])
    @permission_classes([IsAuthenticatedOrReadOnly])
    def post(self, request, movie_id):
        try:
            movie = models.Movie.objects.get(id=movie_id)
            serializer = serializers.CommentRequestSerializer(data=request.data)
            if serializer.is_valid(): # 유효성 검사
                serializer.save(movie_id=movie, user_id=request.user)
                return Response(serializer.data, status = status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except models.Movie.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)