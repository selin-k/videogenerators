
from pydub import AudioSegment 
import speech_recognition as sr
from pydub.playback import play
import os, sys
from PIL import Image
import moviepy.editor as mp
from moviepy.editor import ImageSequenceClip
from moviepy import editor
import os.path as op
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer 
from nltk import ne_chunk
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import logging
from pypexels import PyPexels
import requests
import re
import urllib3
import shutil
from datetime import datetime




def speech_to_text(audio, outputfile):
    DIRECTORY = r'/videogenerators/processing/videos/'
    DIRECTORY1DOWN = r'/videogenerators/processing/'
    DIRECTORYCHUNKS = r'/videogenerators/processing//audio_chunks'
    audio = AudioSegment.from_mp3(audio)
    audio = audio.export("audio.wav", format="wav")
    audio = AudioSegment.from_wav(audio) 
    n = len(audio) 
    audio_len = audio.duration_seconds
    counter = 0
    vidcount = 1
    fh = open(outputfile +".txt", "w+") 
    interval = 5 * 1000
    overlap = 1.5 * 1000
    start = 0
    end = 0
    flag = 0
    vidname = []
    video_filenames = []
    videocount = 0
    
    #Analyze the text with nlp techniques and extract keywords, append to a list
    def nlp(filename):
        print("Analyzing the text...")
        #os.chdir(r"/videogenerators/processing/nlapi-python")
        sys.path.append("/usr/lib/python3/dist-packages/nlapi-python")
        from expertai.client import ExpertAiClient
        #from expertai import client
        import json 

        os.environ["EAI_USERNAME"] = "@@@@@@@"
        os.environ["EAI_PASSWORD"] = "#######"

        text = open(filename + ".txt").read()

        eai = ExpertAiClient()
        language= 'en'
        response = eai.full_analysis(body={"document": {"text": text}}, params={'language': language})
        data = response.json["data"]
        word_list = []

        for val in data["mainLemmas"]:
            print("values: ", val["value"])
            word_list.append(val["value"])


        for label in data["topics"]:
            if label["winner"] == True:
                print("winner topic: ", label["label"])
                word_list.append(label["label"])

        os.chdir("..")
        print(word_list)
        return word_list


    #loop through keywords in the list, find a video for each 
    def pullvideos(wordlist):
        api_key = '@@@@@@@@@@'
        py_pexel = PyPexels(api_key=api_key)
        novid = False
        video_links = []
        length = len(wordlist)


        def search_vids(word, flag, topicused, multiplevids):
            # search for vids
            print(word)
            if multiplevids == True:
                search_videos_page = py_pexel.videos_search(query=word, per_page=5, min_duration=6, max_duration=30)
                links = []
                for video in search_videos_page.entries:
                    for x in video.video_files:
                        link = str(x.get("link"))
                        links.append(link)
                    for link in links:
                        if not link in video_links:
                            video_links.append(link)
                            multiplevids = False
                            return video_links
            else:
                search_videos_page = py_pexel.videos_search(query=word, per_page=1, min_duration=6, max_duration=30)
                     
                for video in search_videos_page.entries:
                    for x in video.video_files:
                        # get link of video from json output >> dictionary
                        link = str(x.get("link"))
                        if not link in video_links:
                            video_links.append(link)
                            return video_links
                        else:
                            if flag == 1 and topicused == True:
                                
                                topic = wordlist[length - 3]
                                multiplevids = True
                                search_vids(topic, flag, topicused, multiplevids)
                            else:
                                topic = wordlist[length - 3]
                                flag = 1
                                topicused = True
                                search_vids(topic, flag, topicused, multiplevids) 
                
            return video_links

        
        # loop through word list and search for vids
        multiplevids = False
        flag = 0
        topicused = False
        for word in wordlist:
            video_links = search_vids(word, flag, topicused, multiplevids)
        video_links = list(set(video_links))
        return video_links



    #download the found videos through their urls to video path
    def downloadvideos(links, wordlist):
        os.chdir(DIRECTORY)
        video_filenames = []
        c = urllib3.PoolManager()
        counter = 0
        linkdict = {}
        file_dups = []
        for link in links:
            if not link == "":
                file_link = re.findall("(.+\.mp4)", link)
                path = "".join(file_link)
                firstpos=path.rfind("/")
                lastpos=path.rfind(".")
                path = path[firstpos+1:lastpos]
                path = re.findall("(\d+)", path)
                path = "".join(path)
                if not path in file_dups:
                    linkdict[link] = path
                    file_dups.append(path)
        for keys, values in linkdict.items():
            filename = str(wordlist[counter]) + ".mp4"
            video_filenames.append(filename)
            with c.request('GET',keys , preload_content=False) as resp, open(filename, 'wb') as out_file:
                shutil.copyfileobj(resp, out_file)
            resp.release_conn()
        counter += 1
        return video_filenames


        
    def makevideofromvideos(video_filenames, video_length):
        print("Making the video...")
        path = DIRECTORY
        directory = sorted(os.listdir(path))
        video_list = video_filenames
        print("VIDEO PRESENT: ", video_list)
        os.chdir("..")
        os.chdir(path) 
        name_list = []
        vidcount = 1
        print("VIDEO LENGTH: ", video_length)
        for vid in video_list:
            print("VID:", vid)
            vidname = "video" + str(vidcount) + ".mp4"
            print("vidname:", vidname)
            my_clip = mp.VideoFileClip(vid)
            if my_clip.duration > video_length:
                start_time = 0
                end_time = video_length
                ffmpeg_extract_subclip(vid, start_time, end_time, targetname=vidname)
            else:
                start_time = 0
                end_time = my_clip.duration
                ffmpeg_extract_subclip(vid, start_time, end_time, targetname=vidname)
            name_list.append(vidname)
            vidcount += 1
        return name_list
        os.chdir("..")
        
        


    try:
        os.mkdir('audio_chunks') 
    except(FileExistsError):
        pass 

    for i in range(0, 2 * n, interval):
        if not os.getcwd() == DIRECTORY1DOWN:
            os.chdir("..")
            os.chdir(DIRECTORYCHUNKS)
        if not os.getcwd() == DIRECTORYCHUNKS:
            os.chdir(DIRECTORYCHUNKS)
        if i == 0: 
            start = 0
            end = interval 
        else:
            start = end - overlap 
            end = start + interval 


        if end >= n:
            end = n
            flag = 1
        one_sec_segment = AudioSegment.silent(duration=500)
        chunk = one_sec_segment + audio[start:end] + one_sec_segment
        filename = 'chunk'+str(counter)+'.wav'
        chunk.export(filename, format ="wav") 
        print("Processing audio...")
        counter += 1
        AUDIO_FILE = filename 

        r = sr.Recognizer()
        
        with sr.AudioFile(AUDIO_FILE) as source:
            audio_listened = r.listen(source) 

        try:
            print("Converting speech to text...")
            #recognize audio + analyze text + get image + export mp4 into a directory no audio --> concatenate all in directory for final vid!
            rec = r.recognize_google(audio_listened)
            fh.write(rec+" ") 

        except sr.UnknownValueError:
            #unrecognized audio exception --> remove the chunk + blank screen
            print("Removing silences and unrecognizable words...")
            os.chdir("..")

        except sr.RequestError as e:
            print("Could not request results.") 

        if flag == 1:
            word_list = nlp(videoname)
            if not word_list == []:
                videocount += len(word_list)
                links = pullvideos(word_list)
                video_filenames.append(downloadvideos(links, word_list))                
                video_length = audio_len / videocount
                print(video_length)
                video_filenames = sum(video_filenames, [])
                vidname = makevideofromvideos(video_filenames, video_length)
                print("VIDEO FILENAMES: ", video_filenames)
                fh.close()
                print("VIDEO LIST:", vidname)
                return vidname, counter
                os.chdir('..') 
                print("Processing completed!")  
            else:
                return [], 0
            break         

            
            

