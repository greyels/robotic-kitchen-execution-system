# Add order to the DB
def add_order(order):
    pass


# Update order in the DB
def update_order(order_id, updates):
    pass


# Get order from the DB by id
def get_order(order_id):
    return "order"


# Get order from the DB by id
def get_robot_orders(robot_id, status):
    return "list_of_order_ids"


# Get current states (idle, busy, failure) of all robots in the system
def get_robot_states(robot_type):
    return "robot_states"


# Update current state (idle, busy, failure) of the robot
def update_robot_state(robot_id, state):
    return "Robot state has been updated"


# Get MQTT topic by robot id
def get_topic_by_robot_id(robot_id):
    return "mqtt_topic"


# Increment failure counter
def increment_failure_count(robot_id):
    return "counter_incremented"


# Get MQTT topic by oven id
def get_topic_by_oven_id(oven_id):
    return "mqtt_topic"
