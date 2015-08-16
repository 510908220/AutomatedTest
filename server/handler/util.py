# -*- coding: UTF-8 -*-

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


class EmailManage(object):
	"""
	邮件发送
	"""

	def __init__(self):
		"""
		设置发送邮件账户及服务器基本信息
		"""
		self.mail_host = "smtp.163.com"  # 设置服务器
		self.mail_user = "m13417710900_1"  # 用户名
		self.mail_pass = "xkrzwyjwqqgfxgcr"  # 口令,<网易有效是一个客户端授权码>
		self.mail_postfix = "163.com"  # 发件箱的后缀

	def send(self, sub, content, to_list=None, char_set="utf-8"):
		if not to_list:
			raise Exception("to_list must not be empty!")
		me = "hzz" + "<" + self.mail_user + "@" + self.mail_postfix + ">"
		msgRoot = MIMEMultipart('related')
		msgRoot['Subject'] = sub
		msgRoot['From'] = me
		msgRoot['To'] = ";".join(to_list)
		msgAlternative = MIMEMultipart('alternative')
		msgRoot.attach(msgAlternative)
		msg = MIMEText(content, _subtype='html', _charset=char_set)
		msgAlternative.attach(msg)
		try:
			server = smtplib.SMTP()
			server.connect(self.mail_host)
			server.login(self.mail_user, self.mail_pass)
			server.sendmail(me, to_list, msgRoot.as_string())
			server.quit()
			return True
		except Exception as e:
			print(e)
			return False


if __name__ == '__main__':
	mailto_list = ["huzhongzhong@yy.com"]
	em = EmailManage()
	flag = em.send("Strife 1.2.3.4", "has more than 100 bug", mailto_list)
