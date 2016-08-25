#!/usr/bin/python
"""
Author-skarumbaiah
Date-06/13/2016

Emotion Analysis: Calculate offset between Elan and game log files for all the participants in the directory. 
For a participant, there should be 2 files for the script to run elan*.eaf with the annotation at Chen's first utterance as "start_Being_Heard_one" and the corresponding game log file.

command line arguments -
Format : -d "directory" -g "game" -e "elan"

options:
-d - directory to look for gamelogs and elan files [default: current directory]
-g - game log file name [default: all files matching GameLog_<participant_id>* - must have sequential ordering]
-e - elan file name [default: all files matching elan_<participant_id>* - must have sequential ordering]
-o - output directory [default: current directory]

Example:
-d "C:/Users/skarumbaiah/Desktop/svn_learninganalytics/trunk/projects/worksheet"
-d "C:/Users/skarumbaiah/Desktop/svn_learninganalytics/trunk/projects/worksheet" -g "GameLog_1_Fri_Sep-25-15_160407.txt" -e "elan1.eaf"
-d "C:/Users/skarumbaiah/Desktop/svn_learninganalytics/trunk/projects/worksheet" -g "GameLog_1_Fri_Sep-25-15_160407.txt" -e "elan1.eaf" -o "C:/Users/skarumbaiah/Desktop/svn_learninganalytics/trunk/projects/worksheet"
None 

Output:
offset.csv - measured offet for each participant
new_<old elan filename> - new Elan file with fixed offsets

Note:
Comment the last line in main that calls the fixElanOffset function to avoid creating new elan files
"""

from xml.dom.minidom import parse as pr
from datetime import datetime
import csv
import os, sys
from fnmatch import fnmatch
import argparse
import math as mt

"""Function to get the elan annotation time (in ms) for the start of annotation given a elan file"""
def getElanTime(efname):
    tree = pr(efname)
    annotationTree = tree.documentElement
    timeslot = None
    timeslot2 = None
    t = None
    t2 = None
    
    #go to the notes tier
    tiers = annotationTree.getElementsByTagName("TIER")
    for tier in tiers:
        if tier.getAttribute("TIER_ID") == "default":#"notes":
            annotations = tier.getElementsByTagName("ANNOTATION")
            for annotation in annotations:
                align_annotations = annotation.getElementsByTagName("ALIGNABLE_ANNOTATION")
                for align_annotation in align_annotations:
                    annotation_value = align_annotation.getElementsByTagName("ANNOTATION_VALUE")[0]
                    if "start_Being_Heard_one" in annotation_value.childNodes[0].data:
                        timeslot = align_annotation.getAttribute("TIME_SLOT_REF1")
                    if "start_Being_Heard_two" in annotation_value.childNodes[0].data:
                        timeslot2 = align_annotation.getAttribute("TIME_SLOT_REF1")
    
    print("Found start_Being_Heard_one annotation at ", timeslot)
    if timeslot2 is not None:
        print("Found start_Being_Heard_two annotation at ", timeslot2)
        
    #go to the time tier
    times = annotationTree.getElementsByTagName("TIME_ORDER")
    for time in times:
        time_slots = time.getElementsByTagName("TIME_SLOT")
        for time_slot in time_slots:
            if time_slot.getAttribute("TIME_SLOT_ID") == timeslot:
                t = time_slot.getAttribute("TIME_VALUE")
                
            if time_slot.getAttribute("TIME_SLOT_ID") == timeslot2:
                t2 = time_slot.getAttribute("TIME_VALUE")
                
    print("Elan annotation times - ", t, "", t2)
    return t, t2

"""Function to get the game log time (in ms) for the start of Chen's conversation given a game log file"""
def getGameLogTime(gfname):
    diff_ms = None
    diff_ms2 = None
    with open(gfname,'r') as file:
        rows = csv.reader(file, dialect='excel', delimiter ='|')
        for row in rows:
            for field in row:
                if "Log In" in field:
                    start_time = row[4]
                    print("Game log start time ", start_time)
                    break
            else:
                continue
            break

        for row in rows:
            for field in row:
                if "Do you have a minute?" in field:
                    if diff_ms is None:
                        #print(row)
                        conv_time = row[4]
                        print("Game log Chen conversation time ", conv_time)
                        frmt = '%H:%M:%S.%f'
                        diff = datetime.strptime(conv_time, frmt) - datetime.strptime(start_time, frmt)
                        diff_ms = diff.seconds *1000
                    else:
                        #print(row)
                        conv_time = row[4]
                        print("Game log Chen conversation time ", conv_time)
                        frmt = '%H:%M:%S.%f'
                        diff = datetime.strptime(conv_time, frmt) - datetime.strptime(start_time, frmt)
                        diff_ms2 = diff.seconds *1000
    
    print("Game log difference time to conversation ", diff_ms, diff_ms2)
    return diff_ms, diff_ms2

