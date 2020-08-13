from JGS.serializer import DocSerializer, DocListSerializer, UserInfoSerializer, UserRegSerializer, GroupCreateSerializer,\
    GroupSerializer, CommentSerializer, CommentCreateSerializer, FavoriteSerializer, BrowseSerializer
from web_models import models
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import serializers
import uuid

# Create your views here.

class UserAuthentication:
    def authenticate(self, request):

        token = request.query_params.get('token')
        user = models.Users.objects.filter(token=token).first()
        if user:
            return (user,token)
        else:
            return (None,None)

class DocView(APIView):
    authentication_classes = [UserAuthentication]
    def get(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        if not id:
            pass
        else:
            result = models.Doc.objects.filter(id=id).first()
            ser = DocListSerializer(instance=result, many=False)
            return Response(ser.data)
        return Response("失败")

    def post(self,request,*args,**kwargs):
        ser = DocSerializer(data=request.data)

        if ser.is_valid():
            ser.save(author_id=request.user.id)
            return Response("成功")
        return Response("失败")

    def patch(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        doc = models.Doc.objects.get(id=id)
        if doc.status == 1:
            return Response('该文档正在被编辑')
        result = models.Doc.objects.filter(id=id).first()
        ser = DocListSerializer(instance=result, data=request.data, many=False, partial=True)
        if ser.is_valid():
            ser.save()
            return Response('成功')
        return Response('失败')


class LoginView(APIView):
    def post(self,request,*args,**kwargs):
        user = models.Users.objects.filter(**request.data).first()
        if not user:
            return Response('登录失败')

        user_token = str(uuid.uuid4())
        user.token = user_token
        user.save()
        return Response(user_token)

class RegisterView(APIView):
    def post(self,request,*args,**kwargs):
        user1 = models.Users.objects.filter(username=request.data['username']).first()
        if user1:
            return Response('用户名已存在')
        user2 = models.Users.objects.filter(email=request.data['email']).first()
        if user2:
            return Response('邮箱已存在')
        ser = UserRegSerializer(data=request.data)
        if ser.is_valid():
            ser.save(nickname=request.data['username'])
            user = models.Users.objects.filter(username=request.data['username']).first()
            user_token = str(uuid.uuid4())
            user.token = user_token
            user.save()
            return Response(user_token)
        return Response('error')

class UserView(APIView):
    authentication_classes = [UserAuthentication]

    def get(self,request,*args,**kwargs):
        ser = UserInfoSerializer(instance=request.user)
        return Response(ser.data)

    def patch(self, request, *args, **kwargs):
        ser = UserInfoSerializer(instance=request.user, data=request.data, partial=True)
        if ser.is_valid():
            ser.save()
            return Response('修改成功')
        return Response('修改失败')

class FavoriteView(APIView):
    authentication_classes = [UserAuthentication]

    def get(self,request,*args,**kwargs):
        doc_id = kwargs.get('pk')
        if not doc_id:
            ser = FavoriteSerializer(instance=request.user, many=False)
            return Response(ser.data)
        else:
            pass
        return Response("失败")

    # 添加收藏
    def put(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        doc = models.Doc.objects.get(id=id)
        request.user.favorite.add(doc)
        return Response('成功')

    # 取消收藏
    def delete(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        doc = models.Doc.objects.get(id=id)
        request.user.favorite.remove(doc)
        return Response('成功')

class BrowseView(APIView):
    authentication_classes = [UserAuthentication]

    def get(self, request, *args, **kwargs):
        doc_id = kwargs.get('pk')
        if not doc_id:
            ser = BrowseSerializer(instance=request.user, many=False)
            return Response(ser.data)
        else:
            pass
        return Response("失败")

    # 添加到最近浏览
    def put(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        doc = models.Doc.objects.get(id=id)
        request.user.browse.add(doc)
        return Response('成功')

class GroupView(APIView):
    authentication_classes = [UserAuthentication]
    # 创建团队
    def post(self,request,*args,**kwargs):
        group = models.Groups.objects.filter(name=request.data['name']).first()
        if group:
            return Response('小组名重复')
        ser = GroupCreateSerializer(data=request.data)
        if ser.is_valid():
            ser.save(leader_id=request.user.id)
            return Response('成功')
        return Response('失败')

    def get(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        result = models.Groups.objects.filter(id=id).first()
        ser = GroupSerializer(instance=result, many=False)
        return Response(ser.data)

    # 解散团队（权限）
    def delete(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        group = models.Groups.objects.get(id=id)
        if request.user.id == group.leader.id:
            models.Groups.objects.get(id=id).delete()
            return Response('解散成功')
        else:
            return Response('解散失败')

    # 加入团队
    def put(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        group = models.Groups.objects.get(id=id)
        group.member.add(request.user)
        return Response('成功')

class GroupMemberView(APIView):
    # 退出团队
    authentication_classes = [UserAuthentication]
    def delete(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        group = models.Groups.objects.get(id=id)
        group.member.remove(request.user)
        return Response('成功')

    # 移除成员(权限)
    def put(self,request,*args,**kwargs):
        group_id = kwargs.get('pk')
        member_id = kwargs.get('pkk')
        group = models.Groups.objects.get(id=group_id)
        if request.user.id == group.leader.id:
            user = models.Users.objects.get(id=member_id)
            group.member.remove(user)
            return Response('成功')
        else:
            return Response('失败')


class CommentView(APIView):
    authentication_classes = [UserAuthentication]

    def post(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        ser = CommentCreateSerializer(data=request.data)

        if ser.is_valid():
            ser.save(commenter_id=request.user.id,document_id=id)
            return Response("成功")
        return Response("失败")

    def get(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        result = models.Comment.objects.filter(document_id=id).all()
        ser = CommentSerializer(instance=result, many=True)
        return Response(ser.data)
