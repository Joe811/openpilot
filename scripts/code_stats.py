#!/usr/bin/env python3
import os
import ast
import stat
import subprocess

fouts = set([x.decode('utf-8') for x in subprocess.check_output(['git', 'ls-files']).strip().split()])

pyf = []
for d in ["cereal", "common", "scripts", "selfdrive", "tools"]:
  for root, dirs, files in os.walk(d):
    for f in files:
      if f.endswith(".py"):
        pyf.append(os.path.join(root, f))

imps = set()

class Analyzer(ast.NodeVisitor):
  def visit_Import(self, node):
    for alias in node.names:
      imps.add(alias.name)
    self.generic_visit(node)

  def visit_ImportFrom(self, node):
    imps.add(node.module)
    self.generic_visit(node)

tlns = 0
for f in sorted(pyf):
  if f not in fouts:
    continue
  xbit = bool(os.stat(f)[stat.ST_MODE] & stat.S_IXUSR)
  src = open(f).read()
  lns = len(src.split("\n"))
  tree = ast.parse(src)
  Analyzer().visit(tree)
  print("%5d %s %s" % (lns, f, xbit))
  tlns += lns

print("%d lines of parsed openpilot python" % tlns)
#print(sorted(list(imps)))
