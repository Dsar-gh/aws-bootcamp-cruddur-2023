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





