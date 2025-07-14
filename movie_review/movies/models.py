from django.db import models
from accounts.models import CustomUser

# Create your models here.
class Movie(models.Model):
    '''
    영화 정보
    '''
    title_kor = models.CharField(max_length=100) # 한국어 제목
    title_ori = models.CharField(max_length=100) # 원어 제목
    poster_url = models.URLField() # 포스터 이미지 URL
    release_date = models.DateField() # 개봉일
    rate = models.FloatField() # 평점
    genre = models.CharField(max_length=100) # 장르
    showtime = models.PositiveIntegerField() # 상영 시간
    plot = models.TextField() # 줄거리

class Cast(models.Model):
    '''
    영화에 대한 1인의 출연 정보 (감독 포함)
    '''
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='casts') # 영화 id
    name = models.CharField(max_length=100) # 출연자 이름
    profile_url = models.URLField() # 출연자 프로필 사진
    role = models.CharField(max_length=100) # 감독도 역할에 포함

    def __str__(self):
        return f'''영화 ID: {self.movie_id}
                   이름: {self.name}
                   프로필 사진 URL: {self.profile_url}
                   역할: {self.role}'''

class Comment(models.Model):
    '''
    영화 코멘트
    '''
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='comments') # 영화 id
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments') # 유저 id
    comment = models.CharField(max_length=100) # 출연자 이름
    created_at = models.DateTimeField(auto_now_add=True) # 코멘트 생성 시간