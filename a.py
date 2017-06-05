#!/usr/bin/env python3

TOKEN = "XXX"

# $ grep issues docs/release/notes-0.8.rst| cut -f 2 -d" "|sed 's/^`//'|sed 's/^#/diofant\/diofant#/'|sed 's/[#/]/ /g' > issues.txt
# $ grep pull docs/release/notes-0.8.rst|cut -f2 -d" "|sed 's/^`#//' > pulls.txt

issues = []
f = io.open('issues.txt', 'r')
for i, l in enumerate(f.readlines()):
    a = l.split(" ")
    issues.append({"owner": a[0], "repo": a[1], "issue": a[2].strip()})
f.close()
for n, i in enumerate(issues):
    req = urllib.request.Request('https://api.github.com/repos/' + i['owner'] + '/' + i['repo'] + '/issues/' + i['issue'])
    req.add_header('Authorization', 'token %s' % TOKEN)
    r = urllib.request.urlopen(req)
    j = json.load(io.StringIO(r.readlines()[0].decode('utf-8')))
    r.close()
    issues[n]['title'] = j['title']
    print(issues[n])
for i in issues:
    if i['repo'] == "sympy":
        print("* `sympy/sympy#" + i['issue'] + " <http://https://github.com/sympy/sympy/issues/" + i['issue'] + ">`_ " + i['title'])
    else:
        print("* `#" + i['issue'] + " <http://https://github.com/diofant/diofant/issues/" + i['issue'] + ">`_ " + i['title'])

f = open('pulls.txt', 'r')
pulls = []
for l in f.readlines():
    pulls.append({'pull': l.strip()})
f.close()
for n, i in enumerate(pulls):
    req = urllib.request.Request('https://api.github.com/repos/diofant/diofant/pulls/' + i['pull'])
    req.add_header('Authorization', 'token %s' % TOKEN)
    r = urllib.request.urlopen(req)
    j = json.load(io.StringIO(r.readlines()[0].decode('utf-8')))
    r.close()
    pulls[n]['title'] = j['title']
    print(pulls[n])
for p in pulls:
    print("* `#" + i['pull'] + " <http://https://github.com/diofant/diofant/pull/"+i['pull'] + ">`_ " + i['title'])
