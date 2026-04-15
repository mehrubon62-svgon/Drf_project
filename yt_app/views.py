from django.shortcuts import render
from rest_framework.decorators import api_view
from .models import * 
from .serializers import *
from rest_framework.response import Response
from django.db.models import Avg , Count , Sum, Q
from django.db.models import Case, IntegerField, Value, When
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
from rest_framework.filters import OrderingFilter , SearchFilter
from django_filters.rest_framework import DjangoFilterBackend
from .pagination import *
from .pagination import CustomPagination
from .filters import *
from rest_framework.generics import ListAPIView , CreateAPIView , DestroyAPIView , RetrieveAPIView , UpdateAPIView 
from rest_framework.views import APIView
from rest_framework import generics, permissions, status
from django.contrib.auth import get_user_model

User = get_user_model()

class UserListApiView(ListAPIView) :
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return User.objects.annotate(
            channels_count = Count('channel')
        )


class UserCreateAPIView(CreateAPIView) : 
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserRetrieveAPIView(RetrieveAPIView) :
    queryset = User.objects.all()
    serializer_class = UserDetailSerializer

class UserChannelsListApiView(ListAPIView) : 
    serializer_class = UserChannelSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        user_id = self.kwargs['pk']
        return Channel.objects.filter(owner_id = user_id)
    
class ChannelListApiView(ListAPIView) :
    serializer_class = ChannelSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        return Channel.objects.annotate(
            subscribers_count = Count('subscribers')
        )
    
class ChannelCreateApiView(CreateAPIView) : 
    permission_classes = [permissions.IsAuthenticated]
    queryset = Channel.objects.all()
    serializer_class = ChannelCreateSerializer

    def create(self , request , *args , **kwargs) : 
        payload = request.data.copy()
        payload["owner"] = request.user.id
        serializer = ChannelCreateSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        channel = serializer.save()
        return Response(ChannelSerializer(channel).data)
    
class ChannelDetailApiView(RetrieveAPIView) :
    queryset = Channel.objects.all()
    serializer_class = ChannelDetailSerializer

class ChannelUpdateApiView(UpdateAPIView) :
    permission_classes = [permissions.IsAuthenticated]
    queryset = Channel.objects.all()
    serializer_class = ChannelUpdateSerializer

    def get_queryset(self):
        return Channel.objects.filter(owner=self.request.user)

    def update(self , request , *args , **kwargs) : 
        channel = self.get_object()
        serializer = self.get_serializer(channel, data=request.data, partial=kwargs.get("partial", False))
        serializer.is_valid(raise_exception=True)
        channel = serializer.save()
        return Response(ChannelSerializer(channel).data)
    
class ChannelDeleteApiView(DestroyAPIView) : 
    permission_classes = [permissions.IsAuthenticated]
    queryset = Channel.objects.all()

    def get_queryset(self):
        return Channel.objects.filter(owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        channel = self.get_object()  
        channel_id = channel.id     
        channel.delete()            
        return Response({
            'status': 'deleted',
            'deleted_channel_id': channel_id 
        })

class ChannelVideoApiView(ListAPIView) : 
    serializer_class = VideoSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend ,OrderingFilter]
    filterset_class = VideoFilter
    ordering_fields = ['created_at', 'views']

    def get_queryset(self):
        return Video.objects.filter(channel=self.kwargs['pk'])
    
class ChannelStatsApiView(RetrieveAPIView) :
    permission_classes = [permissions.IsAuthenticated]
    queryset = Channel.objects.all()
    serializer_class = ChannelStatsSerializer


class VideoListApiView(ListAPIView) : 
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    pagination_class = CustomPagination
    filter_backends = [SearchFilter, DjangoFilterBackend, OrderingFilter]
    search_fields = ['title', 'description']
    filterset_fields = ['channel']
    ordering_fields = ['views', 'created_at']

    def get_queryset(self):
        queryset = Video.objects.all()
        channel_id = self.request.query_params.get('channel')
        if channel_id:
            queryset = queryset.order_by('-views')
        return queryset


