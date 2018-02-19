#!/usr/bin/env python
# coding: utf-8

import argparse
import logging
import subprocess

import yaml

import d3_network.network_controller as network_ctl
import d3_network.network_scanner as network_scn
import robot_software.robot_controller as robot_ctl


def main():
    parser = argparse.ArgumentParser(description='Script used to start both station or robot.')
    parser.add_argument('sys', choices=['robot', 'station'], help='The system to start, `robot` or `station`.')

    args = parser.parse_args()

    logger = logging.getLogger()
    log_formatter = logging.Formatter("%(asctime)s [%(threadName)-12.12s] [%(levelname)-5.5s]  %(message)s")

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(log_formatter)
    logger.addHandler(console_handler)

    logger.setLevel(logging.INFO)

    try:
        with open("config.yml", 'r') as stream:
            try:
                config = yaml.load(stream)
            except yaml.YAMLError as exc:
                logger.error("Could not load config file. Exiting.")
                logger.exception(exc)
                return
    except FileNotFoundError:
        with open("../config.yml", 'r') as stream:
            try:
                config = yaml.load(stream)
            except yaml.YAMLError as exc:
                logger.error("Could not load config file. Exiting.")
                logger.exception(exc)
                return

    logger.info("Config file loaded.\n%s", config)

    if vars(args)['sys'] == 'robot':
        start_robot(config['robot'], logger.getChild('robot'))
    elif vars(args)['sys'] == 'station':
        start_station(config['station'], logger.getChild('station'))
    else:
        parser.print_help()


def start_robot(config, logger):
    if config['network']['scan_for_ip']:
        scanner = network_scn.NmapNetworkScanner()
    else:
        scanner = network_scn.StaticNetworkScanner(config['network']['host_ip'])
    network = network_ctl.NetworkController(config['network']['port'], logger.getChild("network_controller"))

    robot_ctl.RobotController(scanner, network).start()


def start_station(config, logger):
    if not config['simulated_robot']:
        subprocess.call("./scripts/boot_robot.bash", shell=True)

    logger.info("Waiting for robot to connect.")

    network_ctl.NetworkController(config['network']['port'], logger.getChild("network_controller")).host_network()


if __name__ == "__main__":
    main()
