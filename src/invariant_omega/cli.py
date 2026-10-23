"""Private, path-independent OMEGA command line. No automatic publishing or cloud calls."""
from __future__ import annotations
import argparse,datetime,json,os,subprocess,sys
from pathlib import Path
from .validation import ValidationError,compare_values,package_root,verify_frozen

def now() -> str:
    return datetime.datetime.now(datetime.timezone.utc).isoformat()

def write_json(path:Path,data:dict) -> None:
    path.write_text(json.dumps(data,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def run(output:Path, timeout_seconds:float=1200., mode:str='synthetic') -> int:
    if not 1<=timeout_seconds<=7200:
        raise ValidationError('timeout_seconds must be between 1 and 7200')
    if mode not in {'synthetic','fixture','gop-controls'}:raise ValidationError('Unknown mode')
    report=verify_frozen()
    output=output.absolute()
    # Refuse all existing roots, including empty directories and dangling symlinks.
    if output.exists() or output.is_symlink():raise ValidationError('Output must not exist; replay never reuses or overwrites a previous run')
    for parent in output.parents:
        if parent.is_symlink():raise ValidationError('Symlinked output parent is not supported')
    if not output.parent.is_dir():raise ValidationError('Output parent must already exist')
    output.mkdir(mode=0o700)
    receipt={'schema':'invariant.omega.replay.v1','started_utc':now(),'status':'RUNNING','mode':mode,'frozen_integrity':report,'new_independent_experiment':False,'biological_replay':False,'remote_system_preflight':'NOT_EXECUTED_NOT_CLAIMED'}
    write_json(output/'RUN_RECEIPT.json',receipt)
    env={k:v for k,v in os.environ.items() if k not in {'PYTHONPATH','PYTHONHOME'}}
    env.update({'OPENBLAS_NUM_THREADS':'1','OMP_NUM_THREADS':'1','MKL_NUM_THREADS':'1','PYTHONDONTWRITEBYTECODE':'1'})
    command=[sys.executable,'-I','-B','-m','invariant_omega._worker','--output',str(output),'--mode',mode]
    try:
        with (output/'stdout.log').open('w') as stdout,(output/'stderr.log').open('w') as stderr:
            process=subprocess.run(command,cwd=output,env=env,stdout=stdout,stderr=stderr,timeout=timeout_seconds,check=False)
        receipt.update({'worker_exit_code':process.returncode,'status':'PASS' if process.returncode==0 else 'FAILED','completed_utc':now()})
    except OSError as exc:
        receipt.update({'status':'FAILED','completed_utc':now(),'error':str(exc)})
        write_json(output/'RUN_RECEIPT.json',receipt);print(json.dumps(receipt));return 2
    except subprocess.TimeoutExpired:
        receipt.update({'status':'TIMEOUT','completed_utc':now(),'timeout_seconds':timeout_seconds})
        write_json(output/'RUN_RECEIPT.json',receipt);print(json.dumps(receipt));return 124
    if (output/'WORKER_RECEIPT.json').is_file():receipt['worker']=json.loads((output/'WORKER_RECEIPT.json').read_text())
    if process.returncode==0 and mode in {'synthetic','gop-controls'}:
        actual_path=output/('results/synthetic/SYNTHETIC_OMEGA_RESULTS.json' if mode=='synthetic' else 'GOP_CONTROL_RESULTS.json')
        expected_path=package_root()/'reference_results'/('SYNTHETIC_OMEGA_RESULTS.json' if mode=='synthetic' else 'GOP_CONTROL_REFERENCE.json')
        actual=json.loads(actual_path.read_text());expected=json.loads(expected_path.read_text())
        comparison=compare_values(actual,expected)
        write_json(output/'REFERENCE_COMPARISON.json',comparison);receipt['reference_comparison']= {k:v for k,v in comparison.items() if k!='mismatches'}
        if comparison['status']!='PASS':receipt['status']='COMPLETED_REFERENCE_MISMATCH'
    write_json(output/'RUN_RECEIPT.json',receipt);print(json.dumps(receipt,indent=2))
    return 0 if receipt['status']=='PASS' else 1

def main(argv:list[str]|None=None) -> int:
    parser=argparse.ArgumentParser(description=__doc__);sub=parser.add_subparsers(dest='command',required=True)
    sub.add_parser('verify',help='Check original source/protocol/inputs against packaged hashes')
    r=sub.add_parser('run',help='Replay in a fresh local output directory; no cloud engine is invoked');r.add_argument('--output',type=Path,required=True);r.add_argument('--timeout-seconds',type=float,default=1200);r.add_argument('--mode',choices=['synthetic','fixture','gop-controls'],default='synthetic')
    c=sub.add_parser('compare',help='Compare two result JSON objects');c.add_argument('actual',type=Path);c.add_argument('expected',type=Path)
    args=parser.parse_args(argv)
    try:
        if args.command=='verify':print(json.dumps(verify_frozen(),indent=2));return 0
        if args.command=='run':return run(args.output,args.timeout_seconds,args.mode)
        report=compare_values(json.loads(args.actual.read_text()),json.loads(args.expected.read_text()));print(json.dumps(report,indent=2));return 0 if report['status']=='PASS' else 1
    except (ValidationError,OSError,json.JSONDecodeError) as exc:
        print(json.dumps({'status':'FAILED','error':str(exc)}),file=sys.stderr);return 2
if __name__=='__main__':raise SystemExit(main())
