# **PICKem Volleyball Prediction API (Core Version)**

The PICKem Volleyball Prediction API is designed as the core backend for a volleyball prediction game. It enables administrators to set up tournaments, events, and questions and allows users to participate by answering questions to earn points based on the accuracy of their predictions. This API is the foundational version, structured for further expansion in features and functionality.

## **Features**

- **Tournament Management**: Admins can create, manage, and finalize tournaments.
- **Team Management**: Retrieve and assign teams to tournaments.
- **Event and Question Management**: Define prediction questions per event with specific answer types (e.g., YES/NO, single choice, multiple choice).
- **User Predictions**: Users can submit answers to events and have their scores calculated once a tournament is finalized.
- **Score Calculation and Ranking**: After tournament finalization, answers are scored, and user rankings are generated.
- **Authentication**: JWT-based authentication, with support for user roles to differentiate between admin and regular users.

## **Technologies**

- **Framework**: FastAPI for RESTful API design
- **Database**: SQLAlchemy ORM for managing relational data
- **Auth**: JWT-based authentication with OAuth2PasswordBearer flow
- **Validation**: Pydantic schemas and custom validators
- **Logging**: Built-in logging for error tracking and monitoring

## **Endpoints**

### **Authentication**

#### 1. Register a User
   - **Endpoint**: `/auth/register`
   - **Method**: `POST`
   - **Description**: Register a new user.
   - **Example**:
     ```json
     {
       "email": "user@example.com",
       "password": "strongpassword",
       "username": "User123"
     }
     ```

#### 2. Login
   - **Endpoint**: `/auth/jwt/login`
   - **Method**: `POST`
   - **Description**: Login and receive a JWT access token.
   - **Example**:
     ```json
     {
       "username": "user@example.com",
       "password": "strongpassword"
     }
     ```

#### 3. Logout
   - **Endpoint**: `/auth/jwt/logout`
   - **Method**: `POST`
   - **Description**: Invalidate the current session token.

### **Tournament Management**

#### 1. Create Tournament
   - **Endpoint**: `/tournaments/`
   - **Method**: `POST`
   - **Description**: Create a new tournament.
   - **Example**:
     ```json
     {
       "name": "Beach Volleyball Championship",
       "date": "2024-08-10"
     }
     ```

#### 2. Add Teams to Tournament
   - **Endpoint**: `/tournaments/{tournament_id}/teams/add_last`
   - **Method**: `POST`
   - **Description**: Adds a predefined list of teams to the specified tournament.

#### 3. Finalize Tournament
   - **Endpoint**: `/tournaments/{tournament_id}/finalize`
   - **Method**: `POST`
   - **Description**: Scores answers, awards points, and generates user ranking.
   - **Example**:
     ```json
     {
       "tournament_id": "b28d8477-1d62-45ec-b2cd-2c5a7c5b5c1f",
       "ranking": {
         "1": {"user_id": "user1_id", "points": 30},
         "2": {"user_id": "user2_id", "points": 20}
       }
     }
     ```

### **Event Management**

#### 1. Create Event
   - **Endpoint**: `/tournaments/{tournament_id}/events`
   - **Method**: `POST`
   - **Description**: Admins create new events tied to tournaments.
   - **Example**:
     ```json
     {
       "question_type": "single_choice",
       "question_text": "Who will win the match?",
       "points_value": 20
     }
     ```

#### 2. Set Event Solution
   - **Endpoint**: `/events/{event_id}/solution`
   - **Method**: `POST`
   - **Description**: Admin sets the correct answer for an event.
   - **Example**:
     ```json
     {
       "solution": "Team A"
     }
     ```

### **User Answers**

#### 1. Submit Answer
   - **Endpoint**: `/answers/`
   - **Method**: `POST`
   - **Description**: Users submit answers to events.
   - **Example**:
     ```json
     {
       "user_id": "user1_id",
       "event_id": "event1_id",
       "answer": "yes"
     }
     ```

### **Team Management**

#### 1. Get Teams
   - **Endpoint**: `/tournaments/{tournament_id}/teams`
   - **Method**: `GET`
   - **Description**: Retrieve all teams assigned to a specific tournament.

## **Core Version and Future Expansion**

This API represents the foundational logic of the PICKem volleyball prediction game. Future updates are planned to include:

- **Automated Score Calculation**: Enhanced event answer types and complex scoring logic.
- **Improved User Experience**: Detailed stats and user progress tracking.
- **Enhanced Security and Logging**: For real-time monitoring and data security.
- **Additional Question Types**: Increased variety of answer formats, furthering user engagement.

## **Database Models**

### **Structure and Logic**

The following models are used to manage data within the application:

- **User**: Represents application users, containing unique identifiers, usernames, email addresses, password hashes, admin privileges, and total points earned. Each user can have multiple answers related to different events.

- **Tournament**: Contains information about tournaments, including unique identifiers, names, and dates. A tournament can have multiple teams and events associated with it.

- **Team**: Represents teams participating in tournaments, consisting of player names and unique identifiers. Teams can participate in multiple tournaments.

- **Event**: Defines questions related to tournaments, including question types, texts, correct solutions, and point values associated with each event. Each event can have multiple user answers.

- **UserAnswer**: Captures users’ responses to event questions, linking them to user and event identifiers, along with points scored for the response.

### **Protected Endpoints**

Certain endpoints are protected based on user roles:

- **Authenticated User Endpoints**:
  - Submitting answers to events.
  - Retrieving available events and teams.

- **Authenticated Superuser (Admin) Endpoints**:
  - Creating tournaments and events.
  - Setting solutions for events.
  - Finalizing tournaments and calculating rankings.

This core API offers scalable RESTful endpoints, serving as a robust base to introduce advanced features for a complete and interactive user experience.
```
