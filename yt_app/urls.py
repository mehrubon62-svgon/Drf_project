from django.urls import path
from .views import *

urlpatterns = [
    path('users/' , UserListApiView.as_view()) , 
    path('users_create/' , UserCreateAPIView.as_view()) ,  
    path('users/<int:pk>/' , UserRetrieveAPIView.as_view()) ,  
    path('users/<int:pk>/channels/' , UserChannelsListApiView.as_view()) ,

    path('channels/' , ChannelListApiView.as_view()) , 
    path('channel_create/' , ChannelCreateApiView.as_view()) , 
    path('channel/<int:pk>/' , ChannelDetailApiView.as_view()) , 
    path('channel_update/<int:pk>/' , ChannelUpdateApiView.as_view()) , 
    path('channel_delete/<int:pk>/' , ChannelDeleteApiView.as_view()) , 
    path('channel/<int:pk>/videos/' , ChannelVideoApiView.as_view()) , 
    path('channel/<int:pk>/stats/' , ChannelStatsApiView.as_view()) , 

    path('videos/' , VideoListApiView.as_view()) ,
    path('videos/search' , VideoSearchApiView.as_view()) ,
    path('videos/top' , VideoTopApiView.as_view()) ,
    path('videos/<int:pk>/related' , VideoRelatedApiView.as_view()) ,
    path('video/create/' , VideoCreateApiView.as_view()) ,
    path('video/<int:pk>/detail/' , VideoDetailApiView.as_view() ) , 
    path('video/<int:pk>/update/' , VideoUpdateApiView.as_view()) , 
    path('video/<int:pk>/delete/' , VideoDeleteApiView.as_view()) , 

    path('comments/<int:pk>/' , CommentsListAPiView.as_view()) , 
    path('comment/<int:pk>/create/' , CommentCreateApiView.as_view()) , 
    path('comment/<int:pk>/detail/' , CommentDetailApiView.as_view()) , 
    path('comment/<int:pk>/delete/' , CommentDeleteApiView.as_view()) , 

    path('like/<int:pk>/' , LikeCreateApiView.as_view()) , 
    path('like/<int:pk>/video' , LikesVideoListApiView.as_view()),

    path('stats/videos' , StatsVideosApiView.as_view()) ,
    path('stats/users' , StatsUsersApiView.as_view()) ,
    path('stats/channels' , StatsChannelsApiView.as_view()) ,
]
