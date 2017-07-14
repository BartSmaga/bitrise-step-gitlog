#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
logging.basicConfig(level=logging.INFO)

import argparse
import os
import git
import time
import re

def safeindex(data, key):
    """Returns index of the key in data or None if it does not exist"""
    try:
        return data.index(key)
    except ValueError:
        return None

def git_path(path,limit=5):
    """Searches for GIT root directory in parents directories."""
    cur_path = path
    i = 0
    while i < limit:
        if ".git" in os.listdir(cur_path):
            return os.path.abspath(cur_path)
        if os.path.isdir(cur_path):
            cur_path = os.path.abspath(os.path.join(cur_path, os.pardir))
        else:
            cur_path = os.path.abspath(os.path.join(os.path.dirname(cur_path), os.pardir))
        i += 1
    return os.path.abspath(path)

def str_commit(commit):
    """Returns string with description of the commit."""
    message_lines = commit.message.splitlines()
    nonempty_lines = [l for l in message_lines if len(l) > 0]
    #message_str = nonempty_lines[0]
    message_str = '; '.join(nonempty_lines)
    #date_str = time.strftime("%y%m%dT%H%M%SZ", time.gmtime(c.committed_date))
    date_str = time.asctime(time.gmtime(commit.committed_date))
    s = "%s (%s; %s)\n" % (message_str, commit.author.name, date_str)
    return s

def str_commits(version, commits, date=None, ticket_prefix=None):
    """Returns string with formatted commits information. Groups by ticket if ticket_prefix provided."""
    
    s = "#"
    if version is not None:
        s+= " Version %s" % version
    if date is not None:
        date_str = time.strftime("%Y-%m-%d", time.gmtime(date))
        s += " (%s)" % date_str
    s += "\n\n"
        
    if ticket_prefix is not None:
        other_commits = []
        tickets_commits = {}
        ticket_pattern = "%s[0-9]+" % ticket_prefix
        for c in commits:
            message = c.message
            tickets = re.findall(ticket_pattern, message)
            #print(tickets)
            if len(tickets) > 0:
                for t in tickets:
                    if not t in tickets_commits:
                        tickets_commits[t] = []
                    tickets_commits[t].append(c)
            else:
                other_commits.append(c)
        #print(tickets_commits)
        for ticket in sorted(tickets_commits.keys(), reverse=True):
            s += " - %s\n\n" % ticket
            for c in tickets_commits[ticket]:
                m = str_commit(c).strip()
                # remove the ticket reference if at the beginning of the message
                if m[:len(ticket)] == ticket:
                    m = m[len(ticket):].strip()
                s += "   - %s\n" % m
            s += "\n"
        s += " - Other\n\n"
        for c in other_commits:
            s += "   - %s" % str_commit(c)
        s += "\n"
    else:
        for c in commits:
            s += " - %s" % str_commit(c)
        s += "\n"
    
    return s

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('path', nargs='?', default='.', help='GIT repository path')
    parser.add_argument('--last', '-l', type=int, default=None, help='Last versions')
    #parser.add_argument('--branch', '-b', default='master')
    parser.add_argument('--ticket_prefix', '-tp', default=None, help='Ticket prefix, for example JIRA-')
    args = parser.parse_args()

    #parser.print_help()

    repo_path = git_path(args.path)
    try:
        repo = git.Repo(repo_path)
    except git.InvalidGitRepositoryError:
        exit("Invalid GIT Repository at %s" % repo_path)

    # all the commits on the current branch
    all_commits = list(repo.iter_commits())
    
    # get all the tags, the oldest first, note that some may be not on the current branch
    all_tags = sorted(repo.tags, key=lambda t: t.commit.committed_datetime)
    
    # find index for each tag, note that some tags may be on different branches
    # TODO: can be optimized as the tags are alrady sorted
    tags_indices = list(map(lambda t: (t, safeindex(all_commits, t.commit)), all_tags))
    tags_indices = [elem for elem in tags_indices if elem[1] is not None]
    # reverse should be sufficient if the tags are already sorted
    tags_indices = sorted(tags_indices, key=lambda ti: ti[1])
    # add a fake tag at the beginning
    tags_indices.append((None, len(all_commits)))
    #print(tags_indices)
    
    first_tag_index =  tags_indices[0][1]
    try:
        # GIT cannot describe if there are no tags
        last_version = repo.git.describe()
    except:
        last_version = None
    last_commit_date = all_commits[0].committed_date if len(all_commits) > 0 else None
    changelog = str_commits(last_version, all_commits[:first_tag_index], date=last_commit_date, ticket_prefix=args.ticket_prefix)
    
    prev_ti = None
    for ti in tags_indices[:args.last]:
        if prev_ti is not None:
            version = prev_ti[0]
            version_date = version.commit.committed_date
            commits = all_commits[prev_ti[1]:ti[1]]
            changelog += str_commits(version, commits, date=version_date, ticket_prefix=args.ticket_prefix)
        prev_ti = ti
        
    print(changelog)