class VideoSearchApiView(ListAPIView):
    serializer_class = VideoSearchSerializer
    pagination_class = CustomPagination

    def get_queryset(self):
        query = self.request.query_params.get('query', '').strip()
        if not query:
            return Video.objects.none()

        return (
            Video.objects.filter(title__icontains=query) |
            Video.objects.filter(description__icontains=query)
        ).distinct().annotate(
            relevance=(
                Case(
                    When(title__icontains=query, then=Value(3)),
                    default=Value(0),
                    output_field=IntegerField()
                ) +
                Case(
                    When(description__icontains=query, then=Value(2)),
                    default=Value(0),
                    output_field=IntegerField()
                )
            )
        ).order_by('-relevance', '-views', '-created_at')

class VideoTopApiView(ListAPIView):
    serializer_class = VideoSerializer

    def get_queryset(self):
        queryset = Video.objects.all()
        period = self.request.query_params.get('period')
        now = timezone.now()

        if period == 'day':
            queryset = queryset.filter(created_at__gte=now - timedelta(days=1))
        elif period == 'week':
            queryset = queryset.filter(created_at__gte=now - timedelta(days=7))
        elif period == 'month':
            queryset = queryset.filter(created_at__gte=now - timedelta(days=30))

        return queryset.order_by('-views')[:10]


class VideoRelatedApiView(ListAPIView):
    serializer_class = VideoSearchSerializer

    def get_queryset(self):
        video = Video.objects.filter(id=self.kwargs['pk']).first()
        if not video:
            return Video.objects.none()

        title_words = [word for word in video.title.split() if len(word) > 2][:5]
        score = Case(
            When(channel=video.channel, then=Value(3)),
            default=Value(0),
            output_field=IntegerField()
        )

        for word in title_words:
            score = score + Case(
                When(title__icontains=word, then=Value(1)),
                default=Value(0),
                output_field=IntegerField()
            )

        return Video.objects.exclude(id=video.id).annotate(
            relevance=score
        ).filter(relevance__gt=0).order_by('-relevance', '-views', '-created_at')[:10]


class StatsVideosApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        stats = Video.objects.aggregate(
            total_videos=Count('id'),
            total_views=Coalesce(Sum('views'), 0),
            avg_views=Coalesce(Avg('views'), 0)
        )
        return Response(VideoStatsSerializer(stats).data)


class StatsUsersApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        total_users = User.objects.count()
        users_with_channels = User.objects.filter(channel1__isnull=False).distinct().count()
        active_users = User.objects.filter(
            Q(comment__isnull=False) | Q(like__isnull=False) | Q(channel1__isnull=False)
        ).distinct().count()

        data = {
            'total_users': total_users,
            'users_with_channels': users_with_channels,
            'active_users': active_users
        }
        return Response(UserStatsSerializer(data).data)


class StatsChannelsApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        channels = Channel.objects.annotate(
            channel_views=Coalesce(Sum('video__views'), 0),
            videos_count=Count('video')
        )
        total_channels = channels.count()
        top_channel = channels.order_by('-channel_views').first()
        avg_videos_per_channel = channels.aggregate(
            avg=Coalesce(Avg('videos_count'), 0)
        )['avg']

        data = {
            'total_channels': total_channels,
            'top_channel_by_views': ChannelSerializer(top_channel).data if top_channel else None,
            'average_videos_per_channel': avg_videos_per_channel
        }
        return Response(ChannelStatsGlobalSerializer(data).data)

class VideoCreateApiView(CreateAPIView) :
    permission_classes = [permissions.IsAuthenticated]
    queryset = Channel.objects.all()
    serializer_class = VideoCreateSerializer

    def create(self , request , *args , **kwargs) : 
        serializer = VideoCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if serializer.validated_data["channel"].owner_id != request.user.id:
            return Response(
                {"detail": "You can create videos only in your channel"},
                status=status.HTTP_403_FORBIDDEN
            )
        video = serializer.save()
        return Response(VideoSerializer(video).data)
    
