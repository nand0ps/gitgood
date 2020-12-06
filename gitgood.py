import requests
import argparse
import sys
import os
import subprocess
import shutil

GIT_DIRS = ['.git','.git/refs','.git/objects','.git/refs/heads']

def create_dir(path):
    try:
        os.mkdir(path)
    except OSError as e:
        print(e)

def create_repo_structure(basepath):
    for d in GIT_DIRS:
        path = basepath + '/' + d
        create_dir(path)

def get_file(url,path):
    print(url)
    r = requests.get(url,stream=True)
    r.raw.decode_content = True
    with open(path,'wb') as f:
        shutil.copyfileobj(r.raw, f)

def check_repo():
     with open(os.devnull,'w') as DEVNULL:
        proc = subprocess.Popen(['git', 'log', '-p'],stderr=subprocess.PIPE,stdout=DEVNULL)
        check = proc.stderr.read()
        check = check.decode().split('\n')
        for i in check:
            if "read" in i:
                try:
                    check = i
                    return check.split()[-1]
                except:
                    print("ERROR",check)
                    pass
        return ''


def commit_to_object(commit):
    print(commit)
    if type(commit) != str:
        commit = commit.decode()
    subdir = commit[:2]
    commit = commit[2:]
    commit = commit.replace('\n','')
    commit = commit.replace('\r','')
    return (subdir,commit)

def get_commits_recur(objecturl,head,objectspath):
    subdir, commit = commit_to_object(head)
    path = objectspath +'/'+ subdir
    create_dir(path)
    url = objecturl +'/'+subdir+'/'+commit
    commitpath = path + '/' + commit
    get_file(url,commitpath)
    commit = check_repo()
    if commit == '':
        return commit
    else:
        get_commits_recur(objecturl,commit,objectspath)


def get_repo(url,path):
    create_repo_structure(path)
    head_url = url + '/.git/HEAD'
    head_file = path + '/.git/HEAD'
    get_file(head_url,head_file)
    with open(head_file, 'r') as f:
        head = f.read()
    head = head.split()[-1]
    heads_url = url + '/.git/' + head
    heads_file = path + '/.git/' + head 
    get_file(heads_url,heads_file)
    with open(heads_file,'r') as f:
        commit = f.read()

    config_url = url + '/.git/config'
    config_file = path + '/.git/config' 
    get_file(config_url,config_file)
    
    objecturl = url + '/.git/objects'
    objectspath = path + '/.git/objects'
    get_commits_recur(objecturl,commit,objectspath)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url",type=str,help="Target URL")
    parser.add_argument("-d","--dir",type=str,help="Destination directory",default="./")

    args=parser.parse_args()
    create_dir(args.dir)
    os.chdir(args.dir)
    get_repo(args.url,args.dir)


