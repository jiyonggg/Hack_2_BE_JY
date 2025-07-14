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
    age = models.CharField(max_length=100) # 이용 연령
    plot = models.TextField() # 줄거리

class Comment(models.Model):
    '''
    영화 코멘트
    '''
    movie_id = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='comments')
    comment = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)