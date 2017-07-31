[![CircleCI](https://circleci.com/gh/geeeh/BucketList.svg?style=svg)](https://circleci.com/gh/geeeh/BucketList)
[![Coverage Status](https://coveralls.io/repos/github/geeeh/BucketList/badge.svg)](https://coveralls.io/github/geeeh/BucketList)
# Bucket_list
# Introduction
A flask based API application that gives users the opportunity to create, update, delete and view bucket list items. bucket list items are wishes users wish to accomplish before
kicking the bucket.
#API ENDPOINTS
1. `POST v1/auth/login`  login a user
2. `POST v1/auth/register` register a user
3. `POST v1/bucketlists`   create a bucketlist
4.  `GET v1/bucketlists`  view created bucketlists
5. `GET  v1/bucketlists/<id>`  view a specific bucketlist
6. `PUT /bucketlists/<id>` update  a specific bucketlist 
7. `DELETE /bucketlists/<id>` delete a specific bucketlist
8. `POST /bucketlists/<id>/items/` create a bucketlist item
9. `PUT /bucketlists/<id>/items/<item_id>`  update  a specific bucketlist item
10. `DELETE /bucketlists/<id>/items/<item_id>` delete a specific bucketlist item

# Requirements
- python 3.4
- virtualenv 
- autoenv


#installation
- Download the project locally by running : `git  clone https://github.com/geeeh/BucketList.git`
- `cd Bucketlist`
- create a virtualenv file. `virtualenv venv`
- create a .env file and add the following lines:
- `source venv/bin/activate`
- `export APP_SETTINGS=development`
- `export SECRET=<your secret key here. It can be any combination of characters>`   
-  save the file
- Install the requirements in the `requirements.txt` file. Run `pip install -r requirements.txt`
-  Run the application. `python run.py`     
#TESTING
To run tests against the project run:
`python manage.py test`

#CONTRIBUTORS
- Godwin Gitonga

