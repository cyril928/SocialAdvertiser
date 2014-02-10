#!/usr/bin/env/ python
import time
import subprocess

while(1):
	args = ['make','-C','/home/shliew/socialad-final-ver/']
	p = subprocess.Popen(args);
	p.wait()
	time.sleep(3600)
	
