# Week 3 — Decentralized Authentication

## Required Homework

### Creating Amazon Cognito User Pool 

Using Amazon Cognito Console, a user pool is created.

![User pool](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/week3/user-pool-created.PNG)

### Install and Configure Amplify Client-Side Library for Amazon Cognito

- The following command will install `aws-amplify` package and save it in my `package.json`. This way, it'll become one of my project dependencies and will be automatically installed the next time I run `npm` or compose up my `docker-compose.yml`. 

```sh
npm i aws-amplify --save
```

- I added the following Environment Variables to the `frontend-react-js` service in the [`docker-compose.yml`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/docker-compose.yml) file.

```yml
    REACT_APP_AWS_PROJECT_REGION: "${AWS_DEFAULT_REGION}"
    REACT_APP_AWS_COGNITO_REGION: "${AWS_DEFAULT_REGION}"
    REACT_APP_AWS_USER_POOLS_ID: "us-east-1_qLUhJF0h9"
    REACT_APP_CLIENT_ID: "3iipit8oj48lsujj3u0guiqune"
```

- To link my Cognito user pool to my Cruddur, the following lines of code are  added in the [`App.js`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/frontend-react-js/src/App.js) file

```js
import { Amplify } from 'aws-amplify';

Amplify.configure({
  "AWS_PROJECT_REGION": process.env.REACT_APP_AWS_PROJECT_REGION,
  "aws_cognito_region": process.env.REACT_APP_AWS_COGNITO_REGION,
  "aws_user_pools_id": process.env.REACT_APP_AWS_USER_POOLS_ID,
  "aws_user_pools_web_client_id": process.env.REACT_APP_CLIENT_ID,
  "oauth": {}, 
  Auth: {
    // We are not using an Identity Pool
    // identityPoolId: process.env.REACT_APP_IDENTITY_POOL_ID, // REQUIRED - Amazon Cognito Identity Pool ID
    region: process.env.REACT_APP_AWS_PROJECT_REGION,           // REQUIRED - Amazon Cognito Region
    userPoolId: process.env.REACT_APP_AWS_USER_POOLS_ID,         // OPTIONAL - Amazon Cognito User Pool ID
    userPoolWebClientId: process.env.REACT_APP_CLIENT_ID,   // OPTIONAL - Amazon Cognito Web Client ID (26-char alphanumeric string)
  }
});
```
### Conditionally show components based on logged in or logged out

The pages `HomeFeedPage.js`, `DesktopNavigation.js`, `ProfileInfo.js`, and  `DesktopSidebar.js` are modified based on the user's state.

#### [`HomeFeedPage.js`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/frontend-react-js/src/pages/HomeFeedPage.js)

I Modified the code of `checkAuth` method to authenticate Cognito user.

```js
import { Auth } from 'aws-amplify';

// to set a state. But I don't need to add it. It's already existed.
const [user, setUser] = React.useState(null);

const checkAuth = async () => {
  Auth.currentAuthenticatedUser({
    // Optional, By default is false. 
    // If set to true, this call will send a 
    // request to Cognito to get the latest user data
    bypassCache: false 
  })
  .then((user) => {
    console.log('user',user);
    return Auth.currentAuthenticatedUser()
  }).then((cognito_user) => {
      setUser({
        display_name: cognito_user.attributes.name,
        handle: cognito_user.attributes.preferred_username
      })
  })
  .catch((err) => console.log(err));
};

```

#### [`DesktopNavigation.js`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/frontend-react-js/src/components/DesktopNavigation.js)

I didn't change anything. It was already done.

#### [`ProfileInfo.js`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/frontend-react-js/src/components/ProfileInfo.js)

In the `ProfileInfo()` function I modified the code related to the variable `signOut` as follows.

```js
import { Auth } from 'aws-amplify';

const signOut = async () => {
  try {
      await Auth.signOut({ global: true });
      window.location.href = "/"
  } catch (error) {
      console.log('error signing out: ', error);
  }
}
```

