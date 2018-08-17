import ast
import io
import tokenize
from .mapping import tex
from collections import namedtuple

_record = namedtuple('record', ['formula', 'start', 'end'])


class Occur(_record):
    pass


class Line:
    __slots__ = 'nodes',

    def __init__(self, nodes):
        self.nodes = nodes

    def __str__(self):
        return ''.join(map(str, self.nodes))


class Text:
    __slots__ = 'lines',

    def __init__(self, lines):
        self.lines = lines

    def __str__(self):
        def stream():
            for line in self.lines:
                for node in line.nodes:
                    if node:
                        yield node
                yield '\n'

        return ''.join(stream())

    @staticmethod
    def from_str(text: str):
        return Text([Line(list(_)) for _ in text.splitlines()])


class Collector(ast.NodeTransformer):
    def __init__(self):
        self.collected = []

    def visit_Subscript(self, node: ast.Subscript):
        def collect(sym, lineno, colno, span):
            self.collected.append(Occur(sym, lineno, colno, span))

        value = node.value
        slice = node.slice
        if isinstance(value, ast.Name) and value.id == 'tex' and isinstance(
                slice, ast.Index):
            if isinstance(slice.value, ast.Str):
                s = slice.value.s

                if s in tex:
                    collect(tex[s], value.lineno - 1, value.col_offset,
                            len("tex['']") + len(s))

            elif isinstance(slice.value, ast.Tuple):
                elts = iter(slice.value.elts)
                head = next(elts)
                if isinstance(head, ast.Str):
                    s = head.s
                    if s in tex:
                        collect(tex[s], value.lineno - 1, value.col_offset,
                                len("tex['']") + len(s))
                for each in elts:
                    if isinstance(each, ast.Str):
                        s = each.s
                        if s in tex:
                            collect(tex[s], each.lineno - 1, each.col_offset,
                                    len(s) + 2)

        return self.generic_visit(node)


def render_formula(source_code):

    occurs = collect_occurrences(source_code)

    text_obj = Text.from_str(source_code)
    lines = text_obj.lines
    for sym, (l1, c1), (l2, c2) in occurs:
        l1 = l1 - 1
        l2 = l2 - 1
        line = lines[l1]
        nodes = line.nodes
        nodes[c1] = sym

        if l1 == l2:
            for i in range(c1 + 1, c2):
                nodes[i] = ''
        else:
            for i in range(c1 + 1, len(nodes)):
                nodes[i] = ''

            for i in range(l1 + 1, l2):
                nodes = lines[i].nodes
                for i in range(0, len(nodes)):
                    nodes[i] = ''

            nodes = lines[l2].nodes
            for i in range(c2):
                nodes[i] = ''

    return str(text_obj)


def collect_occurrences(source_code: str):

    mapping = tex
    occurs = []
    is_occurring = -1

    op = tokenize.OP
    name = tokenize.NAME
    string = tokenize.STRING
    marker = None
    ios = io.BytesIO()
    ios.write(source_code.encode('utf8'))
    ios.seek(0)

    for each in tokenize.tokenize(ios.readline):
        if is_occurring is -1:
            if each.type is name and each.string == 'tex':
                is_occurring += 1
                marker = each
        elif is_occurring is 0:
            if each.type is op and each.string == '[':
                occurs.append(Occur('', marker.start, each.end))
                is_occurring += 1
            else:
                is_occurring = -1

        elif is_occurring is 1:

            if each.type is op and each.string == ']':
                is_occurring = -1
                occurs.append(Occur('', each.start, each.end))

            elif each.type is op and each.string == ',':
                occurs.append(Occur('', each.start, each.end))

            elif each.type is string:

                v = mapping.get(each.string[1:-1])
                if v:
                    occurs.append(Occur(v, each.start, each.end))
                else:
                    raise NameError("No formula named {}.".format(each.string))

            else:
                occurs.append(Occur(each.string, each.start, each.end))
        else:
            raise TypeError(is_occurring)

    return occurs
