#!/usr/bin/env python3
"""
飞书 Webhook 配置指南生成器
"""

def generate_webhook_guide():
    """生成详细的 Webhook 配置指南"""
    
    guide = """
================================================================================
📚 飞书机器人 Webhook 配置指南
================================================================================

## 步骤 1：创建飞书机器人

### 1.1 访问飞书开发者后台
   - 打开浏览器，访问：https://open.feishu.cn/app
   - 使用飞书账号登录

### 1.2 创建企业自建应用
   - 点击"创建企业自建应用"
   - 填写应用信息：
     * 应用名称：BTC 交易监控机器人
     * 应用描述：自动发送 BTC 市场分析报告
     * 应用图标：（可选）上传图标

### 1.3 创建机器人
   - 在应用详情页，点击"添加机器人"
   - 配置机器人信息：
     * 机器人名称：BTC 交易助手
     * 机器人描述：实时发送 BTC 交易分析
     * 机器人头像：（可选）
   - 点击"确定"创建机器人

## 步骤 2：获取 App ID 和 App Secret

### 2.1 查看 App ID
   - 在应用详情页，顶部显示"App ID"
   - 格式类似：cli_a91d8cf269389bb5
   - **复制这个 ID**，需要在服务器配置中使用

### 2.2 生成 App Secret
   - 在应用详情页，找到"App Secret"部分
   - 点击"生成新的 App Secret"
   - **注意：** 只能查看一次，请务必复制保存
   - 格式类似：Ay4g0buBR9...
   - **复制这个 Secret**，需要在服务器配置中使用

## 步骤 3：配置机器人权限

### 3.1 添加机器人到群聊
   - 在飞书中打开或创建一个群聊
   - 点击群聊设置 -> 群机器人 -> 添加机器人
   - 搜索刚才创建的机器人名称
   - 点击添加
   - 设置机器人的昵称（可选）：BTC 监控助手

### 3.2 配置机器人权限
   在群机器人设置中，确保勾选以下权限：
   
   ✅ 发送消息
   ✅ 上传图片
   ✅ 获取群信息
   ✅ 获取群成员信息
   ✅ 获取消息
   
   保存设置

## 步骤 4：配置 Webhook（推荐方式）

### 4.1 进入 Webhook 配置
   - 回到飞书开发者后台
   - 打开刚创建的应用
   - 在左侧导航栏找到"事件订阅"
   - 或找到"添加事件"

### 4.2 生成 Webhook URL（两种方式）

   方式 A：使用 App ID（推荐）
   - URL 格式：https://open.feishu.cn/open-apis/bot/v2/hook/{你的APP_ID}
   - 示例：https://open.feishu.cn/open-apis/bot/v2/hook/cli_a91d8cf269389bb5
   - 优点：简单，不需要签名
   - 缺点：需要在飞书后台配置 URL

   方式 B：使用 Tenant Access Token
   - 需要使用 App ID 和 App Secret 生成 Token
   - Token 格式：{APP_ID}.{SIGN}.{TIMESTAMP}
   - 签名算法：SHA256(APP_ID + APP_SECRET + TIMESTAMP)
   - URL 格式：https://open.feishu.cn/open-apis/bot/v2/hook/{TOKEN}
   - 优点：更安全，支持更多功能
   - 缺点：配置复杂

### 4.3 配置事件订阅
   在事件订阅页面，选择需要接收的事件：
   
   ✅ 接收群消息
   ✅ 接收私聊消息
   ✅ 机器人进入群
   ✅ 添加机器人到群
   ✅ 删除机器人出群

### 4.4 复制 Webhook URL
   - 复制生成的 Webhook URL
   - 格式类似：https://open.feishu.cn/open-apis/bot/v2/hook/...
   - 保存到安全位置

## 步骤 5：在服务器上配置 Webhook

### 5.1 创建配置文件
   在服务器上创建配置文件：
   
   vim /root/.openclaw/openclaw.json
   
   添加以下内容：
   {
     "channels": {
       "feishu": {
         "appId": "你的APP_ID",
         "appSecret": "你的APP_SECRET",
         "webhook_url": "你的WEBHOOK_URL",
         "user_id": "ou_9cde50d77f516edcf3a661ca32f83b2a"
       }
     }
   }

   替换内容：
   - 你的APP_ID：cli_a91d8cf269389bb5（实际值）
   - 你的APP_SECRET：Ay4g0buBR9...（实际值）
   - 你的WEBHOOK_URL：https://open.feishu.cn/open-apis/bot/v2/hook/...（完整URL）

### 5.2 保存并验证
   保存配置文件
   运行命令验证配置：
   
   python3 -c "
   import json
   with open('/root/.openclaw/openclaw.json', 'r') as f:
       config = json.load(f)
   print('配置验证通过')
   print(f'App ID: {config[\"channels\"][\"feishu\"][\"appId\"]}')
   "

## 步骤 6：测试 Webhook

### 6.1 发送测试消息
   使用测试脚本发送消息：
   
   python3 test_webhook_simple.py

### 6.2 验证接收
   - 检查飞书群聊是否收到测试消息
   - 如果收到，说明配置成功
   - 如果未收到，检查：
     * Webhook URL 是否正确
     * 机器人是否已添加到群
     * 机器人权限是否正确配置
     * 网络连接是否正常

## 步骤 7：生产环境配置

### 7.1 配置 BTC 监控脚本
   确认 btc_monitor.py 使用正确的 Webhook 配置

### 7.2 设置定时任务
   使用 cron 每小时自动运行：
   
   crontab -e
   
   添加：
   0 * * * * python3 /root/.openclaw/workspace/btc_monitor.py

   保存并退出

## 常见问题排查

### 问题 1：Webhook 返回 403 Forbidden
   原因：机器人权限不足
   解决：检查群机器人设置，确保勾选"发送消息"权限

### 问题 2：Webhook 返回 400 Bad Request
   原因：请求格式不正确
   解决：
   - 检查消息格式是否符合飞书 API 规范
   - 确保 msg_type 字段正确（text / post / interactive）
   - 检查 JSON 格式是否正确

### 问题 3：Webhook 返回 19001 Bad Request
   原因：Tenant Access Token 无效或过期
   解决：
   - 重新生成 Token
   - 检查 App ID 和 App Secret 是否正确
   - 确保时间戳准确

### 问题 4：无法在群中找到机器人
   原因：机器人未添加到群或被移除
   解决：
   - 重新将机器人添加到群
   - 检查是否被管理员移除
   - 检查机器人是否被封禁

## 安全建议

### 1. 保护 App Secret
   - 不要将 App Secret 提交到代码仓库
   - 不要在不安全的地方保存
   - 定期轮换 App Secret

### 2. 使用环境变量
   考虑使用环境变量存储敏感信息：
   
   export FEISHU_APP_ID="cli_a91d8cf269389bb5"
   export FEISHU_APP_SECRET="Ay4g0buBR9..."
   export FEISHU_WEBHOOK_URL="https://open.feishu.cn/open-apis/bot/v2/hook/..."

### 3. 限制机器人权限
   只授予必要的权限，避免过度授权

### 4. 监控 Webhook 调用日志
   记录所有 Webhook 调用，便于排查问题

================================================================================
📝 配置检查清单
================================================================================

完成后，请确认以下项目：

□ 飞书机器人已创建
□ App ID 已复制并保存
□ App Secret 已复制并保存（仅一次可见）
□ 机器人已添加到群聊
□ 机器人权限已正确配置
□ Webhook URL 已生成
□ 服务器配置文件已更新
□ 测试消息已成功发送
□ 定时任务已配置

全部确认后，即可开始使用！

================================================================================
"""
    
    return guide

def create_config_template():
    """创建配置文件模板"""
    template = """
{
  "channels": {
    "feishu": {
      "appId": "你的飞书 App ID",
      "appSecret": "你的飞书 App Secret",
      "webhook_url": "你的飞书 Webhook URL",
      "user_id": "ou_9cde50d77f516edcf3a661ca32f83b2a"
    }
  }
}
"""
    
    template_path = "/root/.openclaw/workspace/feishu_config_template.json"
    with open(template_path, 'w', encoding='utf-8') as f:
        f.write(template)
    
    return template_path

def main():
    """主函数"""
    print("生成飞书 Webhook 配置指南...\n")
    
    guide = generate_webhook_guide()
    print(guide)
    
    print("\n" + "=" * 80)
    print("📝 创建配置文件模板...\n")
    
    template_path = create_config_template()
    
    print(f"✅ 配置文件模板已创建: {template_path}")
    print("\n下一步操作：")
    print("1. 按照上述指南配置飞书机器人")
    print("2. 复制 App ID 和 App Secret")
    print("3. 编辑配置文件模板，填入实际值")
    print("4. 保存为 openclaw.json")
    print("5. 测试发送消息\n")

if __name__ == "__main__":
    main()
