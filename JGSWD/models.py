from django.db import models


class Users(models.Model):
    id = models.AutoField(primary_key=True)
    nickname = models.CharField(max_length=20, verbose_name='昵称')
    username = models.CharField(max_length=25, verbose_name='用户名')
    password = models.CharField(max_length=20, verbose_name='密码')
    email = models.EmailField(verbose_name='电子邮箱')
    birthday = models.DateField(verbose_name='生日')
    sex = models.CharField(max_length=5, verbose_name='性别')

    def __str__(self):
        return self.username

    class Meta:
        verbose_name = '用户'
        verbose_name_plural = '用户'


class Groups(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20, verbose_name='组名称')
    leader = models.CharField(max_length=25, verbose_name='组长用户名')
    member = models.ManyToManyField(to='Users', verbose_name='小组成员')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = '小组'
        verbose_name_plural = '小组'


class Doc(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=25, verbose_name='文档名称')
    title = models.CharField(max_length=128, verbose_name='文档标题')
    content = models.TextField(verbose_name='文档内容')
    createtime = models.DateTimeField(auto_now_add=True, verbose_name='文档创建时间')
    updatetime = models.DateTimeField(auto_now=True, verbose_name='文档更新时间')
    updates = models.PositiveIntegerField(default=0, verbose_name='文档被修改次数')
    author = models.ForeignKey(to='Users', to_field='id', verbose_name='文档创建者')
    group = models.ForeignKey(to='Groups', to_field='id', verbose_name='文档所属组')
    delete = models.IntegerField(default=0, verbose_name='文档是否被删除')     # 0表示未被删除，1表示在回收站，2表示彻底删除
    status = models.IntegerField(default=0, verbose_name='文档是否正被编辑')    # 0表示未被编辑，1表示正在被编辑
    favorite = models.ManyToManyField(to='Users', verbose_name='收藏文档')
    browse = models.ManyToManyField(to='Users', verbose_name='浏览记录')

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['-updatetime']
        verbose_name = '文档'
        verbose_name_plural = '文档'


class Comment(models.Model):
    id = models.AutoField(primary_key=True)
    content = models.CharField(max_length=128, verbose_name='评论')
    commenter = models.ForeignKey(to='Users', to_field='id', verbose_name='评论者')
    document = models.ForeignKey(to='Doc', to_field='id', verbose_name='评论文档')

    def __str__(self):
        return self.id

    class Meta:
        verbose_name = '评论'
        verbose_name_plural = '评论'
