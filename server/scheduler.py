# -*- encoding: utf-8 -*-
from pymongo import MongoClient
import xmlrpc.client
import time
import logging
from functools import wraps
from handler import config
from handler import util

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                    datefmt='%a, %d %b %Y %H:%M:%S',
                    filename="scheduler.log",
                    filemode='w')
client = MongoClient('mongodb://localhost:27017/')
db = client[config.DB_NAME]


def log_decorator(f):
	@wraps(f)
	def wrapper(*args, **kwds):
		print('Calling decorated function')
		return f(*args, **kwds)

	return wrapper


def get_machine_state(ip):
	"""
	:param ip: 测试机ip
	:return: 测试机当前状态:-1 表示无法连接, 0 表示空闲,1表示正在执行用例
	"""
	proxy = xmlrpc.client.ServerProxy("http://%s:8000/" % ip)
	try:
		running_state = proxy.proxy_running()
	except Exception as err:
		print(err)
		return -1
	return 1 if running_state else 0


def get_machine_ips():
	tb_machine = db[config.TB_MACHINE]
	ips = [machine_item["ip"] for machine_item in tb_machine.find()]
	return ips


def del_running_case(running_case):
	tb_running_case = db[config.TB_RUNNING_CASE]
	tb_running_case.remove(running_case)


def add_running_case(case, ip):
	"""
	:param case: 正在执行的用例
	:param ip: 用例宿主机器
	:return:
	"""
	tb_running_case = db[config.TB_RUNNING_CASE]
	case["ip"] = ip
	tb_running_case.insert(case)


def get_running_case(ip):
	"""
	:param ip: 测试机ip
	:return: 测试机正在执行的用例
	"""
	tb_running_case = db[config.TB_RUNNING_CASE]
	running_case = tb_running_case.find_one({"ip": ip})
	return running_case


def pop_pending_case():
	"""
	:return:从未执行的用例里选择一个用例
	"""
	tb_pending_case = db[config.TB_PENDING_CASE]
	pending_cases = []
	for case in tb_pending_case.find():
		pending_cases.append(case)

	if pending_cases:
		current_case = pending_cases[-1]
		tb_pending_case.remove(current_case)
		return current_case


def dispatch_case(ip, case):
	"""
	:param ip: 空闲的测试机ip
	:param case: 待分发给测试机的用例
	:return:
	"""
	proxy = xmlrpc.client.ServerProxy("http://%s:8000/" % ip)
	if not proxy.case_exists(case["name"]):
		case_path = config.CASES_DIR.joinpath(case["name"] + ".zip")
		with open(str(case_path), "rb") as f:
			proxy.push_case(case["name"], f.read())
	proxy.run_case(case["name"])


def email_report(task):
	def get_user_emails():
		tb_user = db[config.TB_USER]
		user_emails = []
		for user in tb_user.find():
			user_emails.append(user["email"])
		return user_emails

	email_title = task["version"]
	email_content = ""
	for case_name in task["result"]:
		email_content += (case_name + "<br/>" + task["result"][case_name] + "<br/>")
	em = util.EmailManage()

	user_emails = get_user_emails()
	if user_emails:
		flag = em.send(email_title, email_content, user_emails)
		logging.info("email_report:%s" % str(flag))
	else:
		logging.info("email_report:no user...")


def update_task_result(case, result):
	tb_task = db[config.TB_TASK]
	task = tb_task.find_one(case["task_id"])
	task["result"][case["name"]] = result
	if len(task["result"]) == len(task["cases"]):
		task["finished"] = True
		if task["email"]:
			email_report(task)
	tb_task.update({"_id": task["_id"]}, task)


def case_result_handle(ip):
	"""
	:param ip:正在运行的测试机
	:return:
	"""
	case = get_running_case(ip)
	if not case:
		return
	proxy = xmlrpc.client.ServerProxy("http://%s:8000/" % ip)
	if proxy.case_finished(case["name"]):
		result = proxy.get_result(case["name"])
		logging.info("collect result:%s %s %s" % (ip, case, result))
		update_task_result(case, result)
		del_running_case(case)


def case_handle(ip):
	case = pop_pending_case()
	if case:
		logging.info("dispatch case:%s %s" % (ip, case))
		dispatch_case(ip, case)
		add_running_case(case, ip)


def loop():
	while 1:
		ips = get_machine_ips()
		for ip in ips:
			state = get_machine_state(ip)
			if state == 0:
				case_handle(ip)
				time.sleep(10)
			elif state == 1:
				case_result_handle(ip)
				time.sleep(5)


if __name__ == "__main__":
	loop()
