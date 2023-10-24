import tkinter as tk
from tkinter import filedialog 
from tkinter.filedialog import askopenfile
from PIL import Image, ImageTk
import boto3 

import os
import sys
from tempfile import gettempdir
from contextlib import closing

my_w=tk.Tk() #my_w: my window
my_w.geometry("450x400")
my_w.title("AWS Textract")

l1=tk.Label(my_w,text="Upload an Image",width=30,font=('times',18,'bold'))
l1.pack()

b1=tk.Button(my_w,text='Upload Images And See What It Has!!',width=30,command= lambda:upload_file())
b1.pack()

b2=tk.Button(my_w,text='Read',width=30,command= lambda:getText())
b2.pack()

textExample=tk.Text(my_w,height=10) ###
textExample.pack()

def upload_file():
    aws_mag_con=boto3.session.Session(profile_name='demo_user')
    client=aws_mag_con.client(service_name='textract',region_name='us-east-1')
    global img
    f_types=[("All files", "*.*")]
    filename=filedialog.askopenfilename(filetype=f_types)
    img=Image.open(filename)
    #resizing, I need my image to fit into tkinter geometry of 450x400
    img_resize=img.resize((400,200))
    img=ImageTk.PhotoImage(img_resize)#to display the resized image

    imgbytes=get_image_byte(filename)#to cnvert your image to byte form
    
    b2=tk.Button(my_w,image=img)#to display image in the button also
    b2.pack()
     

    #global s 
    s=""
    response=client.detect_document_text(Document={'Bytes':imgbytes})
    for item in response['Blocks']:
         if item['BlockType']=='WORD':
              print(item['Text'])
              s=s+(item['Text'])+" "
    textExample.insert(tk.END, s)

def get_image_byte(filename):
        with open(filename,'rb') as imgfile:
            return imgfile.read()



def getText():
    aws_mag_con=boto3.session.Session(profile_name='demo_user')
    client=aws_mag_con.client(service_name='polly',region_name='us-east-1')
    result=textExample.get("1.0","end")  ###
    print(result)
    response=client.synthesize_speech(VoiceId='Joanna',OutputFormat='mp3',Text=result,Engine='neural')
    print(response)
    if "AudioStream" in response:
        with closing(response['AudioStream']) as stream:
            output=os.path.join(gettempdir(),"speech.mp3")
            try:
                with open(output,"wb") as file:
                    file.write(stream.read())
            except IOError as error:
                print(error)
                sys.exit(-1)
    else:
        print("Could not find the stream")
        sys.exit(-1)

    if sys.platform=='win32':
        os.startfile(output)

my_w.mainloop()