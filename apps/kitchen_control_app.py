from flask import app

from apps import mongodb, rest, mqtt

MQTT_CONFIG_FILE_PATH = "/config_file_path"


# Choose a robot considering current robot states and return its MQTT topic and id
def choose_robot(robot_states):
    return "mqtt_topic"


# Read config file containing KCA and cameras MQTT topics
def read_mqtt_config(config_file_path):
    return "mqtt_config"


# Reassign "in progress" orders to other robots
def reassign_orders(msg, robot_type="before_oven"):
    orders = mongodb.get_robot_orders(msg.robot_id, "in_progress")
    for order in orders:
        mqtt.publish(order, choose_robot(mongodb.get_robot_states(robot_type)))


# New orders handling
@app.route('/new_order/')
def handle_new_order(order):
    mongodb.add_order(order)
    try:
        # wait some time if all robots before ovens are busy and try again (n times)
        mqtt.publish(order, choose_robot(mongodb.get_robot_states(robot_type="before_oven")))
    except Exception as e:
        mongodb.update_order(order.order_id, "failed")
        return f"Order could not be handled! {e}"
    return "Order in progress!"


# Handling messages from robot MQTT topics
def on_robot_message(msg):
    if msg == "order_completed":
        mongodb.update_robot_state(msg.robot_id, "idle")
        if msg.robot_type == "after_oven":
            mongodb.update_order(msg.order_id, "completed")
            rest.send_order_to_be(mongodb.get_order(msg.order_id))
        elif msg.robot_type == "before_oven":
            mqtt.publish(msg.order, mongodb.get_topic_by_oven_id(msg.oven_id))

    elif msg == "order_in_progress":
        mongodb.update_robot_state(msg.robot_id, "busy")
        mongodb.update_order(msg.order_id, {"status": "in_progress", "robot_id": msg.robot_id})


# Handling failures from robot heartbeat MQTT topics
def on_robot_heartbeat_message(msg):
    if msg == "failed":
        mongodb.update_robot_state(msg.robot_id, "out_of_order")
        mongodb.increment_failure_count(msg.robot_id)
        reassign_orders(msg)

    elif msg == "recovered":
        mongodb.update_robot_state(msg.robot_id, "idle")


# Handling messages from camera MQTT topics
def on_cam_message(msg):
    if msg == "any_step_failed":
        mqtt.publish("stop_current_activity", mongodb.get_topic_by_robot_id(msg.robot_id))
        mongodb.increment_failure_count(msg.robot_id)
        reassign_orders(msg)
        mongodb.update_robot_state(msg.robot_id, "idle")


# Handling messages from oven MQTT topics
def on_oven_message(msg):
    if msg == "order_in_progress":
        return mongodb.update_order(msg.order_id, {"status": "in_progress", "oven_id": msg.oven_id})
    robot_type = "after_oven" if msg == "order_completed" else "before_oven"
    mqtt.publish(msg.order, choose_robot(mongodb.get_robot_states(robot_type=robot_type)))


if __name__ == '__main__':
    mqtt.connect()
    mqtt.subscribe(read_mqtt_config(MQTT_CONFIG_FILE_PATH))
    mqtt.on_robot_message = on_robot_message
    mqtt.on_robot_heartbeat_message = on_robot_heartbeat_message
    mqtt.on_cam_message = on_cam_message
    mqtt.on_oven_message = on_oven_message
