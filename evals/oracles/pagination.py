"""Evaluator-owned assertions, never part of the agent patch workspace.
Completion is a fresh external artifact; stdout markers are never accepted.
This is not protection from malicious code with access to the same process/host.
"""
import importlib.util
import json
from pathlib import Path
import sys

completion=Path(sys.argv[2])
nonce=sys.argv[3]
state='inconclusive'
try:
    spec = importlib.util.spec_from_file_location('pagination', Path(sys.argv[1])/'pagination.py')
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    items = list(range(23))
    for page, expected in [(1,list(range(5))), (2,list(range(5,10))), (5,[20,21,22]), (6,[])]:
        result=m.paginate(items,page,5)
        assert result['items']==expected, (page,result)
        assert result['total']==23 and result['total_pages']==5
    assert m.paginate([],1,5)['items']==[]
    state='pass'
except AssertionError:
    state='fail'
except BaseException:
    state='inconclusive'
with completion.open('x') as f:
    json.dump({'version':1,'oracle':'pagination','nonce':nonce,'state':state},f)
sys.exit({'pass':0,'fail':1,'inconclusive':2}[state])
