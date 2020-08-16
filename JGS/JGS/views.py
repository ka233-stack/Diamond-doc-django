from JGS.serializer import DocSerializer, DocListSerializer, UserInfoSerializer, UserRegSerializer, GroupCreateSerializer,\
    GroupSerializer, CommentSerializer, CommentCreateSerializer, FavoriteSerializer, BrowseSerializer, ModuleSerializer,\
    GroupLessSerializer, MessageSerializer, MessageCreateSerializer, DocPageSerializer
from web_models import models
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
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
        if not request.user:
            return Response("请先登录")

        id = kwargs.get('pk')
        doc = models.Doc.objects.get(id=id)
        ser = GroupLessSerializer(instance=doc.group)
        dict = ser.data['member']
        if (doc.group and ((request.user.id in dict) or request.user == doc.group.leader)) or doc.auth >= 1: # 团队文件且在团队内
            result = models.Doc.objects.filter(id=id).first()
            ser = DocListSerializer(instance=result, many=False)
            return Response(ser.data)
        if doc.group is None and doc.author == request.user: # 个人文件
            result = models.Doc.objects.filter(id=id).first()
            ser = DocListSerializer(instance=result, many=False)
            return Response(ser.data)
        return Response("无权限")

    def post(self,request,*args,**kwargs):
        if not request.user:
            return Response("请先登录")
        ser = DocSerializer(data=request.data)

        if ser.is_valid():
            ser.save(author_id=request.user.id)
            return Response(ser.data)
        return Response("失败")

    def patch(self, request, *args, **kwargs):
        if not request.user:
            return Response("请先登录")
        id = kwargs.get('pk')
        doc = models.Doc.objects.get(id=id)
        ser = GroupLessSerializer(instance=doc.group)
        dict = ser.data['member']
        updates = doc.updates
        if (doc.group and ((request.user.id in dict) or request.user == doc.group.leader)) or doc.auth >= 3:
            if doc.status == 1:
                return Response('该文档正在被编辑')
            else:
                result = models.Doc.objects.filter(id=id).first()
                ser = DocListSerializer(instance=result, data=request.data, many=False, partial=True)
                if ser.is_valid():
                    updates = updates+1
                    ser.save(updates=updates)
                    return Response(ser.data)
        if doc.author == request.user and doc.group is None:
            if doc.status == 1:
                return Response('该文档正在被编辑')
            else:
                result = models.Doc.objects.filter(id=id).first()
                ser = DocListSerializer(instance=result, data=request.data, many=False, partial=True)
                if ser.is_valid():
                    updates = updates+1
                    ser.save(updates=updates)
                    return Response(ser.data)
        else:
            return Response('无权限')


# 用户文件
class DocUserView(APIView):
    authentication_classes = [UserAuthentication]
    def get(self, request, *args, **kwargs):
        result = models.Doc.objects.filter(author=request.user.id, delete=0).all()
        total = len(result)
        page_object = PageNumberPagination()
        result_ = page_object.paginate_queryset(result, request, self)
        ser = DocPageSerializer(instance=result_, many=True)
        dict = ser.data
        for row in dict:
            row['total'] = total
        return Response(ser.data)

# 团队文件
class DocGroupView(APIView):
    authentication_classes = [UserAuthentication]
    def get(self, request, *args, **kwargs):
        id = kwargs.get('pk')
        result = models.Doc.objects.filter(group=id, delete=0).all()
        total = len(result)
        page_object = PageNumberPagination()
        result_ = page_object.paginate_queryset(result, request, self)
        ser = DocPageSerializer(instance=result_, many=True)
        dict = ser.data
        for row in dict:
            row['total'] = total
        return Response(ser.data)

# 回收站中的文件
class DocBinView(APIView):
    authentication_classes = [UserAuthentication]
    def get(self, request, *args, **kwargs):
        result = models.Doc.objects.filter(author=request.user.id, delete=1).all()
        total = len(result)
        page_object = PageNumberPagination()
        result_ = page_object.paginate_queryset(result, request, self)
        ser = DocPageSerializer(instance=result_, many=True)
        dict = ser.data
        for row in dict:
            row['total'] = total
        return Response(ser.data)

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
            message = models.Message(touser=user, category=1, content="欢迎您使用  文档，该网站提供在线文档协作编辑等功能，祝您使用愉快！")
            message.save()
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
            return Response(ser.data)
        return Response('修改失败')

