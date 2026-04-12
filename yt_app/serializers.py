from rest_framework import serializers
from rest_framework.response import Response
from .models import *
from django.db.models import Avg , Count , Sum

class UserSerializer(serializers.ModelSerializer) :
    class Meta :
        model = User
        fields = '__all__'

class ChannelSerializer(serializers.ModelSerializer) :
    videos_count = serializers.SerializerMethodField()
    subcribers_count = serializers.SerializerMethodField()

    owner = UserSerializer(read_only = True)
    owner_id = serializers.PrimaryKeyRelatedField (
        queryset = User.objects.all() , 
        source = 'owner' , 
        write_only = True
    )

    def get_videos_count(self , obj) : 
        videos = Video.objects.filter(channel = obj).count()
        return videos
    
    def get_subcribers_count(self , obj) : 
        subcribers = obj.subscribers.count()
        return subcribers

    class Meta :
        model = Channel
        fields = '__all__'

class ChannelCreateSerializer(serializers.ModelSerializer) : 
    class Meta :
        model = Channel
        fields = ['name' , 'description' , 'owner']

class ChannelUpdateSerializer(serializers.ModelSerializer) :
    updated = serializers.SerializerMethodField()

    def get_updated(self , obj) : 
        return True

    class Meta :
        model = Channel
        fields = ['name' , 'description' , 'owner' , 'updated']

class ChannelDetailSerializer(serializers.ModelSerializer) :
    owner = UserSerializer(read_only = True)
    owner_id = serializers.PrimaryKeyRelatedField (
        queryset = User.objects.all() , 
        source = 'owner' , 
        write_only = True
    )

    last_videos = serializers.SerializerMethodField()

    total_views = serializers.SerializerMethodField()

    def get_total_views(self, obj):
        return Video.objects.filter(channel=obj).aggregate(
            total=Sum('views')
        )['total'] or 0

    def get_last_videos(self, obj) :
        video = Video.objects.filter( channel = obj ).order_by('-created_at')[:5]
        return VideoSerializer(video , many= True).data

    class Meta :
        model = Channel
        fields = '__all__'


class UserDetailSerializer(serializers.ModelSerializer) :
    channel = ChannelSerializer(read_only = True)
    channel_id = serializers.PrimaryKeyRelatedField (
        queryset = Channel.objects.all() , 
        source = 'channel' , 
        write_only = True
    )

    videos_count = serializers.SerializerMethodField()

    def get_videos_count(self , obj) : 
        videos = Video.objects.filter(channel__owner = obj).count()
        return videos

    class Meta :
        model = User
        fields = '__all__'

class VideoSerializer(serializers.ModelSerializer) :
    channel = ChannelSerializer(read_only = True)
    channel_id = serializers.PrimaryKeyRelatedField (
        queryset = Channel.objects.all() , 
        source = 'channel' , 
        write_only = True
    )

    class Meta :
        model = Video
        fields = '__all__'


class VideoSearchSerializer(VideoSerializer):
    relevance = serializers.IntegerField(read_only=True)

    class Meta:
        model = Video
        fields = ['id', 'title', 'description', 'views', 'channel', 'channel_id', 'created_at', 'relevance']

class VideoCreateSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Video
        fields = ['title' , 'description' , 'channel']
    

class VideoDetailSerializer(serializers.ModelSerializer) : 
    total_comments = serializers.SerializerMethodField()
    total_likes = serializers.SerializerMethodField()
    total_views = serializers.SerializerMethodField()

    def get_total_comments(self, obj):
        return Comment.objects.filter(video=obj).count()
    
    def get_total_likes(self, obj):
        return Like.objects.filter(video=obj).count()
    
    def get_total_views(self , obj) : 
        return obj.views
    
    class Meta :
        model = Video
        fields = ['title' , 'description' , 'channel' , 'total_comments' , 'total_likes' , 'total_views']

