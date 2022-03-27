from flask import app

from apps import mongodb, rest, mqtt

MQTT_CONFIG_FILE_PATH = "/config_file_path"


# Choose a robot considering current robot states and return its MQTT topic and id
def choose_robot(robot_states):
    return "mqtt_topic", "robot_id"


# Read config file containing KCA and cameras MQTT topics
def read_mqtt_config(config_file_path):
    return "mqtt_config"


# New orders handling
@app.route('/new_order/')
def handle_new_order(order):
    mongodb.add_order(order)
    try:
        # wait some time if all robots before ovens are busy and try again (n times)
        mqtt_topic, robot_id = choose_robot(mongodb.get_robot_states())
        mqtt.publish(order, mqtt_topic)
    except Exception as e:
        mongodb.update_order(order, "failed")
        return f"Order could not be handled! {e}"
    mongodb.update_robot_state(robot_id, "busy")
    mongodb.update_order(order, "in_progress")
    return "Order is in progress!"


# Handling messages from robot MQTT topics
def on_robot_message(msg):
    if msg == "order_completed!":
        mongodb.update_order(msg.order_id, "completed")
        rest.send_order_to_be(mongodb.get_order(msg.order_id))


# Handling failures from robot heartbeat MQTT topics
def on_robot_heartbeat_failure(msg):
    mongodb.update_robot_state(msg.robot_id, "out_of_order")
    orders = mongodb.get_robot_orders(msg.robot_id, "in_progress")
    for order in orders:
        mqtt_topic, robot_id = choose_robot(mongodb.get_robot_states())
        mongodb.update_robot_state(robot_id, "busy")
        mqtt.publish(order, mqtt_topic)

# Handling messages from camera MQTT topics
def on_cam_message():
    pass

if __name__ == '__main__':
    mqtt.connect()
    mqtt.subscribe(read_mqtt_config(MQTT_CONFIG_FILE_PATH))
    mqtt.on_robot_message = on_robot_message()
    mqtt.on_cam_message = on_cam_message()
