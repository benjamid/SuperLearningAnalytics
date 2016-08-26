#!/usr/bin/python
"""
Author-skarumbaiah
Date-08/08/2016

Emotion Analysis: Calculate inter annotator agreement
Needs Fleiss kappa implementation (fleiss.py)

command line arguments -
Format : -b "block" -f "file" -m "facet" -s "start" -e "end" --combine/--no-combine --weak/--no-weak --all/--only-human --mean-normalize/--no-mean-normalize --global-mean/--no-global-mean

options:
-b - block size (in seconds) [default - 1000 milliseconds]
-f - elan file names of the participants (a list)
-m - multisense facet files (a list)
-s - start time to find kappa for a segment of the video (milliseconds) - must have -e along, must have one entry for each value in -f (elan files)
-e - end time to find kappa for a segment of the video (milliseconds) - must have -s along, must have one entry for each value in -f (elan files)
--combine - combine "other" and "confused" [default - True]
--weak - pick weak category if True else do max vote to resolve conflict [default - False]
--all - consider shamya-mark-facet if True else consider only humans shamya-mark [default - True]
--mean-normalize - do mean normalization on facet data before [default - True]
--global-mean - uses a global mean for mean normalization [default - False]

Examples:
-f elan8-shamya-mark.eaf elan10-shamya-mark.eaf -m 8.FACET_emotient_v4.1.csv 10.FACET_emotient_v4.1.csv
-f elan8-shamya-mark.eaf elan10-shamya-mark.eaf -s 2300058 1681600 -e 2848100 2365200 -m 8.FACET_emotient_v4.1.csv 10.FACET_emotient_v4.1.csv --global-mean
-b 2000 -f elan2-shamya-mark.eaf -m 2.FACET_emotient_v4.1.csv 
-b 1000 -f elan8-shamya-mark.eaf --no-combine -m 8.FACET_emotient_v4.1.csv
-b 1000 -f elan8-shamya-mark.eaf --combine --weak -m 8.FACET_emotient_v4.1.csv
-b 1000 -f elan8-shamya-mark.eaf --combine --weak -m 8.FACET_emotient_v4.1.csv -all
-b 1000 -f elan8-shamya-mark.eaf --no-combine --weak -m 8.FACET_emotient_v4.1.csv --only-human

Output:
Fleiss' kappa value

"""

from fleiss import fleissKappa
from xml.dom.minidom import parse as pr
import argparse,sys
import csv
from operator import itemgetter
from MeanNormalize import get_facet_data_all, get_facet_data_combined, get_global_mean

'''transforms the input annotations into usable matrix'''
def transform_annotation(ts,start_time,end_time,ts_dict):
    
    #replace timeslot with milliseconds
    for this_ts in ts:
        this_ts[0] = ts_dict[this_ts[0]]  
        this_ts[1] = ts_dict[this_ts[1]]  
    
    print(ts)
    
    #fill in neutral
    full_ts = []
    old_ts = None
    
    if int(ts[0][1]) > start_time:
        new_ts = [start_time, "Neutral"]
        full_ts.append(new_ts)
    
    for this_ts in ts:
        if old_ts is not None:
            if int(this_ts[0]) != int(old_ts[1])+1 and int(this_ts[0]) != int(old_ts[1]):
                new_ts = [int(old_ts[1])+1, "Neutral"]
                full_ts.append(new_ts)
        full_ts.append([this_ts[0], this_ts[2]])
        old_ts = this_ts
    
    new_ts = [int(old_ts[1])+1, "Neutral"]
    full_ts.append(new_ts)
    
    if int(full_ts[-1][0]) < int(end_time):
        new_ts = [end_time, "Neutral"]
        full_ts.append(new_ts)
    
    return full_ts   

'''get annotator specific annotations'''
def get_annotations(tiers, tier_name):
    
    ts = []
    #go to the Shamya_EmotionTier tier
    for tier in tiers:
        if tier.getAttribute("TIER_ID") == tier_name:
            annotations = tier.getElementsByTagName("ANNOTATION")
            for annotation in annotations:
                align_annotations = annotation.getElementsByTagName("ALIGNABLE_ANNOTATION")
                for align_annotation in align_annotations:
                    ts1 = align_annotation.getAttribute("TIME_SLOT_REF1")
                    ts2 = align_annotation.getAttribute("TIME_SLOT_REF2")
                    annotation_value = align_annotation.getElementsByTagName("ANNOTATION_VALUE")[0]
                    emotion = annotation_value.childNodes[0].data
                    ts_new = [ts1,ts2,emotion]
                    ts.append(ts_new)
    
    return ts

