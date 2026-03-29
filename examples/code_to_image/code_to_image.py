from pictex import *
from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.token import Token
from itertools import groupby

COLORS = {
    "background": "#1E222A",
    "line_number": "#4B5263",
    "text": "#D7DAE0",
    "keyword": "#C792EA",
    "string": "#C3E88D",
    "comment": "#5C6370",
    "builtin": "#82AAFF",
    "name": "#89DDFF",
    "literal": "#F78C6C",
}

TOKEN_MAP = {
    Token.Keyword: COLORS["keyword"],
    Token.Name.Builtin: COLORS["builtin"],
    Token.Name.Function: COLORS["name"],
    Token.Name.Class: COLORS["name"],
    Token.Name: COLORS["text"],
    Token.String: COLORS["string"],
    Token.Number: COLORS["literal"],
    Token.Comment: COLORS["comment"],
    Token.Operator: COLORS["text"],
    Token.Literal: COLORS["literal"],
}

CODE_SNIPPET = open("code_snippet.py", encoding="utf-8").read()

def get_token_color(token) -> str:
    current_token = token
    while current_token is not None:
        if current_token in TOKEN_MAP:
            return TOKEN_MAP[current_token]
        current_token = current_token.parent

    return COLORS["text"] # default

def parse_python_line(line: str) -> Row:
    python_lexer = get_lexer_by_name("python")
    tokens = lex(line, python_lexer)
    grouped_tokens = [
        (token_type, ''.join(token_text for _, token_text in group))
        for token_type, group in groupby(tokens, key=lambda t: t[0])
    ]
    line_children = []
    for token_type, token_text in grouped_tokens:
        if (token_text == '\n'):
            continue
        color = get_token_color(token_type)
        line_children.append(Text(token_text).color(color))

    return Row(*line_children)


title_bar = Row(
    Row().size(12, 12).background_color("#FF5F56").border_radius('50%'),
    Row().size(12, 12).background_color("#FFBD2E").border_radius('50%'),
    Row().size(12, 12).background_color("#27C93F").border_radius('50%'),
).gap(8).padding(10)

code_lines = []
for i, line in enumerate(CODE_SNIPPET.strip().split('\n'), 1):
    line_number = Text(f"{i: >2}").color(COLORS["line_number"]).margin(0, 15, 0, 0)
    parsed_code_row = parse_python_line(line)
    code_lines.append(Row(line_number, parsed_code_row).align_items('start'))

code_block = Column(*code_lines).padding(15, 20).gap(4)

window = (
    Column(title_bar, code_block)
    .background_color(COLORS["background"])
    .border_radius(10)
    .border(1, "#1A1B1F")
    .box_shadows(Shadow(offset=(0, 10), blur_radius=30, color="#00000050"))
)

canvas = (
    Canvas()
    .font_family("FiraCode-VariableFont_wght.ttf")
    .font_size(16)
    .padding(60)
    .background_color("#757F9A")
)

canvas.render(window, crop_mode=CropMode.CONTENT_BOX).save("result.png")
