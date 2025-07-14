from rest_framework import serializers

from . import models

# Serializers

class CastListResponseSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Cast
        fields = ['name', 'profile_url', 'role']

class MovieDetailResponseSerializer(serializers.ModelSerializer):
    '''
    영화 하나의 상세 정보
    '''
    casts = CastListResponseSerializer(many=True)
    
    class Meta:
        model = models.Movie
        fields = '__all__'

class MovieListResponseSerializer(serializers.ModelSerializer):
    '''
    메인 화면에서 보이는 여러 영화의 정보
    '''
    detail_url = serializers.SerializerMethodField()
    
    def get_detail_url(self, obj):
        return f'http://localhost:8000/movies/{obj.id}/'

    class Meta:
        model = models.Movie
        fields = ['id', 'title_kor', 'poster_url', 'detail_url']


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
    nickname = serializers.SerializerMethodField()
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M")

    class Meta:
        model = models.Comment
        fields = ['id', 'nickname', 'comment', 'created_at']

    def get_nickname(self, obj):
        return obj.user_id.nickname