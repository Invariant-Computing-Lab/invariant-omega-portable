"""Explicit data validation and comparison; no implicit scientific acceptance."""
from __future__ import annotations
import hashlib,json,math
from pathlib import Path
from typing import Any

class ValidationError(ValueError):
    pass


def package_root() -> Path:
    return Path(__file__).resolve().parent


def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda:stream.read(1024*1024),b''):
            h.update(block)
    return h.hexdigest()


def verify_frozen(root: Path | None=None) -> dict:
    base=package_root();root=root or base/'_frozen'
    expected=json.loads((base/'_frozen_hashes.json').read_text(encoding='utf-8'))
    errors=[]
    for relative,digest in expected.items():
        p=root/relative
        if p.is_symlink() or not p.is_file():
            errors.append({'path':relative,'error':'missing_or_symlink'})
        elif sha256_file(p)!=digest:
            errors.append({'path':relative,'error':'sha256_mismatch'})
    extras=[str(p.relative_to(root)) for p in root.rglob('*') if p.is_file() and str(p.relative_to(root)) not in expected and '__pycache__' not in p.parts]
    if extras:
        errors.append({'error':'unexpected_frozen_files','files':sorted(extras)})
    if errors:
        raise ValidationError(json.dumps({'frozen_integrity':'FAILED','errors':errors}))
    p=json.loads((root/'OMEGA_PROTOCOL.json').read_text())
    for field in ['E2B_calls_authorized','Kimi_calls_authorized','provider_calls_authorized']:
        if p['execution'].get(field)!=0:
            raise ValidationError('External calls not permitted: '+field)
    return {'status':'PASS','files_checked':len(expected),'protocol_sha256':expected['OMEGA_PROTOCOL.json'],'manifest_sha256':expected['PACKAGE_MANIFEST.json'],'source_code_unchanged':True,'original_remote_preflight':'NOT_EXECUTED_NOT_CLAIMED'}


def compare_values(actual: Any, expected: Any, *, atol:float=1e-10, rtol:float=1e-8) -> dict:
    """Recursive structured comparison. Exact strings/keys; bounded finite numeric tolerance."""
    if not math.isfinite(atol) or not math.isfinite(rtol) or atol<0 or rtol<0:
        raise ValidationError('Tolerances must be finite and nonnegative')
    mismatches=[];numeric=0;exact=0;maxabs=0.;maxrel=0.
    def visit(a:Any,b:Any,path:str) -> None:
        nonlocal numeric,exact,maxabs,maxrel
        if isinstance(a,bool) or isinstance(b,bool):
            if type(a) is not type(b) or a!=b:mismatches.append({'path':path,'actual':a,'expected':b})
            else:exact+=1
        elif isinstance(a,(int,float)) and isinstance(b,(int,float)):
            numeric+=1
            if not math.isfinite(a) or not math.isfinite(b):
                mismatches.append({'path':path,'error':'nonfinite_numeric'});return
            delta=abs(a-b);maxabs=max(maxabs,delta);maxrel=max(maxrel,delta/max(abs(b),1e-300))
            # Integer counts/seeds must be exact, never rounded into agreement.
            ok=a==b if isinstance(a,int) and isinstance(b,int) else math.isclose(a,b,abs_tol=atol,rel_tol=rtol)
            if not ok:mismatches.append({'path':path,'actual':a,'expected':b,'absolute_difference':delta})
        elif isinstance(a,dict) and isinstance(b,dict):
            if set(a)!=set(b):mismatches.append({'path':path,'missing_keys':sorted(set(b)-set(a)),'extra_keys':sorted(set(a)-set(b))})
            for key in sorted(set(a)&set(b)):visit(a[key],b[key],path+'/'+str(key))
        elif isinstance(a,list) and isinstance(b,list):
            if len(a)!=len(b):mismatches.append({'path':path,'actual_length':len(a),'expected_length':len(b)})
            for index,(aa,bb) in enumerate(zip(a,b)):visit(aa,bb,path+'/'+str(index))
        elif type(a) is not type(b) or a!=b:
            mismatches.append({'path':path,'actual':a,'expected':b})
        else:exact+=1
    visit(actual,expected,'')
    return {'status':'PASS' if not mismatches else 'FAILED','numeric_leaves':numeric,'exact_other_leaves':exact,'max_absolute_difference':maxabs,'max_relative_difference':maxrel,'atol':atol,'rtol':rtol,'mismatch_count':len(mismatches),'mismatches':mismatches,'interpretation':'Computational replay agreement only; not a new independent experiment or biological validation.'}
