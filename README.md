# Team Generator API

## Overview

The Team Generator API is a FastAPI-based application designed to support the organization of games, players, and scores. It allows you to create players, games, rounds, teams, and record scores for teams within rounds. Additionally, it can compute and rank player scores within a game.

## Getting Started
### Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.9 or higher installed
- Docker and Docker Compose (for running PostgreSQL)

### Installation

1. Clone the repository:

   ```
   git clone https://github.com/Kirankumaraswamy/team_generator.git
   ```
   
2. Navigate to the project directory:
   ```
   cd random-team-generator
   ```
   
3. Build docker containers:
   ```
   docker-compose up --build
   ```
   
### Running the Application
1. Build and start the Docker containers for PostgreSQL and the FastAPI app:
   ```
   docker-compose up
   ```
2. The FastAPI app should be accessible at http://localhost:80.

### Usage
1. Heartbeat
* Endpoint: /heartbeat
* Description: Check the status of the Random Team Generator API.
* HTTP Method: GET

2. Player
Endpoint: /player
Description: Create a new player.
HTTP Method: POST
Request Body: JSON object representing a player.
Example Request:

```
Copy code
{
  "user_name": "john_doe"
}
```

3. Games
* Endpoint: /game
* Description: Create a new game.
* HTTP Method: POST
* Request Body: JSON object representing a game.
* Example Request:

```
{
  "name": "My Game",
  "players": ["player1", "player2", "player3"]
}
```

4. Rounds
* Endpoint: /round/{game_name}
* Description: Create a new round for a game.
* HTTP Method: POST
* Path Parameter: game_name (name of the game)
* Request Body: JSON object representing a round.
* Example Request:

```
{
  "round_name": "Round 1",
  "total_teams": 2,
  "shuffle": true,
  "team_names": ["Team A", "Team B"]
}
```

5. Scores
* Endpoint: /score/{game_name}/{round_name}
* Description: Add scores for teams in a round.
* HTTP Method: POST
* Path Parameters: game_name (name of the game), round_name (name of the round)
* Request Body: JSON object with keys as team names and values as scores.
* Example Request:

```
{
  "scores": [
    {"team_name": "Team A", "score": 10},
    {"team_name": "Team B", "score": 15}
  ]
}
```
