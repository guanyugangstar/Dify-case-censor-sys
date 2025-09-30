from flask import Flask, render_template, request, redirect, url_for, flash, Response, stream_with_context, jsonify
import os
import enum
import requests
import json
import secrets
from werkzeug.utils import secure_filename
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

app = Flask(__name__)

# 安全配置 - 使用环境变量或随机生成
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB文件大小限制

# Dify API配置 - 必须通过环境变量设置
DIFY_API_BASE_URL = os.environ.get('DIFY_API_BASE_URL', 'http://localhost/v1')
DIFY_API_TOKEN = os.environ.get('DIFY_API_TOKEN')

# 检查必要的环境变量
if not DIFY_API_TOKEN:
    raise ValueError("DIFY_API_TOKEN环境变量未设置，请设置后重新启动应用")

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {
    'pdf', 'doc', 'docx', 'txt', 'md', 'markdown', 'html',
    'xls', 'xlsx', 'ppt', 'pptx', 'xml', 'epub', 'csv',
    'jpg', 'jpeg', 'png', 'gif', 'webp', 'svg',
    'mp3', 'm4a', 'wav', 'webm', 'amr', 'mpga',
    'mp4', 'mov', 'mpeg'
}

# 文件类型映射
EXT_TYPE_MAP = {
    'application/pdf': 'pdf',
    'application/msword': 'doc',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx',
    'text/plain': 'txt',
    'text/markdown': 'markdown',
    'text/html': 'html',
    'application/vnd.ms-excel': 'xls',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'xlsx',
    'application/vnd.ms-powerpoint': 'ppt',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'pptx',
    'application/xml': 'xml',
    'application/epub+zip': 'epub',
    'image/jpeg': 'jpg',
    'image/png': 'png',
    'image/gif': 'gif',
    'image/webp': 'webp',
    'image/svg+xml': 'svg',
    'audio/mpeg': 'mp3',
    'audio/mp4': 'm4a',
    'audio/wav': 'wav',
    'audio/webm': 'webm',
    'audio/amr': 'amr',
    'video/mp4': 'mp4',
    'video/quicktime': 'mov',
    'video/mpeg': 'mpeg',
    'audio/mpga': 'mpga',
}
EXT_FILETYPE_MAP = {
    'pdf': 'document', 'doc': 'document', 'docx': 'document', 'txt': 'document', 'md': 'document', 'markdown': 'document', 'html': 'document',
    'xls': 'document', 'xlsx': 'document', 'ppt': 'document', 'pptx': 'document', 'xml': 'document', 'epub': 'document',
    'csv': 'document', 'eml': 'document', 'msg': 'document',
    'jpg': 'image', 'jpeg': 'image', 'png': 'image', 'gif': 'image', 'webp': 'image', 'svg': 'image',
    'mp3': 'audio', 'm4a': 'audio', 'wav': 'audio', 'webm': 'audio', 'amr': 'audio', 'mpga': 'audio',
    'mp4': 'video', 'mov': 'video', 'mpeg': 'video',
}
def allowed_file(filename):
    """检查文件扩展名是否被允许"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file(file):
    """全面的文件验证"""
    if not file:
        return False, "未选择文件"
    
    if file.filename == '':
        return False, "文件名不能为空"
    
    if not allowed_file(file.filename):
        return False, f"不支持的文件类型。支持的格式：{', '.join(sorted(ALLOWED_EXTENSIONS))}"
    
    # 检查文件大小（通过读取内容长度）
    file.seek(0, 2)  # 移动到文件末尾
    file_size = file.tell()
    file.seek(0)  # 重置到文件开头
    
    max_size = app.config['MAX_CONTENT_LENGTH']
    if file_size > max_size:
        return False, f"文件过大，最大支持 {max_size // (1024*1024)}MB"
    
    if file_size == 0:
        return False, "文件不能为空"
    
    return True, "文件验证通过"

def guess_type(file):
    """推测文件类型"""
    mime = getattr(file, 'mimetype', None)
    ext = EXT_TYPE_MAP.get(mime)
    if not ext:
        ext = file.filename.rsplit('.', 1)[-1].lower() if '.' in file.filename else ''
    return EXT_FILETYPE_MAP.get(ext, 'custom')

def file_to_dify_input(file, file_id):
    file_type = guess_type(file)
    return {
        'type': file_type,
        'upload_file_id': file_id,
        'transfer_method': 'local_file'
    }

def decode_unicode_dict(d):
    import codecs
    if isinstance(d, dict):
        return {k: decode_unicode_dict(v) for k, v in d.items()}
    elif isinstance(d, list):
        return [decode_unicode_dict(i) for i in d]
    elif isinstance(d, str):
        try:
            return codecs.decode(d, 'unicode_escape')
        except Exception:
            return d
    else:
        return d

# 定义枚举类型
class CategoryEnum(str, enum.Enum):
    合同 = "合同"
    政策 = "政策"

class ContractingPartyEnum(str, enum.Enum):
    甲方 = "甲方"
    乙方 = "乙方"
    丙方 = "丙方"

def filter_nones(obj):
    if isinstance(obj, dict):
        return {k: filter_nones(v) for k, v in obj.items() if v is not None}
    elif isinstance(obj, list):
        return [filter_nones(i) for i in obj if i is not None]
    else:
        return obj

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html', result=None)

@app.route('/upload', methods=['POST'])
def upload():
    review_type = request.form.get('review_type')
    contracting_party = request.form.get('contracting_party')
    file = request.files.get('file')

    # 基本参数验证
    if not review_type:
        flash('请选择审查类型')
        return redirect(url_for('index'))
    
    # 文件验证
    is_valid, message = validate_file(file)
    if not is_valid:
        flash(message)
        return redirect(url_for('index'))
    
    # 合同审查特殊验证
    if review_type == '合同审查':
        if not contracting_party:
            flash('合同审查时需选择甲方、乙方或丙方')
            return redirect(url_for('index'))
        if contracting_party not in [e.value for e in ContractingPartyEnum]:
            flash('合同方类型不合法')
            return redirect(url_for('index'))
    
    # 审查类型验证
    category = '政策' if review_type == '文件审查' else '合同'
    if category not in [e.value for e in CategoryEnum]:
        flash('审查类型不合法')
        return redirect(url_for('index'))

    user_id = 'demo_user'

    # 使用安全的文件名并保存到临时路径
    secure_name = secure_filename(file.filename)
    if not secure_name:
        secure_name = f"upload_{secrets.token_hex(8)}.tmp"
    
    # 确保static目录存在
    os.makedirs('static', exist_ok=True)
    temp_path = os.path.join('static', secure_name)
    file.save(temp_path)

    # 用requests上传文件
    try:
        url = f"{DIFY_API_BASE_URL}/files/upload"
        headers = {"Authorization": f"Bearer {DIFY_API_TOKEN}"}
        with open(temp_path, 'rb') as f:
            files = {'file': (file.filename, f, file.mimetype)}
            data = {'user': user_id}
            resp = requests.post(url, headers=headers, files=files, data=data)
            resp.raise_for_status()
            file_info = resp.json()
            file_info = decode_unicode_dict(file_info)  # 新增：递归反转义
            file_id = file_info['id']
    except Exception as e:
        flash(f'文件上传失败: {e}')
        if os.path.exists(temp_path):
            os.remove(temp_path)
        return redirect(url_for('index'))
    if os.path.exists(temp_path):
        os.remove(temp_path)

    # 组装inputs（只保留官方要求字段）
    file_dict = file_to_dify_input(file, file_id)
    if file_dict['type'] not in ['document', 'image', 'audio', 'video']:
        flash('文件类型不被支持，请上传文档、图片、音频或视频类型文件')
        return redirect(url_for('index'))
    inputs = {
        'file': file_dict,
        'Category': category
    }
    if review_type == '合同审查' and contracting_party in [e.value for e in ContractingPartyEnum]:
        inputs['Contracting_party'] = contracting_party
    print('inputs for chatflow:', inputs, flush=True)

    return Response(json.dumps({
        'inputs': inputs,
        'user_id': user_id
    }, ensure_ascii=False), mimetype='application/json')

@app.route('/stream_chat', methods=['POST'])
def stream_chat():
    data = request.get_json()
    inputs = data.get('inputs')
    user_id = data.get('user_id')
    if not inputs or not user_id:
        return jsonify({'error': '参数缺失'}), 400

    def event_stream():
        try:
            url = f"{DIFY_API_BASE_URL}/chat-messages"
            headers = {
                "Authorization": f"Bearer {DIFY_API_TOKEN}",
                "Content-Type": "application/json"
            }
            payload = {
                "query": "请审查",
                "inputs": inputs,
                "user": user_id,
                "response_mode": "streaming",
                "conversation_id": ""
            }
            with requests.post(url, headers=headers, json=payload, stream=True, timeout=300) as resp:
                for line in resp.iter_lines():
                    if line:
                        if line.startswith(b'data:'):
                            content = line[5:].decode('utf-8').strip()
                            yield f"data: {content}\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"
    return Response(stream_with_context(event_stream()), mimetype='text/event-stream')

# 全局错误处理器
@app.errorhandler(413)
def too_large(e):
    """处理文件过大错误"""
    flash(f'文件过大，请上传小于 {app.config["MAX_CONTENT_LENGTH"] // (1024*1024)}MB 的文件')
    return redirect(url_for('index'))

@app.errorhandler(400)
def bad_request(e):
    """处理请求错误"""
    flash('请求格式错误，请检查上传的文件和参数')
    return redirect(url_for('index'))

@app.errorhandler(500)
def internal_error(error):
    """处理服务器内部错误"""
    app.logger.error(f'Server Error: {error}')
    flash('服务器内部错误，请稍后重试')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=False, port=5050)