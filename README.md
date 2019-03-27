README

Project Title:
	Implementation of APIs in Python 3 using Flask and SQLite. 
	All the four microservices should be hosted as four separate applications.
	Articles microservice with below operations: The following operations should be exposed:
	Post a new article, Retrieve an individual article, Edit an individual article. 
	The last-modified timestamp should be updated, Delete a specific existing article,
	Retrieve the entire contents (including article text) for the n most recent articles
	including title, author, date, and URL.
	Tags microservice with below operations: Add tags for a new URL, Add tags to an existing URL,
	Remove one or more tags from an individual URL, Retrieve the tags for an individual URL,
	Retrieve a list of URLs with a given tag.
	Comments microservice with below operations: Post a new comment on an article,
	Delete an individual comment, Retrieve the number of comments on a given article,
	Retrieve the n most recent comments on a URL.
	Users microservice with below operations: Create new user, Delete existing user, 
	Change existing user’s password.

	All data, including error messages, should be in JSON format with the Content-Type
	header field set to application/json, HTTP status codes, authentication.
	
Getting Started:
		Prerequisites:
		1. Python3 by command "sudo apt-get install python3.6"
		2. Flask by command "pip install Flask"
		3. Pytest by command "pip install -U pytest"
		4. Tavern by command "pip install tavern[pytest]"
		5. Foreman by command "sudo gen install foreman"

Installing:
		1. Python3.6 was installed using the command "sudo apt-get install python3.6"
		2. Make python3 as the default verion using below commands:
			sudo update-alternatives --install /usr/bin/python python /usr/bin/python2.7 1
			sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.6 2
			sudo update-alternatives --config python
		3. Flask was installed using the command "pip install Flask"
		4. Pytest was installed using the command "pip install -U pytest"
		5. Tavern was installed using the command "pip install tavern[pytest]"
		6. Foreman was installed using the command command "sudo gen install foreman"

		

		
	Example of a test case:
	In the below example we will be validating the response that we get from the API against the 
	request that we send. We have to ensure the order of executing the test cases and proper data 
	should be provided in the request. 
	
	---
		test_name: List all articles for a new tag
		stages:
		- name: List all articles for a new tag
			request:
				url: http://localhost:5300/searchArticle/tag1
				method: GET
				headers:
					content-type: application/json
				response:
					status_code: 200
					body:
						[
							{
								"title": "project" 
							},
							{
								"title": "project new" 
							},
						]
           
	---

Deployment:
	The above written steps in Installation and running the test needs to be followed in order.
		
Authors:
	Ratik Shetty	 	
	Rohit Saha		
	Parijat Das		
