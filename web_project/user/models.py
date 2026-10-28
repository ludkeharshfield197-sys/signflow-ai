import hashlib

from django.contrib.auth.hashers import check_password, identify_hasher, make_password
from django.db import models
from django.utils.crypto import constant_time_compare
from rest_framework import serializers


# Create your models here.
class SysUser(models.Model):
    id = models.AutoField(primary_key=True)
    username = models.CharField(max_length=100, unique=True, verbose_name="用户名")
    password = models.CharField(max_length=100, verbose_name="密码")
    avatar = models.CharField(max_length=255, null=True, verbose_name="用户头像")
    email = models.CharField(max_length=100, null=True, verbose_name="用户邮箱")
    phonenumber = models.CharField(max_length=11, null=True, verbose_name="手机号码")
    login_date = models.DateField(null=True, verbose_name="最后登录时间")
    status = models.IntegerField(null=True, verbose_name="帐号状态（0正常 1停用）")
    create_time = models.DateField(null=True, verbose_name="创建时间", )
    update_time = models.DateField(null=True, verbose_name="更新时间")
    remark = models.CharField(max_length=500, null=True, verbose_name="备注")

    class Meta:
        db_table = "sys_user"

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return self.status in (None, 0)

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    def check_password(self, raw_password, *, upgrade_legacy=True):
        try:
            identify_hasher(self.password)
        except ValueError:
            legacy_digest = hashlib.md5(raw_password.encode("utf-8")).hexdigest()
            verified = constant_time_compare(self.password, legacy_digest)
            if verified and upgrade_legacy:
                self.set_password(raw_password)
                self.save(update_fields=["password"])
            return verified
        return check_password(raw_password, self.password)


class SysUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = SysUser
        fields = (
            "id",
            "username",
            "avatar",
            "email",
            "phonenumber",
            "login_date",
            "status",
            "create_time",
            "update_time",
            "remark",
        )
        read_only_fields = fields
