import ast
import os
import re
from .settings import OTREE_AUTHORS_EMAIL, OTREE_DOC_MARKDOWN_EXTENSIONS

# ================== Constants ==================
# Compile OTREE_AUTHORS_EMAIL to re object
for k in OTREE_AUTHORS_EMAIL:
    if isinstance(OTREE_AUTHORS_EMAIL[k], str):
        OTREE_AUTHORS_EMAIL[k] = [OTREE_AUTHORS_EMAIL[k]]
    OTREE_AUTHORS_EMAIL[k] = list(map(lambda x: x.replace(' ', r'\s+'), OTREE_AUTHORS_EMAIL[k]))
    OTREE_AUTHORS_EMAIL[k] = re.compile('(' + '|'.join(OTREE_AUTHORS_EMAIL[k]) + ')', re.IGNORECASE)

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
INC_REG = re.compile(r'{%\s*include\s*(?P<quote>[\'"])(.+?)(?P=quote)\s*%}')
CARD_HTML = """
<div class="card" style="margin-top: 20px">
    <div class="card-header">
        {}
    </div>
    <div class="card-body">{}</div>
</div>

"""

MISSING_DOC = CARD_HTML.format('缺失的游戏说明文档', """
你正在创建游戏<code>{}</code>的说明文档没有找到。<br>
请点击上方的"Configure session"打开设置面板进行游戏参数设置。<br>
如有必要，<b style="color:red">请联系开发者补充填写游戏参数文档</b>，以解释该游戏各个参数的作用。
""")

AUTHORS_TABLE_BODY = """
<table class="table table-hover">
    <thead>
        <tr>
            <th scope="col">游戏<code>app</code>名称</th>
            <th scope="col">开发者（可发送邮件）</th>
        </tr>
    </thead>
    <tbody>{}</tbody>
</table>
"""

AUTHORS_TABLE_CONTENT = """
        <tr>
            <td scope="row"><code>{}</code></td>
            <td>{}</td>
        </tr>
"""


def get_string_from_code(app_name, str_var_name):
    with open(app_name + '/models.py', encoding='utf8') as f:
        co = ast.parse(f.read())
        for stmt in co.body:
            if 'targets' in stmt._fields:
                for v_idx, var in enumerate(stmt.targets):
                    if isinstance(var, ast.Tuple):
                        for t_idx, t_var in enumerate(var.elts):
                            if isinstance(t_var, ast.Name) and t_var.id == str_var_name:
                                return stmt.value.elts[t_idx].s
                    elif isinstance(var, ast.Name) and var.id == str_var_name:
                        return stmt.value.s
    return None


def get_included_markdown_for_reg(reg_match):
    filename = os.path.join(BASE_DIR, reg_match.group(2))
    if not os.path.exists(filename):
        return '\n'
    with open(filename, encoding='utf8') as f:
        return f.read()


def add_author_mailto(doc_author):
    for email, name_reg in OTREE_AUTHORS_EMAIL.items():
        author_str = ''
        for s in name_reg.split(doc_author):
            author_str += s if not name_reg.match(s) else '<a href=mailto:{}>{}</a>'.format(email, s)
        doc_author = author_str
    return doc_author


def gen_docs(app_list, show_missing_doc=True, show_author_table=True, show_author_mail=True):
    # Read app document html
    docs = {}
    apps_no_doc = []
    for app in app_list:
        docs[app] = {'doc': None, 'author': '未知'}
        if os.path.exists(os.path.join(app, 'doc.md')):
            with open(os.path.join(app, 'doc.md'), encoding='utf8') as f:
                import markdown
                doc_content = INC_REG.sub(get_included_markdown_for_reg, f.read())
                docs[app]['doc'] = markdown.markdown(doc_content, extensions=OTREE_DOC_MARKDOWN_EXTENSIONS)
        elif os.path.exists(os.path.join(app, 'doc.html')):
            with open(os.path.join(app, 'doc.html'), encoding='utf8') as f:
                docs[app]['doc'] = f.read()
        else:
            apps_no_doc.append(app)
        try:
            docs[app]['author'] = get_string_from_code(app, 'author')
        except Exception as e:
            print(e)
        if docs[app]['author'] is None: docs[app]['author'] = '未知'
        if show_author_mail:
            docs[app]['author'] = add_author_mailto(docs[app]['author'])
    doc = ''
    for app in app_list:
        if docs[app]['doc'] is not None:
            doc += CARD_HTML.format('游戏<code>{}</code>的说明文档'.format(app), docs[app]['doc'])
    if show_missing_doc and len(apps_no_doc) > 0:
        doc += MISSING_DOC.format('</code>、<code>'.join(apps_no_doc))
    if show_author_table:
        author_content = ''
        for app in app_list:
            author_content += AUTHORS_TABLE_CONTENT.format(app, docs[app]['author'])
        doc += CARD_HTML.format('游戏开发者列表', AUTHORS_TABLE_BODY.format(author_content))
    return doc


def read_doc(app_doc_path):
    if os.path.exists(app_doc_path):
        with open(app_doc_path, encoding='utf8') as f:
            return f.read()
    return ''
