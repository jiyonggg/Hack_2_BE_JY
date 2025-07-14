from rest_framework import serializers

from . import models

# Serializers

class MovieDetailResponseSerializer(serializers.HyperlinkedModelSerializer):
    '''
    영화 하나의 상세 정보
    '''
    
    class Meta:
        model = models.Movie
        fields = '__all__'

class MovieListResponseSerializer(serializers.ModelSerializer):
    '''
    메인 화면에서 보이는 여러 영화의 정보
    '''
    url = serializers.HyperlinkedIdentityField(view_name='movie-detail')
    
    class Meta:
        model = models.Movie
        fields = ['id', 'title_kor', 'poster_url', 'url']

class CommentRequestSerializer(serializers.ModelSerializer):
    '''
    코멘트 작성 요청용 시리얼라이저
    '''
    class Meta:
        model = models.Comment
        fields = ['comment']

class CommentResponseSerializer(serializers.ModelSerializer):
    '''
    1. 영화에 달린 코멘트 목록 열람용 시리얼라이저
    2. 코멘트 작성 시 반환되는 응답용 시리얼라이저
    '''
    comment_set = CommentRequestSerializer(many=True, read_only=True)

    class Meta:
        model = models.Movie
        fields = ['comment_set']