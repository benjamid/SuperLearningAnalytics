import csv
from operator import itemgetter

#gets the global mean of neutral and global mean of max of other
def get_global_mean(facet_file, start_time_list, end_time_list):
    
    neutral = []
    other = []
    
    for i in range(len(facet_file)):
        facet = facet_file[i]
        start_time = start_time_list[i]
        end_time = end_time_list[i]
    
        i = [5,6,7,8,9,11,13,12,14]
        with open(facet,'r') as file:
            reader = csv.reader(file, dialect='excel')
            next(reader, None)
            for row in reader:
                if len(row) < 1:
                    break
                if float(row[0]) > start_time/1000 and float(row[0]) < end_time/1000:
                    n = float(row[10])
                    o = [float(row[ind]) for ind in i]
                    neutral.append(n)
                    other.append(o)
    
    #global mean
    global_mean_neutral = sum(neutral)/len(neutral)
    
    max_other = []
    max_ind = []
    for o in other:
        max_ind.append(max(enumerate(o), key=itemgetter(1))[0])
        max_other.append(max(enumerate(o), key=itemgetter(1))[1])
    
    global_mean_other = sum(max_other)/len(max_other)

    
    return global_mean_neutral, global_mean_other

def get_facet_data_all(file, start_time, end_time, global_mean_neutral, global_mean_other):
    time = []
    neutral = []
    confusion = []
    other = []
    
    i = [5,6,7,8,9,11,12,14]
    with open(file,'r') as file:
        reader = csv.reader(file, dialect='excel')
        next(reader, None)
        for row in reader:
            if len(row) < 1:
                break
            if float(row[0]) > start_time/1000 and float(row[0]) < end_time/1000:
                t = float(row[0])*1000
                n = float(row[10])
                c = float(row[13])
                o = [float(row[ind]) for ind in i]
                time.append(t)
                neutral.append(n)
                confusion.append(c)
                other.append(o)
    
    
    #mean normalize value
    if global_mean_neutral is None:
        avg = sum(neutral)/len(neutral)
    else:
        avg = global_mean_neutral
    mean_norm_neutral = [i-avg for i in neutral]
    
    if global_mean_other is None:
        avg = sum(confusion)/len(confusion)
    else:
        avg = global_mean_other
    mean_norm_confusion = [i-avg for i in confusion]  
    
    max_other = []
    max_ind = []
    for o in other:
        max_ind.append(max(enumerate(o), key=itemgetter(1))[0])
        max_other.append(max(enumerate(o), key=itemgetter(1))[1])
    
    if global_mean_other is None:
        avg = sum(max_other)/len(max_other)
    else:
        avg = global_mean_other
   
    mean_norm_max_other = [i-avg for i in max_other]
    
    l = len(mean_norm_neutral)
    
    emo = []
    for i in range(l):
        if mean_norm_neutral[i] > mean_norm_max_other[i]:
            if mean_norm_neutral[i] > mean_norm_confusion[i]:
                emo.append([time[i],'Neutral'])
            else:
                emo.append([time[i],'Confused'])
        else:
            if mean_norm_max_other[i] > mean_norm_confusion[i]:
                emo.append([time[i],'Other'])
            else:
                emo.append([time[i],'Confused'])
    
    return emo

def get_facet_data_combined(file, start_time, end_time, global_mean_neutral, global_mean_other):
    time = []
    neutral = []
    other = []
    
    i = [5,6,7,8,9,11,13,12,14]
    with open(file,'r') as file:
        reader = csv.reader(file, dialect='excel')
        next(reader, None)
        for row in reader:
            if len(row) < 1:
                break
            if float(row[0]) > start_time/1000 and float(row[0]) < end_time/1000:
                t = float(row[0])*1000
                n = float(row[10])
                o = [float(row[ind]) for ind in i]
                time.append(t)
                neutral.append(n)
                other.append(o)
    
    
    #mean normalize value
    if global_mean_neutral is None:
        avg = sum(neutral)/len(neutral)
    else:
        avg = global_mean_neutral
    mean_norm_neutral = [i-avg for i in neutral]
    
    
    max_other = []
    max_ind = []
    for o in other:
        max_ind.append(max(enumerate(o), key=itemgetter(1))[0])
        max_other.append(max(enumerate(o), key=itemgetter(1))[1])
    
    if global_mean_other is None:
        avg = sum(max_other)/len(max_other)
    else:
        avg = global_mean_other
    mean_norm_max_other = [i-avg for i in max_other] 
    
    l = len(mean_norm_neutral)
    
    emo = []
    for i in range(l):
        if mean_norm_neutral[i] > mean_norm_max_other[i]:
            emo.append([time[i],'Neutral'])
        else:
            emo.append([time[i],'Other'])
    
    return emo
