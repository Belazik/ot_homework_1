import ast
import os
import collections

from nltk import pos_tag


# если строчки со стрингами вроде 'VB', '.py' и т.д.  вызывается часто, то у меня вопрос - каждый раз создается новый
# объект стрингов ? Если да, то вынести в константу сортировка методов внутри класса должна быть следующая - сначала
# публичные методы, потом приватные. В нашем случае, сначала основные, потом вспомогательные. по крайней мере это
# актульно для джавы


def flat(_list):
    """ [(1,2), (3,4)] -> [1, 2, 3, 4]"""
    return sum([list(item) for item in _list], [])


def is_verb(word_):
    if not word_:
        return False
    pos_info = pos_tag([word_])
    # почему именно такие индексы?
    return pos_info[0][1] == 'VB'


# Понятно, что какой тип возвращает, но по коду не понятно, что делает, нужно добавить комментарий к методу,
# что возвращает и каким образом метод работает
def get_filepaths(path_):
    filenames = []
    for dirname, dirs, files in os.walk(path_, topdown=True):
        for file in files:
            if file.endswith('.py'):
                filenames.append(os.path.join(dirname, file))
    return filenames


def open_py_files(filename):
    """Open read-mode py-files and return text to parse."""
    with open(filename, 'r', encoding='utf-8') as attempt_handler:
        print(type(attempt_handler))
        return attempt_handler.read()


# метод get_filepaths должен быть рядом с этим методом, по аналогии с parse_code
# написать комментарий, что оно делает

def get_trees(path_, with_filenames=False, with_file_content=False, main_file_content=None):
    filenames = get_filepaths(path_)
    trees = []
    for filename in filenames:
        tree = parse_code(open_py_files(filename))
        if with_filenames:
            if with_file_content:
                trees.append((filename, main_file_content, tree))
            else:
                trees.append((filename, tree))
        else:
            trees.append(tree)
    return trees


# а нельзя так?
# def parse_code(text_code):
#    return try:
#        ast.parse(text_code)
#    except SyntaxError as e:
#       print(e)
#       None

def parse_code(text_code):
    try:
        tree = ast.parse(text_code)
    except SyntaxError as e:
        print(e)
        tree = None
    return tree


def get_all_names(tree):
    return [node.id for node in ast.walk(tree) if isinstance(node, ast.Name)]


def get_verbs_from_function_name(function_name):
    return [word_ for word_ in function_name.split('_') if is_verb(word_)]


def get_all_words_in_path(path_):
    trees = [t for t in get_trees(path_) if t]
    # опять таки вопрос, на каждый вызов '__' создается новый объект?
    function_names = [f for f in flat([get_all_names(t) for t in trees])
                      if not (f.startswith('__') and f.endswith('__'))]
    return flat([split_snake_case_name_to_words(function_name) for function_name in function_names])


def split_snake_case_name_to_words(name):
    return [n for n in name.split('_') if n]


# комментарий
def get_top_verbs_in_path(path_, top_size=10):
    trees = [t for t in get_trees(path_, None) if t]
    # разбить на строки или вынести в отдельный метод
    fncs = [f for f in
            flat([[node.name.lower() for node in ast.walk(t) if isinstance(node, ast.FunctionDef)] for t in trees]) if
            not (f.startswith('__') and f.endswith('__'))]
    # не информативный лог, может написать какая функция была получена?
    print('functions extracted')
    verbs = flat([get_verbs_from_function_name(function_name) for function_name in fncs])
    return collections.Counter(verbs).most_common(top_size)


# комментарий
def get_top_functions_names_in_path(path, top_size=10):
    t = get_trees(path)
    # разбить на строки или вынести в отдельный метод
    nms = [f for f in
           flat([[node.name.lower() for node in ast.walk(t) if isinstance(node, ast.FunctionDef)] for t in t]) if
           not (f.startswith('__') and f.endswith('__'))]
    return collections.Counter(nms).most_common(top_size)


# а в начале это нельзя указать? Или все точку входа делают внизу у вас?
wds = []
projects = [
    'django',
    'flask',
    'pyramid',
    'reddit',
    'requests',
    'sqlalchemy',
]
for project in projects:
    path = os.path.join('.', project)
    wds += get_top_verbs_in_path(path)

top_size = 200
print('total %s words, %s unique' % (len(wds), len(set(wds))))
# можно так. Или вынести в константу, если этот параметр часто должен меняться из кода
# for word, occurence in collections.Counter(wds).most_common(top_size=200):
for word, occurence in collections.Counter(wds).most_common(top_size):
    print(word, occurence)
