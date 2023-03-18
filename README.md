# Backend Coding Challenge

All the features have been implemented including a django test for each api endpoint

API documentation implemented with Swagger

## Authentication is employed using simple JWT Bearer Token
### To Authenticate
* Access the /signup/ endpoint and provide sign up info: username, email, password
* Access the /authenticate/ endpoint providing email and password to Generate an access token. copy your access token
* All Requests to Authenticated endpoints should be sent with the following key, value in the request headers
{
    "Authorization": "Bearer [access_token]"
}

### Note the [] surrounding access_token should be omitted.


API end Points were tested using Insomnia. 

Unit Testing also implemented.

App dockerized. 


 

