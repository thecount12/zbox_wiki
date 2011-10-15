"""
Implement Markdown Extension

this script supports
- simple table

Simple table syntax:

    || name || desc ||
    | lee | author |

will be:

    <table>
    <tr>
        <th> name </th><th> desc </th>
    </tr>
    <tr>
        <td> lee </td><td> author </td>
    </tr>
    </table>

"""

import re


def escape_table_special_chars(text):
    escape_p = "!\|"
    p_obj = re.compile(escape_p, re.UNICODE)
    return p_obj.sub('\v\f', text)

def unescape_table_special_chars(text):
    return text.replace("\v\f", "|")


def match_table(line):
    if not line:
        return False

    t_p = "^\|{1,2} (?P<cells>.+?) \|{1,2}(?:[ ]*)$"
    p_obj = re.compile(t_p, re.UNICODE)

    if p_obj.match(line) and line.count('|') >= 2:
        return True
    else:
        return False

def parse_cells(line):
    cells_p = "^(?P<splitter>\|){1,2} (?P<cells>.+?) \|{1,2}(?:[ ]*)$"
    p_obj = re.compile(cells_p, re.UNICODE)
    m_obj = p_obj.match(line)

    if m_obj:
        cells = m_obj.group('cells')
        splitter = m_obj.group('splitter')
        cells = [cell.strip()
                for cell in cells.split(splitter)
                if cell.strip()]

        is_table_header = line.startswith("||")
        if not is_table_header:
            total_columns = line.count(" |") + 1
            buf = " </td> <td> ".join(cells)
            buf = "    <td> %s </td>" % buf
        else:
            total_columns = line.count(" ||") + 1
            buf = " </th> <th> ".join(cells)
            buf = "    <th> %s </th>" % buf

        return total_columns, buf

    return None, line


"""
Parsing Rules

||      \what is\ || tbl beginning   || tbl body        || tbl ending      ||
|  previous line  |  None            |  ?               |  ?               |
|  current line   |  startswith('|') |  startswith('|') |  startswith('|') |
|  next line      |  ?               |  ?               |  None            |
"""
def parse_table(text):
    text = escape_table_special_chars(text)
    resp = []

    lines = text.split("\n")
    total_lines = len(lines)
    
    total_columns = None

    for i in xrange(total_lines):
        prev_line = None
        curr_line = lines[i]
        next_line = None

        is_first_line = i == 0
        if not is_first_line:
            prev_line = lines[i - 1]

        is_latest_line = (i + 1) == total_lines
        if not is_latest_line:
            next_line = lines[i + 1]


        is_first_line_of_table = match_table(curr_line) and (not prev_line) and (curr_line.count('||') >= 2)
        is_latest_line_of_table = match_table(curr_line) and (not next_line)

        if is_first_line_of_table:
            resp.append("<table>")

            resp.append("<tr>")
            curr_total_columns, buf = parse_cells(curr_line)
            total_columns = curr_total_columns
            resp.append(buf)
            resp.append("</tr>")

        elif is_latest_line_of_table:
            resp.append("<tr>")

            curr_total_columns, buf = parse_cells(curr_line)
            resp.append(buf)

            if total_columns and curr_total_columns < total_columns:
                buf = "<td>&nbsp;</td>" * (total_columns - curr_total_columns)
                resp.append(buf)

            resp.append("</tr>")
            resp.append("</table>")

        elif match_table(curr_line):
            resp.append("<tr>")
            
            curr_total_columns, buf = parse_cells(curr_line)
            resp.append(buf)

            if total_columns and curr_total_columns < total_columns:
                buf = "<td>&nbsp;</td>" * (total_columns - curr_total_columns)
                resp.append(buf)

            resp.append("</tr>")
            
        else:
            resp.append(curr_line)

    buf = "\n".join(resp)
    buf = unescape_table_special_chars(buf)
    
    return buf
