#filename:page_base.py
from selenium.webdriver.support.wait import WebDriverWait #导入显式等待类WebDriverWait类
from selenium.webdriver.common.by import By

# 页面类的基类,被其他页面类继承
class PageBase:
    # 即墨：以前的那个make_xpath_with_unit_feature和make_xpath_with_feature函数是有bug的，现在这个是OK的
    # 辅助函数
    '''
    函数功能：拼接XPATH字符串中间部分（不过，后面会多个"and"）。例如：XPATH字符串"//*[contains(@text,'设')]"的中间部分是"contains(@text,'设')"!
    即：
    如果loc 给 "text,设置"或"text,设置,0",函数返回"contains(@text,'设置')and"，情况1！
    如果loc = "text,设置,1",函数返回"@text='设置'and"，情况2！
    '''
    def make_xpath_with_unit_feature(self,loc):
        args = loc.split(",")
        feature = ""  # 返回值

        if len(args) == 2:
            feature = "contains(@" + args[0] + ",'" + args[1] + "')" + "and "
        elif len(args) == 3:
            if args[2] == "1":
                feature = "@" + args[0] + "='" + args[1] + "'" + "and "
            elif args[2] == "0":
                feature = "contains(@" + args[0] + ",'" + args[1] + "')" + "and "
        return feature

    '''
    函数功能：给简化的xpath，函数返回标准的xpath字符串。
    即:
    如果loc = "text,设置"或"text,设置,0"，函数返回"//*[contains(@text,'设置')]"，情况1。
    如果loc = "text,设置,1"，函数返回"//*[@text='设置']"，情况2。
    如果loc = ["text,设置"] ，函数返回"//*[contains(@text,'设置')]"，情况1。
    如果loc = ["text,设置", "index,20,1", "index1,50"]，函数返回"//*[contains(@text,'设置')and@index='20'andcontains(@index1,'50')]"，情况3。
    如果loc = "//*[contains(@text,'设')]" ，即故意传个正常的xpath字符串，函数返回"//*[contains(@text,'设')]"，情况4。
    '''
    def make_xpath_with_feature(self,loc):
        feature_start = "//*["
        feature_end = "]"
        feature = ""

        # 如果传的是字符串，即情况1和情况2
        if isinstance(loc, str):
            # 如果是正常的xpath，即情况4
            if loc.startswith("//"):
                return loc
            feature = self.make_xpath_with_unit_feature(loc)
        else:  # 如果传的是列表，即情况3
            for i in loc:
                feature += self.make_xpath_with_unit_feature(i)

        feature = feature.rstrip("and ")  # 删除最右侧的"and "
        ret_loc = feature_start + feature + feature_end
        return ret_loc

    # 辅助函数，被下面的click函数调用
    #函数功能：找满足定位条件loc的单个元素。
    #形参loc：定位元素的条件，loc类似“By.XPATH,"text,Display,1"”、“By.ID,"k001"”。
    #形参time：总共搜索time秒。单位是秒！
    #形参poll：每poll秒搜索一次。单位是秒。
    def find_element(self, loc,time=5.0,poll=1.0):
        by = loc[0]
        value = loc[1]
        if by == By.XPATH:
            value = self.make_xpath_with_feature(value)
        # 下面的是“x”是“self.driver”
        return WebDriverWait(self.driver, time, poll).until(lambda x: x.find_element(by, value))

    #辅助函数,本案例中未被调用
    #函数功能：找满足定位条件loc的一组元素。
    #形参loc：定位元素的条件，loc类似“By.XPATH,"text,Display,1"”、“By.ID,"k001"”。
    # 形参time：总共搜索time秒。单位是秒！
    # 形参poll：每poll秒搜索一次。单位是秒。
    def find_elements(self, loc,time=5.0,poll=1.0):
        by = loc[0]
        value = loc[1]
        if by == By.XPATH:
            value = self.make_xpath_with_feature(value)
        return WebDriverWait(self.driver, time, poll).until(lambda x: x.find_elements(by, value))

    def __init__(self, driver):
        self.driver = driver

    # 函数功能：对loc定位的某元素进行单击
    def click(self, loc):
        self.find_element(loc).click()  # 调用辅助函数

    # 函数功能：对loc定位的某元素进行输入文本text
    def input_text(self, loc, text):
        self.find_element(loc).send_keys(text)  # 调用辅助函数

    #find_toast函数的版本1，不太精简
    #函数功能：根据toast的部分文本内容message找toast，并返回toast的全部文本内容！
    # 形参message: 预期要获取的toast的部分文本内容。比如你toast的文本内容是"登录成功",那么message可以给"成功"。
    # def find_toast(self,message, timeout=3,poll=0.1):
    #     xpath_str = "//*[contains(@text,'" + message + "')]"  # 使用包含的方式定位toast
    #     # toast = driver.find_element(By.XPATH, xpath_str) #不用显式等待时也OK，但是不好
    #     toast = WebDriverWait(self.driver, timeout, poll).until(lambda x: x.find_element(By.XPATH, xpath_str))
    #     return toast.text  # 返回toast的整个文本内容

    #find_toast函数的版本2
    # 函数功能：根据toast的部分文本内容message找toast，并返回toast的全部文本内容！
    # 形参message: 预期要获取的toast的部分文本内容。比如你toast的文本内容是"登录成功",那么message可以给"成功"。
    #形参is_screenshot：是否截图。默认是不截图。
    #形参screenshot_name:如果截图，这里给图片名。
    def find_toast(self, message, is_screenshot=False, screenshot_name=None, timeout=3, poll=0.1):
        xpath_str = "//*[contains(@text,'" + message + "')]"  # 使用包含的方式定位
        toast = self.find_element((By.XPATH, xpath_str), timeout, poll)
        if is_screenshot:
            self.screenshot(screenshot_name)
        return toast.text  # 返回toast的整个文本内容

    #is_toast_exist函数的版本1：里面有函数调用，可能增大CPU
    # 函数功能：根据toast的部分文本内容message来判断toast是否存在。如果存在，就返回True。
    # def is_toast_exist(self, message, is_screenshot=False, screenshot_name=None, timeout=3, poll=0.1):
    #     try:
    #         self.find_toast(message, is_screenshot, screenshot_name, timeout, poll)
    #         return True
    #     except Exception:
    #         return False

    # is_toast_exist函数的版本2
    #函数功能：根据toast的部分文本内容message来判断toast是否存在。如果存在，就返回True。
    def is_toast_exist(self, message,is_screenshot=False,screenshot_name=None,timeout=3, poll=0.1):
        try:
            #定位toast
            xpath_str = "//*[contains(@text,'" + message + "')]"  # 使用包含的方式定位toast
            toast = self.find_element((By.XPATH, xpath_str), timeout, poll)
            #print(toast.text);#输出toast的整个文本内容
            if is_screenshot:
                self.driver.get_screenshot_as_file("./screen/" + screenshot_name + ".png")
            return True
        except Exception:
            return False

    #函数功能：截图
    def screenshot(self, file_name):
        self.driver.get_screenshot_as_file("./screen/" + file_name + ".png")