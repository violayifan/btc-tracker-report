#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Playwright 自动化工具 - 用于访问和分析微信文章
"""

import subprocess
import sys
import json
import os
import tempfile
from pathlib import Path

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

    def _check_playwright(self):
        """检查playwright是否已安装"""
        try:
            result = subprocess.run(
                ["python3", "-c", "import playwright; print('installed')"],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0 and 'installed' in result.stdout:
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
        
        try:
            # 安装playwright
            result = subprocess.run(
                ["pip3", "install", "playwright"],
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            if result.returncode == 0:
                self.log("✅ Playwright 安装成功")
                
                # 安装浏览器
                result = subprocess.run(
                    ["playwright", "install", "chromium"],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    self.log("✅ Chromium 浏览器安装成功")
                    return True
                else:
                    self.log("⚠️ Chromium 浏览器安装失败，但Playwright已安装")
                    return True
            else:
                self.log(f"❌ Playwright 安装失败: {result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"❌ 安装Playwright异常: {str(e)}")
            return False

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
from playwright.async_api import async_playwright
import sys

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True, args=['--disable-blink-features=IdleControl'])
        page = await browser.new_page()
        
        try:
            print("正在访问页面...")
            await page.goto("{url}", wait_until="networkidle", timeout=60000)
            
            # 等待页面加载
            await asyncio.sleep(3)
            
            # 获取页面标题
            title = await page.title()
            print(f"页面标题: {{title}}")
            
            # 尝试获取文章内容
            content = await page.evaluate('''() => {{
                // 尝试多种方式获取文章内容
                let content = "";
                
                // 方法1: body
                const body = document.body;
                if (body) {{
                    content = body.innerText;
                }}
                
                // 方法2: article
                const article = document.querySelector('article, .article, #content');
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
            
            # 保存内容到文件
            import sys
            with open(sys.argv[1], 'w', encoding='utf-8') as f:
                f.write(title + "\\n\\n")
                f.write(content)
            
            print(f"文章内容已保存到: {{sys.argv[1]}}")
            
        except Exception as e:
            print(f"访问页面出错: {{str(e)}}")
            import traceback
            traceback.print_exc()
            
        finally:
            await browser.close()

asyncio.run(main())
"""
        
        script_file = self.temp_dir / "fetch_wechat.py"
        with open(script_file, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        self.log(f"✅ Playwright脚本已创建: {script_file}")
        
        # 创建输出文件
        output_file = self.temp_dir / "article_content.txt"
        
        try:
            result = subprocess.run(
                ["python3", str(script_file), str(output_file)],
                capture_output=True,
                text=True,
                timeout=120, # 2分钟超时
                cwd=str(self.temp_dir)
            )
            
            self.log(f"✅ Playwright执行完成")
            self.log(f"   标准输出: {result.stdout[:500] if result.stdout else 'None'}")
            self.log(f"   错误输出: {result.stderr[:500] if result.stderr else 'None'}")
            
            # 读取保存的内容
            if output_file.exists():
                with open(output_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.log(f"✅ 文章内容已保存，长度: {len(content)} 字符")
                
                return {
                    "success": True,
                    "title": "微信文章",
                    "content": content,
                    "length": len(content),
                    "output_file": str(output_file)
                }
            else:
                return {
                    "success": False,
                    "error": "输出文件未创建"
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

    def batch_fetch_articles(self, urls, output_prefix="article"):
        """批量获取多篇文章"""
        self.log(f"📚 开始批量获取 {len(urls)} 篇文章...")
        
        results = []
        for i, url in enumerate(urls, 1):
            self.log(f"📄 正在处理第 {i}/{len(urls)} 篇文章...")
            
            # 执行获取
            result = self.fetch_wechat_articles(url)
            
            if result.get('success'):
                results.append({
                    'index': i,
                    'url': url,
                    'title': result.get('title', '未知'),
                    'content': result.get('content', ''),
                    'length': result.get('length', 0),
                    'output_file': result.get('output_file', '')
                })
            else:
                results.append({
                    'index': i,
                    'url': url,
                    'error': result.get('error', '未知错误'),
                    'success': False
                })
            
            # 短暂延迟，避免请求过快
            import time
            time.sleep(2)
        
        self.log(f"✅ 批量获取完成")
        return results

    def analyze_batch_articles(self, articles):
        """批量分析文章"""
        self.log(f"📊 开始批量分析 {len(articles)} 篇文章...")
        
        analyzed_results = []
        
        for article in articles:
            if article.get('success') and article.get('content'):
                analysis = self.analyze_article(article['content'])
                analyzed_results.append({
                    'index': article['index'],
                    'url': article['url'],
                    'title': article['title'],
                    'analysis': analysis
                })
            else:
                analyzed_results.append({
                    'index': article['index'],
                    'url': article['url'],
                    'error': 'No content to analyze'
                })
        
        # 生成总结报告
        report = self._generate_batch_report(articles, analyzed_results)
        
        # 保存报告
        report_file = self.temp_dir / "analysis_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump({
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'total_articles': len(articles),
                'successful_fetches': len([r for r in results if r.get('success')]),
                'analysis_results': analyzed_results,
                'report': report
            }, f, ensure_ascii=False, indent=2)
        
        self.log(f"✅ 批量分析完成，报告已保存: {report_file}")
        
        return report

    def _generate_batch_report(self, articles, analyzed_results):
        """生成批量分析报告"""
        successful_analyses = [a for a in analyzed_results if a.get('analysis')]
        
        # 统计关键词
        keyword_stats = {}
        for analysis in successful_analyses:
            for category, word in analysis['analysis']['keywords']:
                key = f"{category}:{word}"
                keyword_stats[key] = keyword_stats.get(key, 0) + 1
        
        # 找出最常见的关键词
        top_keywords = sorted(keyword_stats.items(), key=lambda x: x[1], reverse=True)[:10]
        
        # 提取关键句子
        all_key_sentences = []
        for analysis in successful_analyses:
            all_key_sentences.extend(analysis['analysis']['key_sentences'])
        
        # 生成报告
        report = {
            'summary': {
                'total_articles': len(articles),
                'successful_analysis': len(successful_analyses),
                'top_keywords': top_keywords,
                'total_key_sentences': len(all_key_sentences)
            },
            'recommendations': self._generate_recommendations(successful_analyses),
            'detailed_analysis': successful_analyses
        }
        
        return report

    def _generate_recommendations(self, analyses):
        """生成实践建议"""
        recommendations = []
        
        # 统计主题
        categories = {}
        for analysis in analyses:
            for category, word in analysis['analysis']['keywords']:
                if category not in categories:
                    categories[category] = 0
                categories[category] += 1
        
        # 根据分析结果生成建议
        if categories.get('深度学习', 0) > 0:
            recommendations.append({
                'priority': 'high',
                'category': '技术',
                'title': '关注深度学习技术',
                'description': '多篇文章涉及深度学习，建议深入学习相关框架（PyTorch, TensorFlow）'
            })
        
        if categories.get('量化交易', 0) > 0:
            recommendations.append({
                'priority': 'high',
                'category': '应用',
                'title': '量化交易实践机会',
                'description': '文章包含量化交易内容，可考虑在实际交易中应用相关策略'
            })
        
        if categories.get('投资组合', 0) > 0:
            recommendations.append({
                'priority': 'medium',
                'category': '风险管理',
                'title': '投资组合管理建议',
                'description': '关注资产配置和风险分散的文章'
            })
        
        return recommendations

def main():
    """主函数"""
    wrapper = PlaywrightWrapper()
    
    # 检查参数
    if len(sys.argv) < 2:
        print("使用方法:")
        print("  安装 Playwright:")
        print("    python3 playwright_wrapper.py --install")
        print()
        print("  获取微信文章:")
        print("    python3 playwright_wrapper.py --fetch <url>")
        print()
        print("  批量获取文章:")
        print("    python3 playwright_wrapper.py --batch-fetch <url1,url2,url3>")
        print()
        print("  分析文章:")
        print("    python3 playwright_wrapper.py --analyze <content_file>")
        print()
        print("  完整流程（获取+分析）:")
        print("    python3 playwright_wrapper.py --full <url>")
        return
    
    command = sys.argv[1]
    
    if command == '--install':
        # 安装playwright
        success = wrapper.install_playwright()
        if success:
            print("✅ Playwright 安装完成")
        else:
            print("❌ Playwright 安装失败")
            return
    
    elif command == '--fetch':
        # 获取单篇文章
        url = sys.argv[2]
        result = wrapper.fetch_wechat_articles(url)
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return
    
    elif command == '--batch-fetch':
        # 批量获取文章
        urls = sys.argv[2].split(',')
        results = wrapper.batch_fetch_articles(urls)
        print(json.dumps(results, ensure_ascii=False, indent=2))
        return
    
    elif command == '--analyze':
        # 分析文章
        content_file = sys.argv[2]
        with open(content_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        summary = wrapper.analyze_article(content)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return
    
    elif command == '--full':
        # 完整流程：获取 + 分析
        url = sys.argv[2]
        
        # 获取文章
        wrapper.log("📄 开始完整流程：获取 + 分析")
        fetch_result = wrapper.fetch_wechat_articles(url)
        
        if fetch_result.get('success'):
            # 分析文章
            analysis = wrapper.analyze_article(fetch_result['content'])
            
            # 生成最终报告
            final_report = {
                'fetch_result': fetch_result,
                'analysis_result': analysis,
                'url': url,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            print(json.dumps(final_report, ensure_ascii=False, indent=2))
            
            # 保存报告
            report_file = wrapper.temp_dir / "full_report.json"
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(final_report, f, ensure_ascii=False, indent=2)
            
            wrapper.log(f"✅ 完整报告已保存: {report_file}")
        else:
            print(f"❌ 获取文章失败: {fetch_result.get('error')}")
            return

if __name__ == "__main__":
    from datetime import datetime
    main()
