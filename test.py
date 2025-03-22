import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import os
import time
import socket
import urllib3
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# 设置更长的超时时间
socket.setdefaulttimeout(60)  # 增加到60秒

# 默认代理设置
DEFAULT_PROXY = "http://127.0.0.1:7890"

# 配置urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)  # 禁用SSL警告
http = urllib3.ProxyManager(
    DEFAULT_PROXY,
    headers={
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.89 Safari/537.36",
        "Referer": "https://www.pixiv.net/"
    },
    cert_reqs='CERT_NONE',  # 不验证SSL证书
    timeout=urllib3.Timeout(connect=10.0, read=30.0)
)

class PixivDownloader:
    def __init__(self):
        self.save_path = r"C:\Users\Administrator\Desktop\截图\pixiv"
        self.bookmarks_url = "https://www.pixiv.net/users/95869424/bookmarks/artworks"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.6998.89 Safari/537.36",
            "Referer": "https://www.pixiv.net/"
        }
        # 确保保存目录存在
        if not os.path.exists(self.save_path):
            os.makedirs(self.save_path)
            print(f"创建保存目录: {self.save_path}")
        else:
            print(f"使用现有保存目录: {self.save_path}")
        
        # 设置Chrome选项
        self.chrome_options = Options()
        self.chrome_options.add_argument("--headless")  # 无头模式
        self.chrome_options.add_argument("--disable-gpu")
        self.chrome_options.add_argument("--no-sandbox")
        self.chrome_options.add_argument("--disable-dev-shm-usage")
        # 禁用日志输出
        self.chrome_options.add_argument("--log-level=3")
        self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
        
        # 添加默认代理设置
        self.chrome_options.add_argument(f'--proxy-server={DEFAULT_PROXY}')
        print(f"使用代理: {DEFAULT_PROXY}")
        
        # 添加SSL错误忽略
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--ignore-ssl-errors')
        
        # 设置页面加载策略为急切模式，不等待所有资源加载完成
        self.chrome_options.page_load_strategy = 'eager'
        
        # 指定ChromeDriver路径
        chrome_driver_path = r"D:\Chromedriver\chromedriver-win64\chromedriver.exe"
        
        print("正在启动浏览器...")
        try:
            # 初始化Chrome浏览器
            self.driver = webdriver.Chrome(executable_path=chrome_driver_path, options=self.chrome_options)
            # 设置页面加载超时时间
            self.driver.set_page_load_timeout(30)
            self.driver.set_script_timeout(30)
            print("浏览器已在后台成功启动")
            
            # 测试代理连接
            self.test_proxy_connection()
        except Exception as e:
            print(f"浏览器启动失败: {e}")
            raise
    
    def test_proxy_connection(self):
        """测试代理连接是否正常"""
        try:
            print("正在测试代理连接...")
            # 使用urllib3测试代理连接
            response = http.request('GET', 'https://www.pixiv.net', timeout=10.0)
            if response.status == 200:
                print("代理连接测试成功！")
            else:
                print(f"代理连接测试返回状态码: {response.status}")
        except Exception as e:
            print(f"代理连接测试失败: {e}")
            print("警告: 代理可能无法正常工作，程序可能无法正常访问Pixiv")
        
    def login(self, username, password):
        """登录Pixiv账号"""
        print("正在访问Pixiv登录页面...")
        try:
            # 先访问主页
            try:
                print("正在访问Pixiv主页...")
                self.driver.get("https://www.pixiv.net/")
            except TimeoutException:
                print("访问主页超时，登录失败")
                return False
            
            time.sleep(5)
            
            # # 检查是否已经登录
            # if self.check_login_status():
            #     print("检测到已经登录状态，无需再次登录")
            #     return True
            
            # 查找并点击登录链接
            try:
                print("尝试查找并点击登录链接...")
                login_link = self.driver.find_element(By.XPATH, "//a[contains(@href, '/login.php') and contains(@class, 'signup-form__submit--login')]")
                login_link.click()
                print("已点击登录链接")
                time.sleep(3)
            except Exception as e:
                print(f"未找到登录链接或点击失败: {e}")
                print("尝试直接访问登录页面...")
                try:
                    self.driver.get("https://accounts.pixiv.net/login")
                    time.sleep(5)
                except:
                    print("访问登录页面失败")
                    return False
            
            # 等待登录表单加载
            try:
                print("等待登录表单加载...")
                # 使用您提供的选择器
                WebDriverWait(self.driver, 30).until(
                    EC.presence_of_element_located((By.XPATH, "//input[@autocomplete='username webauthn' or @autocomplete='username']"))
                )
                print("登录表单已加载")
            except TimeoutException:
                print("登录表单加载超时，登录失败")
                return False
            
            print("正在输入登录信息...")
            # 使用您提供的选择器查找并填写用户名和密码
            try:
                # 查找用户名输入框
                username_input = self.driver.find_element(By.XPATH, "//input[@class='sc-bn9ph6-6 dogEql' and @autocomplete='username webauthn']")
                username_input.clear()
                username_input.send_keys(username)
                print("已输入用户名")
                
                # 查找密码输入框
                password_input = self.driver.find_element(By.XPATH, "//input[@class='sc-bn9ph6-6 dogEql' and @autocomplete='current-password webauthn']")
                password_input.clear()
                password_input.send_keys(password)
                print("已输入密码")
                
                # 查找并点击登录按钮
                submit_button = self.driver.find_element(By.XPATH, "//button[@type='submit' and contains(@class, 'sc-2o1uwj-10 ldVSLT')]")
                submit_button.click()
                print("已点击登录按钮")
            except Exception as e:
                print(f"填写表单或点击登录按钮失败: {e}")
                print("登录失败")
                return False
            
            # 等待登录成功 - 增加等待时间
            try:
                print("等待登录处理...")
                time.sleep(10)  # 增加等待时间，给登录过程更多时间
                
                # 保存登录后的页面截图用于调试
                screenshot_path = os.path.join(self.save_path, "login_result.png")
                self.driver.save_screenshot(screenshot_path)
                print(f"已保存登录结果截图: {screenshot_path}")
                
                # 保存页面源码用于调试
                with open(os.path.join(self.save_path, "login_page.html"), "w", encoding="utf-8") as f:
                    f.write(self.driver.page_source)
                print("已保存登录页面源码用于调试")
            except Exception as e:
                print(f"保存调试信息失败: {e}")
            
            # 检查是否真的登录成功
            if self.check_login_status():
                print("登录成功！")
                return True
            else:
                print("登录失败，请检查用户名和密码是否正确")
                return False
            
        except (TimeoutException, NoSuchElementException) as e:
            print(f"登录失败: {e}")
            print("提示: Pixiv在中国大陆无法直接访问，请确保您已连接代理或VPN")
            return False
        except Exception as e:
            print(f"登录过程中发生未知错误: {e}")
            return False
    
    def check_login_status(self):
        """检查是否已登录"""
        try:
            # 多种方式检查登录状态
            
            # 方法1: 检查页面源码中是否包含登出相关文本
            if "logout" in self.driver.page_source.lower():
                print("通过logout文本检测到登录状态")
                return True
            
            # 方法2: 检查URL是否包含mypage
            if "mypage" in self.driver.current_url:
                print("通过mypage URL检测到登录状态")
                return True
            
            # 方法3: 检查是否存在用户菜单按钮
            try:
                user_menu = self.driver.find_elements(By.XPATH, "//button[contains(@class, 'ccl__sc-1lxyknw-0') and contains(@class, 'hZvyDT') and contains(@class, 'sc-pkfh0q-1') and contains(@class, 'ikiFYU')]")
                if user_menu:
                    print("通过用户菜单按钮检测到登录状态")
                    return True
            except:
                pass
            
            # 方法4: 检查是否存在用户名显示
            try:
                username_display = self.driver.find_elements(By.XPATH, "//div[contains(@class, 'user-name')]")
                if username_display:
                    print("通过用户名显示检测到登录状态")
                    return True
            except:
                pass
            
            # 方法5: 尝试查找特定的登录后才会显示的元素
            try:
                logged_in_elements = self.driver.find_elements(By.XPATH, "//a[contains(@href, '/bookmark.php')]")
                if logged_in_elements:
                    print("通过收藏链接检测到登录状态")
                    return True
            except:
                pass
            
            print("未检测到登录状态")
            return False
        except Exception as e:
            print(f"检查登录状态时发生错误: {e}")
            return False
    
    def get_artwork_links(self):
        """获取收藏页面中的所有作品链接"""
        artwork_links = []
        current_page = 1
        has_next_page = True
        
        # 首先访问收藏页面
        print(f"正在访问收藏页面: {self.bookmarks_url}")
        self.driver.get(self.bookmarks_url)
        time.sleep(10)  # 给予足够的初始加载时间
        
        while has_next_page:
            print(f"正在处理第 {current_page} 页")
            page_links = []  # 初始化当前页面的链接列表
            
            # 如果不是第一页，需要构造并访问对应页面的URL
            if current_page > 1:
                page_url = f"{self.bookmarks_url}?p={current_page}"
                self.driver.get(page_url)
                time.sleep(10)  # 增加页面加载等待时间
            
            # 等待作品列表加载
            try:
                print("等待作品列表加载...")
                
                # 等待页面完全加载
                print("等待页面完全加载...")
                WebDriverWait(self.driver, 30).until(
                    lambda driver: driver.execute_script('return document.readyState') == 'complete'
                )
                
                # 滚动页面以触发动态加载
                print("滚动页面以加载更多内容...")
                for _ in range(3):  # 多次滚动以确保加载
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(5)  # 每次滚动后等待更长时间
                
                # 使用显式等待机制等待作品列表容器
                max_retries = 5
                retry_count = 0
                while retry_count < max_retries:
                    try:
                        print(f"尝试第 {retry_count + 1} 次查找作品列表...")
                        
                        # 等待并切换到第一个charcoal-token类的div
                        # 等待并获取主容器元素，但不切换frame
                        # main_container = WebDriverWait(self.driver, 10).until(
                        #     EC.presence_of_element_located((By.CSS_SELECTOR, "div.charcoal-token[data-theme='default']"))
                        # )
                        # print("页面主容器已加载")

                        # 尝试查找作品列表容器
                        try:
                            # 首先找到ul容器
                            artwork_list = WebDriverWait(self.driver, 100).until(
                                EC.presence_of_element_located((By.XPATH, "//ul[contains(@class, 'sc-9y4be5-1') and contains(@class, 'jtUPOE')]"))
                            )
                            print("找到作品列表容器")
                            
                            # 在ul中查找所有li元素
                            li_elements = artwork_list.find_elements(By.CSS_SELECTOR, "li")
                            print(f"找到 {len(li_elements)} 个作品项")
                            
                            # 遍历每个li元素，查找其中的链接
                            artwork_elements = []
                            for li in li_elements:
                                try:
                                    # 在每个li中查找包含artworks的链接
                                    links = li.find_elements(By.CSS_SELECTOR, "a.sc-d98f2c-0.sc-rp5asc-16.iUsZyY.sc-bdnxRM.fGjAxR")
                                    for link in links:
                                        href = link.get_attribute("href")
                                        if href:
                                            # 如果链接不以https://www.pixiv.net开头，添加前缀
                                            if not href.startswith("https://www.pixiv.net"):
                                                href = "https://www.pixiv.net" + href
                                            artwork_elements.append(link)
                                except Exception as e:
                                    print(f"处理单个作品项时出错: {e}")
                                    continue
                            
                            print(f"找到 {len(artwork_elements)} 个作品链接")
                            
                        except Exception as e:
                            print(f"查找作品列表容器失败: {e}")
                            self.driver.save_screenshot('error.png')
                            artwork_elements = []
                        
                        if artwork_elements:
                            for element in artwork_elements:
                                try:
                                    href = element.get_attribute("href")
                                    if href and href not in artwork_links:
                                        artwork_links.append(href)
                                        page_links.append(href)
                                except Exception as e:
                                    print(f"处理作品链接时出错: {e}")
                                    continue
                            
                            # 检查是否有下一页
                            try:
                                next_page_links = self.driver.find_elements(By.CSS_SELECTOR, "a.sc-d98f2c-0.sc-xhhh7v-2.cCkJiq.sc-xhhh7v-1-filterProps-Styled-Component.kKBslM")
                                if next_page_links:
                                    current_page += 1
                                    print(f"找到下一页链接，将继续处理第 {current_page} 页")
                                else:
                                    has_next_page = False
                                    print("已到达最后一页")
                            except Exception as e:
                                print(f"检查下一页时出错: {e}")
                                has_next_page = False
                            
                            break  # 成功找到作品列表，退出重试循环
                        else:
                            print("未找到任何作品链接，将重试")
                            retry_count += 1
                            time.sleep(5)
                    except Exception as e:
                        print(f"第 {retry_count + 1} 次尝试失败: {e}")
                        retry_count += 1
                        time.sleep(5)
                
                if retry_count >= max_retries:
                    print("达到最大重试次数，停止获取作品链接")
                    has_next_page = False
            
            except Exception as e:
                print(f"处理页面时发生错误: {e}")
                has_next_page = False
            
            # 打印当前页面获取的链接数量
            print(f"当前页面找到 {len(page_links)} 个作品链接")
        
        print(f"共找到 {len(artwork_links)} 个作品链接")
        return artwork_links

    def download_artwork(self, artwork_links):
        """下载收藏的作品"""
        print(f"开始下载 {len(artwork_links)} 个作品")
        
        for index, artwork_url in enumerate(artwork_links, 1):
            try:
                print(f"\n正在处理第 {index} 个作品: {artwork_url}")
                
                # 访问作品详情页
                self.driver.get(artwork_url)
                time.sleep(5)  # 等待页面加载
                
                # 等待页面加载完成
                WebDriverWait(self.driver, 30).until(
                    lambda driver: driver.execute_script('return document.readyState') == 'complete'
                )
                
                # 尝试点击展开按钮
                try:
                    expand_button = WebDriverWait(self.driver, 5).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "button.sc-emr523-0.guczbC"))
                    )
                    expand_button.click()
                    print("已点击展开按钮")
                    time.sleep(3)  # 等待展开动画完成
                except:
                    print("未找到展开按钮或点击失败，继续处理")
                
                # 查找图片容器
                try:
                    img_container = WebDriverWait(self.driver, 10).until(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-1e1hy3c-1.iHTUPI"))
                    )
                    
                    # 查找所有图片元素
                    img_elements = img_container.find_elements(By.TAG_NAME, "img")
                    print(f"找到 {len(img_elements)} 个图片")
                    
                    # 遍历并下载图片
                    for img_index, img in enumerate(img_elements, 1):
                        try:
                            img_url = img.get_attribute("src")
                            if not img_url:
                                continue
                            
                            # 构造文件名
                            artwork_id = artwork_url.split("/")[-1]
                            file_name = f"{artwork_id}_{img_index}.png"
                            file_path = os.path.join(self.save_path, file_name)
                            
                            # 检查文件是否已存在
                            if os.path.exists(file_path):
                                print(f"文件已存在，跳过: {file_name}")
                                continue
                            
                            print(f"正在下载图片: {file_name}")
                            # 使用urllib3下载图片
                            response = http.request('GET', img_url)
                            if response.status == 200:
                                with open(file_path, 'wb') as f:
                                    f.write(response.data)
                                print(f"图片下载成功: {file_name}")
                            else:
                                print(f"图片下载失败，状态码: {response.status}")
                        
                        except Exception as e:
                            print(f"下载图片时出错: {e}")
                            continue
                    
                except Exception as e:
                    print(f"处理图片容器时出错: {e}")
                    continue
                
            except Exception as e:
                print(f"处理作品时出错: {e}")
                continue
        
        print("\n所有作品处理完成！")

