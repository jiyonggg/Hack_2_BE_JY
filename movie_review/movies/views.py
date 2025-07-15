from django.shortcuts import render
from django.db.models.query import QuerySet
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
def init_db():
    '''
    데이터베이스에 외부 영화 정보 저장
    '''
    if models.Movie.objects.exists():
        print('DB is already initialized!')
        return
    
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
        print(f'a movie instance created: {instance.title_kor}')

        for cast in casts:
            cast_info = dict()
            cast_info['name'] = cast.get('name', '')
            cast_info['profile_url'] = cast.get('image_url', '')
            cast_info['role'] = cast.get('character', '')
            cast_info['movie_id'] = instance
            cast = models.Cast.objects.create(**cast_info)
            print(f'a cast instance for {cast.movie_id} created: {cast.name}, {cast.role}')
        
    print('DB is successfully initialized.')

class MovieList(generics.ListAPIView):
    '''
    모든 영화 목록을 조회
    '''
    queryset = models.Movie.objects.all()
    serializer_class = serializers.MovieListResponseSerializer

class MovieListofTopTen(generics.ListAPIView):
    '''
    메인 페이지용 api로, 영화를 인기순으로 10개를 보여줌
    '''
    queryset = models.Movie.objects.order_by('-rate')[:10]
    serializer_class = serializers.MovieListResponseSerializer
    pagination_class = None

class MovieDetail(generics.RetrieveAPIView):
    '''
    한 영화의 상세 정보를 조회
    '''
    queryset = models.Movie.objects.all()
    serializer_class = serializers.MovieDetailResponseSerializer
    lookup_url_kwarg = 'movie_id'

class MovieSearch(generics.ListAPIView):
    '''
    한국어 제목을 바탕으로 영화 검색. 영화 제목 내 검색어 포함을 기준으로 검색됨
    '''
    queryset = models.Movie.objects.all()
    serializer_class = serializers.MovieListResponseSerializer
    
    def get(self, request, *args, **kwargs):
        return self.list(request, *args, **kwargs)
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        keyword = request.query_params.get('title', '')
        queryset = queryset.filter(title_kor__icontains=keyword)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# class CommentList(APIView):
#     authentication_classes = [JWTAuthentication]
#     permission_classes = [IsAuthenticatedOrReadOnly]
    
#     def get(self, request, movie_id):
#         try:
#             movie = models.Movie.objects.get(id=movie_id)
#             comment = models.Comment.objects.filter(movie_id=movie)
#             serializer = serializers.CommentResponseSerializer(comment, many=True)
#             return Response(serializer.data, status=status.HTTP_200_OK)
#         except models.Movie.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)

#     def post(self, request, movie_id):
#         try:
#             movie = models.Movie.objects.get(id=movie_id)
#         except models.Movie.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)
        
#         serializer = serializers.CommentRequestSerializer(data=request.data)
#         print(request.user)
#         if serializer.is_valid(): # 유효성 검사
#             serializer.save(movie_id=movie, user_id=request.user)
#             return Response(serializer.data, status = status.HTTP_201_CREATED)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 위의 코드를 최대한 보존하고 페이지네이션 기능만 추가
class CommentList(generics.GenericAPIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get(self, request, movie_id):
        try:
            movie = models.Movie.objects.get(id=movie_id)
            comment = models.Comment.objects.filter(movie_id=movie)

            page = self.paginate_queryset(comment)

            if page is not None:
                serializer = serializers.CommentResponseSerializer(page, many=True)
                return self.get_paginated_response(serializer.data)
            
            serializer = serializers.CommentResponseSerializer(comment, many=True)
            return Response(serializer.data)
        except models.Movie.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
    def post(self, request, movie_id):
        try:
            movie = models.Movie.objects.get(id=movie_id)
        except models.Movie.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = serializers.CommentRequestSerializer(data=request.data)
        print(request.user)
        if serializer.is_valid(): # 유효성 검사
            serializer.save(movie_id=movie, user_id=request.user)
            return Response(serializer.data, status = status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)