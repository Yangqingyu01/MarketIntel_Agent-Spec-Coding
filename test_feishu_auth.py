"""Test Feishu authorization flow."""

from feishu.sender import get_authorization_url, get_user_access_token

# 飞书授权流程说明
print("===== 飞书授权流程 ======")
print("1. 首先需要在飞书开放平台配置回调地址")
print("2. 然后访问授权URL进行授权")
print("3. 获取授权码后兑换访问令牌")
print()

# 步骤1: 配置回调地址
print("步骤1: 请在飞书开放平台配置回调地址")
print("- 登录飞书开放平台: https://open.feishu.cn/")
print("- 进入应用管理: cli_a9622eff8523dbd3")
print("- 进入 '安全与授权' 页面")
print("- 在 '重定向URL' 中添加: http://localhost:8080/api/feishu/callback")
print()

# 步骤2: 生成授权URL
print("步骤2: 生成授权URL")
redirect_uri = "http://localhost:8080/api/feishu/callback"
auth_url = get_authorization_url(redirect_uri, state="test123")
print("请访问以下URL进行授权:")
print(auth_url)
print()

# 步骤3: 获取授权码
print("步骤3: 获取授权码")
print("- 授权成功后，会跳转到回调地址并附带code参数")
print("- 例如: http://localhost:8080/api/feishu/callback?code=xxx&state=test123")
print("- 请复制code参数的值")
print()

# 步骤4: 兑换访问令牌
print("步骤4: 兑换访问令牌")
print("- 服务器会自动处理回调并兑换访问令牌")
print("- 浏览器会显示授权结果，包含访问令牌信息")
print("- 请保存获取到的访问令牌，用于后续测试")

# 步骤5: 测试消息发送
print("\n步骤5: 测试消息发送")
print("- 使用获取到的访问令牌测试飞书消息发送功能")
print("- 运行: python test_feishu_token.py")
