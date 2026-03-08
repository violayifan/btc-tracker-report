#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Playwright 自动化工具 - Python 3.6 兼容版本
修复了 subprocess.run() 兼容性问题
"""

import subprocess
import sys
import json
import os
import tempfile
from pathlib import Path
from datetime import datetime

class PlaywrightWrapper:
    def __init__(self):
        self.workspace = Path("/root/.openclaw/workspace")
        self.log_file = self.workspace / "playwright_wrapper.log"

        # 检查playwright是否已安装
        self.playwright_installed = self._check_playwright()

        # 临时文件目录
        self.temp_dir = self.workspace / "temp_playwright"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        print(log_message.strip())
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message)

    def _run_command(self, cmd, cwd=None, timeout=60):
        """Python 3.6 兼容的命令执行"""
        try:
            # 使用 subprocess.Popen 而不是 subprocess.run()
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                universal_newlines=True,
                cwd=cwd
            )

            # 使用 communicate() 获取输出
            stdout, stderr = proc.communicate(timeout=timeout)

            if proc.returncode == 0:
                return {
                    "success": True,
                    "stdout": stdout,
                    "stderr": stderr
                }
            else:
                return {
                    "success": False,
                    "error": f"Command failed with return code {proc.returncode}",
                    "stdout": stdout,
                    "stderr": stderr
                }

        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "error": f"Command timeout after {timeout} seconds"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _check_playwright(self):
        """检查playwright是否已安装"""
        try:
            result = self._run_command(
                ["python3", "-c", "import playwright; print('installed')"],
                timeout=10
            )

            if result["success"] and 'installed' in result["stdout"]:
                self.log("✅ Playwright 已安装")
                return True
            else:
                self.log("❌ Playwright 未正确安装")
                return False

        except Exception as e:
            self.log(f"❌ 检查Playwright失败: {str(e)}")
            return False

    def install_playwright(self):
        """安装playwright"""
        self.log("📦 开始安装 Playwright...")

        # 安装playwright
        install_result = self._run_command(
            ["pip3", "install", "playwright"],
            timeout=300
        )

        if not install_result["success"]:
            self.log(f"❌ Playwright 安装失败: {install_result['error']}")
            return False

        self.log("✅ Playwright 安装成功")

        # 安装浏览器
        browser_result = self._run_command(
            ["playwright", "install", "chromium"],
            timeout=300
        )

        if browser_result["success"]:
            self.log("✅ Chromium 浏览器安装成功")
        else:
            self.log("⚠️ Chromium 浏览器安装失败，但Playwright已安装")

        return True

    def fetch_wechat_articles(self, url):
        """使用playwright访问微信文章"""
        self.log(f"🔍 开始访问微信文章: {url}")

        if not self.playwright_installed:
            success = self.install_playwright()
            if not success:
                return {"success": False, "error": "Playwright安装失败"}

        # 创建playwright脚本
        script_content = f"""
import asyncio
import sys
import json

