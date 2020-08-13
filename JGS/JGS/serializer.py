from rest_framework import serializers
from web_models import models


class DocSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Doc
        exclude = ['author']


class DocListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Doc
        exclude = []
        depth = 1


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Users
        exclude = []


class UserRegSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Users
        exclude = ['nickname']


class FavoriteSerializer(serializers.ModelSerializer):
    favorite_info = serializers.SerializerMethodField()
    class Meta:
        model = models.Users
        fields = ['id', 'username', 'favorite_info']

    def get_favorite_info(self,obj):
        return [row for row in obj.favorite.all().values()]

class BrowseSerializer(serializers.ModelSerializer):
    browse_info = serializers.SerializerMethodField()

    class Meta:
        model = models.Users
        fields = ['id', 'username', 'browse_info']

    def get_browse_info(self, obj):
        return [row for row in obj.browse.all().values()]

class GroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Groups
        exclude = ['leader', 'member']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Groups
        exclude = []
        depth = 1

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        exclude = []
        depth = 1

class CommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        exclude = ['document', 'commenter']
        depth = 1