if __name__ == "__main__":
    # 创建下载器实例
    downloader = PixivDownloader()
    
    # 登录账号
    username = "1601698207@qq.com"
    password = "q131450580"
    if downloader.login(username, password):
        # 获取收藏作品链接
        artwork_links = downloader.get_artwork_links()
        print(f"准备下载 {len(artwork_links)} 个作品")
        # 下载作品
        downloader.download_artwork(artwork_links)
    else:
        print("登录失败，程序退出")



# import urllib3
# from bs4 import BeautifulSoup
# from selenium import webdriver

# 使用
# # 默认代理设置
# DEFAULT_PROXY = "http://127.0.0.1:7890"

# # 指定ChromeDriver路径
# chrome_driver_path = r"D:\Chromedriver\chromedriver-win64\chromedriver.exe"

# 功能步骤：
# 1.登录：
# 找到https://www.pixiv.net/  后找到  https://www.pixiv.net/<a href="/login.php?ref=wwwtop_accounts_index" class="signup-form__submit--login">登录</a>
# 点击后找到<input type="text" autocomplete="username webauthn" placeholder="邮箱地址或pixiv ID" autocapitalize="off" class="sc-bn9ph6-6 dogEql" value="" style="padding-right: 8px;">
# 输入账号：1601698207@qq.com
# 找到<input type="password" autocomplete="current-password webauthn" placeholder="密码" autocapitalize="off" class="sc-bn9ph6-6 dogEql" value="" style="padding-right: 36px;">
# 输入密码：q131450580
# 然后点击<button type="submit" disabled="" class="charcoal-button sc-2o1uwj-10 ldVSLT" data-variant="Primary" data-full-width="true">登录</button>
# 2.进入主页后找到收藏界面，并找到所有的收藏：
# 进入主页后找到< class="ccl__sc-1lxyknw-0 hZvyDT sc-pkfh0q-1 ikiFYU">点击后找到class="sc-d98f2c-0 sc-1hmmdyq-3 sc-199m2iw-3 fkdacG fWlXiW gtm-user-menu-bookmark" 的a标签的href属性并在前面添加https://www.pixiv.net/前缀后跳转收藏界面。进入收藏界面后class="sc-9y4be5-1 jtUPOE"的ul标签然后遍历各个li标签找到其中的a标签中的href属性，并添加前缀https://www.pixiv.net后跳转详细界面，如果点击不了就遍历下一个li标签中的链接。
# 最后找到class="sc-d98f2c-0 sc-xhhh7v-2 cCkJiq sc-xhhh7v-1-filterProps-Styled-Component kKBslM"的a标签中的href属性并添加https://www.pixiv.net/为前缀，并于获取当前界面的链接进行比较如果不同则跳转合成后的链接所指的界面，如果相同则退出程序并输出已经遍历完成最后一页
# 3.在进入详细界面以后找到<button type="button" class="sc-emr523-0 guczbC">按钮并点击，如果没有这个按钮则跳过这个步骤，然后找到<div role="presentation" class="sc-1e1hy3c-1 iHTUPI">并遍历其中所有的img标签，找到其中的src属性并添加有的img标签，找到其中的src属性，然后下载图片（png）保存到C:\Users\Administrator\Desktop\截图\pixiv

# 函数设计：
#  def __init__(self)
#  def test_proxy_connection(self)
#  def login(self, username, password)
#  def check_login_status(self)
#  def get_artwork_links(self)
#  def download_artwork(self, artwork_links)
# if __name__ == "__main__"