#### [`DesktopSidebar.js`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/frontend-react-js/src/components/DesktopSidebar.js)

I rearranged the `if` statements, to make the code clearer.

```js
  let trending;
  let suggested;
  let join;
  if (props.user) {
    trending = <TrendingSection trendings={trendings} />
    suggested = <SuggestedUsersSection users={users} />
  } else {
    join = <JoinSection />
  }
```

### Implement API Calls to Amazon Cognito for Custom Login, Signup, Recovery and Forgot Password Page

#### Sign-in Page [`SigninPage.js`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/frontend-react-js/src/pages/SigninPage.js)

In the `SigninPage()` function I modified the code related to the variable `onsubmit` to try signing in and trigger an error if the user name or password incorrect are. Then confirmed if these changes are working.

```js

import { Auth } from 'aws-amplify';

const [errors, setErrors] = React.useState('');
  
  const onsubmit = async (event) => {
    setErrors('')
    event.preventDefault();
    Auth.signIn(email, password)
    .then(user => {
      console.log('user',user)
      localStorage.setItem("access_token", user.signInUserSession.accessToken.jwtToken)
      window.location.href = "/"
    })
    .catch(error => { 
      if (error.code == 'UserNotConfirmedException') {
        window.location.href = "/confirm"
      }
      setErrors(error.message)
    });
    return false
  }
  ```
  ![sign-in](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/week3/sgin-in.PNG)

To try my code one more time, I created a user in Amazon Cognito user pool and an error was triggered when I tried to sign in. It's because the user is created manually from AWS Cognito Console and  wasn't verified. To solve this issue, I run the following command.

```sh
aws cognito-idp admin-set-user-password --user-pool-id us-east-1_qLUhJF0h9 --username Dsar --password Test1234?  --permanent
```
![sign in worked](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/journal/assets/week3/prefered-name-added.PNG)


#### Sign up Page [`SignupPage.js`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/frontend-react-js/src/pages/SignupPage.js)

We shouldn't be creating users by ourselves manually, therefore I  modified the `SignupPage.js` page so that users can sign up themselves.
In the `SignupPage()` function, I modified the code related to the variable `onsubmit` to try signing up as follows: 

```js
import { Auth } from 'aws-amplify';

const [errors, setErrors] = React.useState('');

const onsubmit = async (event) => {
    event.preventDefault();
    setErrors('')
    console.log('username',username)
    console.log('email',email)
    console.log('name',name)
    try {
        const { user } = await Auth.signUp({
        username: email,
        password: password,
        attributes: {
            name: name,
            email: email,
            preferred_username: username,
        },
        autoSignIn: { // optional - enables auto sign in after user is confirmed
            enabled: true,
        }
        });
        console.log(user);
        window.location.href = `/confirm?email=${email}`
    } catch (error) {
        console.log(error);
        setErrors(error.message)
    }
    return false
}
```

#### Confirmation Page [`ConfirmationPage.js`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/frontend-react-js/src/pages/ConfirmationPage.js)

In the `ConfirmationPage()` function, I changed the code related to the variables `resend_code` and `onsubmit` to try signing up as follows: 

```js
import { Auth } from 'aws-amplify';

const resend_code = async (event) => {
    setErrors('')
    try {
      await Auth.resendSignUp(email);
      console.log('code resent successfully');
      setCodeSent(true)
    } catch (err) {
      // does not return a code
      // does cognito always return english
      // for this to be an okay match?
      console.log(err)
      if (err.message == 'Username cannot be empty'){
        setErrors("You need to provide an email in order to send Resend Activiation Code")   
      } else if (err.message == "Username/client id combination not found."){
        setErrors("Email is invalid or cannot be found.")   
      }
    }
}

const onsubmit = async (event) => {
    event.preventDefault();
    setErrors('')
    try {
      await Auth.confirmSignUp(email, code);
      window.location.href = "/"
      console.log("hey, your account is confirmed now go to the signin page and log in to see your home feedback.")
    } catch (error) {
      setErrors(error.message)
    }
    return false
  }
```

