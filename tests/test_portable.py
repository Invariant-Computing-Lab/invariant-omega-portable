from __future__ import annotations
import contextlib,io,json,math,os,pathlib,shutil,subprocess,sys,tempfile,unittest
from invariant_omega.validation import ValidationError,compare_values,verify_frozen,package_root
from invariant_omega.cli import main,run

class ComparisonTests(unittest.TestCase):
    def test_identical_structure(self):self.assertEqual(compare_values({'a':[1,2.,'x',True,None]},{'a':[1,2.,'x',True,None]})['status'],'PASS')
    def test_numeric_tolerance(self):self.assertEqual(compare_values(1.000000001,1.)['status'],'PASS')
    def test_reject_numeric_difference(self):self.assertEqual(compare_values(1.01,1.)['status'],'FAILED')
    def test_exact_integer_counts(self):self.assertEqual(compare_values(10000000001,10000000000)['status'],'FAILED')
    def test_reject_nonfinite_actual(self):self.assertEqual(compare_values(float('nan'),1.)['status'],'FAILED')
    def test_reject_nonfinite_reference(self):self.assertEqual(compare_values(1.,float('inf'))['status'],'FAILED')
    def test_bool_not_numeric(self):self.assertEqual(compare_values(True,1)['status'],'FAILED')
    def test_missing_key(self):self.assertEqual(compare_values({'a':1},{'a':1,'b':2})['status'],'FAILED')
    def test_extra_key(self):self.assertEqual(compare_values({'a':1,'b':2},{'a':1})['status'],'FAILED')
    def test_list_length(self):self.assertEqual(compare_values([1,2],[1])['status'],'FAILED')
    def test_status_exact(self):self.assertEqual(compare_values({'status':'SUPPORT'},{'status':'CHALLENGE'})['status'],'FAILED')
    def test_nested_path(self):self.assertEqual(compare_values({'a':[1.,3.]},{'a':[1.,2.]})['mismatches'][0]['path'],'/a/1')
    def test_negative_tolerance(self):
        with self.assertRaises(ValidationError):compare_values(1.,1.,atol=-1)
    def test_nan_tolerance(self):
        with self.assertRaises(ValidationError):compare_values(1.,1.,rtol=float('nan'))
    def test_full_reference_self(self):
        r=json.loads((package_root()/'reference_results/SYNTHETIC_OMEGA_RESULTS.json').read_text());c=compare_values(r,r);self.assertEqual(c['status'],'PASS');self.assertGreater(c['numeric_leaves'],1000)

class IntegrityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory();cls.root=pathlib.Path(cls.temp.name)/'frozen';shutil.copytree(package_root()/'_frozen',cls.root)
    @classmethod
    def tearDownClass(cls):cls.temp.cleanup()
    def test_original_integrity(self):self.assertEqual(verify_frozen()['files_checked'],23)
    def test_reject_protocol_change(self):
        p=self.root/'OMEGA_PROTOCOL.json';b=p.read_bytes()
        try:
            p.write_bytes(b+b' ')
            with self.assertRaises(ValidationError):verify_frozen(self.root)
        finally:p.write_bytes(b)
    def test_reject_source_change(self):
        p=self.root/'omega_synth.py';b=p.read_bytes()
        try:
            p.write_bytes(b+b'\n# modified\n')
            with self.assertRaises(ValidationError):verify_frozen(self.root)
        finally:p.write_bytes(b)
    def test_missing_file(self):
        p=self.root/'omega_status.py';b=p.read_bytes()
        try:
            p.unlink()
            with self.assertRaises(ValidationError):verify_frozen(self.root)
        finally:p.write_bytes(b)
    def test_extra_file(self):
        p=self.root/'unexpected.py'
        try:
            p.write_text('x=1')
            with self.assertRaises(ValidationError):verify_frozen(self.root)
        finally:p.unlink(missing_ok=True)

class InterfaceTests(unittest.TestCase):
    def setUp(self):self.temp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.temp.name)
    def tearDown(self):self.temp.cleanup()
    def test_refuse_existing_empty_directory(self):
        with self.assertRaises(ValidationError):run(self.root)
    def test_refuse_existing_nonempty_directory_without_write(self):
        p=self.root/'important.txt';p.write_text('unchanged')
        with self.assertRaises(ValidationError):run(self.root)
        self.assertEqual(p.read_text(),'unchanged')
    def test_refuse_missing_parent(self):
        with self.assertRaises(ValidationError):run(self.root/'absent'/'run')
    def test_refuse_symlink(self):
        p=self.root/'linked';p.symlink_to(self.root/'notthere')
        with self.assertRaises(ValidationError):run(p)
    def test_invalid_timeout(self):
        with self.assertRaises(ValidationError):run(self.root/'run',timeout_seconds=0)
    def test_unknown_mode(self):
        with self.assertRaises(ValidationError):run(self.root/'run',mode='remote')
    def test_cli_reports_missing_json(self):
        with contextlib.redirect_stderr(io.StringIO()):self.assertEqual(main(['compare',str(self.root/'missing'),str(self.root/'another')]),2)
    def test_installed_fixture_outside_repository(self):
        dest=self.root/'fixture'
        result=subprocess.run([sys.executable,'-I','-B','-m','invariant_omega','run','--output',str(dest),'--mode','fixture','--timeout-seconds','60'],cwd=self.root,capture_output=True,text=True,timeout=70)
        self.assertEqual(result.returncode,0,result.stderr+result.stdout)
        r=json.loads((dest/'RUN_RECEIPT.json').read_text());self.assertEqual(r['status'],'PASS');self.assertEqual(r['worker']['blocked_external_event_attempts'],[])
        self.assertFalse(r['biological_replay']);self.assertEqual(r['worker']['fixture']['family'],2080)
        self.assertEqual(r['remote_system_preflight'],'NOT_EXECUTED_NOT_CLAIMED')
    def test_audit_blocks_network_and_subprocess(self):
        # Test the same policy events in a disposable interpreter, never contacts a network.
        source="""import sys,socket,subprocess\nfrom invariant_omega._worker import BLOCKED_EVENTS\nhits=[]\ndef guard(event,args):\n if event in BLOCKED_EVENTS:\n  hits.append(event); raise RuntimeError('blocked')\nsys.addaudithook(guard)\nfor f in [lambda:socket.socket().connect(('127.0.0.1',1)),lambda:subprocess.run([sys.executable,'-c','pass'])]:\n try:f()\n except RuntimeError:pass\n else:raise AssertionError('guard did not block')\nassert hits==['socket.connect','subprocess.Popen'],hits\n"""
        r=subprocess.run([sys.executable,'-I','-B','-c',source],capture_output=True,text=True,timeout=20);self.assertEqual(r.returncode,0,r.stderr)

if __name__=='__main__':unittest.main(verbosity=2)
