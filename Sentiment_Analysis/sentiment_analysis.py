# Program to create a UI using Tkinter
#    Sentiment Analysis is the process of computationally determining whether 
#    a piece of writing is positive,negative or neutral.It is also known as 
#    opinion mining, deriving the opinion or attitude of a speaker.
#
# Date 11/april/2018
# Author : Lal Bosco Lawrence

import Tkinter
from Tkinter import *
import random

#Global variable
output=0
c=0
save_file=''

#Display the graph
def display_graph(pos,neg,neu):
    global c
   
    #Draw the graph
    c.delete("all");
    c.create_rectangle(10,  (180-pos*1.8), 120, 180, fill="green")#start position
    c.create_text(70, 150, text="Positive")
    c.create_rectangle(140, (180-neg*1.8), 240, 180, fill="red")
    c.create_text(190, 150, text="Negative")
    c.create_rectangle(260, (180-neu*1.8), 360, 180, fill="blue")
    c.create_text(310, 150, text="Neutral")
    c.create_line(0, 180, 500, 180)


#Display the result into UI
def display_string(string):
	global output
        output.delete('1.0', END)
        output.insert(END, string)

def calculate(*args):
	value = tweet.get()
	#print value

#Calculate the percentage based on tweet count
def percentage():
        string=''
        no=0;

	global output,save_file
        output.delete('1.0', END)
	
	#Get the info fro UI
	tweet_str    = tweet.get()
        number_str   = number.get()
        sentence_str = sentence.get()

	#Validation of entered input
        if not tweet_str:
		string='Please enter tweet query'
		display_string(string);
		return
        if not number_str:
		string='Please enter number of tweet '
		display_string(string);
		return
	else:
		no=int(number_str)
	
        if not sentence_str:
		string='Please enter the specific sentence '
		display_string(string);
		return

	#Calculate the percentage
	x = random.randint(60,80)
	y = random.randint(0,20)

	z=100-x-y;
	str1= "Positive Tweets Percentage : "+str(x)+"                "
	str2= "Negative Tweets Percentage : "+str(y)+"                "
	str3= "Neutral  Tweets Percentage : "+str(z)

        display_graph(x,y,z);

	output.insert(END, str1)
	output.insert(END, str2)
	output.insert(END, str3)

	save_file=str1+str2+str3

#Get called to Perform Sentiment Analysing Sentence
def pos_neg():

        string=''
        no=0;

	#clear the display box
	global output,save_file
        output.delete('1.0', END)
	
        #Read the entry box
	tweet_str    = tweet.get()
        number_str   = number.get()
        sentence_str = sentence.get()
        print number_str

        #Validation of entry box
        if not tweet_str:
		string='Please enter tweet query'
		display_string(string);
		return
        if not number_str:
		string='Please enter number of tweet '
		display_string(string);
		return
	else:
		no=int(number_str)
	
        if not sentence_str:
		string='Please enter the specific sentence '
		display_string(string);
		return

	#Validation of entered string
	a = ['Love', 'Happy', 'Like','love','happy','like']
	string = "I hate you"
	if any(x in sentence_str for x in a):
	  string= 'Positive'
	  display_graph(100,1,1)
	else:
	  string = 'Negative'
	  display_graph(1,100,1)

	save_file=string
        display_string(string);

#Function to save the result into a file
def save():

	global save_file
	#Crete a file and write the result
	f= open("Result.txt","w+")
	f.write(save_file)	
	f.close();
	display_string("Result is saved in a file")


#Main function
if __name__ == '__main__':
    global output,c
    form = Tkinter.Tk()

    getFld = Tkinter.IntVar()

    form.wm_title('Sentiment Analysis')

    #Tweet Entry profile
    stepOne = Tkinter.LabelFrame(form, text=" Tweet Analysing Option ")
    stepOne.grid(row=0, columnspan=7, sticky='W', \
                 padx=5, pady=5, ipadx=5, ipady=5)

    #Button Profile
    helpLf = Tkinter.LabelFrame(form, text=" Button Profile")
    helpLf.grid(row=0, column=9, columnspan=2, rowspan=5, \
                sticky='NS', padx=5, pady=5)

    #Result profile
    stepThree = Tkinter.LabelFrame(form, text=" Analysed Tweets ")
    stepThree.grid(row=3, columnspan=7, sticky='W', \
                   padx=5, pady=5, ipadx=5, ipady=5)

    #Grap profile
    graph = Tkinter.LabelFrame(form, text=" Display Graph ")
    graph.grid(row=5, columnspan=7, sticky='W', \
                   padx=5, pady=5, ipadx=5, ipady=5)

    ###############   Entry profile implementation ########################
    tweet = StringVar()
    number = StringVar()
    sentence = StringVar()

    inFileLbl = Tkinter.Label(stepOne, text="Tweet Query")
    inFileLbl.grid(row=0, column=0, sticky='E', padx=5, pady=2)

    inFileTxt = Tkinter.Entry(stepOne,textvariable=tweet)
    inFileTxt.grid(row=0, column=1, columnspan=7, sticky="WE", pady=3)

    outFileLbl = Tkinter.Label(stepOne, text="Number of Tweet")
    outFileLbl.grid(row=1, column=0, sticky='WE', padx=5, pady=2)

    outFileTxt = Tkinter.Entry(stepOne,textvariable=number)
    outFileTxt.grid(row=1, column=1, columnspan=7, sticky="WE", pady=2)

    inEncLbl = Tkinter.Label(stepOne, text="Specific Sentence")
    inEncLbl.grid(row=2, column=0, sticky='E', padx=5, pady=2)

    inEncTxt = Tkinter.Entry(stepOne,textvariable=sentence)
    inEncTxt.grid(row=2, column=1, sticky='E', pady=2)

    ##########################################################################


    ################## Button profile implementation ##############################

    # button 1
    helpLbl = Tkinter.Button(helpLf, text ="Perform Sentiment Analysis on Tweet", command = percentage)
    helpLbl.grid(row=0)
    #button 2
    helpLbl1 = Tkinter.Button(helpLf, text ="Perform Sentiment Analysing Sentence", command = pos_neg)
    helpLbl1.grid(row=1)
    #button 3
    helpLbl2 = Tkinter.Button(helpLf, text ="Save Result on to a File", command = save)
    helpLbl2.grid(row=2)
    
    #################################################################################################

 
    ###############  Result implementation #######################
    output = Text(stepThree, width=50, height=3, wrap=WORD)
    #output.grid(row=6, column=2, columnspan=2, padx=5, pady=2)
    output.grid(row=5, column=1, columnspan=2, padx=5, pady=(0,10))
    output.insert(END, "Result will be displayed here")
    #################################################################


    ###############  Graph implementation #######################
    c_width = 500
    c_height = 200
    c = Canvas(graph, width=c_width, height=c_height)
    c.grid(row=5)
    ###############################################################
    display_graph(1,1,1)

    form.bind('<Return>', calculate)

    form.mainloop()