class VideoDetailApiView(RetrieveAPIView) :
    queryset = Video.objects.all()
    serializer_class = VideoDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        video = self.get_object()
        video.views += 1
        video.save()
        serializer = self.get_serializer(video)
        return Response(serializer.data)
    
class VideoUpdateApiView(UpdateAPIView) : 
    permission_classes = [permissions.IsAuthenticated]
    queryset = Video.objects.all()
    serializer_class = VideoCreateSerializer

    def get_queryset(self):
        return Video.objects.filter(channel__owner=self.request.user)
    
    def update(self, request, *args, **kwargs):
        video = self.get_object()
        
        old_data = {
            'title': video.title,
            'description': video.description
        }
        
        serializer = self.get_serializer(video, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        diff = {}
        for field in old_data:
            if old_data[field] != serializer.data[field]:
                diff[field] = {
                    'old': old_data[field],
                    'new': serializer.data[field]
                }
        
        return Response({
            'updated_object': serializer.data,
            'diff': diff
        })
    

class VideoDeleteApiView(DestroyAPIView) : 
    permission_classes = [permissions.IsAuthenticated]
    queryset = Video.objects.all()

    def get_queryset(self):
        return Video.objects.filter(channel__owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        video = self.get_object()  
        video_comments = video.comment.count()
        video_likes = video.like.count()
        video_views = video.views
        
        video.delete()            
        return Response({
            'status': 'deleted',
            'comments_was' : video_comments , 
            'likes_was' : video_likes , 
            'video_views' : video_views
        })
    

class CommentsListAPiView(ListAPIView) : 
    serializer_class = CommentSerializer
    pagination_class = CustomPagination
    filter_backends = [OrderingFilter]
    ordering_fields = ['created_at']


    def get_queryset(self):
        user_id = self.kwargs['pk']
        return Comment.objects.filter(user_id = user_id)
    

class CommentCreateApiView(CreateAPIView) :
    permission_classes = [permissions.IsAuthenticated] 
    queryset = Comment.objects.all()
    serializer_class = CommentCreateSerializer

    def create(self , request , *args , **kwargs) : 
        payload = request.data.copy()
        payload["user"] = request.user.id
        serializer = CommentCreateSerializer(data=payload)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(video_id=self.kwargs['pk'])
        return Response(CommentSerializer(comment).data)
    
class CommentDetailApiView(RetrieveAPIView) :
    queryset = Comment.objects.all()
    serializer_class = CommentDetailSerializer


class CommentDeleteApiView(DestroyAPIView) : 
    permission_classes = [permissions.IsAuthenticated]
    queryset = Comment.objects.all()

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        comment = self.get_object()  
        comment_id = comment.id     
        comment.delete()            
        return Response({
            'status': 'deleted',
            'deleted_comment_id': comment_id 
        })
    
class LikeCreateApiView(CreateAPIView) : 
    permission_classes = [permissions.IsAuthenticated]
    queryset = Like.objects.all()
    serializer_class = LikeCreateSerializer
    
    def create(self, request, *args, **kwargs):
        video_id = self.kwargs['pk']

        like, created = Like.objects.get_or_create(user_id=request.user.id, video_id=video_id)

        if not created:
            like.delete()
            return Response({
                'liked': False,
                'total_likes': Like.objects.filter(video_id=video_id).count()
            })

        return Response({
            'liked': True,
            'total_likes': Like.objects.filter(video_id=video_id).count()
        })
    
class LikesVideoListApiView(ListAPIView) :
    serializer_class = LikeVideoSerializer

    def get_queryset(self):
        return Like.objects.filter(video_id=self.kwargs['pk'])
