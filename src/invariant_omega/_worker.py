"""Isolated worker. Historical cloud/deployment preflight is deliberately not invoked."""
from __future__ import annotations
import argparse,datetime,json,os,platform,sys,traceback
from pathlib import Path
from .validation import package_root,sha256_file,verify_frozen

BLOCKED_EVENTS={'socket.connect','socket.bind','subprocess.Popen','os.system','os.exec','os.posix_spawn','os.posix_spawnp'}

def main() -> int:
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True,type=Path);parser.add_argument('--mode',choices=['fixture','synthetic','gop-controls'],required=True);args=parser.parse_args()
    output=args.output.resolve();frozen=package_root()/'_frozen';attempts=[]
    def audit(event:str,arguments:tuple) -> None:
        if event in BLOCKED_EVENTS:
            attempts.append(event)
            raise RuntimeError('Local replay forbids external network/process event: '+event)
    sys.addaudithook(audit);sys.dont_write_bytecode=True
    receipt={'mode':args.mode,'python':platform.python_version(),'platform':list(os.uname()) if hasattr(os,'uname') else [sys.platform,os.name],'blocked_external_event_attempts':attempts,'audit_hook_boundary':'Python audit events; not an operating-system sandbox','original_remote_preflight':'NOT_EXECUTED_NOT_CLAIMED','scientific_source_modified':False,'new_independent_experiment':False}
    exitcode=0
    try:
        verify_frozen();sys.path.insert(0,str(frozen));sys.path.insert(0,str(frozen/'reference'))
        import omega_common as common
        common.PKG=frozen;common.ROOT=output;common.PROTOCOL=frozen/'OMEGA_PROTOCOL.json';common.PYTHON=Path(sys.executable)
        import numpy as np
        import scipy
        import omega_synth as synth
        receipt.update({'numpy':np.__version__,'scipy':scipy.__version__,'numpy_path':np.__file__,'scipy_path':scipy.__file__})
        if np.__version__!='2.3.5' or scipy.__version__!='1.17.0':raise RuntimeError('Use pinned NumPy 2.3.5 and SciPy 1.17.0; other environments not accepted by this release')
        if args.mode=='synthetic':
            receipt['outputs']=synth.run()
            receipt['result_sha256']=sha256_file(output/'results/synthetic/SYNTHETIC_OMEGA_RESULTS.json')
        elif args.mode=='gop-controls':
            import omega_gop as g
            values=[g.g1_gauge(),g.g2_inverse_square(),g.g3_quintic_stochastic(),g.g4_s05(),g.g5_s07(),g.g6_quantum_learned(),g.g7_memory()]
            common.write(output/'GOP_CONTROL_RESULTS.json',values)
            receipt['case_count']=len(values)
            receipt['foundation_tests']='NOT_RUN_BY_THIS_MODE'
            receipt['result_sha256']=sha256_file(output/'GOP_CONTROL_RESULTS.json')
        else:
            import hashlib
            from reference.rari_neurobrain.world import Bank
            from omega_localfleet import LocalFleet
            key=hashlib.sha256(common.protocol()['synthetic']['seed_label'].encode()).digest()
            row=synth._direct_probe(LocalFleet(),Bank(key),'closed_test',2080,'balanced',0)
            common.write(output/'FIXTURE_RESULT.json',row)
            receipt['fixture']={'family':row['family'],'rank':row['Fhat']['rank'],'reconstruction_mse':row['reconstruction_mse'],'filter_mse':row['filter_mse']}
        receipt['status']='PASS'
    except Exception as exc:
        receipt.update({'status':'FAILED','error':type(exc).__name__+': '+str(exc),'traceback':traceback.format_exc()});exitcode=1
    receipt['completed_utc']=datetime.datetime.now(datetime.timezone.utc).isoformat()
    (output/'WORKER_RECEIPT.json').write_text(json.dumps(receipt,indent=2,allow_nan=False)+'\n');return exitcode
if __name__=='__main__':raise SystemExit(main())
