from pictex import *
from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.token import Token

COLORS = {
    "background": "#282C34",
    "line_number": "#636D83",
    "text": "#ABB2BF",
    "keyword": "#C678DD",
    "string": "#98C379",
    "comment": "#7F848E",
    "builtin": "#7058a8",
    "name": "#61AFEF",
    "literal": "#D19A66",
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

CODE_SNIPPET = """
from pictex import Row, Text

# Create a simple, styled component
def create_banner(text: str) -> Row:
    '''This function demonstrates PicTex's power!'''
    banner = Row(
        Text(text).font_size(40).color("white")
    ).padding(20).background_color("#5D3FD3")

    return banner

# Render the final image
banner.render(create_banner("Hello, World! ✨")).show()
"""

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
    line_children = []
    for token_type, token_text in tokens:
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
    code_lines.append(Row(line_number, parsed_code_row).vertical_align('top'))

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
    .font_family("Consolas")
    .font_size(16)
    .padding(60)
    .background_color("#757F9A")
)

canvas.render(window, crop_mode=CropMode.CONTENT_BOX).save("result.png")
