import ast
import os
import collections

from nltk import pos_tag

# если строчки со стрингами вроде 'VB', '.py' и т.д.  вызывается часто, то у меня вопрос - каждый раз создается новый объект стрингов ?
# Если да, то вынести в константу
# сортировка методов внутри класса должна быть следующая - сначала публичные методы, потом приватные. В нашем случае, сначала основные, потом вспомогательные.
# по крайней мере это актульно для джавы

def flat(_list):
    """ [(1,2), (3,4)] -> [1, 2, 3, 4]"""
    return sum([list(item) for item in _list], [])

def is_verb(word):
    if not word:
        return False
    pos_info = pos_tag([word])
    #почему именно такие индексы?
    return pos_info[0][1] == 'VB'

#_path не используется, убрать?
# Понятно, что какой тип возвращает, но по коду не понятно, что делает, нужно добавить комментарий к методу, что возвращает и каким образом метод работает
def get_filepaths(_path):
    path = Path
    filenames = []
    for dirname, dirs, files in os.walk(path, topdown=True):
        for file in files:
            if file.endswith('.py'):
                filenames.append(os.path.join(dirname, file))
    return filenames

#по названию метода, можно подумать, что оно ничего не возвращает. Или переделать название или добавить комментарий, что возвращает
def open_py_files(filename):
    with open(filename, 'r', encoding='utf-8') as attempt_handler:
        return attempt_handler.read()

#метод get_filepaths должен быть рядом с этим методом, по аналогии с parse_code
#написать комментарий, что оно делает
#_path не используется
def get_trees(_path, with_filenames=False, with_file_content=False, main_file_content=None):
    path = Path
    filenames = get_filepaths(path)
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


#а нельзя так?
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
    return [word for word in function_name.split('_') if is_verb(word)]


def get_all_words_in_path(path):
    trees = [t for t in get_trees(path) if t]
    #опять таки вопрос, на каждый вызов '__' создается новый объект?
    function_names = [f for f in flat([get_all_names(t) for t in trees])
                      if not (f.startswith('__') and f.endswith('__'))]
    return flat([split_snake_case_name_to_words(function_name) for function_name in function_names])


def split_snake_case_name_to_words(name):
    return [n for n in name.split('_') if n]

#комментарий
def get_top_verbs_in_path(path, top_size=10):
    global Path
    Path = path
    trees = [t for t in get_trees(None) if t]
    #разбить на строки или вынести в отдельный метод
    fncs = [f for f in
            flat([[node.name.lower() for node in ast.walk(t) if isinstance(node, ast.FunctionDef)] for t in trees]) if
            not (f.startswith('__') and f.endswith('__'))]
    #не информативный лог, может написать какая функция была получена?
    print('functions extracted')
    verbs = flat([get_verbs_from_function_name(function_name) for function_name in fncs])
    return collections.Counter(verbs).most_common(top_size)

#комментарий
def get_top_functions_names_in_path(path, top_size=10):
    t = get_trees(path)
    #разбить на строки или вынести в отдельный метод
    nms = [f for f in
           flat([[node.name.lower() for node in ast.walk(t) if isinstance(node, ast.FunctionDef)] for t in t]) if
           not (f.startswith('__') and f.endswith('__'))]
    return collections.Counter(nms).most_common(top_size)

#а в начале это нельзя указать? Или все точку входа делают внизу у вас?
Path = ''
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

top_size=200
print('total %s words, %s unique' % (len(wds), len(set(wds))))
#можно так. Или вынести в константу, если этот параметр часто должен меняться из кода
#for word, occurence in collections.Counter(wds).most_common(top_size=200):
for word, occurence in collections.Counter(wds).most_common(top_size):
    print(word, occurence)
