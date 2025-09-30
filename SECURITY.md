# 安全配置说明

## 环境变量配置

### 必需的环境变量

1. **DIFY_API_TOKEN** (必需)
   - 从Dify控制台获取的API令牌
   - 用于访问Dify API服务
   - 示例：`DIFY_API_TOKEN=app-xxxxxxxxxxxxxxxxx`

2. **SECRET_KEY** (推荐)
   - Flask应用的密钥，用于session加密
   - 如未设置，系统会自动生成随机密钥
   - 生产环境建议手动设置强密钥
   - 示例：`SECRET_KEY=your-very-secure-random-key-here`

### 可选的环境变量

1. **DIFY_API_BASE_URL**
   - Dify API的基础URL
   - 默认值：`http://localhost/v1`
   - 云服务示例：`https://api.dify.ai/v1`

2. **FLASK_ENV**
   - Flask运行环境
   - 可选值：`development`, `production`
   - 默认值：`development`

## 配置方法

### 方法1：使用.env文件（推荐）

1. 复制 `.env.example` 为 `.env`
2. 编辑 `.env` 文件，填入实际值
3. 应用会自动加载环境变量

### 方法2：系统环境变量

**Windows PowerShell:**
```powershell
$env:DIFY_API_TOKEN="your-token-here"
$env:SECRET_KEY="your-secret-key"
```

**Windows CMD:**
```cmd
set DIFY_API_TOKEN=your-token-here
set SECRET_KEY=your-secret-key
```

**Linux/macOS:**
```bash
export DIFY_API_TOKEN="your-token-here"
export SECRET_KEY="your-secret-key"
```

## 安全特性

### 文件上传安全

1. **文件类型限制**
   - 只允许预定义的安全文件类型
   - 支持文档、图片、音频、视频格式

2. **文件大小限制**
   - 最大文件大小：16MB
   - 防止大文件攻击

3. **文件名安全**
   - 使用 `secure_filename()` 处理文件名
   - 防止路径遍历攻击

4. **临时文件管理**
   - 上传后自动清理临时文件
   - 避免磁盘空间占用

### 应用安全

1. **密钥管理**
   - 移除硬编码密钥
   - 使用环境变量管理敏感信息
   - 自动生成随机密钥

2. **错误处理**
   - 全局错误处理器
   - 友好的错误提示
   - 防止敏感信息泄露

3. **输入验证**
   - 严格的参数验证
   - 文件完整性检查
   - 防止恶意输入

## 部署建议

### 生产环境

1. 设置强随机的 `SECRET_KEY`
2. 使用HTTPS协议
3. 配置防火墙规则
4. 定期更新依赖包
5. 启用日志监控

### 开发环境

1. 使用 `.env` 文件管理配置
2. 不要提交 `.env` 文件到版本控制
3. 定期检查依赖包安全性

## 注意事项

⚠️ **重要提醒**

1. 永远不要在代码中硬编码API密钥
2. 不要将 `.env` 文件提交到Git仓库
3. 定期轮换API密钥
4. 监控异常的文件上传行为
5. 在生产环境中禁用调试模式