#### Recover Page [`RecoverPage.js`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/frontend-react-js/src/pages/RecoverPage.js)

`Recover Page` as well, is modified as follows. In the `RecoverPage()` function, I changed the code related to both variables `onsubmit_send_code` and `onsubmit_confirm_code` to be able to recover the password.

```js
import { Auth } from 'aws-amplify';

const onsubmit_send_code = async (event) => {
  event.preventDefault();
  setErrors('')
  Auth.forgotPassword(username)
  .then((data) => setFormState('confirm_code') )
  .catch((err) => setErrors(err.message) );
  return false
}

const onsubmit_confirm_code = async (event) => {
  event.preventDefault();
  setErrors('')
  if (password == passwordAgain){
    Auth.forgotPasswordSubmit(username, code, password)
    .then((data) => setFormState('success'))
    .catch((err) => setErrors(err.message) );
  } else {
    setErrors('Passwords do not match')
  }
  return false
}
```

### Authenticating Server Side

- I added in the [`HomeFeedPage.js`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/frontend-react-js/src/pages/HomeFeedPage.js) a header to pass along the access token

```js
  headers: {
    Authorization: `Bearer ${localStorage.getItem("access_token")}`
  },
```

- I replace the code below in [`app.py`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/app.py) to allow the `Authorization` header and expose it

```py
cors = CORS(
  app, 
  resources={r"/api/*": {"origins": origins}},
  headers=['Content-Type', 'Authorization'], 
  expose_headers='Authorization',
  methods="OPTIONS,GET,HEAD,POST"
)
```

- I added the following package in [`requirements.txt`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/backend-flask/requirements.txt) and installed it using `pip install -r requirements.txt`.

