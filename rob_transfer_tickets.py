# -*- coding:utf-8 -*-
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import time


class RobTickets(object):

    def __init__(self):
        self.option = webdriver.ChromeOptions()
        self.option.add_argument("--no-sandbox")
        # 将chrome浏览器隐藏
        # self.option.add_argument("--headless")
        self.login_url = "https://kyfw.12306.cn/otn/resources/login.html"
        # https://kyfw.12306.cn/otn/leftTicket/init
        # 12306首页
        self.initmy_url = "https://kyfw.12306.cn/otn/view/index.html"
        # 车票查询首页
        self.search_url = "https://kyfw.12306.cn/otn/leftTicket/init"
        # 车票换乘查询首页
        self.search_transfer_url = "https://kyfw.12306.cn/otn/lcQuery/init"
        # 车票预定提交界面
        self.passenger_url = "https://kyfw.12306.cn/otn/confirmPassenger/initDc"
        # 换乘车票预定提交界面
        self.transfer_passenger_url = "https://kyfw.12306.cn/otn/lcConfirmPassenger/initLc"
        # 注意下面Chrome的大小写字母开头必须是大写
        self.driver = webdriver.Chrome(executable_path='/ScrapyProject/virtualenv/py3/lib/python3.6/site-packages/chromedriver',
                                       chrome_options=self.option)

    # 判断抢票类型
    def judge_rob_type(self):
        self.rob_type = input("请输入抢票类型(输入1或2): 1.直达  2.换乘\n>>")
        self.from_station = input("请输入出发地\n>>")
        self.to_station = input("请输入目的地\n>>")
        self.passengers = input("请输入乘客姓名（如有多个请用英文逗号隔开）\n>>").split(",")
        return self.rob_type


    # 换乘信息输入
    def wait_transter_input(self):
        self.depart_transter_time = input("请输入乘车日期\n>>")
        self.transfer_trains = input("请输入车次（如有多个车次用英文逗号隔开）\n>>").split(",")
        step = 2
        # 将用户输入的车次信息分为2个一组，防止抢到了不匹配的车次。
        self.transfer_trains = [self.transfer_trains[i:i + step] for i in range(0, len(self.transfer_trains), step)]

    # 信息输入
    def wait_input(self):
        # 手动输入（较灵活）
        self.depart_time = input("请输入出发时间\n>>")
        self.trains = input("请输入车次（如有多个车次用英文逗号隔开）\n>>").split(",")

    def _login(self):
        self.driver.get(self.login_url)
        self.driver.find_element_by_xpath(".//ul/li[2][@class='login-hd-account']").click()
        time.sleep(1)
        # 输入用户名
        self.driver.find_element_by_id("J-userName").send_keys("xxxxxx")
        time.sleep(1)
        # 输入密码
        self.driver.find_element_by_id("J-password").send_keys("xxxxxx")
        # 显式等待
        WebDriverWait(self.driver, 1000).until(
            EC.url_to_be(self.initmy_url)
        )
        print("登陆成功！")

    def _order_ticket(self):
        # 判断抢票类型
        if self.rob_type == "1":
            # 请求订票页面
            self.driver.get(self.search_url)
            # 等待用户输入出发地并进行比较
            WebDriverWait(self.driver, 1000).until(
                EC.text_to_be_present_in_element_value((By.ID, "fromStationText"), self.from_station)
            )
            # 等待用户输入目的地并进行比较
            WebDriverWait(self.driver, 1000).until(
                EC.text_to_be_present_in_element_value((By.ID, "toStationText"), self.to_station)
            )

            # 等待用户输入出发时间并进行比较
            WebDriverWait(self.driver, 1000).until(
                EC.text_to_be_present_in_element_value((By.ID, "train_date"), self.depart_time)
            )

            # 不停的循环查询，直到抢到票为止！
            MASK_LOOP = True
            while MASK_LOOP:
	            # 等待查询按钮是否可点击
	            WebDriverWait(self.driver, 1000).until(
	                EC.element_to_be_clickable((By.ID, "query_ticket"))
	            )
	            # 如果可以点击则触发查询事件
	            searchBtn = self.driver.find_element_by_id("query_ticket")
	            searchBtn.click()
	            # 等待车次信息显示出来
	            WebDriverWait(self.driver, 1000).until(
	                EC.presence_of_element_located((By.XPATH, ".//tbody[@id='queryLeftTable']/tr"))
	            )
	            # 获取需要的tr标签
	            tr_list = self.driver.find_elements_by_xpath(".//tbody[@id='queryLeftTable']/tr[not(@datatran)]")
	            print("正在努力抢票中，请稍等...")
	            # 遍历满足条件的车次信息
	            for tr in tr_list:
	                train_number = tr.find_element_by_class_name("number").text
	                if train_number in self.trains:
	                    left_ticket = tr.find_element_by_xpath(".//td[4]").text
	                    # print(train_number)
	                    if left_ticket == "有" or left_ticket.isdigit():
	                    	MASK_LOOP = False
                                print("太好了，终于抢到了！")
	                        orderBtn = tr.find_element_by_class_name("btn72")
	                        orderBtn.click()
	                        # 等待是否来到了乘客页面
	                        WebDriverWait(self.driver, 1000).until(
	                            EC.url_to_be(self.passenger_url)
	                        )
	                        # 选择用户
	                        presence_list = self.driver.find_elements_by_xpath(".//ul[@id='normal_passenger_id']/li")
	                        # print(presence_list)
	                        for presence_label in presence_list:
	                            # time.sleep(1)
	                            presence_name = presence_label.find_element_by_xpath("./label").text
	                            # print(presence_name)
	                            if presence_name in self.passengers:
	                                # print(presence_name)
	                                presence_label.find_element_by_class_name("check").click()

	                        # 提交订单
	                        time.sleep(2)
	                        self.driver.find_element_by_id("submitOrder_id").click()
	                        time.sleep(1)
	                        self.driver.find_element_by_id("qr_submit_id").click()
	                        break

        elif self.rob_type == "2":
            # 请求订票页面
            self.driver.get(self.search_transfer_url)
            # 等待用户输入出发地并进行比较
            WebDriverWait(self.driver, 1000).until(
                EC.text_to_be_present_in_element_value((By.ID, "fromStationText"), self.from_station)
            )
            # 等待用户输入目的地并进行比较
            WebDriverWait(self.driver, 1000).until(
                EC.text_to_be_present_in_element_value((By.ID, "toStationText"), self.to_station)
            )

            # 等待用户输入出发时间并进行比较
            WebDriverWait(self.driver, 1000).until(
                EC.text_to_be_present_in_element_value((By.ID, "train_start_date"), self.depart_transter_time)
            )

            # 不停的循环查询，直到抢到票为止！
            MASK_LOOP = True
            while MASK_LOOP:
	            # 等待查询按钮是否可点击
	            WebDriverWait(self.driver, 1000).until(
	                EC.element_to_be_clickable((By.ID, "_a_search_btn"))
	            )
	            # 如果可以点击则触发查询事件
	            searchBtn = self.driver.find_element_by_id("_a_search_btn")
	            searchBtn.click()
	            # 等待车次信息显示出来
	            WebDriverWait(self.driver, 1000).until(
	                EC.presence_of_element_located((By.XPATH, ".//tbody[@id='middle_div_new_tbody']/tr"))
	            )
	            # 获取需要的tr标签
	            tr_list = self.driver.find_elements_by_xpath("//tbody[@id='middle_div_new_tbody']/tr[@id and not(@style)]")
	            print("正在努力抢票中，请稍等...")
	            # 遍历满足条件的车次信息
	            trains_list = []
	            for tr in tr_list:
	                train_number = tr.find_element_by_class_name("number").text
	                trains_list.append(train_number)
	            # 将车次信息分为两个一组
	            step = 2
	            new_trains_list = [trains_list[i:i+step] for i in range(0, len(trains_list), step)]
	            # 将tr标签也分为两个一组
	            new_tr_list = [tr_list[i:i+step] for i in range(0, len(tr_list), step)]
	            # 利用zip函数将车次和tr标签组合在一起
	            res_list = list(zip(new_trains_list, new_tr_list))
	            for res in res_list:
	                if res[0] in self.transfer_trains:
	                    NUM = 0
	                    for tr in res[1]:
	                        # 二等座
	                        second_class = tr.find_element_by_xpath(".//td[4]").text
	                        # 硬座
	                        hard_seat = tr.find_element_by_xpath(".//td[10]").text
	                        # 硬卧
	                        hard_sleeper = tr.find_element_by_xpath(".//td[8]").text
	                        if second_class == "有" or second_class.isdigit() or hard_seat == "有" or hard_seat.isdigit() \
	                                or hard_sleeper == "有" or hard_sleeper.isdigit():
	                            NUM = NUM + 1
	                        else:
	                            continue
	                    # 判断所选的两个车次是否都有票
	                    if NUM == 2:
	                        # print(res[1][0])
	                        orderBtn = res[1][0].find_element_by_class_name("no-br")
	                        orderBtn.click()
	                        time.sleep(1)
	                        self.driver.find_element_by_id("dialog_lc_ok").click()
	                        # 等待是否来到了乘客页面
	                        WebDriverWait(self.driver, 1000).until(
	                            EC.url_to_be(self.transfer_passenger_url)
	                        )
	                        # 遍历账户中已存在的用户
	                        presence_list = self.driver.find_elements_by_xpath(".//ul[@id='normal_passenger_id']/li")
	                        # 判断我们输入的用户，是否在账户中存在
	                        for presence_label in presence_list:
	                            presence_name = presence_label.find_element_by_xpath("./label").text
	                            # 如果用户匹配，则选中用户
	                            if presence_name in self.passengers:
	                                presence_label.find_element_by_class_name("check").click()
	                        # 提交订单
	                        time.sleep(2)
	                        self.driver.find_element_by_id("submitOrder_id").click()
	                        time.sleep(1)
	                        self.driver.find_element_by_id("qr_submit_id").click()
	                        print("太好了，终于抢到了！")
	                        break
	                    else:
	                        continue

    def run(self):
        rob_type = self.judge_rob_type()
        # 判断抢票类型
        if rob_type == "1":
            self.wait_input()
        elif rob_type == "2":
            self.wait_transter_input()
        self._login()
        self._order_ticket()


if __name__ == '__main__':
    spider = RobTickets()
    spider.run()