class UserGroupView(APIView):
    authentication_classes = [UserAuthentication]
    def get(self,request,*args,**kwargs):

        result = models.Groups.objects.filter().all()
        ser = GroupLessSerializer(instance=result, many=True)
        dict = ser.data
        queryset = None
        for row in dict:
            if request.user.id == row['leader'] or (request.user.id in row['member']):
                if queryset is None:
                    queryset = models.Groups.objects.filter(id=row['id']).all()
                else:
                    queryset = queryset | models.Groups.objects.filter(id=row['id']).all()
        ser_ = GroupSerializer(instance=queryset, many=True)
        return Response(ser_.data)


class FavoriteView(APIView):
    authentication_classes = [UserAuthentication]

    def get(self,request,*args,**kwargs):
        ser = FavoriteSerializer(instance=request.user, many=False)
        page_object = PageNumberPagination()
        queryset = None
        total = 0
        for row in ser.data['favorite']:
            if queryset is None:
                queryset = models.Doc.objects.filter(id=row).all()
                total = total +1
            else:
                queryset = queryset | models.Doc.objects.filter(id=row).all()
                total = total + 1
        if queryset is None:
            return Response('查询结果为空')
        result_ = page_object.paginate_queryset(queryset, request, self)
        ser = DocPageSerializer(instance=result_, many=True)
        dict = ser.data
        for row in dict:
            row['total'] = total
        return Response(dict)

        # doc_id = kwargs.get('pk')
        # if not doc_id:
        #     ser = FavoriteSerializer(instance=request.user, many=False)
        #     return Response(ser.data)
        # else:
        #     pass
        # return Response("失败")

    # 添加收藏
    def put(self,request,*args,**kwargs):
        if not request.user:
            return Response("请先登录")
        id = kwargs.get('pk')
        doc = models.Doc.objects.get(id=id)
        touser = doc.author
        message = models.Message(touser=touser,category=5, content="您的文档 "+"《"+doc.title+"》"+"被他人收藏")
        message.save()
        request.user.favorite.add(doc)
        return Response('成功')

    # 取消收藏
    def delete(self,request,*args,**kwargs):
        if not request.user:
            return Response("请先登录")
        id = kwargs.get('pk')
        doc = models.Doc.objects.get(id=id)
        request.user.favorite.remove(doc)
        return Response('成功')

