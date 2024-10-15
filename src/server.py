from opcua import ua, Server
from opcua.common.callback import CallbackType
import datetime
import random
import time
import threading
import socket
import shutil
import os
try:
    from IPython import embed
except ImportError:
    import code

    def embed():
        vars = globals()
        vars.update(locals())
        shell = code.InteractiveConsole(vars)
        shell.interact()



def create_machine_node(idx, server, machine_name):
    # get Objects node, this is where we should put our custom stuff
    objects = server.get_objects_node()
    machine_folder = objects.add_folder(idx,machine_name)
    machine = machine_folder.add_object(idx, machine_name)
    on_off = machine.add_variable(idx, "On/Off State", False, ua.VariantType.String)
    job_id = machine.add_variable(idx, "Job ID", 0, ua.VariantType.Int32)
    job_name = machine.add_variable(idx, "Job Name", "", ua.VariantType.String)
    spindle_rpm = machine.add_variable(idx, "Spindle RPM", 0.0, ua.VariantType.Float)
    prog_fully_exec = machine.add_variable(idx, "Program Fully Executed", 0.0, ua.VariantType.Float)
    feed_rate = machine.add_variable(idx, "Feed Rate", 0.0, ua.VariantType.Float)
    rapid_inv = machine.add_variable(idx, "Rapid Inverse", 0.0, ua.VariantType.Float)
    tool_number = machine.add_variable(idx, "Tool Number", 0, ua.VariantType.Int32)
    tool_name = machine.add_variable(idx, "Tool Name", "", ua.VariantType.String)
    tool_dimensions = machine.add_variable(idx, "Tool Dimensions", "", ua.VariantType.String)
    prog_status = machine.add_variable(idx, "Program Status", "", ua.VariantType.String)

    for var in machine.get_children():
        var.set_writable()

    return {
        "On/Off State": on_off,
        "Job ID": job_id,
        "Job Name": job_name,
        "Spindle RPM": spindle_rpm,
        "Program Fully Executed": prog_fully_exec,
        "Feed Rate": feed_rate,
        "Rapid Inverse": rapid_inv,
        "Tool Number": tool_number,
        "Tool Name": tool_name,
        "Tool Dimensions": tool_dimensions,
        "Program Status": prog_status
    }


def setup_server_nodes(idx, server):
    server_node = server.nodes.objects.add_object(idx, "ServerDetails")
    server_name = server_node.add_variable(idx, "Server Name", "", ua.VariantType.String)
    server_ip = server_node.add_variable(idx, "Server IP Address", "", ua.VariantType.String)
    server_model = server_node.add_variable(idx, "Server Model", "", ua.VariantType.String)
    server_build = server_node.add_variable(idx, "Server Build", "", ua.VariantType.String)
    manufacturer_name = server_node.add_variable(idx, "Manufacturer Name", "", ua.VariantType.String)

    for var in server_node.get_children():
        var.set_writable()

    return {
        "Server Name": server_name,
        "Server IP Address": server_ip,
        "Server Model": server_model,
        "Server Build": server_build,
        "Manufacturer Name": manufacturer_name
    }


def setup_security(server):
    # Setting up security policies
    server.set_security_policy([
        ua.SecurityPolicyType.NoSecurity,
        ua.SecurityPolicyType.Basic256Sha256_SignAndEncrypt,
        ua.SecurityPolicyType.Basic256Sha256_Sign
    ])

    # Load server certificate and private key
    server.load_certificate("certs/server_cert.pem")
    server.load_private_key("certs/server_private_key.pem")

    trusted_cert_dir = "certs/trusted"
    rejected_cert_dir = "certs/rejected"

    if not os.path.exists(trusted_cert_dir):
        os.makedirs(trusted_cert_dir)
    if not os.path.exists(rejected_cert_dir):
        os.makedirs(rejected_cert_dir)

class SubHandler(object):
    """
    Subscription Handler. To receive events from server for a subscription.
    """

    def datachange_notification(self, node, val, data):
        print(f"Data change event on node: {node}, with value: {val}")

    def event_notification(self, event):
        print(f"Event: {event}")


def update_machine_data(nodes, server_details):
    while True:
        for machine, node_dict in nodes.items():
            node_dict["On/Off State"].set_value(random.choice([0,4]))
            node_dict["Job ID"].set_value(random.randint(1000, 9999))
            node_dict["Job Name"].set_value(f"Job_{random.randint(1, 100)}")
            node_dict["Spindle RPM"].set_value(random.uniform(500, 5000))
            node_dict["Program Fully Executed"].set_value(random.uniform(0, 100))
            node_dict["Feed Rate"].set_value(random.uniform(0, 100))
            node_dict["Rapid Inverse"].set_value(random.uniform(0, 100))
            node_dict["Tool Number"].set_value(random.randint(1, 20))
            node_dict["Tool Name"].set_value(f"Tool_{random.randint(1, 20)}")
            node_dict["Tool Dimensions"].set_value(f"{random.uniform(10, 100):.2f}x{random.uniform(10, 100):.2f}x{random.uniform(10, 100):.2f}")
            node_dict["Program Status"].set_value(random.choice(["Running", "Stopped", "Paused"]))

        server_details["Server Name"].set_value(f"Server_{random.randint(1, 10)}")
        server_details["Server IP Address"].set_value(socket.gethostbyname(socket.gethostname()))
        server_details["Server Model"].set_value(f"Model_{random.randint(1, 100)}")
        server_details["Server Build"].set_value(f"Build_{random.randint(1, 1000)}")
        server_details["Manufacturer Name"].set_value(f"Manufacturer_{random.randint(1, 10)}")

        time.sleep(random.randint(300,1200))  # Update data every 5 seconds


def main():
    # Setup the server
    server = Server()
    server.set_endpoint("opc.tcp://0.0.0.0:4840/freeopcua/server/")
    server.set_server_name("OPC UA Server for Multiple Machines")

    # Setup namespaces
    uri = "http://example.org/machines"
    idx = server.register_namespace(uri)

    # get Objects node, this is where we should put our custom stuff
    objects = server.get_objects_node()

    # Create machine nodes
    machines = ["Machine1"]
    machine_nodes = {}
    for machine_name in machines:
        machine_nodes[machine_name] = create_machine_node(idx, server, machine_name)

    # Create server nodes
    server_nodes = setup_server_nodes(idx, server)

    # Setup security
    setup_security(server)

    # Start the server
    server.start()
    print(f"Server started at {server.endpoint}")

    # Start thread to update machine data
    updater_thread = threading.Thread(target=update_machine_data, args=(machine_nodes, server_nodes))
    updater_thread.daemon = True
    updater_thread.start()


    try:
        while True:
            time.sleep(1)
    finally:
        server.stop()
        print("Server stopped")


if __name__ == "__main__":
    main()