```txt
Flask-AWSCognito
```
- I added the following Environment Variables to the `backend-flask` service in the  [`docker-compose.yml`](https://github.com/Dsar-gh/aws-bootcamp-cruddur-2023/blob/main/docker-compose.yml) file.

```yml
    AWS_COGNITO_USER_POOL_ID: "us-east-1_0Q5vXK9LL"
    AWS_COGNITO_USER_POOL_CLIENT_ID: "7fj55tsbg8upiqmjmnok1pi3ku"  
```
- I created a new file [`/lib/cognito_jwt_token.py`]() under `backend-flask`

```py
import time
import requests
from jose import jwk, jwt
from jose.exceptions import JOSEError
from jose.utils import base64url_decode

class FlaskAWSCognitoError(Exception):
  pass

class TokenVerifyError(Exception):
  pass

def extract_access_token(request_headers):
    access_token = None
    auth_header = request_headers.get("Authorization")
    if auth_header and " " in auth_header:
        _, access_token = auth_header.split()
    return access_token

class CognitoJwtToken:
    def __init__(self, user_pool_id, user_pool_client_id, region, request_client=None):
        self.region = region
        if not self.region:
            raise FlaskAWSCognitoError("No AWS region provided")
        self.user_pool_id = user_pool_id
        self.user_pool_client_id = user_pool_client_id
        self.claims = None
        if not request_client:
            self.request_client = requests.get
        else:
            self.request_client = request_client
        self._load_jwk_keys()


    def _load_jwk_keys(self):
        keys_url = f"https://cognito-idp.{self.region}.amazonaws.com/{self.user_pool_id}/.well-known/jwks.json"
        try:
            response = self.request_client(keys_url)
            self.jwk_keys = response.json()["keys"]
        except requests.exceptions.RequestException as e:
            raise FlaskAWSCognitoError(str(e)) from e

    @staticmethod
    def _extract_headers(token):
        try:
            headers = jwt.get_unverified_headers(token)
            return headers
        except JOSEError as e:
            raise TokenVerifyError(str(e)) from e

    def _find_pkey(self, headers):
        kid = headers["kid"]
        # search for the kid in the downloaded public keys
        key_index = -1
        for i in range(len(self.jwk_keys)):
            if kid == self.jwk_keys[i]["kid"]:
                key_index = i
                break
        if key_index == -1:
            raise TokenVerifyError("Public key not found in jwks.json")
        return self.jwk_keys[key_index]

    @staticmethod
    def _verify_signature(token, pkey_data):
        try:
            # construct the public key
            public_key = jwk.construct(pkey_data)
        except JOSEError as e:
            raise TokenVerifyError(str(e)) from e
        # get the last two sections of the token,
        # message and signature (encoded in base64)
        message, encoded_signature = str(token).rsplit(".", 1)
        # decode the signature
        decoded_signature = base64url_decode(encoded_signature.encode("utf-8"))
        # verify the signature
        if not public_key.verify(message.encode("utf8"), decoded_signature):
            raise TokenVerifyError("Signature verification failed")

    @staticmethod
    def _extract_claims(token):
        try:
            claims = jwt.get_unverified_claims(token)
            return claims
        except JOSEError as e:
            raise TokenVerifyError(str(e)) from e

    @staticmethod
    def _check_expiration(claims, current_time):
        if not current_time:
            current_time = time.time()
        if current_time > claims["exp"]:
            raise TokenVerifyError("Token is expired")  # probably another exception

    def _check_audience(self, claims):
        # and the Audience  (use claims['client_id'] if verifying an access token)
        audience = claims["aud"] if "aud" in claims else claims["client_id"]
        if audience != self.user_pool_client_id:
            raise TokenVerifyError("Token was not issued for this audience")

    def verify(self, token, current_time=None):
        """ https://github.com/awslabs/aws-support-tools/blob/master/Cognito/decode-verify-jwt/decode-verify-jwt.py """
        if not token:
            raise TokenVerifyError("No token provided")

        headers = self._extract_headers(token)
        pkey_data = self._find_pkey(headers)
        self._verify_signature(token, pkey_data)

        claims = self._extract_claims(token)
        self._check_expiration(claims, current_time)
        self._check_audience(claims)

        self.claims = claims 
        return claims

```
- *********???????Used some code from this library `Flask-AWSCognito` 

```py
from lib.cognito_jwt_token import CognitoJwtToken, extract_access_token, TokenVerifyError
```

```py
app = Flask(__name__)

# Cognito backend side
cognito_jwt_token = CognitoJwtToken(
  user_pool_id=os.getenv("AWS_COGNITO_USER_POOL_ID"), 
  user_pool_client_id=os.getenv("AWS_COGNITO_USER_POOL_CLIENT_ID"),
  region=os.getenv("AWS_DEFAULT_REGION")
)
```

```py
@app.route("/api/activities/home", methods=['GET'])
#@xray_recorder.capture('activities_home')
def data_home():
  #data = HomeActivities.run(Logger=LOGGER)
  access_token = extract_access_token(request.headers)
  try:
    claims = cognito_jwt_token.verify(access_token)
    # authenicatied request
    app.logger.debug("authenicated")
    app.logger.debug(claims)
    app.logger.debug(claims['username'])
    data = HomeActivities.run(cognito_user_id=claims['username'])
  except TokenVerifyError as e:
    # unauthenicatied request
    app.logger.debug(e)
    app.logger.debug("unauthenicated")
    data = HomeActivities.run()
  return data, 200

```

- Added this code to `home_activities.py`

```py


# pass cognito_user_id to see if the user is auth.ed or not
def run(cognito_user_id=None):
# ...
# ...
      if cognito_user_id != None:
        extra_crud = {
          'uuid': '248959df-3079-4947-b847-9e0892d1bab4',
          'handle':  'Lore',
          'message': 'My dear brother, it the humans that are the problem',
          'created_at': (now - timedelta(hours=1)).isoformat(),
          'expires_at': (now + timedelta(hours=12)).isoformat(),
          'likes': 1042,
          'replies': []
        }
        results.insert(0,extra_crud)
```

- To remove the access token after signing out, I added these lines of code to `ProfileInfo.js`

```js
    try {
        await Auth.signOut({ global: true });
        window.location.href = "/"
        localStorage.removeItem("access_token")
    }
```




