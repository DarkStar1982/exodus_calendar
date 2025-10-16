#!/usr/bin/env python3
import argparse
import hashlib
import threading
import time
import os
import sys
from concurrent import futures
from math import modf

sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))
sys.path.append(os.path.join(os.path.dirname(__file__), '.', 'protos'))

from exodus_calendar.utils import mars_datetime_now
import grpc
import mntp_pb2
import mntp_pb2_grpc


DEFAULT_PORT = 1955
DEFAULT_SERVER = "localhost"
MAX_SKEW = 1 
MAX_AGE = 88775.244
SYS_PRECISION = 9

def check_packet_integrity(packet):
	decoded = {
		"header":packet.Header,
		"root_delay": packet.RootDelay,
		"dispersion": packet.Dispersion,
		"reference_id": packet.ReferenceID,
		"reference_timestamp": packet.ReferenceTimestamp,
		"origin_timestamp": packet.OriginTimestamp,
		"receive_timestamp": packet.ReceiveTimestamp,
		"transmit_timestamp": packet.TransmitTimestamp
	}

	# encode packet contents
	packet_as_str = ''
	for value in decoded.values():
		packet_as_str = packet_as_str + str(value)
	
	# add hashsum
	str_bytes= packet_as_str.encode('utf-8')
	sha256hex = hashlib.sha256(str_bytes).hexdigest()
	return (sha256hex == packet.SHA2Checksum)


class MNTP_Client():
	version = 1
	mode = 0
	poll = 1
	precision = 1

	def __init__(self, p_server, p_port):
		self.port = p_port
		self.server = p_server

	def form_client_packet(self):
		packet = {
			"header": self.version<<24 | self.mode<<16 | self.poll<<8 | self.precision,
			"root_delay": 0,
			"dispersion": 0,
			'reference_id': 0,
			'reference_timestamp':0,
			'origin_timestamp':0,
			'receive_timestamp':0,
			'transmit_timestamp':mars_datetime_now(format="ms"),
		}
		packet_as_str = ''
		for value in packet.values():
			packet_as_str = packet_as_str + str(value)
		
		# update hashsum field
		str_bytes= packet_as_str.encode('utf-8')
		sha256hex = hashlib.sha256(str_bytes).hexdigest()
		packet['sha2checksum'] = sha256hex
		return packet

	def process_timing_data(self, packet_data):
		T4 = mars_datetime_now(format="ms")
		T3 = packet_data.TransmitTimestamp
		T2 = packet_data.ReceiveTimestamp
		T1 = packet_data.OriginTimestamp
		delay = (T4 - T1) - (T3 - T2)
		offset = ((T2 - T1) + (T3 - T4))/2
		dispersion = (1 >> SYS_PRECISION) + MAX_SKEW/MAX_AGE*(T1-T3)

		print(f"T1:{T1}, T2:{T2}, T3:{T3}, T4:{T4}")
		print(f"d={delay}")
		print(f"t={offset}")
		print(f"e={dispersion}")

	def mntp_call(self):
		while(True):
			with grpc.insecure_channel(f"{self.server}:{self.port}") as channel:
				stub = mntp_pb2_grpc.MNTP_ServiceStub(channel)
				client_packet = self.form_client_packet()
				response = stub.ProcessTimeSyncRequest(mntp_pb2.MNTP_Packet(
					Header = client_packet["header"], 
					RootDelay = client_packet["root_delay"], 
					Dispersion = client_packet["dispersion"], 
					ReferenceID = client_packet["reference_id"],
					ReferenceTimestamp = client_packet["reference_timestamp"], 
					OriginTimestamp = client_packet["origin_timestamp"], 
					ReceiveTimestamp = client_packet["receive_timestamp"],
					TransmitTimestamp = client_packet["transmit_timestamp"], 
					SHA2Checksum = client_packet['sha2checksum']
				))
				if check_packet_integrity(response):
					self.process_timing_data(response)
				else:
					raise Exception("Server packet checksum failed!")
			time.sleep(self.poll)

	def client_run(self):
		client_thread = threading.Thread(target=self.mntp_call)
		client_thread.start()
		client_thread.join()


