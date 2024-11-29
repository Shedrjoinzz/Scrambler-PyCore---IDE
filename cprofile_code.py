# from metapensiero.pytkell import exec_code
from radon.complexity import cc_visit
from radon.visitors import ComplexityVisitor

def profile_user_code(user_code: str):
    code = user_code
    blocks = cc_visit(code)
    _dict = {}
    for block in blocks:
        _dict[block.name] = block.complexity
    
    return _dict