class BrowseView(APIView):
    authentication_classes = [UserAuthentication]

    def get(self, request, *args, **kwargs):
        ser = BrowseSerializer(instance=request.user, many=False)
        page_object = PageNumberPagination()
        queryset = None
        total = 0
        for row in ser.data['browse']:
            if queryset is None:
                queryset = models.Doc.objects.filter(id=row).all()
                total = total+1
            else:
                queryset = queryset | models.Doc.objects.filter(id=row).all()
                total = total + 1
        if queryset is None:
            return Response('查询结果为空')
        result_ = page_object.paginate_queryset(queryset, request, self)
        ser = DocPageSerializer(instance=result_, many=True)
        dict = ser.data
        for row in dict:
            row['total'] = total
        return Response(dict)
        # doc_id = kwargs.get('pk')
        # if not doc_id:
        #     ser = BrowseSerializer(instance=request.user, many=False)
        #     return Response(ser.data)
        # else:
        #     pass
        # return Response("失败")

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
        if not request.user:
            return Response("请先登录")
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
        group = models.Groups.objects.get(id=id)
        isManager = False
        if group.leader.token == request.auth:
            isManager = True
        result = models.Groups.objects.filter(id=id).first()
        ser = GroupSerializer(instance=result, many=False)
        dict = ser.data
        dict['isManager'] = isManager
        return Response(dict)

    # 解散团队（权限）
    def delete(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        group = models.Groups.objects.get(id=id)
        if request.user.id == group.leader.id:
            ser = GroupLessSerializer(instance=group)
            for row in ser.data['member']:
                touser = models.Users.objects.filter(id=row).first()
                message = models.Message(touser=touser, category=8, content="您加入的" + group.name + "团队已解散")
                message.save()
            models.Groups.objects.get(id=id).delete()
            models.Doc.objects.filter(group=group).all().delete()
            return Response('解散成功')
        else:
            return Response('解散失败')

    # 加入团队
    def put(self,request,*args,**kwargs):
        if not request.user:
            return Response("请先登录")
        id = kwargs.get('pk')
        group = models.Groups.objects.get(id=id)
        if request.data['decision'] is True:
            group.member.add(request.user)
            user_id = request.data['user_id']
            message = models.Message(touser_id=user_id, category=3, content="您已成功加入"+group.name+"小组")
            message.save()
        else:
            user_id = request.data['user_id']
            message = models.Message(touser_id=user_id, category=3, content="您加入" + group.name + "小组的申请已被拒绝")
            message.save()
        return Response('成功')

class GroupMemberView(APIView):
    # 退出团队
    authentication_classes = [UserAuthentication]
    def delete(self,request,*args,**kwargs):
        if not request.user:
            return Response("请先登录")
        id = kwargs.get('pk')
        group = models.Groups.objects.get(id=id)
        group.member.remove(request.user)
        touser = group.leader
        message = models.Message(touser=touser, category=6, content=request.user.username+"退出了您的"+group.name+"团队")
        message.save()
        return Response('成功')

    # 移除成员(权限)
    def put(self,request,*args,**kwargs):
        group_id = kwargs.get('pk')
        member_id = kwargs.get('pkk')
        group = models.Groups.objects.get(id=group_id)
        if request.user.id == group.leader.id:
            user = models.Users.objects.get(id=member_id)
            group.member.remove(user)
            touser = user
            message = models.Message(touser=touser, category=7, content="您被移出了" + group.name + "团队")
            message.save()
            return Response('成功')
        else:
            return Response('失败')


class CommentView(APIView):
    authentication_classes = [UserAuthentication]

    def post(self,request,*args,**kwargs):
        if not request.user:
            return Response("请先登录")
        id = kwargs.get('pk')
        doc = models.Doc.objects.get(id=id)
        ser = GroupLessSerializer(instance=doc.group)
        dict = ser.data['member']

        if (doc.group and ((request.user.id in dict) or request.user == doc.group.leader)) or doc.auth >= 2:
            ser = CommentCreateSerializer(data=request.data)
            if ser.is_valid():
                touser = doc.author
                message = models.Message(touser=touser, category=4, content="您的文档 " + "《" + doc.title + "》" + "被他人评论")
                message.save()
                ser.save(commenter_id=request.user.id, document_id=id)
                return Response(ser.data)
        if doc.author == request.user and doc.group is None:
            ser = CommentCreateSerializer(data=request.data)
            if ser.is_valid():
                touser = doc.author
                if touser != request.user:
                    message = models.Message(touser=touser, category=4, content="您的文档 " + "《" + doc.title + "》" + "被他人评论")
                    message.save()
                ser.save(commenter_id=request.user.id, document_id=id)
                return Response(ser.data)
        else:
            return Response("无权限")


    def get(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        result = models.Comment.objects.filter(document_id=id).all()
        ser = CommentSerializer(instance=result, many=True)
        return Response(ser.data)


class ModuleView(APIView):
    authentication_classes = [UserAuthentication]

    # 获取个人及默认模板列表
    def get(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        if id:
            result = models.Module.objects.filter(id=id).first()
            ser = ModuleSerializer(instance=result, many=False)
            return Response(ser.data)
        else:
            result = models.Module.objects.filter(creater=None).all() | models.Module.objects.filter(creater=request.user).all()
            ser = ModuleSerializer(instance=result, many=True)
            return Response(ser.data)

    def post(self,request,*args,**kwargs):
        ser = ModuleSerializer(data=request.data, many=False)
        if ser.is_valid():
            ser.save(creater=request.user)
            return Response(ser.data)

class MessageView(APIView):
    authentication_classes = [UserAuthentication]

    def get(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        if id:
            result = models.Message.objects.filter(id=id).first()
            ser = MessageSerializer(instance=result, many=False)
            return Response(ser.data)
        else:
            result = models.Message.objects.filter(touser=request.user).all()
            ser = MessageSerializer(instance=result, many=True)
            count = 0
            for row in ser.data:
                if row['status'] == 1:
                    count = count + 1
            dict = ser.data
            dict[0]['count'] = count    # 在第一条信息中存储了一共几条未读
            return Response(dict)

    def post(self,request,*args,**kwargs):      # 申请加入团队生成给组长的消息 传过来小组ID、申请人为当前用户、消息类型：2
        group = models.Groups.objects.filter(id=request.data['group_id']).first()
        if group is None:
            return Response('团队不存在')
        ser = MessageCreateSerializer(data=request.data)
        ser_ = GroupLessSerializer(instance=group)
        dict = ser_.data['member']
        if request.user == group.leader or (request.user.id in dict):
            return Response('已在该组中')
        if ser.is_valid():
            ser.save(touser=group.leader, senduser=request.user, group=group,
                                 content="用户名为"+request.user.username+"的用户申请加入您的"+group.name+"小组。")

        return Response('成功')

    def patch(self,request,*args,**kwargs):
        id = kwargs.get('pk')
        result = models.Message.objects.filter(id=id).first()
        ser = MessageSerializer(data=request.data, instance=result, partial=True)
        if ser.is_valid():
            ser.save()
            return Response('成功')

        return Response('失败')


