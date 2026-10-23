from omega_common import *
import json
def show(n,p):
 p=pathlib.Path(p)
 if p.is_file():
  try:print(n,json.dumps(read(p),indent=2))
  except Exception:print(n,p.read_text()[-8000:])
def main():
 print('=== RARI OMEGA FINAL V2 STATUS ===');print('SERVICE',json.dumps(unit_props(UNIT),sort_keys=True));
 phases={}
 if (ROOT/'phases').exists():
  for d in sorted((ROOT/'phases').iterdir()):
   if d.is_dir():
    if (d/'COMMIT.json').is_file(): phases[d.name]='COMMITTED'
    elif (d/'FAILURE.json').is_file(): phases[d.name]='FAILED'
    else: phases[d.name]='STARTED'
 if phases: print('PHASES',json.dumps(phases,sort_keys=True))
 for n,p in [('FAILURE',ROOT/'FAILURE.json'),('PREFLIGHT',ROOT/'control/PREFLIGHT.json'),('SYNTHETIC',ROOT/'results/synthetic/SYNTHETIC_OMEGA_RESULTS.json'),('REALBIO',ROOT/'results/realbio/REALBIO_OMEGA_RESULTS.json'),('GOP',ROOT/'results/gop/GOP_OMEGA_RESULTS.json'),('FORMULATION',ROOT/'results/OMEGA_FORMULATION.json'),('AUDIT',ROOT/'results/INDEPENDENT_AUDIT_OMEGA.json'),('RESULTS_LOCK',ROOT/'RESULTS_LOCK.json'),('FINAL_STATUS',ROOT/'FINAL_STATUS.json'),('DRIVE',ROOT/'control/DRIVE_RECEIPT.json')]:show(n,p)
 if (V1/'BUDGET_STATE.json').is_file():
  x=read(V1/'BUDGET_STATE.json');print('OLD_SHARED_BUDGET',json.dumps({'active_since_epoch':x.get('active_since_epoch'),'holds':x.get('holds'),'available_usd':x.get('available_usd')},sort_keys=True))
 return 0
if __name__=='__main__':raise SystemExit(main())
