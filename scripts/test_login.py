import os, sys
import pytest
import allure
import time
sys.path.append(os.getcwd()) #用于解决：pytest找不到模块问题！
from base.base_yaml import yml_data_with_filename_and_key
from base.base_driver import init_driver
from page.page_login import PageLogin #导入此页面类
from appium import webdriver

#辅助函数：用于再处理测试数据
def data_with_key(key):
    return yml_data_with_filename_and_key("data_login", key)

class TestLogin:
    def setup(self):
        self.driver = init_driver()
        self.page_login = PageLogin(self.driver) #页面类的构造函数

    def teardown(self):
        self.driver.quit()

    @allure.step(title="测试“登录”模块的测试脚本")
    @pytest.mark.parametrize("dict_data", data_with_key("test_login"))
    def test_login(self,dict_data):#形参dict_data是字典类型
        username = dict_data["username"];
        password = dict_data["pwd"];
        toast = dict_data["toast"];
        screen = dict_data["screen"];

        #步骤1：点击“我的”选项卡
        allure.attach('', '点击“我的”选项卡')
        self.page_login.click_my();
        #步骤2：点击“登录/注册”
        allure.attach('', '点击“登录/注册”')
        self.page_login.click_loginreg();
        #步骤3：点击“用UC账号登录”或“切换到旧版登录”
        allure.attach('', '点击“UC”按钮')
        self.page_login.click_uc();
        #步骤4：输入手机号
        allure.attach("输入的数据是"+username,"输入账号" )
        self.page_login.input_zanhao(username)
        #步骤5：输入密码
        allure.attach("输入的数据是" + password,"输入密码" )
        self.page_login.input_pwd(password);
        #步骤6：点击“登录”按钮
        allure.attach('', '点击“登录”按钮')
        self.page_login.click_login();
        #步骤7：断言登录是否成功
        allure.attach("要找的toast的关键字是："+toast,"判断某toast是否存在" );
        ret=self.page_login.is_toast_exist(toast,True,screen,20);
        # 步骤8：上传截图图片到Allure测试报告中
        allure.attach(open('./screen/' + screen + '.png', 'rb').read(), "本次截图", allure.attachment_type.PNG)
        assert ret;


