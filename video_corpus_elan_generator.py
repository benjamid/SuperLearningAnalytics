#!/usr/bin/python
"""
Author-skarumbaiah
Date-06/23/2016

Script to create elan files for all participants in the video corpus for event and remark annotation 
Links to the appropriate video and audio files
Creates new file with name elan<participant#>.eaf

prereq-
expects the template elan.eaf in the same folder as the script which is how it is SVN

example-
-p "C:/Users/skarumbaiah/Desktop/test/"
"""

from xml.dom.minidom import parse as pr
import os
import sys
import argparse

def generate_elan(dirc):
    tree = pr('elan.eaf')
    annotationTree = tree.documentElement
    
    for j in range(80):
        i = j+1
        audiofile = dirc +str(i)+".wav"
        if os.path.isfile(audiofile):
            headers = annotationTree.getElementsByTagName("HEADER")

            for header in headers:
                media = header.getElementsByTagName("MEDIA_DESCRIPTOR")

                for med in media:
                    if med.hasAttribute("MEDIA_URL") and not med.hasAttribute("EXTRACTED_FROM") :
                        name = "file:///" + dirc + str(i) + ".mp4"
                        med.setAttribute("MEDIA_URL", name )
                
                    if med.hasAttribute("RELATIVE_MEDIA_URL") and not med.hasAttribute("EXTRACTED_FROM"):
                        name = "./" + str(i) + ".mp4"
                        med.setAttribute("RELATIVE_MEDIA_URL", name )
                
                    if med.hasAttribute("EXTRACTED_FROM"):
                        name = "file:///" + dirc  + str(i) + ".mp4"
                        med.setAttribute("EXTRACTED_FROM", name )
                
                    if med.hasAttribute("MEDIA_URL") and med.hasAttribute("EXTRACTED_FROM"):
                        name = "file:///" + dirc  + str(i) + ".wav"
                        med.setAttribute("MEDIA_URL", name )
                
                    if med.hasAttribute("RELATIVE_MEDIA_URL") and med.hasAttribute("EXTRACTED_FROM"):
                        name = "./" + str(i) + ".wav"
                        med.setAttribute("RELATIVE_MEDIA_URL", name )
 
                        new_efname =  dirc + 'elan' + str(i) +'.eaf'
                        tree.writexml( open(new_efname, 'w'),
                               indent="  ",
                               addindent="  ",
                               newl='\n')
                
print("Created new elan files")

def main(args):
    """ parse command like argument"""
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--path")

    args = parser.parse_args()

    dirc = args.path
        
    print("Looking in the directory -", dirc)
    generate_elan(dirc)

if __name__ == '__main__':
    main(sys.argv[1:])
    
