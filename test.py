#!/usr/bin/env python2.7
"""Helper script to generate a TrustKit or HPKP pin from a PEM/DER certificate file.
"""
from subprocess import check_output

if __name__ == '__main__':

    branches_to_exclude = ['origin/NGW', 'origin/alpha-pdf-android-fix']

    # A list of all branches merged into develop except master, develop itself and 
    # the ones defined in the exclusion list
    raw_branch_list = check_output('git --no-pager branch -r --merged origin/develop', shell=True)
    branches_merged = [branch_name.strip() for branch_name in raw_branch_list.split('\n') 
                        if
                            branch_name.strip() and 
                            branch_name.strip() != 'origin/master' and
                            branch_name.strip() != 'origin/develop' and 
                            '->' not in branch_name.strip() and
                            branch_name.strip() not in branches_to_exclude]
    print branches_merged                     
    # A list of all branches not merged into develop except master, develop itself and 
    # the ones defined in the exclusion list               
        
        
    raw_branch_list = check_output('git --no-pager branch -r --no-merged origin/develop', shell=True)
    branches_not_merged = [branch_name.strip() for branch_name in raw_branch_list.split('\n') 
                        if
                            branch_name.strip() and 
                            branch_name.strip() != 'origin/master' and
                            branch_name.strip() != 'origin/develop' and 
                            '->' not in branch_name.strip() and
                            branch_name.strip() not in branches_to_exclude]
    print branches_not_merged    
    for branch_name in branches_merged:
        raw = check_output('git --no-pager log ' + branch_name + ' ^origin/develop --format="%ci, %h, %cn, %s"', shell=True)
        print '%s --------> \n' % branch_name 
        print raw
    for branch_name in branches_not_merged:
        raw = check_output('git --no-pager log ' + branch_name + ' ^origin/develop --format="%ci, %h, %cn, %s"', shell=True)
        print '%s --------> \n' % branch_name 
        print raw

    