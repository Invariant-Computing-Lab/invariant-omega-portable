from __future__ import annotations
import hashlib,json,os,pathlib,zipfile
from omega_common import *
DRIVE_ID='1id9BWVOEQcS9eyOOy7JkuS_7Qfhkyhy6'
def build_archive():
 d=ROOT/'delivery';d.mkdir(parents=True,exist_ok=True);zpath=d/'omega_final.zip'
 include=[]
 for rel in ['OMEGA_FREEZE.json','FINAL_STATUS.json','RESULTS_LOCK.json','control/PREFLIGHT.json','control/FINAL_MANIFEST.json','results/INDEPENDENT_AUDIT_OMEGA.json']:
  p=ROOT/rel
  if p.is_file():include.append(p)
 for base in [ROOT/'results',ROOT/'phases',ROOT/'private',ROOT/'synthetic_workspace']:
  if base.exists():include += [p for p in all_files(base) if p not in include]
 # GOP frozen source archive is included once, not the mutable extracted working copy.
 include.append(PKG/'inputs/GOP_TOE_FOUNDATION_v1_0.zip');include.append(PKG/'OMEGA_PROTOCOL.json');include.append(PKG/'inputs/LEGACY_REALBIO_V5_SUMMARY.json')
 with zipfile.ZipFile(zpath,'w',zipfile.ZIP_DEFLATED,compresslevel=3,allowZip64=True) as z:
  for p in sorted(set(include)):
   if str(p).startswith(str(PKG)):arc='source_inputs/'+p.name
   else:arc=str(p.relative_to(ROOT))
   z.write(p,arc)
 rec={'at':utc(),'archive':str(zpath),'sha256':sha(zpath),'size_bytes':zpath.stat().st_size,'old_v4_results_lock_sha256':sha(V4/'RESULTS_LOCK.json'),'gop_core_sha256':EXPECTED_GOP_CORE};write(ROOT/'control/LOCAL_PACKAGE_RECEIPT.json',rec);return rec
def upload():
 z=ROOT/'delivery/omega_final.zip';require(z.is_file(),'OMEGA_ARCHIVE_NOT_READY');remote='gdrive:final_runs/rari_omega_final_v2';base=['rclone','--drive-root-folder-id',DRIVE_ID,'--retries','3','--low-level-retries','5','--drive-chunk-size','64M','--log-level','NOTICE'];p=cmd(base+['copyto',str(z),remote+'/omega_final.zip','--checksum'],timeout=7200);require(p.returncode==0,'OMEGA_DRIVE_COPY_FAILED:'+p.stderr[-700:]);md5=hashlib.md5(z.read_bytes()).hexdigest();q=cmd(base+['md5sum',remote+'/omega_final.zip'],timeout=300);require(q.returncode==0 and q.stdout.split()[0].lower()==md5,'OMEGA_DRIVE_MD5_MISMATCH');rec={'at':utc(),'status':'VERIFIED_IMMUTABLE_ARCHIVE','remote':remote+'/omega_final.zip','sha256':sha(z),'md5':md5,'root_folder_id':DRIVE_ID};write(ROOT/'control/DRIVE_RECEIPT.json',rec);return rec
def main():
 if not (ROOT/'delivery/omega_final.zip').is_file():build_archive()
 print(json.dumps(upload(),indent=2));return 0
if __name__=='__main__':raise SystemExit(main())
