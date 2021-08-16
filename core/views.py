from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.shortcuts import render
from django.http import HttpResponse
from flask import Flask, render_template, request
from werkzeug.utils import secure_filename
import os
import sys
import boto3
import json
import csv
import requests
import time
import pyaudio
import wave
import math
import struct
import boto3
from array import array
from struct import pack
from sys import byteorder
from requests.auth import HTTPBasicAuth
import copy
from django.views.decorators.csrf import csrf_exempt
# os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="gcloud_json.json"
# from google.cloud import speech_v1p1beta1 as speech
# from google.cloud import translate_v2

# client = speech.SpeechClient()
# from trp import Document as trpDoc
session = boto3.Session(
    aws_access_key_id=key,
    aws_secret_access_key=key,)

s3 = session.client('s3')

BUCKET_NAME='speech-trans'

from .models import Document

global final
global arr

class DocumentCreateView(CreateView):
    model = Document
    fields = ['upload', ]
    success_url = reverse_lazy('home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        documents = Document.objects.all()
        context['documents'] = documents
        return context


def extract(request, file_name):

    session = boto3.Session(
        aws_access_key_id=key,
        aws_secret_access_key=key,)

    #s3 = session.client('s3')
    s3 = session.resource('s3')
    documentName = "audio/"+file_name
    object_acl = s3.ObjectAcl('speech-trans',documentName)
    response = object_acl.put(ACL='public-read')
    
    if request.method == 'POST':
        if request.POST.get('exportMenu'):
            response = HttpResponse(content_type='text/csv')

            writer = csv.writer(response)
            # print("\n\n Final in export")
            global final
            global arr
            # print(final)
            # print("\n\n Final in export")
            # writer.writerow(['cID', 'Customer Name', 'Address', 'E-mail', 'GST IN'])
            # for cust in CustomerMaster.objects.all().values_list('cID', 'cName', 'address', 'email', 'gstIN'):
            #     writer.writerow(cust)

            # writer.writerow(['WELCOME','TO','NSTORE','SPEECH','TO','TEXT'])
            csv_col=['Item','Quantity','Price']
            p = 0
            t = 0
            disp=[]
            while(p<len(final)):
                if(final[p]=='@'):
                    print(arr[t],end='  ')
                    disp.append(arr[t])
                    t=t+1
                    if (len(final)>p+1) and (final[p+1]!='@'):
                        print('\n')
                        writer.writerow(disp)
                        disp.clear()
                else :
                    print(final[p],end=' ')
                    disp.append(final[p])
                p=p+1

            csv_name = file_name + '.csv'
            response['Content-Disposition'] = 'attachment; filename='+csv_name
            return response
        
        else:
            dateUploaded = request.POST['doc_obj']
            audioURL = request.POST['url']
            print(dateUploaded)

            file_doc = Document.objects.filter(uploaded_at__startswith=str(dateUploaded))
            print(file_doc)
           
           


            ###################################################################
        
            
            aws_access_key_id = key
            aws_secret_access_key = key
            region = "ap-south-1"
            
            session = boto3.Session(
            aws_access_key_id=key,
            aws_secret_access_key=key)
            trans = boto3.client('transcribe')
            transcribe = boto3.client('transcribe', region_name='ap-south-1')
            try:
                trans.get_transcription_job(TranscriptionJobName='trans_with_model18')
                trans.delete_transcription_job(TranscriptionJobName='trans_with_model18')
            except:
                pass
            response = trans.start_transcription_job(
                TranscriptionJobName='trans_with_model18',
                LanguageCode='en-US',
                MediaFormat='wav',
                Media={
                    'MediaFileUri':audioURL
                },
                OutputBucketName='speech-trans',
                ModelSettings={
                    'LanguageModelName': 'newmodel'
                },
                ContentRedaction={
                    'RedactionType': 'PII',
                    'RedactionOutput': 'redacted'
                },
            )

            while True:
                status=trans.get_transcription_job(TranscriptionJobName='trans_with_model18')
                if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                    break
                print('not yet')
                time.sleep(5)
            script=status['TranscriptionJob']['Transcript']
            #print(script)
            print(status)
            link=script['RedactedTranscriptFileUri']
            print(link)
            jsonfile=requests.get(link)
            print(jsonfile)
            s3 = session.resource('s3')
            object_acl = s3.ObjectAcl('speech-trans','redacted-trans_with_model18.json')
            response = object_acl.put(ACL='public-read')
            trans.delete_transcription_job(TranscriptionJobName='trans_with_model18')
            #--------------
            arr=[]
            file123=requests.get('https://s3.ap-south-1.amazonaws.com/speech-trans/redacted-trans_with_model18.json')
            newfile=file123.json()
            file234=newfile['results']['transcripts']
            file456=file234[0]
            file567=file456['transcript']
            #========================================================#
            aws_access_key_id = key
            aws_secret_access_key = key
            region = "ap-south-1"
            comprehend = boto3.client(service_name='comprehend', region_name='ap-south-1')
            newjson=json.loads(json.dumps(comprehend.detect_entities(Text=file567, LanguageCode='en'), sort_keys=True, indent=4))
            for data in newjson['Entities']:
                if(data['Type'] == "QUANTITY"):
                    arr.append(data['Text'])
            #print(arr)
            n=0
            while(n<len(arr)):
                file567=file567.replace(arr[n],'@')
                n=n+1
            file567=file567.replace("MRP",'')
            file567=file567.replace('retail price','')
            #print(result_1)
            listfin = file567.split(' ')
            print(listfin)
            t=0
            p=0
            disp=[]
            final=20*['','','']
            final[0]=listfin[0]
            j=0
            i=1
            while(len(listfin)>i):
                if(listfin[i]!='@'):
                    final[j]=final[j]+' '+listfin[i]
                elif (listfin[i]=='@'):
                    if (listfin[i-1]!='@'):
                        j=j+1
                    final[j]='@'
                    j=j+1
                    t=t+1
                i=i+1
            print(final)
            t=0        
                    
            neat_op = []      
            with open('newcodE1.csv', 'w', newline='',encoding='utf-8') as file:
                writer=csv.writer(file)
                #writer.writerow(['WELCOME','TO','NSTORE','SPEECH-TO','TEXT'])
                writer.writerow(['ITEM NAME', 'QUANTITY','PRICE'])
                while(p<len(final)):
                    if(final[p]=='@'):
                        if(t<len(arr)):
                            print(arr[t],end='  ')
                            neat_op.append(arr[t])
                            neat_op.append("  ")
                            disp.append(arr[t])
                        t=t+1
                        if (len(final)>p+1) and (final[p+1]!='@'):
                            print('\n')
                            neat_op.append("\n")
                            writer.writerow(disp)
                            disp.clear()
                    else :
                        print(final[p],end=' ')
                        disp.append(final[p])
                        neat_op.append(final[p]) 
                        neat_op.append("  ")
                    p=p+1

            ###################################################################

    return render(request, "core/extract.html", {"name":file_name, "file":file_doc, "url":audioURL, "audio_result":neat_op } )

    # "audio_result": final

final = [] 
def record(request):
    global final
    global arr
    if request.method == 'POST':
        if request.POST.get('start'):
            global final
            global arr
            # Start Code
            final = "start" 

            THRESHOLD = 500  # audio levels not normalised.
            CHUNK_SIZE = 1024
            SILENT_CHUNKS = 3 * 44100 / 1024  # about 3sec
            FORMAT = pyaudio.paInt16
            FRAME_MAX_VALUE = 2 ** 15 - 1
            NORMALIZE_MINUS_ONE_dB = 10 ** (-1.0 / 20)
            RATE = 44100
            CHANNELS = 1
            TRIM_APPEND = RATE // 4

            def is_silent(data_chunk):
                """Returns 'True' if below the 'silent' threshold"""
                return max(data_chunk) < THRESHOLD

            def normalize(data_all):
                """Amplify the volume out to max -1dB"""
                # MAXIMUM = 16384
                normalize_factor = (float(NORMALIZE_MINUS_ONE_dB * FRAME_MAX_VALUE)
                                    // max(abs(i) for i in data_all))

                r = array('h')
                for i in data_all:
                    r.append(int(i * normalize_factor))
                return r

            def trim(data_all):
                _from = 0
                _to = len(data_all) - 1
                for i, b in enumerate(data_all):
                    if abs(b) > THRESHOLD:
                        _from = max(0, i - TRIM_APPEND)
                        break

                for i, b in enumerate(reversed(data_all)):
                    if abs(b) > THRESHOLD:
                        _to = min(len(data_all) - 1, len(data_all) - 1 - i + TRIM_APPEND)
                        break

                return copy.deepcopy(data_all[_from:(_to + 1)])

            def record():
                """Record a word or words from the microphone and 
                return the data as an array of signed shorts."""

                p = pyaudio.PyAudio()
                stream = p.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, output=False, frames_per_buffer=CHUNK_SIZE)

                silent_chunks = 0
                audio_started = False
                data_all = array('h')

                while True:
                    # little endian, signed short
                    data_chunk = array('h', stream.read(CHUNK_SIZE))
                    if byteorder == 'big':
                        data_chunk.byteswap()
                    data_all.extend(data_chunk)

                    silent = is_silent(data_chunk)

                    if audio_started:
                        if silent:
                            silent_chunks += 1
                            if silent_chunks > SILENT_CHUNKS:
                                break
                        else: 
                            silent_chunks = 0
                    elif not silent:
                        audio_started = True              

                sample_width = p.get_sample_size(FORMAT)
                stream.stop_stream()
                stream.close()
                p.terminate()

                data_all = trim(data_all)  # we trim before normalize as threshhold applies to un-normalized wave (as well as is_silent() function)
                data_all = normalize(data_all)
                return sample_width, data_all

            def record_to_file(path):
                "Records from the microphone and outputs the resulting data to 'path'"
                sample_width, data = record()
                data = pack('<' + ('h' * len(data)), *data)

                wave_file = wave.open(path, 'wb')
                wave_file.setnchannels(CHANNELS)
                wave_file.setsampwidth(sample_width)
                wave_file.setframerate(RATE)
                wave_file.writeframes(data)
                wave_file.close()

            
            print("Wait in silence to begin recording; wait in silence to terminate")
            record_to_file('output.wav')
            print("done")

            mic_record_cust='output.wav'
            #============================UPLOAD AUDIO TO S3====================================
            s3 = boto3.resource('s3')
            s3.meta.client.upload_file(mic_record_cust, 'speech-trans', 'micaudio_cust')
            #==================================================================================



            session = boto3.Session(
            aws_access_key_id=key,
            aws_secret_access_key=key)
            trans = boto3.client('transcribe')
            transcribe = boto3.client('transcribe', region_name='ap-south-1')
            try:
                trans.get_transcription_job(TranscriptionJobName='trans_with_model_mic1')
                trans.delete_transcription_job(TranscriptionJobName='trans_with_model_mic1')
            except:
                pass
            response = trans.start_transcription_job(
                TranscriptionJobName='trans_with_model_mic1',
                LanguageCode='en-US',
                MediaFormat='wav',
                Media={
                    'MediaFileUri': 'https://speech-trans.s3.ap-south-1.amazonaws.com/micaudio_cust'
                },
                OutputBucketName='speech-trans',
                ModelSettings={
                    'LanguageModelName': 'newmodel'
                },
                ContentRedaction={
                    'RedactionType': 'PII',
                    'RedactionOutput': 'redacted'
                },
            )
            s=0
            while True:
                status=trans.get_transcription_job(TranscriptionJobName='trans_with_model_mic1')
                if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                    break
                if s==0:
                    print('Processing..')
                    s=s+1
                time.sleep(5)
            script=status['TranscriptionJob']['Transcript']
            #print(script)
            print(status)
            link=script['RedactedTranscriptFileUri']
            print(link)
            jsonfile=requests.get(link)
            print(jsonfile)
            s3 = session.resource('s3')
            object_acl = s3.ObjectAcl('speech-trans','redacted-trans_with_model_mic1.json')
            response = object_acl.put(ACL='public-read')
            trans.delete_transcription_job(TranscriptionJobName='trans_with_model_mic1')
            #--------------
            arr=[]
            file123=requests.get('https://s3.ap-south-1.amazonaws.com/speech-trans/redacted-trans_with_model_mic1.json')
            newfile=file123.json()
            file234=newfile['results']['transcripts']
            file456=file234[0]
            file567=file456['transcript']
            #========================================================#
            aws_access_key_id = key
            aws_secret_access_key = key
            region = "ap-south-1"
            comprehend = boto3.client(service_name='comprehend', region_name='ap-south-1')
            newjson=json.loads(json.dumps(comprehend.detect_entities(Text=file567, LanguageCode='en'), sort_keys=True, indent=4))
            for data in newjson['Entities']:
                if(data['Type'] == "QUANTITY"):
                    arr.append(data['Text'])
            #print(arr)
            n=0
            while(n<len(arr)):
                file567=file567.replace(arr[n],'@')
                n=n+1
            file567=file567.replace("MRP",'')
            file567=file567.replace('retail price','')
            #print(result_1)
            listfin = file567.split(' ')
            print(listfin)
            t=0
            p=0
            disp=[]
            final=20*['','','']
            final[0]=listfin[0]
            j=0
            i=1
            while(len(listfin)>i):
                if(listfin[i]!='@'):
                    final[j]=final[j]+' '+listfin[i]
                elif (listfin[i]=='@'):
                    if (listfin[i-1]!='@'):
                        j=j+1
                    final[j]='@'
                    j=j+1
                    t=t+1
                i=i+1
            print(final)
            t=0        

            neat_op = []      
            with open('newcodE1.csv', 'w', newline='',encoding='utf-8') as file:
                writer=csv.writer(file)
                #writer.writerow(['WELCOME','TO','NSTORE','SPEECH-TO','TEXT'])
                writer.writerow(['ITEM NAME', 'QUANTITY','PRICE'])
                while(p<len(final)):
                    if(final[p]=='@'):
                        if(t<len(arr)):
                            print(arr[t],end='  ')
                            neat_op.append(arr[t])
                            neat_op.append("  ")
                            disp.append(arr[t])
                        t=t+1
                        if (len(final)>p+1) and (final[p+1]!='@'):
                            print('\n')
                            neat_op.append("\n")
                            writer.writerow(disp)
                            disp.clear()
                    else :
                        print(final[p],end=' ')
                        disp.append(final[p])
                        neat_op.append(final[p]) 
                        neat_op.append("  ")
                    p=p+1

                # neat_op = []

                # with open('innovator.csv', 'w', newline='',encoding='utf-8') as file:
                #     writer=csv.writer(file)
                #     writer.writerow(['ITEM NAME', 'QUANTITY','PRICE'])
                #     csv_col=['Item','Quantity','Price']
                #     while(p<len(final)):
                #         if(final[p]=='@'):
                #             # print(arr[t],end='  ')
                #             # print("while if")
                #             neat_op.append(arr[t])
                #             neat_op.append("  ")
                #             disp.append(arr[t])
                #             t=t+1
                #             if (len(final)>p+1) and (final[p+1]!='@'):
                #                 # print('\n')
                #                 # neat_op.append("\n")
                #                 writer.writerow(disp)
                #                 disp.clear()
                #         else :
                #             # print(final[p],end=' ')
                #             # print("while else")
                #             disp.append(final[p])
                #             neat_op.append(final[p]) 
                #             neat_op.append("  ")
                #             # print(disp)
                #         p=p+1    
                
                # break


            return render(request, "core/record.html", {"audio_result":neat_op } )
        
        if request.POST.get('stop'):
            # Stop code
            final = "stop"
            # return render(request, "core/record.html", {"audio_result":final } )

        if request.POST.get('exportMenu'):
            response = HttpResponse(content_type='text/csv')

            writer = csv.writer(response)
            # global arr
            print("\n\n\n\n Final from Export CSV ")
            print(final)

            p = 0
            t = 0
            disp=[]

            writer.writerow(['ITEM NAME', 'QUANTITY','PRICE'])
            while(p<len(final)):
                if(final[p]=='@'):
                    if(t<len(arr)):
                        print(arr[t],end='  ')
                        disp.append(arr[t])
                    t=t+1
                    if (len(final)>p+1) and (final[p+1]!='@'):
                        print('\n')
                        writer.writerow(disp)
                        disp.clear()
                else:
                    print(final[p],end=' ')
                    disp.append(final[p])
                p=p+1

            csv_name = 'output.csv'
            response['Content-Disposition'] = 'attachment; filename='+csv_name
            return response

    return render(request, "core/record.html", {"audio_result" : final })

@csrf_exempt
def api(request):
    
    
    if request.method == 'POST':
        aud = request.FILES['file']
        session = boto3.Session(
            aws_access_key_id=key,
            aws_secret_access_key=key,)

        s3 = session.client('s3')
        if aud:
            filename = str(aud)
            response = s3.put_object(
                    ACL='public-read',
                    Body = aud,
                    Bucket = BUCKET_NAME,
                    Key = str(aud),   
                    )   
        trans = boto3.client('transcribe')
        transcribe = boto3.client('transcribe', region_name='ap-south-1')
        media_uri = "https://speech-trans.s3.ap-south-1.amazonaws.com/"+filename
        try:
            trans.get_transcription_job(TranscriptionJobName=L'FASKNEW_2')
            trans.delete_transcription_job(TranscriptionJobName='FASKNEW_2')
        except:
            pass
        response = trans.start_transcription_job(
            TranscriptionJobName='FASKNEW_2',
            LanguageCode='en-US',
            MediaFormat='wav',
            Media={
                'MediaFileUri': media_uri,
            },
            OutputBucketName='speech-trans',
            ModelSettings={
                'LanguageModelName': 'newmodel'
            },
            ContentRedaction={
                'RedactionType': 'PII',
                'RedactionOutput': 'redacted'
            },
        )
        s=0
        while True:
            status=trans.get_transcription_job(TranscriptionJobName='FASKNEW_2')
            if status['TranscriptionJob']['TranscriptionJobStatus'] in ['COMPLETED', 'FAILED']:
                break
            if s==0:
                print('Processing..')
                s=s+1
            time.sleep(5)
        script=status['TranscriptionJob']['Transcript']
        #print(script)
        print(status)
        link=script['RedactedTranscriptFileUri']
        print(link)
        jsonfile=requests.get(link)
        print(jsonfile)
        s3 = session.resource('s3')
        object_acl = s3.ObjectAcl('speech-trans','redacted-FASKNEW_2.json')
        response = object_acl.put(ACL='public-read')
        trans.delete_transcription_job(TranscriptionJobName='FASKNEW_2')
        #-------------- 
        arr=[]
        file123=requests.get('https://s3.ap-south-1.amazonaws.com/speech-trans/redacted-FASKNEW_2.json')
        newfile=file123.json()
        file234=newfile['results']['transcripts']
        file456=file234[0]
        file567=file456['transcript']
        #========================================================#
        aws_access_key_id = key
        aws_secret_access_key = key
        region = "ap-south-1"
        comprehend = boto3.client(service_name='comprehend', region_name='ap-south-1')
        newjson=json.loads(json.dumps(comprehend.detect_entities(Text=file567, LanguageCode='en'), sort_keys=True, indent=4))
        for data in newjson['Entities']:
            if(data['Type'] == "QUANTITY"):
                arr.append(data['Text'])
        #print(arr)
        n=0
        while(n<len(arr)):
            file567=file567.replace(arr[n],'@')
            n=n+1
        file567=file567.replace("MRP",'')
        file567=file567.replace('retail price','')
        #print(result_1)
        listfin = file567.split(' ')
        print(listfin)
        t=0
        p=0
        disp=[]
        final=20*['','','']
        final[0]=listfin[0]
        j=0
        i=1
        while(len(listfin)>i):
            if(listfin[i]!='@'):
                final[j]=final[j]+' '+listfin[i]
            elif (listfin[i]=='@'):
                if (listfin[i-1]!='@'):
                    j=j+1
                final[j]='@'
                j=j+1
                t=t+1
            i=i+1
        print(final)
        t=0
        #final_str = []
                
        with open('innovators1.csv', 'w', newline='',encoding='utf-8') as file:
            writer=csv.writer(file)
            #writer.writerow(['WELCOME','TO','NSTORE','SPEECH','TO','TEXT'])
            csv_col=['Item','Quantity','Price']
            while(p<len(final)):
                if(final[p]=='@'):
                    print(arr[t],end='  ')
                    #final_str.append(arr[t])
                    disp.append(arr[t])
                    t=t+1
                    if (len(final)>p+1) and (final[p+1]!='@'):
                        print('\n')
                        writer.writerow(disp)
                        disp.clear()
                else :
                    print(final[p],end=' ')
                    disp.append(final[p])
                p=p+1

        exampleReader = csv.reader(open('innovators1.csv'))
        csvList = list(exampleReader)
        print(csvList)
        print(type(csvList))
        final_str = ""
        for ele in csvList:
            for li in ele:
                final_str += li
                final_str += ", "
            final_str += '\n'
        print(final_str)
        print(type(final_str))
    return HttpResponse(final_str)