'''get annotations in regular intervals'''
def regularize_annotations(full_ts, block, weak):
    annot = []
    old_ts = None
    vote = {"Neutral":0, "Skip":0, "Confused":0, "Other":0}
    for this_ts in full_ts:
        if old_ts is not None:
            diff_ts = int(this_ts[0]) - int(old_ts[0])
            n = int(diff_ts / block)
            
            for i in range(n):
                annot.append(old_ts[1])
                
            extra = diff_ts % block
            
            total = 0
            for keys in vote:
                total += vote[keys]
            
            now = block - total
            if now > extra :
                now = extra
                extra = 0
            else:
                extra -= now
            
            vote[old_ts[1]] += now
            if total + now >= block:
                if weak is True:
                    #pick weaker category
                    if vote["Other"] > 0:
                        emotion = "Other"
                    elif vote["Confused"] >0:
                        emotion = "Confused"
                    elif vote["Skip"] > 0:
                        emotion = "Skip"
                    else:
                        emotion = "Neutral"
                else:
                    #max vote
                    emotion = (max(vote, key=vote.get))
                    
                annot.append(emotion)
            
                for keys in vote:
                    vote[keys] = 0
                
                vote[old_ts[1]] +=extra
            
        old_ts = this_ts
     
    if sum(vote.values()) != 0:
        emotion = (max(vote, key=vote.get))
        annot.append(emotion) 
        
    return annot

'''updates annotation matrix as needed by kappa'''
def update_kappa_matrix(annot, emo):
    
    for i in range(len(annot)):
        for j in range(len(annot[0])):
            if annot[i][j] == "Neutral":
                emo[i][0] += 1
            elif annot[i][j] == "Confused":
                emo[i][1] += 1
            elif annot[i][j] == "Other":
                emo[i][2] += 1    
    return emo

'''get FACET data as neutral vs other'''
def get_facet_data(file,start_time, end_time):

    facet = []
    with open(file,'r') as file:
        reader = csv.reader(file, dialect='excel')
        next(reader, None)
        for row in reader:
            if len(row) < 1:
                break
            if float(row[0]) > start_time/1000 and float(row[0]) < end_time/1000:
                frame = [float(row[0])*1000, max(enumerate(row[5:15]), key=itemgetter(1))[0]]
                facet.append(frame)
    
    for f in facet:
        if f[1] == 5:
            f[1] = "Neutral"
        elif f[1] ==8:
            f[1] = "Confused"
        else:
            f[1] = "Other"
    
    return facet

