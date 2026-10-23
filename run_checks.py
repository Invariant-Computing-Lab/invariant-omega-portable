import subprocess,sys
if __name__=='__main__':sys.exit(subprocess.call([sys.executable,'-m','unittest','discover','-s','tests','-v']))