def concatenate_clips(videoname, vidnames, counter, og_audio):
        DIRECTORY = r'/videogenerators/processing/videos/'
        # all the video{num}.mp4 format vids must be concatenated and exported with the og audio in the background
        os.chdir(DIRECTORY)
        new_list = []
        #open the filenames in video format
        for vids in vidnames:
            clip = mp.VideoFileClip(vids)
            clip_resized = clip.resize(height=360)
            new_list.append(clip_resized)
        print("NEW LIST: ", new_list)
        #concatenate all the chunk videos into one 
        concat_clip = mp.concatenate_videoclips(new_list, method="compose")
        audio = mp.AudioFileClip(og_audio)
        #set the original audio from which the video is made in the background
        new_clip = concat_clip.set_audio(audio)
        clip_duration = new_clip.duration
        start_time = 0
        # for this to work counter needs to be properly ascending
        end_time = clip_duration - counter
        #export as mp4 file and cut out the silent bit at the end due to the 1 min i added to the chunks during stt
        new_clip.write_videofile(videoname + '.mp4')
        #ffmpeg_extract_subclip(videoname + 'test.mp4', start_time, end_time, targetname=videoname + '.mp4')


cc = 0
while True:
    if __name__ == "__main__":
        isempty = True
        path_string = r"/var/www/html/videos"
        destination_path = r"/var/www/html/processed_audios"
        path = os.listdir(r"/var/www/html/videos")
        if os.path.isdir(path_string):
            if path:
                isempty = False
                for fn in path:
                    if fn.lower().endswith(".mp3"):
                        audio = fn
                        audio = path_string + "/" + audio
        if isempty == False:

            videoname = input("What is the name of the output video? ")
            videoname = str(cc)
            outputfilename = videoname 
            vidnames, counter = speech_to_text(audio, outputfilename)
            if not vidnames == []:
                concatenate_clips(videoname, vidnames, counter, audio)
                cc += 1
        else:
            print("record new audio from https://videogenerators.com")
        try:
            print(shutil.move(audio, destination_path))

        except:
            print("error")
            pass
        


     
    
