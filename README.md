# hackchallenge-backend
Backend for AppDev Hack Challenge Fall '23 (Backend) 

App Name: CUSunsets

App Tagline: See pictures and rating of sunsets wherever you are!

Link(s) to any other public GitHub repo(s) of your app. If you have one repo for iOS / Android and one for Backend, please link to your backend repo in your iOS / Android README, and your iOS / Android repo in your backend README.

Some screenshots of your app (highlight important features): On Frontend GitHub

A short description of your app (its purpose and features):
Allows users to post pictures of the sunset along with a description, location, and rating out of 10. Users can then see the posts for a particular day and overall rating for any day.

A list of how your app addresses each of the requirements:
Backend:

1 GET route to get posts by day_id

1 GET route to get posts by id

1 POST route to create a post

1 DELETE route to delete a post

There are two tables in the database: a Day table of all the days and a Post table of all the posts. The relationship between them is one to many, with one day relating to many posts.

Has been deployed on Google Cloud at link: http://34.86.124.11/

Anything else you want your grader to know
Note: The link, screenshots, and description will be used for the Hack Challenge website where we will showcase everyone’s final projects

Backend was submitted separately from frontend and design as these two parts of the team got an extension. They will link their work to our later. 
