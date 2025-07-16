from flask import Flask, render_template, request, redirect, url_for, flash, Response, stream_with_context, jsonify
import os
import enum
import requests
import json

app = Flask(__name__)
app.secret_key = 'app-np0W2uc7cipLyCoxkM3BF8i2'  # 用于flash消息

# Dify API配置（建议用环境变量管理）
DIFY_API_BASE_URL = 'http://localhost/v1'
DIFY_API_TOKEN = os.environ.get('DIFY_API_TOKEN', 'app-np0W2uc7cipLyCoxkM3BF8i2')

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
def guess_type(file):
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

    if not review_type or not file:
        flash('类型和文件为必填项')
        return redirect(url_for('index'))
    if review_type == '合同审查':
        if not contracting_party:
            flash('合同审查时需选择甲方、乙方或丙方')
            return redirect(url_for('index'))
        if contracting_party not in [e.value for e in ContractingPartyEnum]:
            flash('合同方类型不合法')
            return redirect(url_for('index'))
    category = '政策' if review_type == '文件审查' else '合同'
    if category not in [e.value for e in CategoryEnum]:
        flash('审查类型不合法')
        return redirect(url_for('index'))

    user_id = 'demo_user'

    # 保存上传文件到临时路径
    temp_path = os.path.join('static', file.filename)
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
            with requests.post(url, headers=headers, json=payload, stream=True, timeout=120) as resp:
                for line in resp.iter_lines():
                    if line:
                        if line.startswith(b'data:'):
                            content = line[5:].decode('utf-8').strip()
                            yield f"data: {content}\n\n"
        except Exception as e:
            yield f"data: [ERROR] {str(e)}\n\n"
    return Response(stream_with_context(event_stream()), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(debug=True) 