class MNTP_Server(mntp_pb2_grpc.MNTP_Service):
	version_info = 1
	mode = 1
	poll = 1
	precision = 1
	ref_timestamp = mars_datetime_now(format="ms")

	def decode_client_packet(self, packet):
		if check_packet_integrity(packet):
			client_version = packet.Header>>24 & 0x000000FF
			mode = packet.Header>>16 & 0x000000FF
			poll = packet.Header>>8 & 0x000000FF
			precision = packet.Header & 0x000000FF
			sha2hash = packet.SHA2Checksum
			print(f"Client packet header: {client_version} | {mode} | {poll} | {precision}")
			print(f"Client packet checksum: {sha2hash}")
			return (packet.TransmitTimestamp, packet.Header)
		else:
			raise Exception("Packet checksum failed")

	def form_server_packet(self, origin_ts, receive_ts):
		packet = {
			"header": self.version_info<<24 | self.mode<<16 | self.poll<<8 | self.precision,
			"root_delay": 0,
			"dispersion": 0,
			"reference_id":1,
			"reference_timestamp": self.ref_timestamp,
			"origin_timestamp": origin_ts,
			"receive_timestamp": receive_ts,
			"transmit_timestamp":mars_datetime_now(format="ms"),
		}

		# encode packet contents
		packet_as_str = ''
		for value in packet.values():
			packet_as_str = packet_as_str + str(value)
		# add hashsum		
		str_bytes= packet_as_str.encode('utf-8')
		sha256hex = hashlib.sha256(str_bytes).hexdigest()
		packet['sha2checksum'] = sha256hex
		return packet

	def ProcessTimeSyncRequest(self, request, context):
		receive_ts = mars_datetime_now(format="ms")
		origin_ts, header = self.decode_client_packet(request)
		packet = self.form_server_packet(origin_ts, receive_ts)

		print("Client packet received: " + str(header))
		return mntp_pb2.MNTP_Packet(
			Header = packet["header"], 
			RootDelay = packet["root_delay"], 
			Dispersion = packet["dispersion"], 
			ReferenceID = packet["reference_id"],
            ReferenceTimestamp = packet["reference_timestamp"], 
            OriginTimestamp = packet["origin_timestamp"], 
            ReceiveTimestamp = packet["receive_timestamp"],
            TransmitTimestamp = packet["transmit_timestamp"],
            SHA2Checksum = packet['sha2checksum']
        )


def serve(p_port):
	port = f"{p_port}"
	server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
	mntp_pb2_grpc.add_MNTP_ServiceServicer_to_server(MNTP_Server(), server)
	server.add_insecure_port("[::]:" + port)
	server.start()
	print("Starting Martian NTP server listening on " + port)
	server.wait_for_termination()


def main():
	parser = argparse.ArgumentParser(
		prog='mntp.py',
		description='A demo of Martian flavor of NTP protocol, using gRPC as transport layer'
	)

	parser.add_argument(
		'-s',
		"--server", 
		action='store_true',
		help='Runs MNTP utility in server mode'
	)
	parser.add_argument(
		'-c',
		"--client", 
		action='store_true',
		help='Runs MNTP utility in client mode'
	)

	parser.add_argument(
		"-p",
		"--port",
		type=int,
		dest='PORT',
		help='Set MNTP port in both server and client mode'
	)

	parser.add_argument(
		"-m",
		"--mntp",
		type=str,
		dest='SERVER',
		help='Set remote server address for client, localhost by default'
	)


	args = parser.parse_args()

	if args.PORT:
		port = args.PORT
	else:
		port = DEFAULT_PORT

	if args.server:
		serve(port)
	
	if args.client:
		if args.SERVER:
			server = args.SERVER
		else:
			server = DEFAULT_SERVER
		client = MNTP_Client(server, port)
		client.client_run()
		return

	parser.print_help()

main()
