#Import all the necessary libraries
from tkinter import *

#Define the tkinter instance
win= Toplevel()
win.title("Rounded Button")

#Define the size of the tkinter frame
win.geometry("700x300")

#Define the working of the button

def my_command():
   text.config(text= "You have clicked Me...")

#Import the image using PhotoImage function
click_btn= PhotoImage(file='../IMG/loadButton.png')

#Let us create a label for button event
# img_label= Label(image=click_btn)

#Let us create a dummy button and pass the image
canvasmy = Canvas(win, height="200", width="200")
button= Button(canvasmy, image=click_btn,command= my_command,borderwidth=0)
button.place(x=50,y=50)
button= Button(canvasmy, image=click_btn,command= my_command,borderwidth=0)
button.place(x=50,y=90)
canvasmy.pack()

win.mainloop()