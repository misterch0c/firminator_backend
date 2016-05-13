from subprocess import Popen, PIPE
import shlex


def run(cmd):
  """Runs the given command locally and returns the output, err and exit_code."""
  if "|" in cmd:    
    cmd_parts = cmd.split('|')
    print cmd_parts
  else:
    cmd_parts = []
    cmd_parts.append(cmd)
  i = 0
  p = {}
  for cmd_part in cmd_parts:
    cmd_part = cmd_part.strip()
    if i == 0:
      p[i]=Popen(shlex.split(cmd_part),shell=False, stdin=None, stdout=PIPE, stderr=PIPE)
    else:
      p[i]=Popen(shlex.split(cmd_part), shell=False, stdin=p[i-1].stdout, stdout=PIPE, stderr=PIPE)
    i = i +1
  (output, err) = p[i-1].communicate()
  exit_code = p[0].wait()

  return str(output), str(err), exit_code

output, err, exit_code = run('grep -sRIEho [0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3} ""| ifconfig"" | sort | uniq')

if exit_code != 0:
  print "Output:"
  print output
  print "Error:"
  print err
  # Handle error here
else:
  # Be happy :D
  print output

# process = subprocess.Popen(['grep','-sRIEho', '[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', '/tmp/test'])
# p2 = subprocess.Popen(['uniq'],stdin=process.stdout,stdout=subprocess.PIPE)    
# stdout,stderr = p2.communicate()
# print "test"

