from __future__ import annotations
import pathlib,json
from omega_common import *
def main():
 issues=[];checks=[]
 def ck(cond,name,detail=None):
  checks.append({'check':name,'pass':bool(cond),'detail':detail});
  if not cond:issues.append(name if detail is None else name+':'+str(detail))
 ck(sha(V4/'RESULTS_LOCK.json')==EXPECTED_V4_LOCK,'OLD_V4_LOCK_UNCHANGED')
 a7=read(V4/'results/INDEPENDENT_AUDIT_V7.json');ck(a7.get('approved') is True and not a7.get('issues'),'V7_PRIOR_AUDIT_APPROVED')
 syn=read(ROOT/'results/synthetic/SYNTHETIC_OMEGA_RESULTS.json');ck(syn.get('status')=='COMPLETED_ALL_DECLARED_SYNTHETIC_ATTEMPTS','SYNTH_TERMINAL')
 ck(len(syn.get('hypothesis_cards',{}))==10,'SYNTH_TEN_CARDS',len(syn.get('hypothesis_cards',{})))
 bio=read(ROOT/'results/realbio/REALBIO_OMEGA_RESULTS.json');ck(bio.get('status')=='COMPLETED_ALL_NINE_REALBIO_TRACK_REPLAY_AND_TRANSLATION_ATTEMPTS','REALBIO_TERMINAL');ck(len(bio.get('tracks',[]))==9,'REALBIO_NINE_TRACKS',len(bio.get('tracks',[])))
 gop=read(ROOT/'results/gop/GOP_OMEGA_RESULTS.json');ck(gop.get('core_sha256')==EXPECTED_GOP_CORE and gop.get('core_mutated') is False,'GOP_CORE_UNCHANGED');ck(len(gop.get('finite_tests',[]))==7,'GOP_SEVEN_FINITE_TESTS');ck(all(x.get('status')=='UNRESOLVED_NOT_TESTED_BY_THIS_BATTERY' for x in gop.get('unresolved',[])),'GOP_UNIVERSAL_LIMITS_PRESERVED')
 ck((ROOT/'delivery/GOP_OMEGA_ADDON.zip').is_file(),'GOP_ADDON_EXISTS')
 # Old worker/budget state still quiescent after local-only work.
 clean=read(V4/'control/CLEANUP.json');c=clean.get('counts',{});ck(clean.get('all_paused') and c.get('paused')==100 and c.get('running')==0,'OLD_COHORT_STILL_PAUSED')
 led=read(V1/'BUDGET_STATE.json');ck(led.get('active_since_epoch') is None and not led.get('holds'),'OLD_PROVIDER_BUDGET_STILL_IDLE')
 out={'schema':'rari.omega.independent_deterministic_audit.v1','approved':not issues,'issues':issues,'checks':checks,'scope':'completion,immutability,and evidence-integrity audit; does not require favorable scientific outcomes','assumptions':['Real-bio R2 is retrospective retained-evidence replay/translation; frozen scorer replay or unit-like evidence does not equal new prospective biological validation.','Synthetic confirmation is new local simulation under a frozen public seed namespace.','GOP finite sidecar does not validate universal U, GR, QFT, Lorentz covariance, global apparatus closure, or human/clinical relevance.']}
 write(ROOT/'results/INDEPENDENT_AUDIT_OMEGA.json',out);print(json.dumps(out,indent=2));return 0 if out['approved'] else 2
if __name__=='__main__':raise SystemExit(main())
