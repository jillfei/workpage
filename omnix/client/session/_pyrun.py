import subprocess
node = r"C:\Program Files\nodejs\node.exe"
script = r"C:\Users\zhaonan\Desktop\多agent\_check.js"
out = []
try:
    r = subprocess.run([node, script], capture_output=True, text=True, timeout=30)
    out.append("rc=" + str(r.returncode))
    out.append("STDOUT=" + (r.stdout or ""))
    out.append("STDERR=" + (r.stderr or ""))
except Exception as e:
    out.append("SUBPROCESS_ERROR: " + repr(e))
open(r"C:\Users\zhaonan\Desktop\多agent\_pyout.txt", "w", encoding="utf-8").write("\n".join(out))
