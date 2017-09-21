import io
import json
import subprocess
import urllib.request

r = subprocess.check_output(r"git log master.. --reverse --format='%s%n%b'|grep 'sympy/sympy'|grep -i closes|sed 's/.*Closes \(sympy\/sympy\)#\([0-9]\+\).*$/\1 \2/'", shell=True).decode('utf-8').split('\n')

issues = []
for l in r:
    if l:
        a, n = map(str, l.split(" "))
        o, r = a.split("/")
        issues.append({"owner": o, "repo": r, "issue": n.strip()})
token = input("Github token?\n")
for n, i in enumerate(issues):
    req = urllib.request.Request('https://api.github.com/repos/' + i['owner'] + '/' + i['repo'] + '/issues/' + i['issue'])
    req.add_header('Authorization', 'token ' + token)
    r = urllib.request.urlopen(req)
    j = json.load(io.StringIO(r.readlines()[0].decode('utf-8')))
    r.close()
    issues[n]['title'] = j['title']
for i in issues:
    if i['repo'] == "sympy":
        print("* :sympyissue:`" + i['issue'] + "` " + i['title'])
    else:
        print("* :issue:`" + i['issue'] + "` " + i['title'])

exit(0)

#-------------------------------------------
f = open('pulls.txt', 'r')
pulls = []
for l in f.readlines():
    pulls.append({'pull': l.strip()})
f.close()
for n, i in enumerate(pulls):
    req = urllib.request.Request('https://api.github.com/repos/diofant/diofant/pulls/' + i['pull'])
    req.add_header('Authorization', 'token ' + token)
    r = urllib.request.urlopen(req)
    j = json.load(io.StringIO(r.readlines()[0].decode('utf-8')))
    r.close()
    pulls[n]['title'] = j['title']
    print(pulls[n])
for p in pulls:
    print("* :pull:`" + i['pull'] + "` " + i['title'])
