# Online-class-bot

This is a bot that I've made using python and selenium to join my online classes on Microsoft Teams Platform. Just add your credential in login_cred.py and you are good to go.

### Working:
It will open the teams website on new chrome window and sign you in.
Now it will go to the calender's tab and capture all the classes scheduled in your calender.
Now we will create thread where it will wait for the class to start and then it will join the class through your calender. 
And same thread will wait for the class ending time and leave the class on the time.
Upon the completion of the classes it will automatically end it self.


### Things you have to take care of:
On teams side:
* Make sure you have calender icon on your left.
* You have arranged your classes in your teams (In the case of overlapping classes, only the one that begins earlier will be joined.)

On Code side: 
* Install selenium driver 
* Install selenium package and win10toast package for python.
* Whenever chrome get's update download the same version chrome driver and put it in the same folder as a chrome.
* In run_script.bat file change the path of python and script file according to your pc.