def main(args):
    """ parse command like argument"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-b", "--block")
    parser.add_argument("-f", "--file", nargs ='*')
    parser.add_argument("-m", "--facet", nargs = '*')
    parser.add_argument("-s", "--start", nargs ='*')
    parser.add_argument("-e", "--end", nargs ='*')
    
    parser.add_argument('--combine', dest='combine', action='store_true')
    parser.add_argument('--no-combine', dest='combine', action='store_false')
    parser.set_defaults(combine=True)
 
    parser.add_argument('--weak', dest='weak', action='store_true')
    parser.add_argument('--no-weak', dest='weak', action='store_false')
    parser.set_defaults(weak=False)   

    parser.add_argument('--all', dest='all', action='store_true')
    parser.add_argument('--only-human', dest='all', action='store_false')
    parser.set_defaults(all=True)
 
    parser.add_argument('--mean-normalize', dest='mean', action='store_true')
    parser.add_argument('--no-mean-normalize', dest='mean', action='store_false')
    parser.set_defaults(mean=True)
    
    parser.add_argument('--global-mean', dest='global_mean', action='store_true')
    parser.add_argument('--no-global-mean', dest='global_mean', action='store_false')
    parser.set_defaults(mean=False)
    
    
    args = parser.parse_args()
    
    if args.block is not None:
        block = int(args.block)
    else:
        block = 1000
    
    filename = args.file
    print(filename)
    facet_file = args.facet
    combine = args.combine
    weak = args.weak 
    all = args.all
    mean = args.mean
    global_mean = args.global_mean
    start_time_list = args.start if args.start is not None else None
    end_time_list = args.end if args.end is not None else None
    
    print("file =", filename, "facet file =", facet_file, "block =", block, "combine =", combine, "weak =", weak)
    time_dict_list = []
    emotion_kappa = []
        
    total = len(filename)
    
    for i in range(total):
        print(filename[i])
        tree = pr(filename[i])
        annotationTree = tree.documentElement
        tiers = annotationTree.getElementsByTagName("TIER")
        #put time tier to a dictionary
        ts_dict = {}
                
        times = annotationTree.getElementsByTagName("TIME_ORDER")
        for time in times:
            time_slots = time.getElementsByTagName("TIME_SLOT")
            for time_slot in time_slots:
                ts_dict[time_slot.getAttribute("TIME_SLOT_ID")] = time_slot.getAttribute("TIME_VALUE")

        time_dict_list.append(ts_dict)
    
    #get start and end time
    if start_time_list is None or end_time_list is None:
        start_time_list = []
        end_time_list = []
        
        for i in range(total):
            ts_dict = time_dict_list[i]
            start_time_slot = None
            end_time_slot = None
            #go to the Shamya_looking-at-screenTier tier
            tree = pr(filename[i])
            annotationTree = tree.documentElement
            tiers = annotationTree.getElementsByTagName("TIER")
            for tier in tiers:
                if tier.getAttribute("TIER_ID") == "Shamya_looking-at-screenTier":
                    annotations = tier.getElementsByTagName("ANNOTATION")
                    for annotation in annotations:
                        align_annotations = annotation.getElementsByTagName("ALIGNABLE_ANNOTATION")
                        for align_annotation in align_annotations:
                            if start_time_slot is None:
                                start_time_slot = align_annotation.getAttribute("TIME_SLOT_REF1")
                            end_time_slot = align_annotation.getAttribute("TIME_SLOT_REF2")
                
            print("start_time_slot = ", start_time_slot, " end_time_slot = ", end_time_slot)
                
            #pick start time
            start_time_list.append(int(ts_dict[start_time_slot]))
            end_time_list.append(int(ts_dict[end_time_slot]))
     
        
    if global_mean is True:
        print("Finding global mean...")
        global_mean_neutral, global_mean_other = get_global_mean(facet_file, start_time_list, end_time_list)
    else:
        global_mean_neutral = None
        global_mean_other = None
    
    
    for i in range(total): 
        print(filename[i])
        tree = pr(filename[i])
        annotationTree = tree.documentElement
        tiers = annotationTree.getElementsByTagName("TIER")
        #put time tier to a dictionary
        ts_dict = time_dict_list[i]
                      
        start_time = int(start_time_list[i])
        end_time = int(end_time_list[i])

        print("start_time = ", start_time, " end_time = ", end_time)
        
        #Shamya annotations
        shamya_ts = get_annotations(tiers, "Shamya_EmotionTier")
        print("shamya ts ", shamya_ts)
        shamya_full_ts = transform_annotation(shamya_ts, start_time, end_time,ts_dict)
        print("shamya full ts ", shamya_full_ts)
        
        #Mark annotations
        mark_ts = get_annotations(tiers, "Mark_EmotionTier")
        print("mark ts", mark_ts)
        mark_full_ts = transform_annotation(mark_ts, start_time, end_time,ts_dict)
        print("mark full ts", mark_full_ts)
        
        
        #get annotation based on the block size
        shamya_annot = regularize_annotations(shamya_full_ts, block, weak)
        print("shamya block sized annot", shamya_annot)
        mark_annot = regularize_annotations(mark_full_ts, block, weak)
        print("mark block sized annot", mark_annot)
        
        if all is True:
            print(facet_file[i])
            
            #get FACET data
            #Mean Normalized
            if mean is True:                    
                if combine is True:
                    #has to be separate as mean of max would differ with/without the confusion column
                    facet = get_facet_data_combined(facet_file[i], start_time, end_time, global_mean_neutral, global_mean_other)
                else:
                    facet = get_facet_data_all(facet_file[i], start_time, end_time, global_mean_neutral, global_mean_other)
            else:
                facet = get_facet_data(facet_file[i], start_time, end_time)
                
            print("facet full", facet[:10])
            
            facet_annot = regularize_annotations(facet, block, weak)
            print("facet block sized annot", facet_annot)
            
            #print("FACET - Neutral =", facet_annot.count('Neutral'), "Confused =", facet_annot.count('Confused'), "Other =", facet_annot.count('Other'), "Skip =", facet_annot.count('Skip'))
            
        #print("SHAMYA - Neutral =", shamya_annot.count('Neutral'), "Confused =", shamya_annot.count('Confused'), "Other =", shamya_annot.count('Other'), "Skip =", shamya_annot.count('Skip'))
        #print("MARK - Neutral =", mark_annot.count('Neutral'), "Confused =", mark_annot.count('Confused'), "Other =", mark_annot.count('Other'), "Skip =", mark_annot.count('Skip'))
        
        #Delete skips and combine annotations
        if all is True:
            #change [s,m,f] if you need pairwise [m,f] or [s,f]
            annot = [[s,m,f] for s,m,f in zip(shamya_annot,mark_annot, facet_annot) if s != "Skip" and m != "Skip"]
        else:
            annot = [[s,m] for s,m in zip(shamya_annot,mark_annot) if s != "Skip" and m != "Skip"]
        
        #[Neutral, Confused, Other]
        emot = [[0,0,0] for i in range((len(annot)))]
        
        #update kappa matrix
        emot = update_kappa_matrix(annot, emot)    
        
        emotion_kappa = emotion_kappa + emot
      
    #if combine merge other and confused
    if combine is True:
        emotion_kappa = [[l[0], (l[1]+l[2])] for l in emotion_kappa]
                    
    print(len(emotion_kappa))
    
    #compute fleiss' kappa
    kappa = fleissKappa(emotion_kappa)
    print(kappa)

if __name__ == "__main__":
    main(sys.argv[1:])
