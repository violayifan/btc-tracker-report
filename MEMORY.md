# MEMORY.md - Long-Term Memory

_This file stores distilled, curated memories that persist across sessions._

---

## Workspace Status

- **Last Updated**: 2026-03-08
- **Status**: Active workspace, regular BTC monitoring running, Arxiv daily analysis configured
- **Location**: /root/.openclaw/workspace

---

## Identity & Persona

**My Name**: Not yet chosen
**Creature**: AI assistant
**Vibe**: Helpful, direct, data-driven
**Emoji**: 

---

## Human Profile

- **Timezone**: GMT+8 (Asia/Shanghai)
- **Primary Interest**: AI stocks, Hong Kong market investing, High-frequency trading data
- **Investment Focus**: AI application companies, IPO analysis, earnings predictions, China commodity futures
- **Risk Tolerance**: Moderate, uses stop-loss and position sizing
- **Research Interests**: High-frequency market data, tick-by-tick order flow, CTP interface
- **Exchange Monitoring**: Interested in official exchange announcements (e.g., Binance announcements)

---

## Key Systems & Automation

### BTC Monitoring System
- **Script**: `btc_monitor.py` (basic), `btc_advanced_monitor_v2.py` (advanced)
- **Frequency**: Hourly via cron (`0 * * * *`)
- **Auto-update Script**: `auto_update.sh`
- **Reports**: Saved to `/root/.openclaw/workspace/reports/`
- **GitHub Integration**: Auto-commit and push to https://github.com/violayifan/btc-tracker-report
- **GitHub Pages**: https://violayifan.github.io/btc-tracker-report

### Arxiv Quant Daily Paper Analysis (NEW - 2026-03-08)
- **Script**: `arxiv_quant_daily.py`
- **Frequency**: Daily at 8 AM via cron (`0 8 * * *`)
- **Purpose**: Automatically fetch, analyze, and summarize top quant finance papers from arXiv
- **Workflow**:
  1. Searches arXiv API for q-fin.* category papers (20 most recent)
  2. Scores papers based on category, keywords, authors
  3. Selects highest-scoring paper
  4. Analyzes paper (extracts contributions, methodology, applications)
  5. Generates Markdown report
  6. Saves to knowledge base: `/root/.openclaw/workspace/knowledge_base/arxiv_quant/arxiv_quant_YYYYMMDD.md`
  7. [PENDING FIX] Creates Feishu document and sends to user
- **Status**: Paper search, analysis, knowledge base storage working; Feishu integration needs fix
- **Issue**: subprocess to openclaw command fails; need to use feishu_doc tool directly

### Data Source Status (2026-03-01)
- **KuCoin API**: ✅ Working reliably
- **Binance API**: ❌ Failing (response format exceptions)
- **OKX API**: ❌ Failing (response format exceptions)
- **K-line Data**: ❌ Failing (using simulated data as fallback)
- **Note**: Currently dependent on KuCoin API as single working source

### Deep Research Capability
- **Tool**: MiroMind AI (dr.miromind.ai)
- **Location**: `/opt/openclaw/skills/deepreseach-search-skill/`
- **Use Cases**: Multi-round web searches, complex analysis, market research
- **Output**: Markdown reports with citations

### Tavily Search API
- **API Key**: Configured and working
- **Key Location**: `/root/.openclaw/workspace/.tavily_api_key`
- **Search Script**: `/root/.openclaw/workspace/tavily_search.sh`
- **Usage**: For real-time news and web search
- **Configured**: 2026-03-01

---

## Investment Knowledge Base

### Hong Kong AI IPO Stocks (2025-2026 Wave)

**Core Three**:
1. **MiniMax (00100.HK)** - C-end application focused, 73% overseas revenue, highest growth
2. **Zhipu AI (02513.HK)** - B/G end enterprise solutions, GLM LLM series
3. **Yunzhisheng (09678.HK)** - Vertical AI solutions, voice/document intelligence

**Investment Themes**:
- C-end/Global: MiniMax, SenseTime, Kuaishou
- B/G Industrial: Zhipu AI, Yunzhisheng, Fourth Paradigm
- Vertical Applications: Yunzhisheng (voice/docs), SenseTime (vision)

### Valuation Paradigm Shift
- **Old Model**: Traditional PE/PB ratios
- **New Model**: PS (Price/Sales), Token usage, model status, global market share
- **Comparables**: OpenAI, Anthropic, Mistral (international LLM leaders)

### Capital Flow Patterns
- **Hong Kong AI Sector**: Institutional buying, retail selling at highs
- **Key Players**: Korean investors, Middle East sovereign funds (ADIA), US/EU tech funds
- **Behavior**: "Buy on dips, sell on rips" for retail; institutions accumulating

### China Commodity Futures High-Frequency Data
- **Data Availability**: Tick-by-tick order and execution data confirmed available
- **CTP Interface**: Official API provides millisecond-level real-time push
- **Exchanges**: SHFE, DCE, CZCE, INE, GFEX all support tick data via CTP
- **Data Types**: Tick orders (逐笔委托), Tick executions (逐笔成交), Level-2 depth
- **Access Methods**: CTP MD API (free with trading account), Commercial providers (Wind, iFind), VNPY (open-source)
- **Reference**: VNPY documentation at https://www.vnpy.com/docs/cn/community/info/gateway.html

---

## Risk Management Framework

### Earnings Trading Strategy
- **Heavy Position (>30%)**: Reduce by half pre-earnings, lock in gains
- **Moderate Position (10-30%)**: Hold with stop-loss, monitor capital flows
- **Light Position (<10%)**: Hold through earnings, risk manageable
- **Key Triggers**: Revenue expectations, gross margin trends, overseas revenue %, 2026 guidance

### Volatility Expectations
- **AI New Stocks**: Daily swings 10-20% common post-IPO
- **Earnings Events**: +15% to -25% move possible
- **Holding Period**: Short-medium term for catalyst trades

---

## Technical Capabilities

### Available Skills
- `feishu-doc`: Feishu document operations
- `feishu-drive`: Feishu cloud storage
- `feishu-wiki`: Feishu knowledge base
- `deepreseach-websearch`: MiroMind AI deep research
- `healthcheck`: Security hardening and risk assessment
- `weather`: Weather forecasts
- `skill-creator`: Create AgentSkills

### Channels
- **Primary**: Feishu (direct message)
- **Active**: Currently active in DM with user `ou_9cde50d77f516edcf3a661ca32f83b2a`

### Tool Configuration Status
- **Browser Control**: Requires gateway restart and Chrome extension tab attachment
- **Web Search**: Requires `BRAVE_API_KEY` configuration for web_search tool
- **Web Fetch**: Limited effectiveness on dynamic JavaScript-heavy sites (like Binance)

---

## Important Dates & Events

### Upcoming Events
- **2026-03-02**: MiniMax 2025 full year earnings (Hong Kong market close, 20:00 GMT+8 call)

---

## Lessons Learned

### Research Best Practices
- Use MiroMind AI for complex, multi-source market analysis
- Combine fundamentals, capital flows, sentiment for comprehensive view
- Provide scenario analysis (surprise/meet/miss) with probabilities
- Include risk warnings and position sizing guidance

### Communication Style
- Be direct, no filler, action-oriented
- Provide data first, then interpretation
- Include specific price targets and stop-loss levels
- Acknowledge uncertainty, use probabilities not predictions

---

## To Be Continued

_This file will evolve as more is learned. Update with new insights, patterns, and user preferences._
