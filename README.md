# 文件/合同审查系统（Flask+Dify）

## 项目简介
本项目为基于Flask的全栈一体化文件/合同审查系统，支持文件上传、类型选择（文件审查/合同审查）、合同身份选择（甲方/乙方），并通过Dify API实现智能审核，结果实时展示。

## 主要功能
- 文件/合同上传与类型选择
- 合同审查时支持甲方/乙方身份输入
- 一次表单提交，后端自动串联Dify文件上传与工作流调用
- 审核结果本地展示，无需持久化
- 现代简约大方UI，苹果风格美化，响应式布局
- 初审/复审结果分离独立展示，交互体验优化
- 支持GitHub版本管理与回滚
- 前端支持Markdown语法渲染，所有AI输出内容均可高亮显示

## 系统界面截图

![系统主界面](static/屏幕截图%202025-07-16%20163231.png)

## 目录结构
```
censor_system/
  app.py                # Flask主程序
  templates/
    index.html          # 前端表单页面
  static/               # 静态资源目录（可选）
  README.md             # 项目说明文档
  requirements.txt      # 依赖包列表
```

## 安装与运行
1. 安装依赖
   ```bash
   pip install -r requirements.txt
   ```
2. 配置Dify API Token（推荐用环境变量）
   - Windows:
     ```powershell
    $env:DIFY_API_TOKEN=" 你的Dify API Token"
     ```
   - Linux/macOS:
     ```bash
     export DIFY_API_TOKEN="你的Dify API Token"
     ```
3. 启动服务
   ```bash
   python app.py
   ```
4. 访问
   - 打开浏览器访问 http://127.0.0.1:5000

## 依赖环境
- Python 3.7+
- Flask
- requests

## 注意事项
- Dify API Token请妥善保管，避免泄露。
- 文件上传大小、类型受Dify官方API限制。
- 本系统仅作演示用途，未做持久化与安全加固。

## 特色亮点
- 现代简约风格UI，圆角卡片、阴影、舒适配色，兼容移动端
- 初审结果与复审结果分为独立卡片，交互清晰
- 审核进度实时反馈，用户体验友好
- 支持GitHub远程仓库，便于团队协作与历史回滚


## 联系与反馈
如有问题或建议，请联系开发者。 