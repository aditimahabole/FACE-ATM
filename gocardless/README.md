# Steps
+ Link :  https://www.datacamp.com/tutorial/face-detection-python-opencv
+ Step 1 :  Install all dependencies
         
        pip install django
        pip install face-recognition
        pip install opencv-python
        pip install numpy
        pip install pandas

+ Step 2 : make a python file in which we will work on face recognition
+ ##### To run  python file use 
            
        python your_file_name.py
        python face_recognise.py

+ Open CV takes Input from camera
+ Face recognition is a model that recognize faces
+ Taking Input from camera
  
        video_capture = cv2.VideoCapture(0)
        
+ Notice that we have passed the parameter 0 to the VideoCapture() function. This tells OpenCV to use the default camera on our device.
  
### To create and run Django project

+ To initalize the project

        django-admin startproject [project name]
        cd [project name]
        django-admin startproject facefairmain
        cd facefairmain

+ To create an app inside it like Home page , about page whatever

        python manage.py startapp [name of app]
        python manage.py startapp person

+ Before running app you have to make migrations so that it can detect the changes

        python manage.py makemigrations
        python manage.py migrate 

+ To run the app

        python manage.py runserver
  
        