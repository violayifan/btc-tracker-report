#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Arxiv 量化投资论文每日分析脚本
每天早上8点自动从arxiv.org挑选热门量化投资论文，分析并整理
"""

import requests
import feedparser
from datetime import datetime
import json
import os
import re
from pathlib import Path

class ArxivQuantDaily:
    def __init__(self):
        self.workspace = Path("/root/.openclaw/workspace")
        self.knowledge_base = self.workspace / "knowledge_base" / "arxiv_quant"
        self.knowledge_base.mkdir(parents=True, exist_ok=True)
        self.log_file = self.workspace / "arxiv_quant_daily.log"

        # Arxiv API 配置
        self.arxiv_base_url = "http://export.arxiv.org/api/query"
        # 使用通配符搜索 q-fin 分类下的所有子分类
        self.search_query = "cat:q-fin.*"
        self.max_results = 20  # 获取最近的20篇论文

        # 临时文件，用于与主会话交互
        self.temp_paper_data_file = self.workspace / "temp_arxiv_paper.json"
        self.temp_report_file = self.workspace / "temp_arxiv_report.md"

    def log(self, message):
        """记录日志"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] {message}\n"
        print(log_message.strip())
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(log_message)

    def search_arxiv_papers(self):
        """从 arXiv 搜索量化投资相关论文"""
        self.log("🔍 开始搜索 arXiv 论文...")

        # 直接使用搜索查询，不需要 all: 前缀
        params = {
            'search_query': self.search_query,
            'start': 0,
            'max_results': self.max_results,
            'sortBy': 'submittedDate',
            'sortOrder': 'descending'
        }

        try:
            response = requests.get(self.arxiv_base_url, params=params, timeout=30)
            response.raise_for_status()

            # 解析 Atom feed
            feed = feedparser.parse(response.content)
            papers = []

            for entry in feed.entries:
                paper = {
                    'id': entry.id.split('/')[-1],
                    'title': entry.title.strip(),
                    'authors': [author.name for author in entry.authors],
                    'summary': entry.summary.strip(),
                    'published': entry.published,
                    'url': entry.link,
                    'primary_category': entry.tags[0]['term'] if entry.tags else 'Unknown'
                }
                papers.append(paper)

            self.log(f"✅ 找到 {len(papers)} 篇相关论文")
            return papers

        except Exception as e:
            self.log(f"❌ 搜索 arXiv 论文失败: {str(e)}")
            return []

    def select_best_paper(self, papers):
        """从论文列表中挑选最热门/最重要的一篇"""
        if not papers:
            return None

        # 排序策略
        priority_keywords = [
            'deep learning', 'reinforcement learning', 'transformer',
            'attention', 'neural network', 'quantitative', 'algorithmic',
            'trading', 'portfolio', 'risk', 'forecasting', 'prediction'
        ]

        def score_paper(paper):
            score = 0

            # 类别得分
            if 'q-fin' in paper['primary_category']:
                score += 10
            elif 'cs.LG' in paper['primary_category'] or 'cs.AI' in paper['primary_category']:
                score += 5

            # 关键词得分
            title_lower = paper['title'].lower()
            for keyword in priority_keywords:
                if keyword in title_lower:
                    score += 3

            # 摘要关键词得分
            summary_lower = paper['summary'].lower()
            for keyword in priority_keywords:
                if keyword in summary_lower:
                    score += 2

            # 作者数量
            score += min(len(paper['authors']) * 0.5, 5)

            return score

        # 按得分排序
        scored_papers = [(paper, score_paper(paper)) for paper in papers]
        scored_papers.sort(key=lambda x: x[1], reverse=True)

        best_paper = scored_papers[0][0]
        self.log(f"✅ 选中论文: {best_paper['title']}")
        self.log(f"   得分: {scored_papers[0][1]}")
        self.log(f"   类别: {best_paper['primary_category']}")

        return best_paper

    def analyze_paper(self, paper):
        """分析论文内容"""
        self.log("📖 开始分析论文...")

        analysis = {
            'basic_info': {
                'title': paper['title'],
                'authors': paper['authors'],
                'published': paper['published'],
                'url': paper['url'],
                'category': paper['primary_category']
            },
            'summary': paper['summary'],
            'key_contributions': self._extract_key_contributions(paper),
            'methodology': self._extract_methodology(paper),
            'potential_applications': self._extract_applications(paper),
            'detailed_summary': self._generate_detailed_summary(paper),
            'evaluation': self._generate_evaluation(paper),
            'analysis_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        self.log("✅ 论文分析完成")
        return analysis

    def _extract_key_contributions(self, paper):
        """从摘要中提取关键贡献"""
        summary = paper['summary']
        contributions = []

        # 尝试提取不同类型的贡献
        patterns = [
            r'(?i)(?:we|this paper|our(?: method)? )\s+(?:propose|present|introduce|develop|show|demonstrate)\s+[^.]+\.',
            r'(?i)(?:our )?(?:approach|method|framework|model|system)\s+(?:achieves|provides|enables|delivers)\s+[^.]+\.',
            r'(?i)(?:the )?(?:main|key|primary)\s+(?:contribution|innovation|contribution)\s+(?:is|are|of)\s+[^.]+\.'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, summary)
            contributions.extend(matches)
            if len(contributions) >= 3:
                break

        # 如果没有找到足够多的贡献，使用摘要的前几句
        if len(contributions) < 3:
            sentences = summary.split('.')
            for sentence in sentences:
                if len(contributions) >= 3:
                    break
                if len(sentence.strip()) > 50:  # 只保留有意义的句子
                    contributions.append(sentence.strip())

        return contributions[:5] if contributions else ["见摘要部分"]

    def _extract_methodology(self, paper):
        """提取方法论信息"""
        summary = paper['summary'].lower()

        methods = []

        # 机器学习方法
        ml_methods = {
            'deep learning': '深度学习/神经网络',
            'neural network': '神经网络',
            'reinforcement learning': '强化学习',
            'machine learning': '机器学习',
            'supervised learning': '监督学习',
            'unsupervised learning': '无监督学习',
            'transformer': 'Transformer架构',
            'attention mechanism': '注意力机制',
            'rnn': '循环神经网络 (RNN)',
            'lstm': '长短期记忆网络 (LSTM)',
            'gru': '门控循环单元 (GRU)',
            'cnn': '卷积神经网络 (CNN)',
            'autoencoder': '自编码器',
            'gan': '生成对抗网络 (GAN)',
            'variational autoencoder': '变分自编码器 (VAE)',
        }

        # 量化金融方法
        quant_methods = {
            'time series': '时间序列分析',
            'portfolio': '投资组合优化',
            'risk management': '风险管理',
            'risk-adjusted': '风险调整',
            'sharpe ratio': '夏普比率优化',
            'sortino ratio': '索提诺比率',
            'maximum drawdown': '最大回撤',
            'value at risk': '风险价值 (VaR)',
            'expected shortfall': '预期损失 (ES)',
            'algorithmic trading': '算法交易',
            'high-frequency trading': '高频交易',
            'backtest': '回测分析',
            'benchmark': '基准测试',
            'out-of-sample': '样本外测试',
            'in-sample': '样本内测试',
        }

        # 其他方法
        other_methods = {
            'forecasting': '预测模型',
            'prediction': '预测',
            'classification': '分类任务',
            'regression': '回归分析',
            'clustering': '聚类分析',
            'anomaly detection': '异常检测',
        }

        # 检查所有方法
        all_methods = {}
        all_methods.update(ml_methods)
        all_methods.update(quant_methods)
        all_methods.update(other_methods)

        for keyword, method_name in all_methods.items():
            if keyword in summary:
                if method_name not in methods:
                    methods.append(method_name)

        return methods if methods else ['见论文详细内容']

    def _extract_applications(self, paper):
        """提取潜在应用"""
        summary = paper['summary'].lower()
        title = paper['title'].lower()

        applications = []

        app_keywords = {
            'trading': '量化交易',
            'algorithmic trading': '算法交易',
            'high-frequency trading': '高频交易',
            'portfolio management': '投资组合管理',
            'portfolio optimization': '投资组合优化',
            'risk management': '风险管理',
            'risk control': '风险控制',
            'asset pricing': '资产定价',
            'market analysis': '市场分析',
            'market prediction': '市场预测',
            'price forecasting': '价格预测',
            'volatility forecasting': '波动率预测',
            'credit risk': '信用风险',
            'fraud detection': '欺诈检测',
            'market making': '做市商策略',
            'execution': '交易执行',
            'order routing': '订单路由',
        }

        for keyword, app_name in app_keywords.items():
            if keyword in summary or keyword in title:
                if app_name not in applications:
                    applications.append(app_name)

        return applications if applications else ['量化金融研究']

    def _generate_detailed_summary(self, paper):
        """生成详细的论文总结"""
        summary = paper['summary']
        title = paper['title']

        # 提取关键信息
        detailed = {
            'research_objective': self._extract_research_objective(summary),
            'approach': self._extract_approach(summary),
            'key_findings': self._extract_key_findings(summary),
            'data_and_scope': self._extract_data_and_scope(summary),
            'limitations': self._extract_limitations(summary)
        }

        return detailed

    def _extract_research_objective(self, summary):
        """提取研究目标"""
        objectives = []

        patterns = [
            r'(?i)we\s+(?:aim to|seek to|investigate|study|explore|examine)\s+[^.]+\.',
            r'(?i)this paper\s+(?:aims to|investigates|studies|explores|examines)\s+[^.]+\.',
            r'(?i)our\s+(?:goal|objective|aim)\s+is\s+to\s+[^.]+\.'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, summary)
            objectives.extend(matches)
            if objectives:
                break

        return objectives[0] if objectives else "研究量化投资相关的理论和方法问题"

    def _extract_approach(self, summary):
        """提取研究方法/方法学"""
        # 查找描述方法的句子
        sentences = summary.split('.')
        approach_sentences = []

        approach_keywords = ['method', 'approach', 'framework', 'model', 'algorithm',
                          'technique', 'strategy', 'architecture', 'system']

        for sentence in sentences:
            for keyword in approach_keywords:
                if keyword in sentence.lower() and len(sentence) > 50:
                    approach_sentences.append(sentence.strip())
                    break

        return approach_sentences[:2] if approach_sentences else ["见论文详细内容"]

    def _extract_key_findings(self, summary):
        """提取关键发现"""
        findings = []

        patterns = [
            r'(?i)we\s+(?:find|observe|show|demonstrate|reveal)\s+[^.]+\.',
            r'(?i)our\s+(?:results?|finding|analysis)\s+(?:show|indicate|reveal|demonstrate)\s+[^.]+\.',
            r'(?i)the\s+(?:results?|findings?)\s+(?:show|indicate|reveal|demonstrate)\s+[^.]+\.'
        ]

        for pattern in patterns:
            matches = re.findall(pattern, summary)
            findings.extend(matches)
            if len(findings) >= 2:
                break

        return findings[:3] if findings else ["见论文详细内容"]

    def _extract_data_and_scope(self, summary):
        """提取数据和研究范围"""
        data_info = []

        # 查找数据相关的内容
        sentences = summary.split('.')
        data_sentences = []

        data_keywords = ['data', 'dataset', 'sample', 'period', 'year', 'range',
                        'futures', 'stocks', 'equity', 'bond', 'fx', 'commodity']

        for sentence in sentences:
            for keyword in data_keywords:
                if keyword in sentence.lower() and len(sentence) > 30:
                    data_sentences.append(sentence.strip())
                    break

        return data_sentences[:2] if data_sentences else ["见论文详细内容"]

    def _extract_limitations(self, summary):
        """提取研究局限性"""
        # 查找局限性的内容
        sentences = summary.split('.')
        limitation_sentences = []

        limitation_keywords = ['limitation', 'constraint', 'challenge', 'drawback',
                           'however', 'although', 'despite', 'nevertheless']

        for sentence in sentences:
            for keyword in limitation_keywords:
                if keyword in sentence.lower() and len(sentence) > 30:
                    limitation_sentences.append(sentence.strip())
                    break

        return limitation_sentences[:2] if limitation_sentences else ["基于论文摘要无法判断"]

    def _generate_evaluation(self, paper):
        """生成论文评价"""
        summary = paper['summary']
        title = paper['title']

        evaluation = {
            'innovation': self._evaluate_innovation(summary),
            'practical_value': self._evaluate_practical_value(summary),
            'theoretical_contribution': self._evaluate_theoretical_contribution(summary),
            'data_quality': self._evaluate_data_quality(summary),
            'applicability': self._evaluate_applicability(summary),
            'overall_rating': self._calculate_overall_rating(summary)
        }

        return evaluation

    def _evaluate_innovation(self, summary):
        """评估创新性"""
        innovation_indicators = ['novel', 'innovative', 'new', 'first', 'original',
                               'breakthrough', 'groundbreaking', 'pioneering']

        score = 0
        for indicator in innovation_indicators:
            if indicator in summary.lower():
                score += 1

        if score >= 2:
            return "高 - 提出了新的方法或框架，具有创新性"
        elif score == 1:
            return "中 - 在现有方法基础上有所改进"
        else:
            return "一般 - 主要是对现有方法的应用或比较"

    def _evaluate_practical_value(self, summary):
        """评估实用价值"""
        practical_keywords = ['real-world', 'practical', 'application', 'implement',
                           'deploy', 'industry', 'trading', 'portfolio', 'risk']

        score = sum(1 for keyword in practical_keywords if keyword in summary.lower())

        if score >= 4:
            return "高 - 具有很强的实际应用价值"
        elif score >= 2:
            return "中 - 有一定的实用价值"
        else:
            return "一般 - 主要是理论性研究"

    def _evaluate_theoretical_contribution(self, summary):
        """评估理论贡献"""
        theory_keywords = ['theoretical', 'framework', 'model', 'formal', 'proof',
                         'theorem', 'convergence', 'optimality']

        score = sum(1 for keyword in theory_keywords if keyword in summary.lower())

        if score >= 3:
            return "高 - 提出了重要的理论框架或模型"
        elif score >= 1:
            return "中 - 有一定的理论贡献"
        else:
            return "一般 - 主要是实证研究"

    def _evaluate_data_quality(self, summary):
        """评估数据质量"""
        data_indicators = ['large-scale', 'comprehensive', 'comprehensive',
                          'diverse', 'multiple', 'various', 'extensive',
                          '2010', '2015', '2020', '2025']  # 时间跨度

        score = sum(1 for indicator in data_indicators if indicator in summary.lower())

        if score >= 3:
            return "高 - 使用了大规模、多样化的数据集"
        elif score >= 1:
            return "中 - 数据集较为充分"
        else:
            return "无法判断 - 摘要中未详细描述数据"

    def _evaluate_applicability(self, summary):
        """评估适用性"""
        applicability_keywords = ['out-of-sample', 'robust', 'generalize',
                                'applicable', 'scalable', 'adaptable']

        score = sum(1 for keyword in applicability_keywords if keyword in summary.lower())

        if score >= 2:
            return "高 - 模型具有较好的泛化能力"
        elif score == 1:
            return "中 - 模型有一定的适用性"
        else:
            return "一般 - 需要进一步验证泛化能力"

    def _calculate_overall_rating(self, summary):
        """计算综合评分"""
        # 基于关键词的简单评分
        high_value_keywords = ['outperform', 'superior', 'significant', 'substantial',
                            'improvement', 'better', 'exceed']

        score = sum(1 for keyword in high_value_keywords if keyword in summary.lower())

        if score >= 3:
            return "⭐⭐⭐⭐⭐ 优秀 - 强烈推荐阅读"
        elif score >= 2:
            return "⭐⭐⭐⭐ 良好 - 值得参考"
        elif score >= 1:
            return "⭐⭐⭐ 一般 - 可以了解"
        else:
            return "⭐⭐ 较低 - 按需阅读"

    def generate_markdown(self, analysis):
        """生成 Markdown 文档"""
        date_str = datetime.now().strftime("%Y-%m-%d")

        md_content = f"""# Arxiv 量化投资论文日报 - {date_str}

## 📄 论文基本信息

**标题**: {analysis['basic_info']['title']}

**作者**: {', '.join(analysis['basic_info']['authors'][:5])}
{', '.join(analysis['basic_info']['authors'][5:]) if len(analysis['basic_info']['authors']) > 5 else ''}

**发布时间**: {analysis['basic_info']['published']}

**论文类别**: {analysis['basic_info']['category']}

**论文链接**: {analysis['basic_info']['url']}

**PDF链接**: {analysis['basic_info']['url'].replace('abs', 'pdf')}.pdf

**分析时间**: {analysis['analysis_date']}

---

## 📝 论文摘要

{analysis['summary']}

---

## 🎯 关键贡献

"""

        for i, contribution in enumerate(analysis['key_contributions'], 1):
            md_content += f"{i}. {contribution.strip()}\n"

        md_content += f"""
---

## 🔬 研究方法

"""

        for method in analysis['methodology']:
            md_content += f"- {method}\n"

        md_content += f"""

---

## 💡 潜在应用

"""

        for app in analysis['potential_applications']:
            md_content += f"- {app}\n"

        md_content += f"""

---

## 📊 详细总结

### 研究目标

{analysis['detailed_summary']['research_objective']}

### 研究方法/方法学

"""

        for approach in analysis['detailed_summary']['approach']:
            md_content += f"{approach}\n\n"

        md_content += f"""### 关键发现

"""

        for finding in analysis['detailed_summary']['key_findings']:
            md_content += f"- {finding}\n"

        md_content += f"""

### 数据和研究范围

"""

        for data_info in analysis['detailed_summary']['data_and_scope']:
            md_content += f"{data_info}\n\n"

        md_content += f"""### 研究局限性

"""

        for limitation in analysis['detailed_summary']['limitations']:
            md_content += f"- {limitation}\n"

        md_content += f"""

---

## 🏆 论文评价

### 创新性
**评价**: {analysis['evaluation']['innovation']}

### 实用价值
**评价**: {analysis['evaluation']['practical_value']}

### 理论贡献
**评价**: {analysis['evaluation']['theoretical_contribution']}

### 数据质量
**评价**: {analysis['evaluation']['data_quality']}

### 适用性
**评价**: {analysis['evaluation']['applicability']}

### 综合评分
**{analysis['evaluation']['overall_rating']}**

---

## 📖 阅读建议

**适合人群**:
"""

        for app in analysis['potential_applications']:
            md_content += f"- {app}从业者\n"

        md_content += f"""
- 量化金融研究人员
- 金融科技工程师

**阅读重点**:
- 论文摘要和引言（了解研究背景）
- 方法论部分（理解核心创新）
- 实验结果（评估实际效果）
- 结论部分（了解未来研究方向）

**预期收获**:
- 了解最新的量化金融研究进展
- 学习新的方法和技术
- 获取实践应用的灵感
- 发现新的研究机会

---

## ⚠️ 注意事项

1. 本报告主要基于论文摘要进行分析，完整理解需要阅读全文
2. 论文的实际效果需要在实际场景中验证
3. 不同市场环境下，模型的适用性可能有所不同
4. 建议结合自身需求，评估论文的实用价值

---

*本报告由自动化系统生成，仅供参考。*
"""

        return md_content

    def save_to_knowledge_base(self, content, paper_title):
        """保存到知识库"""
        date_str = datetime.now().strftime("%Y%m%d")
        filename = f"arxiv_quant_{date_str}.md"
        filepath = self.knowledge_base / filename

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            self.log(f"✅ 文档已保存到知识库: {filepath}")
            return filepath
        except Exception as e:
            self.log(f"❌ 保存到知识库失败: {str(e)}")
            return None

    def save_temp_files(self, analysis, md_content):
        """保存临时文件供主会话使用"""
        # 保存论文数据
        try:
            with open(self.temp_paper_data_file, 'w', encoding='utf-8') as f:
                json.dump(analysis, f, ensure_ascii=False, indent=2)
            self.log(f"✅ 临时论文数据已保存: {self.temp_paper_data_file}")
        except Exception as e:
            self.log(f"❌ 保存临时论文数据失败: {str(e)}")

        # 保存 Markdown 报告
        try:
            with open(self.temp_report_file, 'w', encoding='utf-8') as f:
                f.write(md_content)
            self.log(f"✅ 临时报告已保存: {self.temp_report_file}")
        except Exception as e:
            self.log(f"❌ 保存临时报告失败: {str(e)}")

    def run(self):
        """执行完整流程"""
        self.log("=" * 60)
        self.log("🚀 Arxiv 量化投资论文日报任务开始")
        self.log("=" * 60)

        # 1. 搜索论文
        papers = self.search_arxiv_papers()
        if not papers:
            self.log("❌ 未找到论文，任务结束")
            return False, None, None

        # 2. 选择最佳论文
        best_paper = self.select_best_paper(papers)
        if not best_paper:
            self.log("❌ 未选中论文，任务结束")
            return False, None, None

        # 3. 分析论文
        analysis = self.analyze_paper(best_paper)

        # 4. 生成 Markdown
        md_content = self.generate_markdown(analysis)
        self.log("✅ Markdown 文档生成完成")

        # 5. 保存到知识库
        kb_path = self.save_to_knowledge_base(md_content, best_paper['title'])
        if not kb_path:
            self.log("⚠️ 知识库保存失败")

        # 6. 保存临时文件
        self.save_temp_files(analysis, md_content)

        # 总结
        self.log("=" * 60)
        self.log("✅ 任务完成")
        self.log(f"📄 论文: {best_paper['title']}")
        self.log(f"💾 知识库: {kb_path}")
        self.log(f"📝 临时文件已保存，等待主会话创建飞书文档")
        self.log("=" * 60)

        return True, analysis, md_content


def main():
    """主函数"""
    analyzer = ArxivQuantDaily()
    success, analysis, md_content = analyzer.run()

    if success:
        print("\n✅ Arxiv 量化投资论文日报任务执行成功")
        print("📝 临时文件已保存，请由主会话创建飞书文档并发送")
        exit(0)
    else:
        print("\n❌ Arxiv 量化投资论文日报任务执行失败")
        exit(1)


if __name__ == "__main__":
    main()
