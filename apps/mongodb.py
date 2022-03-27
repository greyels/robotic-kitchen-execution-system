# Add order to the DB
def add_order(order):
    pass

# Update order in the DB
def update_order(order_id, update):
    pass

# Get order from the DB by id
def get_order(order_id):
    return "order"

# Get order from the DB by id
def get_robot_orders(robot_id, status=None):
    return "list_of_order_ids"

# Get current states (idle, busy, failure) of all robots in the system
def get_robot_states():
    return "robot_states"

# Update current state (idle, busy, failure) of the robot
def update_robot_state(robot_id, state):
    return "Robot state has been updated"