async def main():
    try:
        from playwright.async_api import async_playwright

        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, args=['--disable-blink-features=IdleControl'])
            page = await browser.new_page()

            try:
                print("正在访问页面...")
                await page.goto("{url}", wait_until="networkidle", timeout=60000)

                # 等待页面加载
                await asyncio.sleep(3)

                # 尝试获取页面标题
                title = await page.title()
                print(f"页面标题: {{title}}")

                # 尝试多种方式获取文章内容
                content = await page.evaluate('''() => {{
                    // 尝试多种方式获取文章内容
                    let content = "";

                    // 方法1: body
                    const body = document.body;
                    if (body) {{
                        content = body.innerText;
                    }}

                    // 方法2: article
                    const article = document.querySelector('article, .article, #content, .weui-msg_article');
                    if (article) {{
                        content = article.innerText;
                    }}

                    // 方法3: wechat_article
                    const wechatArticle = document.querySelector('.weui-msg_article, .weui-msg_article__content');
                    if (wechatArticle) {{
                        content = wechatArticle.innerText;
                    }}

                    return content;
                }}''')

                print(f"获取到内容长度: {{len(content)}}")
                print(f"内容预览: {{content[:500]}}")

                # 将内容保存到文件
                content = {{
                    "title": title,
                    "content": content,
                    "url": "{url}",
                    "timestamp": "{datetime.now().isoformat()}"
                }}

                # 保存到标准输出
                print("---CONTENT_START---")
                print(json.dumps(content, ensure_ascii=False))
                print("---CONTENT_END---")

            except Exception as e:
                print(f"访问页面出错: {{str(e)}}")
                import traceback
                traceback.print_exc()

            finally:
                await browser.close()

    except Exception as e:
        print(f"Playwright初始化失败: {{str(e)}}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    asyncio.run(main())
"""
        script_file = self.temp_dir / "fetch_wechat_v2.py"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)

        self.log(f"✅ Playwright脚本已创建: {script_file}")

        # 创建输出文件
        output_file = self.temp_dir / "article_content.json"

        try:
            # 运行脚本
            result = self._run_command(
                ["python3", str(script_file)],
                cwd=str(self.temp_dir),
                timeout=120  # 2分钟超时
            )

            # 解析输出
            if result["success"]:
                stdout = result["stdout"]
                content_data = None

                # 查找内容开始和结束标记
                content_start = "---CONTENT_START---"
                content_end = "---CONTENT_END---"

                if content_start in stdout and content_end in stdout:
                    # 提取JSON内容
                    start_idx = stdout.find(content_start) + len(content_start)
                    end_idx = stdout.find(content_end)

                    if start_idx > 0 and end_idx > start_idx:
                        json_str = stdout[start_idx:end_idx]
                        try:
                            content_data = json.loads(json_str)
                            self.log(f"✅ 文章内容已解析: {len(content_data.get('content', ''))} 字符")
                        except Exception as e:
                            self.log(f"⚠️ JSON解析失败: {str(e)}")

                # 保存输出
                if content_data:
                    with open(output_file, 'w', encoding='utf-8') as f:
                        f.write(json.dumps(content_data, ensure_ascii=False, indent=2))
                    self.log(f"✅ 文章内容已保存: {output_file}")

                    return {
                        "success": True,
                        "title": content_data.get('title', '未知'),
                        "content": content_data.get('content', ''),
                        "length": len(content_data.get('content', '')),
                        "url": content_data.get('url', ''),
                        "output_file": str(output_file)
                    }
                else:
                    return {
                        "success": False,
                        "error": "无法解析文章内容"
                    }
            else:
                self.log(f"⚠️ 输出中未找到内容标记")
                return {
                    "success": False,
                    "error": "无法解析文章内容"
                }

        except Exception as e:
            self.log(f"❌ Playwright执行失败: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }

    def analyze_article(self, content):
        """分析文章内容"""
        self.log("📖 开始分析文章内容...")

        # 简单的关键词分析
        keywords = {
            '深度学习': ['deep learning', 'neural network', 'transformer', 'lstm', 'gru'],
            '强化学习': ['reinforcement learning', 'rl', 'q-learning'],
            '机器学习': ['machine learning', 'ml', 'supervised learning', 'unsupervised learning'],
            '时间序列': ['time series', 'forecasting', 'prediction', 'anomaly detection'],
            '投资组合': ['portfolio', 'asset allocation', 'risk management', 'optimization'],
            '量化交易': ['quantitative trading', 'algorithmic trading', 'high-frequency trading'],
            '金融': ['finance', 'financial', 'econometrics', 'asset pricing']
        }

        found_keywords = []
        content_lower = content.lower()

        for category, words in keywords.items():
            for word in words:
                if word in content_lower:
                    found_keywords.append((category, word))

        # 提取关键句子
        sentences = content.split('。')
        key_sentences = []

        # 寻找包含重要关键词的句子
        important_patterns = ['认为', '提出', '发现', '研究', '分析', '结果表明', '实验显示', '本文', '方法']

        for sentence in sentences:
            if any(pattern in sentence for pattern in important_patterns):
                if len(sentence) > 10:
                    key_sentences.append(sentence.strip())
                    if len(key_sentences) >= 3:
                        break

        # 生成总结
        summary = {
            'title': '微信文章分析',
            'keywords': found_keywords,
            'key_sentences': key_sentences,
            'content_length': len(content),
            'analysis_timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.log(f"✅ 文章分析完成")
        self.log(f"   找到关键词: {len(found_keywords)} 个")
        self.log(f"   关键句子: {len(key_sentences)} 个")

        return summary

    def run_full_process(self, url):
        """执行完整流程：获取 + 分析"""
        self.log(f"🚀 开始完整流程: 获取并分析微信文章")

        # 获取文章
        fetch_result = self.fetch_wechat_articles(url)

        if not fetch_result.get('success'):
            self.log(f"❌ 获取文章失败: {fetch_result.get('error')}")
            return {
                "success": False,
                "error": fetch_result.get('error'),
                "fetch_result": fetch_result
            }

        # 分析文章
        if fetch_result.get('content'):
            analysis = self.analyze_article(fetch_result['content'])

            # 生成最终报告
            final_report = {
                'fetch_result': fetch_result,
                'analysis_result': analysis,
                'url': url,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }

            # 保存报告
            report_file = self.temp_dir / "full_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(final_report, f, ensure_ascii=False, indent=2)

            self.log(f"✅ 完整报告已保存: {report_file}")

            return {
                "success": True,
                "final_report": final_report,
                "report_file": str(report_file)
            }
        else:
            return {
                "success": False,
                "error": "No content to analyze",
                "fetch_result": fetch_result
            }

    def run(self):
        """主函数"""
        cmd = sys.argv[1] if len(sys.argv) > 1 else '--help'

        if cmd == '--help':
            self.print_help()
            return

        elif cmd == '--install':
            # 安装playwright
            success = self.install_playwright()
            if success:
                print("✅ Playwright 安装完成")
            else:
                print("❌ Playwright 安装失败")
            return

        elif cmd == '--fetch':
            # 获取单篇文章
            url = sys.argv[2] if len(sys.argv) > 2 else ''
            if not url:
                print("❌ 请提供URL")
                return

            result = self.fetch_wechat_articles(url)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        elif cmd == '--analyze':
            # 分析文章内容
            content_file = sys.argv[2] if len(sys.argv) > 2 else ''
            if not content_file or not Path(content_file).exists():
                print("❌ 文件不存在")
                return

            with open(content_file, 'r', encoding='utf-8') as f:
                content = f.read()

            analysis = self.analyze_article(content)
            print(json.dumps(analysis, ensure_ascii=False, indent=2))

        elif cmd == '--full':
            # 完整流程：获取 + 分析
            url = sys.argv[2] if len(sys.argv) > 2 else ''
            if not url:
                print("❌ 请提供URL")
                return

            result = self.run_full_process(url)
            print(json.dumps(result, ensure_ascii=False, indent=2))

        else:
            print("❌ 未知命令")
            self.print_help()

    def print_help(self):
        """打印帮助信息"""
        print("""
使用方法:
  安装 Playwright:
    python3 playwright_wrapper.py --install

  获取微信文章:
    python3 playwright_wrapper.py --fetch <url>

  分析文章内容:
    python3 playwright_wrapper.py --analyze <content_file>

  完整流程（获取 + 分析）:
    python3 playwright_wrapper.py --full <url>

示例:
  python3 playwright_wrapper.py --install
  python3 playwright_wrapper.py --fetch "https://mp.weixin.qq.com/..."
  python3 playwright_wrapper.py --full "https://mp.weixin.qq.com/..."
""")

def main():
    """主函数"""
    wrapper = PlaywrightWrapper()
    wrapper.run()

if __name__ == "__main__":
    main()
