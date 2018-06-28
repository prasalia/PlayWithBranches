#!/usr/bin/env python2.7
""" Analyze Git repository to find out stale branches.
"""
from subprocess import check_output
import json
from datetime import datetime

if __name__ == '__main__':

    branch_age_threshold = 0
    branches_to_exclude = []
    base_branch = 'develop'

    def get_last_log_details_on_branch(branch_name):
        """ Return a dict containing details of the latest log record for a branch.
        """
        raw_output = check_output('git --no-pager log -n 1 ' + branch_name + ' --format="%h,%an,%cn,%cd,%s" --date=short', shell=True)
        log_list = raw_output.split(',', 4)
        diff = check_output('git --no-pager diff ' + branch_name + '..' + base_branch + ' | head -1', shell=True)
        # If the diff is blank it effectively means that the branch was created but never used
        if diff == '':
            log_list[0] = ''
            log_list[2] = ''
            log_list[3] = 'Never'
            log_list[4] = ''
        log_details =   {
                            'id' : log_list[0].strip(),
                            'author' : log_list[1].strip(),
                            'last_committed_by' : log_list[2].strip(),
                            'last_committed_date' : log_list[3].strip(),
                            'commit_message' : log_list[4].strip()
                        }
        return log_details

    def get_last_commit_date_on_branch(branch_name):
        """ Return the last commit date of the HEAD revision for a given branch in YYYY-MM-DD format.
        """
        raw_output = check_output('git --no-pager log -n 1 ' + branch_name + ' --format="%cd" --date=short', shell=True)
        return raw_output.strip('\n')

    def get_last_commit_by_on_branch(branch_name):
        """ Return the name of the last committer for a given branch.
        """
        raw_output = check_output('git --no-pager log -n 1 ' + branch_name + ' --format="%cn"', shell=True)
        return raw_output.strip('\n')

    def get_author_for_branch(branch_name):
        """ Return the name of the author i.e creator of a given branch.
        """
        raw_output = check_output('git --no-pager log -n 1 ' + branch_name + ' --format="%an"', shell=True)
        return raw_output.strip('\n')

    def get_last_commit_message_on_branch(branch_name):
        """ Return the name of the last committer for a given branch.
        """
        raw_output = check_output('git --no-pager log -n 1 ' + branch_name + ' --format="%s"', shell=True)
        return raw_output.strip('\n')

    def is_branch_old(branch_name):
        """ Return True if the given branch was last used more than the no of threshold days, False otherwise.
        """
        return (datetime.now().date() - datetime.strptime(get_last_commit_date_on_branch(branch_name), '%Y-%m-%d').date()).days >= branch_age_threshold

    # Get all branches merged into develop except master, develop itself and 
    # the ones defined in the exclusion list
    raw_branch_list = check_output('git --no-pager branch -r --merged origin/' + base_branch, shell=True)
    branches_merged = [branch_name.strip() for branch_name in raw_branch_list.split('\n') 
                        if
                            branch_name.strip() and 
                            branch_name.strip() != 'origin/master' and
                            branch_name.strip() != 'origin/develop' and 
                            '->' not in branch_name.strip() and
                            branch_name.strip() not in branches_to_exclude]
    # Get all branches not merged into develop except master, develop itself and 
    # the ones defined in the exclusion list                      
    raw_branch_list = check_output('git --no-pager branch -r --no-merged origin/' + base_branch, shell=True)
    branches_not_merged = [branch_name.strip() for branch_name in raw_branch_list.split('\n') 
                        if
                            branch_name.strip() and 
                            branch_name.strip() != 'origin/master' and
                            branch_name.strip() != 'origin/develop' and 
                            '->' not in branch_name.strip() and
                            branch_name.strip() not in branches_to_exclude]
 
    # Get all branches merged into develop but having commits that do not exist in develop
    # Ideally there should be no such branches and as such are safe candidates for deletion
    # But if there are any such branches, then review them with the developers before deleting
    branches_merged_but_has_commits = {}    
    for branch_name in branches_merged:
        raw_commit_list = check_output('git --no-pager log ' + branch_name + ' ^origin/' + base_branch + ' --format="id: %h, commited_by: %cn, committed_on: %cd, commit_message: %s" --date=short', shell=True)
        # Another way of finding commits on a branch that do not exist on another branch
        # raw_commit_list = check_output('git --no-pager cherry -v origin/develop ' + branch_name, shell=True)
        branches_merged_but_has_commits[branch_name] = [commit.strip() for commit in raw_commit_list.split('\n') if commit.strip()]
    
    # All branches not merged into develop and having commits that do not exist in develop
    # Review such branches with the developers before deletion
    # Non merged branches that do not have any commits not already in develop means that
    # those branches were created but never used. These branches can be deleted depending upon
    # when they were created. Review them with the developers before deleting 
    branches_not_merged_but_has_commits = {}
    for branch_name in branches_not_merged:
        raw_commit_list = check_output('git --no-pager log ' + branch_name + ' ^origin/' + base_branch + ' --format="id: %h, commited_by: %cn, committed_on: %cd, commit_message: %s" --date=short', shell=True)
        # Another way of finding commits on a branch that do not exist on another branch
        # raw_commit_list = check_output('git --no-pager cherry -v origin/develop ' + branch_name, shell=True)
        branches_not_merged_but_has_commits[branch_name] = [commit.strip() for commit in raw_commit_list.split('\n') if commit.strip()]

    branches_merged_for_deletion = {
                                    branch:get_last_log_details_on_branch(branch)
                                    for branch, commit in branches_merged_but_has_commits.items() 
                                    if commit == []
                                    }
    branches_to_be_reviewed_1 = {branch:commit for branch, commit in branches_merged_but_has_commits.items() if commit != []}

    branches_not_merged_for_deletion = {
                                        branch:get_last_log_details_on_branch(branch)
                                        for branch, commit in branches_not_merged_but_has_commits.items() 
                                        if commit == [] and is_branch_old(branch)
                                        }
    branches_to_be_reviewed_2 = {
                                branch:get_last_log_details_on_branch(branch)
                                for branch, commit in branches_not_merged_but_has_commits.items() 
                                if commit != [] and is_branch_old(branch)
                                }

    #print get_last_log_details_on_branch('branch1')

    print json.dumps(branches_merged_for_deletion, indent=4, sort_keys=True)
    print '#########################################'
    print json.dumps(branches_to_be_reviewed_1, indent=4, sort_keys=True)
    print '#########################################'
    print json.dumps(branches_not_merged_for_deletion, indent=4, sort_keys=True)
    print '#########################################'    
    print json.dumps(branches_to_be_reviewed_2, indent=4, sort_keys=True)