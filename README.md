# robotic-kitchen-execution-system
## Distributed execution system for pizza cooking robots

### General System Design
![General System Design](/img/general_system_design.png)

### Execution System Description:
Main backend (on-premise or serverless/cloud (ex. AWS Lambda)) handles orders from clients, maintain states of all kitchens in the pool and distribute orders to the most suitable location/kitchen.  
Particular kitchen server interacts with the main backend getting/updating orders, configuration and logs, propagating states and monitoring statistics.  
There are the next tools installed on the kitchen server - web server and execution control app, NoSQL database and message broker. 
All applications/tools are deployed in separate docker containers using docker compose.  
Interaction between kitchen robots, cameras and control system is implemented using message queue/broker via configured topics and QoS.  
Also there are heartbeat messages between robots and execution system for notifications about robot failures.
Monitoring system is going to check number of failures for each robot and escalate to the main backend if threshold has been exceeded.
Robot states and orders statuses are maintained by the database (NoSQL).  
Two replicas of execution control system could be installed for redundancy/automatic failover.

### Q&A:
- Q: What elements does your system have? 
- A: The system consists of the next elements:
  - Main backend for execution control over several kitchens and interaction with clients (handle orders)
  - Kitchen execution system (lightweight server) to control over one kitchen location and consists of:
    - Kitchen Control Application (Web Server (Nginx/uWSGI) + Python app (Flask)):
      - interacts with the main backend
      - maintain robots, ovens and orders states
      - responsible for devices synchronization activities
      - could be divided into several applications (web server, synchronisation, state machine control)
    - Database (MongoDB):
      - stores orders, ovens and robots states and other useful meta information
    - Message Queue/Broker (MQTT/RabbitMQ):
      - used as a main tool for interaction between robots, control application and kitchen cameras
- Q: What are the interactions between those elements?
- A: All interactions between robots, ovens, cameras and the execution system are performed via publishing/reading messages to/from the preconfigured message queue/broker.
  System elements send messages to each other based on different events happen in the system, ex.:
  - Getting a new order by the system
  - Order completion by robots or ovens
  - Events from cameras when one of cooking steps is failed
  - Robot failures  
  More details about possible interactions could be found in [apps/kitchen_control_app.py] file.
- Q: What are the differences between cooking 1 pizza, 2 pizzas, and N pizzas?
- A: The main issue with simultaneous cooking of N pizzas is more complex synchronization between robots and ovens. 
  Since more robots are going to be added in the nearest time we should consider now that number of robots before/after ovens is more than number of ovens.
  So, ovens could be a bottleneck of the system, and robots will compete each other for an idle oven.
- Q: What happens if 1 robot fails? What if 2 robots fail?
- A: 
  - In case 1 robot fails -> KCA is notified about the failure via heartbeat mechanism, mark robot in the DB as out of order, check if there are more robots available to complete the order and reassign the order to another available robot sending message to it via message broker.
  - In case 2 robot fails:
    - Both robots before oven -> KCA is notified about failures via heartbeat mechanism, mark robots in the DB as out of order, check if there are more robots available and notify the main backend with "kitchen out of order" error.
    - Both robots after oven -> the same as in case above.
    - One robot before oven and one robot after oven -> KCA is notified about failures via heartbeat mechanism, mark robots in the DB as out of order, check if there are more robots available to complete the order and reassign the order to another available robot sending message to it via message broker.
- Q: Why is it easy to add new robots into your system?
- A: To add new robot to the system you just need to install one of two SW/FW versions (before/after ovens) to the robot system and add a new topic (robot\<number>) to the message broker. New topic number is assigned to the robot on the installation stage.

### Other information
Topics not covered due to strict time limitations:
- Logging
- Monitoring
- CI/CD
- Unit testing
- Metrics