"""Function to fix the given elan file given an offset"""
def fixElanOffest(efname, dirc, offset):
    tree = pr(dirc+"/"+efname)
    annotationTree = tree.documentElement

    #go to the time tier
    times = annotationTree.getElementsByTagName("TIME_ORDER")
    for time in times:
        time_slots = time.getElementsByTagName("TIME_SLOT")
        for time_slot in time_slots:
            if int(time_slot.getAttribute("TIME_VALUE")) + offset > 0:
                time_slot.setAttribute("TIME_VALUE", str(int(time_slot.getAttribute("TIME_VALUE")) + offset))
 
    new_efname = dirc + "/" + 'new_' + efname
    tree.writexml( open(new_efname, 'w'),
               indent="  ",
               addindent="  ",
               newl='\n')
    print("Fixed offfset output at ", new_efname)
     
    return

def main(args):
    """ parse command like argument"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--directory")
    parser.add_argument("-g", "--gamelog")
    parser.add_argument("-e", "--elan")
    parser.add_argument("-o", "--output")
    args = parser.parse_args()

    print(str(args))
    cwd = os.getcwd()

    if args.directory is not None:
        dirc = args.directory
    else:
        dirc = cwd
        
    gamelog = args.gamelog
    elan = args.elan
    
    if args.output is not None:
        op = args.output
    else:
        op = cwd
        
    print("Looking in the directory -", dirc)
    print("Specified gamelog file ", gamelog)
    print("Specified elan file ", elan)

    #open output file
    open(op +"/"+"offset.csv", 'w').close()
    op = open(op +"/"+"offset.csv", 'w')
    ln = 'Participant' + ',' + "offset1 (in ms)" + ',' + "offset2 (in ms)" + ',' + "diff in offset (in s)" + ',' + "average offset (in ms)" + '\n'
    op.write(ln)
    
    if gamelog is None:
        num_participant = len([file for file in os.listdir(dirc) if fnmatch(file,'GameLog_*')])
    else:
        num_participant = 1
        
    for i in range(82):#num_participant):
    #for i in [36]:
        i+=1
        #print("Participant ", i)
        
        if num_participant == 1:
            efname = elan
            gfname = gamelog
        else:
            efname = "elan"+str(i)+".eaf"
            gfname = "GameLog_"+str(i)+"_*"
    
        #get game log time
        for file in os.listdir(dirc):
            if fnmatch(file,efname):
                offset = None
                offset2 = None
                diff  =None
                offset_fix = None
                
                efname = dirc +"/"+ "elan"+str(i)+".eaf"
                #get start time from Elan file
                et, et2 = getElanTime(efname)
                
                for gamelogfile in os.listdir(dirc):
                    if fnmatch(gamelogfile,gfname):
                        gfname = gamelogfile
                    
                print(gfname)
                gfname = dirc +"/"+ gfname
                
                gt, gt2 = getGameLogTime(gfname)
                
                if gt is not None:
                    if et is not None:
                        offset = int(et)-int(gt)
                if gt2 is not None:
                    if et2 is not None:
                        offset2 = int(et2)-int(gt2)
                    
                if offset is not None:
                    if offset2 is not None:
                        diff = (offset-offset2)/1000
                print("offset1 = ", offset)
                print("offset2 = ", offset2)
                print("Difference ", diff, "seconds")
                
                #average of the two offsets
                if offset is not None:
                    if offset2 is not None:
                        offset_fix = mt.ceil((offset + offset2)/2)
                    else:
                        offset_fix = offset
                else:
                    if offset2 is not None:
                        offset_fix = offset2
                    else:
                        offset_fix = 0
                
                if offset_fix == 0:
                    avgoffset = None
                else:
                    avgoffset = offset_fix
                           
                ln = str(i) + ',' + str(offset) + ',' + str(offset2) + ',' + str(diff) + ',' + str(avgoffset) + '\n'
                op.write(ln)
                
                #fix time slot with the specified offset
                fixElanOffest("elan"+str(i)+".eaf", op, offset_fix)
                
    print("all offset output at offset.csv")
    
if __name__ == "__main__":
    main(sys.argv[1:])