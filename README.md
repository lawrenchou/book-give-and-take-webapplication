# BOOK GIVING PROJECT

#### Video Demo: https://youtu.be/3nADO4Yjd88

#### Description: 
#### This web application is a platform for people to locally give and recieve books from others. 

##### 1. appication.py
###### - This is where almost my code goes. I'm going to mention only the important function down below. 

** login and logout ** is to let user login by providing username and password via a simple form and remember which user have logged in. 

** logout ** remembering which user have log themselves out of the webpage.

** register ** is the route used to display the register form and check whether user provide enough information or not
It also handles storing user's information into the database.

** giving ** giving is the route that requiring neccesary information from users whenever they giving their books via a form, 
checking if users have provided enough information or not. 
It also handles storing it in the database. 

Notice that ** gallery ** only display the books that posted by users that are in user's location (location that user provided in the register form). 
** gallery ** gallery is the route that's kinda nested with couple other route (request and storing-messages). 
It is used to display the "gallery", let user see what books others (in user's location) have posted, choose their book if they will, 
and sent their request via a form to the book's owner. 
(it haven't sent the request here yet, it storing the request message in a table in the database instead, and it's going to sent it later). 

** notificaiton ** is the route that we connect users to each others. 
It shows if somebody want to recieve your book(s) (in case you've already posted your book via the giving form earlier) 
or if the book's owner have accepted your request for their book(s) (in case you sent your request to them earlier). 
It also handle if you (the book's owner) decide to accept somebody request or not.

** blogs ** this is where all the users can connect to each others freely 
(doesn't depend on whether user have sent their request or did they post their book yet). 
Users can post their thoughts, experiences, questions, wonder here. 

** history ** is where user can see all of their activities on this webpage. 
There are 4 main actions is Donated (means user posted their book on the platform)

** account ** is where user can keep track of what book(s) the user has posted, also his/her information

##### 2. helpers.py

** function login_required(f) ** to make sure only who has login (by providing username and password) have ability to access to all the information

##### 3. project.db

** basic and personal ** are tables used to store users's information.

** books ** is the table used to store all available books. 

** messages ** is the table used to store the messages that would be display in ** notification ** section. 

** history ** is the table used to store all the actions that have been done.

** blogs ** is the table used to store all the things users have shared. 

##### 4. /templates

this folder contains all the HTML templates used in the web application. 

##### 5. /static

this folder contains images and CSS file. 