class UserChannelSerializer(serializers.ModelSerializer) :
    videos_count = serializers.SerializerMethodField()

    def get_videos_count(self , obj) : 
        videos = Video.objects.filter( channel = obj ).count()
        return videos

    class Meta :
        model = Channel
        fields = '__all__'

class CommentSerializer(serializers.ModelSerializer) :
    user = UserSerializer(read_only = True)
    user_id = serializers.PrimaryKeyRelatedField (
        queryset = User.objects.all() , 
        source = 'user' , 
        write_only = True
    )

    class Meta :
        model = Comment
        fields = '__all__'

class CommentCreateSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Comment
        fields = ['text' , 'user' ]

class CommentDetailSerializer(serializers.ModelSerializer) :
    user = UserSerializer(read_only = True)
    user_id = serializers.PrimaryKeyRelatedField (
        queryset = User.objects.all() , 
        source = 'user' , 
        write_only = True
    )

    video = VideoSerializer(read_only = True)
    video_id = serializers.PrimaryKeyRelatedField (
        queryset = Video.objects.all() , 
        source = 'video' , 
        write_only = True
    )

    class Meta :
        model = Comment
        fields = '__all__'

class LikeSerializer(serializers.ModelSerializer) :
    total_likes = serializers.SerializerMethodField()

    def get_total_likes(self , obj) :
        return Video.objects.filter(video = obj.video).count()
    
    class Meta :
        model = Like
        fields = '__all__'

class LikeCreateSerializer(serializers.ModelSerializer) :
    class Meta :
        model = Like
        fields = ['user']

class LikeVideoSerializer(serializers.ModelSerializer) :
    total_likes = serializers.SerializerMethodField()
    users = serializers.SerializerMethodField()
    is_liked_by_current_user = serializers.SerializerMethodField()

    def get_total_likes(self, obj):
        return Like.objects.filter(video=obj.video).count()

    def get_users(self, obj):
        likes = Like.objects.filter(video=obj.video)
        users = [like.user for like in likes]
        return UserSerializer(users, many=True).data

    def get_is_liked_by_current_user(self, obj):
        user_id = self.context['request'].query_params.get('user') 
        return Like.objects.filter(video=obj.video, user_id=user_id).exists()
    
    class Meta :
        model = Like
        fields = '__all__'

class ChannelStatsSerializer(serializers.ModelSerializer) : 
    videos_count = serializers.SerializerMethodField()
    total_views = serializers.SerializerMethodField()
    avg_views_per_video = serializers.SerializerMethodField()
    top_video = serializers.SerializerMethodField()

    def get_total_views(self, obj):
        return Video.objects.filter(channel=obj).aggregate(
            total=Sum('views')
        )['total'] or 0
    
    def get_avg_views_per_video(self, obj):
        views = Video.objects.filter(channel=obj).aggregate(
            total=Sum('views')
        )['total'] or 0
        videos = Video.objects.filter(channel = obj).count()
        if videos == 0 :
            return 0
        return round(views / videos)

    def get_videos_count(self , obj) : 
        videos = Video.objects.filter(channel = obj).count()
        return videos
    
    def get_top_video(self , obj) :
        video = Video.objects.filter(channel = obj).order_by('-views').first()
        if video :
            return VideoSerializer(video).data
        return None
    
    class Meta :
        model = Channel
        fields = '__all__'


class VideoStatsSerializer(serializers.Serializer):
    total_videos = serializers.IntegerField()
    total_views = serializers.IntegerField()
    avg_views = serializers.FloatField()


class UserStatsSerializer(serializers.Serializer):
    total_users = serializers.IntegerField()
    users_with_channels = serializers.IntegerField()
    active_users = serializers.IntegerField()


class ChannelStatsGlobalSerializer(serializers.Serializer):
    total_channels = serializers.IntegerField()
    top_channel_by_views = ChannelSerializer(read_only=True, allow_null=True)
    average_videos_per_channel = serializers.FloatField()
