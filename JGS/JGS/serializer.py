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

    class Meta:
        model = models.Users
        fields = ['favorite']


class BrowseSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Users
        fields = ['browse']
    # browse_info = serializers.SerializerMethodField()
    #
    # class Meta:
    #     model = models.Users
    #     fields = ['id', 'username', 'browse_info']
    #
    # def get_browse_info(self, obj):
    #     return [row.nickname for row in obj.browse.all().values()]

class GroupCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Groups
        exclude = ['leader', 'member']


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Groups
        exclude = []
        depth = 1

class GroupLessSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Groups
        exclude = []


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

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Module
        exclude = []
        depth = 1

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Message
        exclude = []


class MessageCreateSerializer(serializers.ModelSerializer):     # 只有在申请加入团队时产生消息
    class Meta:
        model = models.Message
        exclude = ['touser', 'senduser', 'content']

class DocPageSerializer(serializers.ModelSerializer):     # 只有在申请加入团队时产生消息
    nickname = serializers.SerializerMethodField()
    class Meta:
        model = models.Doc
        fields = ['id','title','content','updates','delete','createtime','updatetime','status','auth','author',
                  'group','nickname']

    def get_nickname(self, obj):
        return obj.author.nickname
