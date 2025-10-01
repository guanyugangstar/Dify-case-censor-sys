# 智能文件审查系统 📋



## 🚀 项目简介

![系统主界面截图](static/屏幕截图2025-10-02015427.png)
智能文件审查系统是一个基于Flask和Dify AI的全栈Web应用，专为文件和合同智能审查而设计。系统采用现代化的模块化架构，提供直观的用户界面和强大的AI审查能力。

### ✨ 核心特性

- 🔍 **智能审查**：集成Dify AI工作流，支持文件和合同的智能分析
- 📄 **多格式支持**：支持多种文档格式上传和处理
- 🎯 **角色定制**：合同审查支持甲方/乙方身份选择
- 📱 **响应式设计**：现代化UI，完美适配PC和移动端
- ⚡ **实时反馈**：审查进度实时显示，用户体验流畅
- 📊 **结果展示**：初审/复审结果分离展示，支持Markdown渲染
- 💾 **文件下载**：支持审查结果导出为Word文档
- 🔄 **撤销功能**：支持操作撤销，提升用户体验

## 🏗️ 系统架构

```
智能文件审查系统
├── 前端界面 (HTML/CSS/JavaScript)
├── Flask Web框架
├── 模块化服务层
│   ├── Dify AI集成
│   ├── 文件处理服务
│   └── 数据验证服务
└── 配置管理系统
```

## 📁 项目结构

```
censor_system/
├── app.py                      # Flask应用入口
├── app_original.py             # 原始版本备份
├── app_refactored.py           # 重构版本备份
├── requirements.txt            # Python依赖包
├── startup.bat                 # Windows启动脚本
├── .gitignore                  # Git忽略文件
├── SECURITY.md                 # 安全说明文档
├── chatflow API文档.md         # API文档
│
├── config/                     # 配置模块
│   ├── __init__.py
│   ├── constants.py            # 常量定义
│   └── settings.py             # 配置设置
│
├── routes/                     # 路由模块
│   ├── __init__.py
│   └── main.py                 # 主要路由
│
├── services/                   # 服务层
│   ├── __init__.py
│   ├── dify_client.py          # Dify API客户端
│   ├── file_service.py         # 文件处理服务
│   └── validation.py           # 数据验证服务
│
├── utils/                      # 工具模块
│   ├── __init__.py
│   ├── exceptions.py           # 异常处理
│   └── logger.py               # 日志管理
│
├── templates/                  # 模板文件
│   └── index.html              # 主页面模板
│
├── static/                     # 静态资源
│   ├── favicon.ico             # 网站图标
│   ├── marked.min.js           # Markdown渲染库
│   └── 屏幕截图 2025-07-16 163231.png
│
├── logs/                       # 日志目录
│   └── .gitkeep
│
└── test_files/                 # 测试文件
    ├── test.txt
    ├── test_document.txt
    ├── test_upload.txt
    └── test_stream_details.py
```

## 🛠️ 安装与配置

### 环境要求

- Python 3.7+
- pip 包管理器
- 稳定的网络连接（用于Dify API调用）

### 快速开始

1. **克隆项目**
   ```bash
   git clone <repository-url>
   cd censor_system
   ```

2. **安装依赖**
   ```bash
   pip install -r requirements.txt
   ```

3. **环境配置**
   
   创建 `.env` 文件并配置必要参数：
   ```env
   DIFY_API_TOKEN=your_dify_api_token_here
   DIFY_BASE_URL=https://api.dify.ai/v1
   FLASK_ENV=development
   FLASK_DEBUG=True
   ```

   或使用环境变量：
   
   **Windows (PowerShell):**
   ```powershell
   $env:DIFY_API_TOKEN="your_dify_api_token_here"
   ```
   
   **Linux/macOS:**
   ```bash
   export DIFY_API_TOKEN="your_dify_api_token_here"
   ```

4. **启动应用**
   
   **方式一：Python命令**
   ```bash
   python app.py
   ```
   
   **方式二：Windows批处理（推荐）**
   ```bash
   startup.bat
   ```

5. **访问应用**
   
   打开浏览器访问：`http://127.0.0.1:5050`

## 📋 功能说明

### 🔍 文件审查功能

- **文件上传**：支持拖拽上传和点击选择
- **类型选择**：文件审查 / 合同审查
- **身份选择**：合同审查时可选择甲方/乙方身份
- **智能分析**：基于Dify AI的深度文档分析
- **结果展示**：初审和复审结果分离显示

### 💾 下载功能

- **Word导出**：将审查结果导出为Word文档
- **路径选择**：支持用户自定义保存路径（现代浏览器）
- **兼容性**：自动降级到传统下载方式

### 🎨 用户界面

- **现代设计**：苹果风格的简约界面
- **响应式布局**：完美适配各种设备尺寸
- **实时反馈**：操作状态实时显示
- **Markdown支持**：AI输出内容支持富文本渲染

## 🔧 技术栈

### 后端技术
- **Flask 2.3.3** - Web框架
- **Requests 2.31.0** - HTTP客户端
- **python-dotenv 1.0.0** - 环境变量管理
- **python-docx 0.8.11** - Word文档处理

### 前端技术
- **HTML5** - 页面结构
- **CSS3** - 样式设计
- **JavaScript (ES6+)** - 交互逻辑
- **Marked.js** - Markdown渲染

### AI集成
- **Dify API** - AI工作流引擎
- **智能文档分析** - 文件内容理解
- **自然语言处理** - 审查结果生成

## 🔒 安全说明

- ✅ API Token安全存储（环境变量）
- ✅ 文件上传类型验证
- ✅ 请求参数验证
- ✅ 错误信息安全处理
- ⚠️ 生产环境需要额外的安全加固


*智能文件审查系统主界面 - 现代化设计，操作简便*

## 🚀 版本历史

### v1.1.0 (最新)
- ✨ 修复下载功能，添加文件保存路径选择
- 🔧 集成File System Access API
- 🛠️ 优化用户体验和兼容性

### v1.0.0
- 🎉 初始版本发布
- ✨ 基础文件审查功能
- 🎨 现代化UI设计
- 🔗 Dify AI集成

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🆘 故障排除

### 常见问题

**Q: 启动时提示"Dify API Token未配置"**
A: 请确保正确设置了环境变量 `DIFY_API_TOKEN`

**Q: 文件上传失败**
A: 检查网络连接和文件格式是否支持

**Q: 下载功能不工作**
A: 确保浏览器支持现代Web API，或使用最新版本浏览器

### 日志查看

系统日志保存在 `logs/` 目录下，可以通过查看日志文件排查问题。

## 📞 联系方式

- 📧 邮箱：[开发者邮箱]
- 🐛 问题反馈：[GitHub Issues]
- 📖 文档：[项目Wiki]

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！

*最后更新：2025年1月*