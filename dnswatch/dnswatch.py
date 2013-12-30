# -*- coding: utf-8 -*-
import dns.resolver
import json
import datetime
from random import choice
from os import listdir
from os.path import isfile, join
import git
import argparse

#nameservers to pick from
nameservers = dns.resolver.Resolver().nameservers
with open("dnsservers.lst") as f:
        content = f.readlines()
for ip in content:
    if ip not in nameservers:
        nameservers.append(ip.strip())


def GenerateResolver():
    '''Create resolver and load DNS settings'''
    global nameservers
    resolver = dns.resolver.Resolver()
    resolver.nameservers = [choice(nameservers)]
    return resolver


def CreateResult(answer, time=None):
    if time is None:
        time = datetime.datetime.utcnow()
    d = {}
    d['name'] = answer.name.to_text(True)
    d['answers'] = []
    for a in answer:
        if a.to_text() != '92.242.140.2':
            d['answers'].append(a.to_text())
    d['answers'].sort()
    return d


def Query(domain):
    resolver = GenerateResolver()
    return CreateResult(resolver.query(domain))


def GetFileOutput(domain):
    try:
        return json.dumps(Query(domain))
    except:
        d = {}
        d['name'] = domain
        d['answers'] = []
        return json.dumps(d)


def AttemptToUpdateResult(path, domain):
    with open(path + 'results/' + domain, 'r') as content_file:
        content = content_file.read()
    content = content.strip()
    updated = GetFileOutput(domain).strip()
    if content != updated:
        with open(path + 'results/' + domain, 'w') as content_file:
            content_file.write(updated)
        return True
    return False


def UpdateResults(path):
    files = [f for f in listdir(path + 'results/') if isfile(join(path +
        'results/', f))]
    anyupdated = False
    repo = git.Repo(path)
    for f in files:
        if AttemptToUpdateResult(path, f):
            anyupdated = True
        repo.git.add(path + 'results/' + f)
    if anyupdated:
        repo.git.commit(m='automated update')
    return anyupdated


parser = argparse.ArgumentParser(description='Update DNS log entry data')
parser.add_argument('repo', metavar='repository', type=str, nargs=1,
                   help='The path to the local git repository')
args = parser.parse_args()
repo = args.repo[0]

#Get new results from the repository
git.Repo(repo).remotes.origin.pull()
if UpdateResults(repo):
    # We need to push results
    git.Repo(repo).remotes.origin.push()