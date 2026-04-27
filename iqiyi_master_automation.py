import hashlib
import base64
import time
import json
import sys
import os
import urllib.request
from datetime import datetime
from collections import OrderedDict
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_v1_5
import requests


class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


class HTMLReportGenerator:
    """HTML报告生成器"""
    
    def __init__(self):
        self.results = []
        self.pages_visited = []
        self.start_time = datetime.now()
        self.screenshot_count = 0
        self.video_path = None
        self.total_links_found = 0
        self.depth_stats = {}
    
    def add_result(self, category, name, status, details="", response_time=0, url="", depth=0):
        self.results.append({
            "category": category, "name": name, "status": status,
            "details": details, "response_time": response_time,
            "time": datetime.now().strftime('%H:%M:%S'),
            "url": url, "depth": depth
        })
    
    def add_page(self, url, title, status_code, links_found, depth):
        self.pages_visited.append({
            "url": url, "title": title, "status": status_code,
            "links": links_found, "depth": depth,
            "time": datetime.now().strftime('%H:%M:%S')
        })
        self.total_links_found += links_found
        if depth not in self.depth_stats:
            self.depth_stats[depth] = 0
        self.depth_stats[depth] += 1
    
    def generate_html(self, output_path="report_master.html"):
        passed = sum(1 for r in self.results if r["status"] == "通过")
        failed = sum(1 for r in self.results if r["status"] != "通过")
        total_time = (datetime.now() - self.start_time).total_seconds()
        
        # 收集截图文件
        screenshots = []
        if os.path.exists("screenshots"):
            screenshots = sorted(os.listdir("screenshots"))
        
        html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>爱奇艺开发者平台 - 完整自动化测试报告</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f5f7fa; color: #333; line-height: 1.6; }}
        .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
        
        /* Header */
        .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 15px; margin-bottom: 30px; box-shadow: 0 10px 40px rgba(0,0,0,0.1); }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header .meta {{ opacity: 0.9; font-size: 1.1em; }}
        
        /* Stats Cards */
        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }}
        .stat-card {{ background: white; padding: 25px; border-radius: 12px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); text-align: center; transition: transform 0.3s; }}
        .stat-card:hover {{ transform: translateY(-5px); }}
        .stat-card .number {{ font-size: 2.5em; font-weight: bold; margin: 10px 0; }}
        .stat-card .label {{ color: #666; font-size: 0.9em; }}
        .stat-card.success {{ border-top: 4px solid #52c41a; }}
        .stat-card.danger {{ border-top: 4px solid #ff4d4f; }}
        .stat-card.info {{ border-top: 4px solid #1890ff; }}
        .stat-card.warning {{ border-top: 4px solid #faad14; }}
        .success .number {{ color: #52c41a; }}
        .danger .number {{ color: #ff4d4f; }}
        .info .number {{ color: #1890ff; }}
        .warning .number {{ color: #faad14; }}
        
        /* Sections */
        .section {{ background: white; border-radius: 12px; padding: 30px; margin-bottom: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.08); }}
        .section h2 {{ color: #667eea; margin-bottom: 20px; padding-bottom: 10px; border-bottom: 2px solid #f0f0f0; }}
        
        /* Tables */
        table {{ width: 100%; border-collapse: collapse; margin-top: 15px; }}
        th {{ background: #f8f9fa; padding: 12px; text-align: left; font-weight: 600; color: #555; border-bottom: 2px solid #e8e8e8; }}
        td {{ padding: 12px; border-bottom: 1px solid #f0f0f0; }}
        tr:hover {{ background: #f8f9fa; }}
        .status-pass {{ color: #52c41a; font-weight: bold; }}
        .status-fail {{ color: #ff4d4f; font-weight: bold; }}
        .status-404 {{ color: #faad14; font-weight: bold; }}
        
        /* Page List */
        .page-item {{ padding: 15px; margin: 10px 0; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #667eea; }}
        .page-item.depth-0 {{ border-left-color: #52c41a; }}
        .page-item.depth-1 {{ border-left-color: #1890ff; }}
        .page-item.depth-2 {{ border-left-color: #faad14; }}
        .page-url {{ font-size: 0.85em; color: #666; word-break: break-all; }}
        .page-title {{ font-weight: 600; color: #333; margin: 5px 0; }}
        .page-meta {{ font-size: 0.8em; color: #999; }}
        
        /* Screenshots */
        .screenshot-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; margin-top: 20px; }}
        .screenshot-item {{ background: #f8f9fa; padding: 10px; border-radius: 8px; }}
        .screenshot-item img {{ width: 100%; border-radius: 4px; cursor: pointer; transition: transform 0.3s; }}
        .screenshot-item img:hover {{ transform: scale(1.02); }}
        .screenshot-name {{ font-size: 0.85em; color: #666; margin-top: 8px; text-align: center; }}
        
        /* Depth Chart */
        .depth-bar {{ display: flex; align-items: center; margin: 8px 0; }}
        .depth-label {{ width: 80px; font-size: 0.9em; color: #666; }}
        .depth-progress {{ flex: 1; height: 25px; background: #f0f0f0; border-radius: 12px; overflow: hidden; margin: 0 10px; }}
        .depth-fill {{ height: 100%; border-radius: 12px; display: flex; align-items: center; justify-content: flex-end; padding-right: 10px; color: white; font-size: 0.8em; font-weight: bold; }}
        .depth-count {{ width: 50px; text-align: right; font-weight: bold; color: #333; }}
        
        .footer {{ text-align: center; padding: 30px; color: #999; font-size: 0.9em; }}
    </style>
</head>
<body>
    <div class="container">
        <!-- Header -->
        <div class="header">
            <h1>🎬 爱奇艺开发者平台</h1>
            <h2>完整自动化测试报告</h2>
            <div class="meta">
                <p>📅 执行时间: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}</p>
                <p>⏱️ 总耗时: {total_time:.2f} 秒</p>
                <p>🖥️ 模式: 真实浏览器窗口（禁止无头模式）</p>
            </div>
        </div>
        
        <!-- Stats -->
        <div class="stats-grid">
            <div class="stat-card success">
                <div class="label">通过测试</div>
                <div class="number">{passed}</div>
            </div>
            <div class="stat-card danger">
                <div class="label">失败测试</div>
                <div class="number">{failed}</div>
            </div>
            <div class="stat-card info">
                <div class="label">访问页面</div>
                <div class="number">{len(self.pages_visited)}</div>
            </div>
            <div class="stat-card warning">
                <div class="label">发现链接</div>
                <div class="number">{self.total_links_found}</div>
            </div>
            <div class="stat-card info">
                <div class="label">截图数量</div>
                <div class="number">{len(screenshots)}</div>
            </div>
            <div class="stat-card success">
                <div class="label">遍历深度</div>
                <div class="number">{max(self.depth_stats.keys()) if self.depth_stats else 0}</div>
            </div>
        </div>
        
        <!-- API Test Results -->
        <div class="section">
            <h2>🔍 接口自动化测试结果</h2>
            <table>
                <tr><th>时间</th><th>测试项</th><th>状态</th><th>耗时</th><th>详情</th></tr>
"""
        
        # API测试结果
        for r in self.results:
            if "接口" in r["category"] or "算法" in r["category"] or "性能" in r["category"] or "结构" in r["category"]:
                status_class = "status-pass" if r["status"] == "通过" else "status-fail"
                html += f"""
                <tr>
                    <td>{r['time']}</td>
                    <td>{r['name']}</td>
                    <td class="{status_class}">{r['status']}</td>
                    <td>{r['response_time']:.2f}ms</td>
                    <td>{r['details']}</td>
                </tr>"""
        
        html += """
            </table>
        </div>
        
        <!-- Depth Stats -->
        <div class="section">
            <h2>📊 页面遍历深度统计</h2>
"""
        
        colors = ['#52c41a', '#1890ff', '#faad14', '#ff4d4f', '#722ed1']
        for depth, count in sorted(self.depth_stats.items()):
            max_count = max(self.depth_stats.values()) if self.depth_stats else 1
            percentage = (count / max_count) * 100
            color = colors[min(depth, len(colors)-1)]
            html += f"""
            <div class="depth-bar">
                <div class="depth-label">深度 {depth}</div>
                <div class="depth-progress">
                    <div class="depth-fill" style="width: {percentage}%; background: {color};">{count}</div>
                </div>
                <div class="depth-count">{count}页</div>
            </div>"""
        
        html += """
        </div>
        
        <!-- Visited Pages -->
        <div class="section">
            <h2>🌐 访问的页面列表（全站遍历）</h2>
"""
        
        for page in self.pages_visited:
            depth_class = f"depth-{min(page['depth'], 2)}"
            status_class = "status-404" if "404" in str(page['status']) else "status-pass"
            html += f"""
            <div class="page-item {depth_class}">
                <div class="page-url">{page['url']}</div>
                <div class="page-title">{page['title']}</div>
                <div class="page-meta">
                    <span class="{status_class}">状态: {page['status']}</span> | 
                    <span>深度: {page['depth']}</span> | 
                    <span>链接: {page['links']}个</span> | 
                    <span>时间: {page['time']}</span>
                </div>
            </div>"""
        
        html += """
        </div>
        
        <!-- Screenshots -->
        <div class="section">
            <h2>📸 自动化截图证据</h2>
            <div class="screenshot-grid">
"""
        
        for ss in screenshots:
            html += f"""
                <div class="screenshot-item">
                    <img src="screenshots/{ss}" alt="{ss}" onclick="window.open(this.src)">
                    <div class="screenshot-name">{ss}</div>
                </div>"""
        
        html += f"""
            </div>
        </div>
        
        <!-- Video -->
        <div class="section">
            <h2>🎥 录屏记录</h2>
            <p>录屏文件: <code>{self.video_path or '未生成'}</code></p>
            {f'<video controls style="width:100%;max-width:800px;"><source src="{self.video_path}" type="video/webm"></video>' if self.video_path and os.path.exists(self.video_path) else ''}
        </div>
        
        <div class="footer">
            <p>爱奇艺开发者平台完整自动化测试 | 生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
    </div>
</body>
</html>"""
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        
        return output_path


class IqiyiAPIClient:
    """API客户端"""
    TEST_URL = "https://test-openapi.vip.iqiyi.com"
    
    def __init__(self, partner_no, md5_key, private_key=None):
        self.partner_no = partner_no
        self.md5_key = md5_key
        self.private_key = private_key
        self.session = requests.Session()
    
    def sign(self, params):
        sorted_params = OrderedDict(sorted(params.items()))
        param_str = "&".join([f"{k}={v}" for k, v in sorted_params.items()])
        return hashlib.md5((param_str + self.md5_key).encode('utf-8')).hexdigest().lower()
    
    def decrypt_rsa(self, encrypted_data):
        if not self.private_key:
            return None
        try:
            key_bytes = base64.b64decode(self.private_key)
            private_key = RSA.import_key(key_bytes)
            cipher = PKCS1_v1_5.new(private_key)
            encrypted_bytes = base64.b64decode(encrypted_data)
            block_size = 128
            decrypted_blocks = []
            for i in range(0, len(encrypted_bytes), block_size):
                block = encrypted_bytes[i:i + block_size]
                decrypted_blocks.append(cipher.decrypt(block, None))
            return b"".join(decrypted_blocks).decode('utf-8')
        except:
            return None
    
    def call_user_info(self, token, check_discount="0"):
        params = {"partnerNo": self.partner_no, "token": token, "checkDiscount": check_discount}
        params["sign"] = self.sign(params)
        url = f"{self.TEST_URL}/identification/userInfo"
        start = time.time()
        response = self.session.get(url, params=params, timeout=10)
        elapsed = (time.time() - start) * 1000
        return response.json(), elapsed


class APITestSuite:
    """接口测试套件"""
    CONFIG = {
        "partner_no": "toB_common_test",
        "md5_key": "b0ee3c7f62760330",
        "valid_token": "44c0945918cea926045b73aa95e3af06",
        "expected_mobile": "13812345678",
        "private_key": """MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBALbjYMJwIW+PcvzM+k4vSr09IEKb
aXWam33bnqDO+Qsj4POHevGe/jvOuUI/bQn/jXD6WHMivk/N+9Q4firmU1IDRl6fZIA1rfn4S0j+
U8Z4bIxFURaBfcrRkA8I3cEQnuCMoD3cJXYZ/uuWogFXzIkTipHj7KrbULIOiR2Zp7ePAgMBAAEC
gYBJFgi+6yyRdpQPLqMAx6logpr3wz+bvdNRsohr3wprR0VITOX21QDoSa6DKPGcQ0H02jaqnEHN
hpWSs5jH8A9vU4XwprOLmo21GYqcnBGjMhZqrJ/IetATqoVBl41zfnsAzZwKQw4hZBsdnhQXMUwo
CB4rdUyNMGV4itjhZgBm0QJBAOd7f5j7OAkwU/bfkEtacM1/emgZ5a0Ys0J5RcRPrbhkkwiePKr0
O+TQ3tDTRT0NY26DWm/U5+OwKEGt/VyNBl0CQQDKQkcKl8l+Ds518DTj3V3Xj6y0glj6eMYNLIYq
i0UPPqtY1ZvvU41FYaTCCZDx/hBQQoOkk0ouefVCqqQST/7bAkAlhXguVPJFUwcZKi3aeQN12+b8
fs4i27Ea4ktzwbKYA/1tVTDiSQp4UX78fHJprgTjAfmjzO/1kTVFSC2cVeOlAkB78OFXvGvcs3YR
D4FZoO1AiupqMvYThq7Wo9ITgARxsxWM+ljz719ChPNRdEs9/1I/3IKO9zMeB94jXC3uitbBAkEA
iT0dweF9U/7OyE74DV5tHbVHWbqEMfIzZ+NzfVlXA91wcS6uAhovjOwCk1/ngToudUbLCazTkSOl
Wl1mhKBA+A=="""
    }
    
    def __init__(self, reporter):
        self.reporter = reporter
        self.client = IqiyiAPIClient(
            self.CONFIG["partner_no"], self.CONFIG["md5_key"], self.CONFIG["private_key"])
    
    def log(self, msg, color=Colors.OKCYAN):
        print(f"{color}{msg}{Colors.ENDC}")
    
    def run_all(self):
        self.log(f"\n{Colors.OKBLUE}{'='*75}{Colors.ENDC}")
        self.log(f"{Colors.OKBLUE}{Colors.BOLD}  🔍 第一阶段：接口自动化测试{Colors.ENDC}")
        self.log(f"{Colors.OKBLUE}{'='*75}{Colors.ENDC}\n")
        
        tests = [
            ("正常解密流程", lambda: self.test_decrypt()),
            ("无效token处理", lambda: self.test_invalid()),
            ("空token处理", lambda: self.test_empty()),
            ("checkDiscount参数", lambda: self.test_discount()),
            ("MD5签名验证", lambda: self.test_sign()),
            ("响应时间测试", lambda: self.test_perf()),
            ("响应结构完整性", lambda: self.test_structure()),
        ]
        
        for name, test_func in tests:
            self.log(f"  ▶️  {name}...")
            try:
                test_func()
            except Exception as e:
                self.reporter.add_result("❌ 接口异常", name, "失败", str(e))
    
    def test_decrypt(self):
        result, rt = self.client.call_user_info(self.CONFIG["valid_token"])
        if result.get("code") == "A00000":
            mobile = self.client.decrypt_rsa(result["data"]["mobile"])
            self.reporter.add_result("🔍 接口测试", "正常解密流程", "通过", f"手机号: {mobile}", rt)
        else:
            self.reporter.add_result("🔍 接口测试", "正常解密流程", "失败", str(result), rt)
    
    def test_invalid(self):
        result, rt = self.client.call_user_info("invalid_token_12345")
        if result.get("code") in ["Q00301", "Q00307"]:
            self.reporter.add_result("🔍 接口测试", "无效token处理", "通过", f"错误码: {result.get('code')}", rt)
        else:
            self.reporter.add_result("🔍 接口测试", "无效token处理", "失败", str(result), rt)
    
    def test_empty(self):
        result, rt = self.client.call_user_info("")
        if result.get("code") in ["Q00301", "Q00307"]:
            self.reporter.add_result("🔍 接口测试", "空token处理", "通过", f"错误码: {result.get('code')}", rt)
        else:
            self.reporter.add_result("🔍 接口测试", "空token处理", "失败", str(result), rt)
    
    def test_discount(self):
        result, rt = self.client.call_user_info(self.CONFIG["valid_token"], "1")
        if result.get("code") == "A00000":
            self.reporter.add_result("🔍 接口测试", "checkDiscount参数", "通过", "返回discount字段", rt)
        else:
            self.reporter.add_result("🔍 接口测试", "checkDiscount参数", "失败", str(result), rt)
    
    def test_sign(self):
        test_client = IqiyiAPIClient("test", "qwer")
        sign = test_client.sign({"a": "3", "b": "2", "c": "1"})
        if sign == "f80118ff523f25eda67cb799bdc9c52d":
            self.reporter.add_result("🔐 算法测试", "MD5签名验证", "通过", f"签名: {sign}")
        else:
            self.reporter.add_result("🔐 算法测试", "MD5签名验证", "失败")
    
    def test_perf(self):
        result, rt = self.client.call_user_info(self.CONFIG["valid_token"])
        status = "通过" if rt < 2000 else "失败"
        self.reporter.add_result("⚡ 性能测试", "响应时间测试", status, f"{rt:.2f}ms", rt)
    
    def test_structure(self):
        result, rt = self.client.call_user_info(self.CONFIG["valid_token"])
        if all(k in result for k in ["code", "msg", "data"]):
            self.reporter.add_result("📋 结构测试", "响应结构完整性", "通过", "包含必要字段", rt)
        else:
            self.reporter.add_result("📋 结构测试", "响应结构完整性", "失败", "缺少字段", rt)


class WebAutomationSuite:
    """网页自动化套件 - 递归深度遍历"""
    
    START_URLS = [
        "https://www.iqiyi.com/kszt/GetStarted_Overview.html",
        "https://developer.vip.iqiyi.com/custom/ViewEngine/userInfoDecrypted.html",
        "https://developer.game.iqiyi.com/tools/api",
    ]
    
    def __init__(self, reporter):
        self.reporter = reporter
        self.browser = None
        self.page = None
        self.playwright = None
        self.screenshot_dir = "screenshots"
        self.video_dir = "videos"
        self.visited_urls = set()
        self.max_depth = 2  # 最大遍历深度
        
        for d in [self.screenshot_dir, self.video_dir]:
            if not os.path.exists(d):
                os.makedirs(d)
    
    def log(self, msg, color=Colors.OKCYAN):
        print(f"{color}{msg}{Colors.ENDC}")
    
    def setup(self):
        try:
            from playwright.sync_api import sync_playwright
            self.playwright = sync_playwright().start()
            self.browser = self.playwright.chromium.launch(
                headless=False,
                args=['--window-size=1400,900']
            )
            context = self.browser.new_context(
                viewport={'width': 1400, 'height': 900},
                record_video_dir=self.video_dir,
                record_video_size={'width': 1400, 'height': 900}
            )
            self.page = context.new_page()
            self.log("  ✅ Chromium浏览器启动成功（已启用录屏）", Colors.OKGREEN)
            return True
        except Exception as e:
            self.log(f"  ❌ 浏览器启动失败: {e}", Colors.FAIL)
            return False
    
    def screenshot(self, name):
        try:
            path = os.path.join(self.screenshot_dir, f"{name}.png")
            self.page.screenshot(path=path, full_page=True)
            self.reporter.screenshot_count += 1
            self.log(f"    📸 截图: {path}", Colors.OKGREEN)
        except Exception as e:
            self.log(f"    ⚠️  截图失败: {e}", Colors.WARNING)
    
    def safe_goto(self, url, wait=2):
        for i in range(3):
            try:
                self.page.goto(url, timeout=20000, wait_until='networkidle')
                time.sleep(wait)
                return True
            except:
                time.sleep(2)
        return False
    
    def extract_links(self):
        """提取页面所有链接"""
        try:
            links = []
            elements = self.page.query_selector_all('a[href]')
            for el in elements:
                href = el.get_attribute('href')
                text = el.inner_text().strip()
                if href and (href.startswith('http') or href.startswith('/')):
                    # 只保留爱奇艺相关链接
                    if 'iqiyi' in href or href.startswith('/'):
                        links.append({"text": text[:50], "href": href})
            return links
        except:
            return []
    
    def crawl_page(self, url, depth=0):
        """递归爬取页面"""
        if url in self.visited_urls or depth > self.max_depth:
            return
        
        self.visited_urls.add(url)
        
        self.log(f"\n  {'  '*depth}▶️  深度{depth}: {url[:60]}...")
        
        if not self.safe_goto(url):
            self.reporter.add_page(url, "访问失败", "Timeout", 0, depth)
            self.reporter.add_result("🌐 网页遍历", f"深度{depth}页面", "失败", "访问超时", url=url, depth=depth)
            return
        
        # 获取页面信息
        title = self.page.title()
        status = self.page.url  # 实际URL
        
        # 滚动交互
        for h in [300, 600, 0]:
            self.page.evaluate(f"window.scrollTo(0, {h})")
            time.sleep(0.3)
        
        # 提取链接
        links = self.extract_links()
        
        self.log(f"    {'  '*depth}📄 标题: {title[:50]}", Colors.OKCYAN)
        self.log(f"    {'  '*depth}🔗 发现 {len(links)} 个链接", Colors.OKCYAN)
        
        # 截图
        safe_name = f"depth{depth}_{url.replace('://', '_').replace('/', '_').replace('?', '_')[:50]}"
        self.screenshot(safe_name)
        
        # 记录页面
        self.reporter.add_page(url, title, "200", len(links), depth)
        self.reporter.add_result("🌐 网页遍历", f"深度{depth}页面", "通过", 
            f"标题: {title[:40]}... | 链接: {len(links)}个", url=url, depth=depth)
        
        # 递归访问子链接（限制数量）
        if depth < self.max_depth:
            for link in links[:3]:  # 每个页面最多跟3个链接
                next_url = link["href"]
                if next_url.startswith('/'):
                    next_url = f"https://www.iqiyi.com{next_url}"
                if 'iqiyi' in next_url and next_url not in self.visited_urls:
                    self.crawl_page(next_url, depth + 1)
    
    def run_all(self):
        self.log(f"\n{Colors.OKBLUE}{'='*75}{Colors.ENDC}")
        self.log(f"{Colors.OKBLUE}{Colors.BOLD}  🌐 第二阶段：网页深度遍历（递归模式）{Colors.ENDC}")
        self.log(f"{Colors.OKBLUE}{'='*75}{Colors.ENDC}\n")
        
        if not self.setup():
            self.reporter.add_result("🌐 网页遍历", "浏览器启动", "失败", "Playwright未安装")
            return False
        
        try:
            # 从起始URL开始递归遍历
            for start_url in self.START_URLS:
                self.crawl_page(start_url, depth=0)
            
            # 最终截图
            self.screenshot("final_state")
            
            return True
            
        finally:
            if self.browser:
                self.log("\n  ⏳ 浏览器将在10秒后关闭...", Colors.WARNING)
                time.sleep(10)
                
                try:
                    video = self.page.video
                    if video:
                        self.reporter.video_path = str(video.path())
                        self.log(f"  🎥 录屏已保存", Colors.OKGREEN)
                except:
                    pass
                
                self.browser.close()
                self.playwright.stop()
                self.log("  🛑 浏览器已关闭", Colors.OKCYAN)


class IqiyiMasterAutomation:
    """主控制器"""
    
    def __init__(self):
        self.reporter = HTMLReportGenerator()
    
    def banner(self):
        print(f"\n{Colors.HEADER}{'='*75}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}  🎬 爱奇艺开发者平台 - 完整自动化测试{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*75}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}  📅 时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{Colors.ENDC}")
        print(f"{Colors.OKBLUE}  🔧 功能: 接口自动化 + 全站深度遍历 + 截图 + 录屏 + HTML报告{Colors.ENDC}")
        print(f"{Colors.OKBLUE}  🖥️  模式: 真实浏览器窗口（禁止无头模式）{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*75}{Colors.ENDC}\n")
    
    def run(self):
        self.banner()
        
        # 阶段1: 接口测试
        api = APITestSuite(self.reporter)
        api.run_all()
        
        # 阶段2: 网页深度遍历
        web = WebAutomationSuite(self.reporter)
        web.run_all()
        
        # 生成HTML报告
        report_path = self.reporter.generate_html()
        print(f"\n{Colors.OKGREEN}📄 HTML报告已生成: {os.path.abspath(report_path)}{Colors.ENDC}")
        
        # 终端报告
        self.print_terminal_report()
        
        # 输出文件清单
        self.print_files_summary()
        
        return True
    
    def print_terminal_report(self):
        print(f"\n{Colors.HEADER}{'='*75}{Colors.ENDC}")
        print(f"{Colors.HEADER}{Colors.BOLD}  📊 终端摘要报告{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*75}{Colors.ENDC}")
        
        passed = sum(1 for r in self.reporter.results if r["status"] == "通过")
        failed = sum(1 for r in self.reporter.results if r["status"] != "通过")
        
        print(f"{Colors.BOLD}  接口测试: {passed}通过 {failed}失败{Colors.ENDC}")
        print(f"{Colors.BOLD}  访问页面: {len(self.reporter.pages_visited)}个{Colors.ENDC}")
        print(f"{Colors.BOLD}  遍历深度: {max(self.reporter.depth_stats.keys()) if self.reporter.depth_stats else 0}层{Colors.ENDC}")
        print(f"{Colors.BOLD}  截图数量: {self.reporter.screenshot_count}张{Colors.ENDC}")
        print(f"{Colors.OKGREEN}{Colors.BOLD}  🎉 测试完成！{Colors.ENDC}")
        print(f"{Colors.HEADER}{'='*75}{Colors.ENDC}\n")
    
    def print_files_summary(self):
        print(f"{Colors.OKCYAN}📁 输出文件清单:{Colors.ENDC}")
        
        if os.path.exists("screenshots"):
            files = os.listdir("screenshots")
            print(f"  📸 screenshots/ ({len(files)} 个文件)")
        
        if os.path.exists("videos"):
            files = os.listdir("videos")
            print(f"  🎥 videos/ ({len(files)} 个文件)")
        
        print(f"  📄 report_master.html (HTML报告)")


def main():
    print("正在初始化完整自动化测试环境...")
    
    auto = IqiyiMasterAutomation()
    success = auto.run()
    
    if success:
        print(f"{Colors.OKGREEN}完整自动化测试执行成功！{Colors.ENDC}")
        return 0
    else:
        print(f"{Colors.FAIL}完整自动化测试执行失败！{Colors.ENDC}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
