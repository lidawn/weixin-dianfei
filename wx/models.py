from django.db import models

class User(models.Model):
	weixin_id = models.CharField(max_length=100)
	#area
	quyu = models.CharField(max_length=20)
	#building
	louhao = models.CharField(max_length=30)
	#room
	fangjian = models.IntegerField()
	#isbounded
	is_bounded = models.BooleanField(default=False)
	#history
	history = models.TextField(blank=True,null=True)
