# mini-exchange
A simple stocks exchange api

## Run
Using existing `docker-compose.yml` file
```
docker-compose up -d
```

## Docs
Run docker-compose and check http://localhost:8000/docs

## Test
```
PYTHONPATH=./src python -m unittest discover -s tests
```

## Technical Details
### Diagram
![image](https://user-images.githubusercontent.com/28277745/209925010-f86e15d9-d560-4202-b7cc-8f621054c4dc.png)

### Components
1. `streamer` emulates stock update events and publishes them on a vernemq topic.
2. `worker` consumes streamer events from vernemq topic using eventsourcing.
3. `web` provides API to handle different user requests and connects to the same event store to sync with the latest updates.
