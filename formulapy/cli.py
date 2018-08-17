from .api import *
from wisepy.talking import Talking
from Redy.Tools.PathLib import Path
talking = Talking()


@talking.alias('file')
def for_file(filename: str, w: "overwrite file or not" = False):
    with Path(filename).open('r', encoding=('utf8', 'gb18030')) as fr:
        original_text = fr.read()
        text = render_formula(original_text)

    if w:
        with Path(filename).open('w', encoding='utf8') as fw:
            try:
                fw.write(text)
            except UnicodeEncodeError:
                print('UnicodeEncoding Error found.')
                fw.write(original_text)
    else:
        print(text)


@talking.alias('text')
def for_text(text: str):
    print(render_formula(text))


def run():
    talking.on()
