from pictex import *

DATA_MATRIX = [
    ["Product", "Category", "Price", "In Stock"],
    ["Leather Watch", "Accessories", "$120.00", "Yes"],
    ["Wireless Earbuds", "Electronics", "$89.99", "Yes"],
    ["Coffee Maker", "Home Goods", "$45.50", "No"],
    ["Running Shoes", "Apparel", "$110.00", "Yes"],
]

def approximate_column_widths(data_matrix: list) -> list[float]:
    """
    Calculates an approximate width for each column based on the longest
    string in that column, using a simple heuristic.
    """
    # These constants can be tweaked for different fonts and font sizes.
    APPROX_CHAR_WIDTH = 30  # An estimated average width of a character in pixels.
    HORIZONTAL_PADDING = 24

    num_columns = len(data_matrix[0])
    max_chars_per_column = [0] * num_columns

    # First, find the maximum number of characters in each column.
    for row in data_matrix:
        for i, cell_text in enumerate(row):
            if len(cell_text) > max_chars_per_column[i]:
                max_chars_per_column[i] = len(cell_text)

    # Now, calculate the approximate pixel width for each column.
    column_widths = [
        (count * APPROX_CHAR_WIDTH) + HORIZONTAL_PADDING
        for count in max_chars_per_column
    ]
    return column_widths

def create_table_cell(text: str, is_header: bool = False, width: float = None) -> Text:
    cell = Text(text).padding(8, 12).size(width=width).text_align("center")

    if is_header:
        cell.font_weight(700).color("white")
    else:
        cell.color("#34495e")

    return cell

def create_table_row(row_data: list, column_widths: list, is_header: bool = False, is_odd: bool = False) -> Row:
    cells = [
        create_table_cell(item, is_header=is_header, width=col_width)
        for item, col_width in zip(row_data, column_widths)
    ]

    table_row = Row(*cells).vertical_align('center')

    if is_header:
        table_row.background_color("#34495e")
    elif is_odd:
        table_row.background_color("#ecf0f1")
    else:
        table_row.background_color("white")

    return table_row

column_widths = approximate_column_widths(DATA_MATRIX)
table_rows = []
header_row = create_table_row(DATA_MATRIX[0], column_widths, is_header=True)
table_rows.append(header_row)

for i, row_data in enumerate(DATA_MATRIX[1:]):
    data_row = create_table_row(row_data, column_widths, is_header=False, is_odd=(i % 2 != 0))
    table_rows.append(data_row)

table = Column(*table_rows)
canvas = Canvas().font_family("Arial")
canvas.render(table).save("table.png")
