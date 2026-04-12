from django.db import models

class User(models.Model) : 
    username = models.CharField(max_length=150)
    email = models.EmailField()
    created_at = models.DateTimeField( auto_now_add=True )

    def __str__(self):
        return self.username

class Channel(models.Model) :
    name = models.CharField(max_length=200)
    description = models.TextField( blank=True , null=True )
    owner = models.ForeignKey(User , on_delete=models.CASCADE , related_name='channel1')
    subscribers = models.ManyToManyField(User , related_name='channel' , blank=True)
    created_at = models.DateTimeField( auto_now_add=True )

    def __str__(self):
        return self.name

class Video(models.Model) : 
    title = models.CharField(max_length=250)
    description = models.TextField( blank=True , null=True )
    views = models.IntegerField(default=0)
    channel = models.ForeignKey(Channel , on_delete=models.CASCADE , related_name='video')
    created_at = models.DateTimeField( auto_now_add=True )

    def __str__(self):
        return self.title

class Comment(models.Model) : 
    text = models.TextField()
    user = models.ForeignKey(User , on_delete=models.CASCADE , related_name='comment')
    video = models.ForeignKey(Video , on_delete=models.CASCADE , related_name='comment')
    created_at = models.DateTimeField( auto_now_add=True )

    def __str__(self):
        return self.text

class Like(models.Model) : 
    user = models.ForeignKey(User , on_delete=models.CASCADE , related_name='like')
    video = models.ForeignKey(Video , on_delete=models.CASCADE , related_name='like') 
    created_at = models.DateTimeField( auto_now_add=True )

    def __str__(self):
        return str(self.id)

    class Meta :
        unique_together = ('user' , 'video')

