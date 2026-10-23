from pathlib import Path
import csv,hashlib,base64,io,zipfile
root=Path(__file__).resolve().parents[1];src=root/'src';dist=root/'dist';dist.mkdir(exist_ok=True)
entries={str(p.relative_to(src)):p.read_bytes() for p in sorted(src.rglob('*')) if p.is_file() and '__pycache__' not in p.parts};info='invariant_omega_portable-0.2.0.dist-info'
entries[info+'/METADATA']=b'Metadata-Version: 2.1\nName: invariant-omega-portable\nVersion: 0.2.0\nSummary: Isolated private replay of preserved OMEGA kernels\nRequires-Python: >=3.11\nRequires-Dist: numpy==2.3.5\nRequires-Dist: scipy==1.17.0\n\nNo license granted; private preparation package.\n'
entries[info+'/WHEEL']=b'Wheel-Version: 1.0\nGenerator: invariant-private-repro-builder-1\nRoot-Is-Purelib: true\nTag: py3-none-any\n'
entries[info+'/entry_points.txt']=b'[console_scripts]\ninvariant-omega = invariant_omega.cli:main\n'
entries[info+'/top_level.txt']=b'invariant_omega\n'
rows=[]
for n,b in sorted(entries.items()):rows.append([n,'sha256='+base64.urlsafe_b64encode(hashlib.sha256(b).digest()).rstrip(b'=').decode(),str(len(b))])
s=io.StringIO(newline='');w=csv.writer(s,lineterminator='\n');w.writerows(rows+[[info+'/RECORD','','']]);entries[info+'/RECORD']=s.getvalue().encode()
p=dist/'invariant_omega_portable-0.2.0-py3-none-any.whl'
with zipfile.ZipFile(p,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
 for n,b in sorted(entries.items()):z.writestr(n,b)
print(p,p.stat().st_size,hashlib.sha256(p.read_bytes()).hexdigest())
