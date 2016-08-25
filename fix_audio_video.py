#!/usr/bin/python
"""
Author-skarumbaiah
Date-06/23/2016

Script to create elan files for all participants in the video corpus for event and remark annotation 
Links to the appropriate video and audio files
Creates new file with name elan<participant#>.eaf

prereq-
place the template elan.eaf in the same folder as audio and video files 
template (elan.eaf) can be found in SVN

-e : elan file path
-a : audio video path

input:
new_elan_<num>.eaf files from elan_offset_calibrator script

example-
-e "E:/ENGAGE_Videos/Video Corpus Annotation/offset corrected elans with game log"
-a "E:/ENGAGE_Videos"
"""

from xml.dom.minidom import parse as pr
import os
import sys
import argparse

def generate_elan(elan,audio):
    
    for j in range(80):
        i = j+1
        
        if os.path.isfile(elan+'new_elan' + str(i) +'.eaf'):
            count = 0
            tree = pr(elan+'new_elan' + str(i) +'.eaf')
            annotationTree = tree.documentElement
            headers = annotationTree.getElementsByTagName("HEADER")

            for header in headers:
                media = header.getElementsByTagName("MEDIA_DESCRIPTOR")

                for med in media:
                    if count == 0:
                        if med.hasAttribute("MEDIA_URL") and not med.hasAttribute("EXTRACTED_FROM") :
                            count = 1
                            name = "file:///" + audio + str(i) + ".mp4"
                            med.setAttribute("MEDIA_URL", name )
                
                        if med.hasAttribute("RELATIVE_MEDIA_URL") and not med.hasAttribute("EXTRACTED_FROM"):
                            count = 1
                            name = "./" + str(i) + ".mp4"
                            med.setAttribute("RELATIVE_MEDIA_URL", name )
                    else:
                        if med.hasAttribute("EXTRACTED_FROM"):
                            name = "file:///" + audio  + str(i) + ".wav"
                            med.setAttribute("EXTRACTED_FROM", name )
                
                        if med.hasAttribute("MEDIA_URL"):
                            name = "file:///" + audio  + str(i) + ".wav"
                            med.setAttribute("MEDIA_URL", name )
                
                        if med.hasAttribute("RELATIVE_MEDIA_URL"):
                            name = "./" + str(i) + ".wav"
                            med.setAttribute("RELATIVE_MEDIA_URL", name )
 
            open(elan + 'elan' + str(i) +'.eaf', 'w').close()
            new_efname =  elan + 'elan' + str(i) +'.eaf'
            tree.writexml( open(new_efname, 'w'),
                               indent="  ",
                               addindent="  ",
                               newl='\n')
                
print("Created new elan files")

def main(args):
    """ parse command like argument"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-e", "--elan")
    parser.add_argument("-a", "--audio")

    args = parser.parse_args()

    elan = args.elan
    audio = args.audio
       
    print("Looking for audio in the directory -", audio) 
    print("Looking for elan in the directory -", elan)
    generate_elan(elan,audio)

if __name__ == '__main__':
    main(sys.argv[1:])
    