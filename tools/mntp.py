#!/usr/bin/env python3
import argparse
import hashlib
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


PORT = 1955
SERVER = "localhost"

class MNTP_Client():
	version = 1
	mode = 0
	poll = 1
	precision = 1

	def form_client_packet(self):
		packet = {
			"header": self.version<<24 | self.mode<<16 | self.poll<<8 | self.precision,
			"root_delay": 0,
			"dispersion": 0,
			'reference_id': 0,
			'root_delay': 0,
			'dispersion': 0,
			'reference_id':0,
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

	def client_call(self):
		print("Will try to request timestamp ...")
		with grpc.insecure_channel(f"{SERVER}:{PORT}") as channel:
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
			T4 = mars_datetime_now(format="ms")
			T3 = response.TransmitTimestamp
			T2 = response.ReceiveTimestamp
			T1 = response.OriginTimestamp
			print(f"T1:{T1}, T2:{T2}, T3:{T3}, T4:{T4}")
			print(f"d={(T4 - T1) - (T3 - T2)}")
			print(f"t={((T2 - T1) + (T3 - T4))/2}")


class MNTP_Server(mntp_pb2_grpc.MNTP_Service):
	version_info = 1
	mode = 1
	poll = 1
	precision = 1
	ref_timestamp = mars_datetime_now(format="ms")
	
	def check_packet_integrity(self, packet):
		packet_as_str = ''
		decoded = {}
		decoded["header"] = packet.Header
		decoded["root_delay"] = packet.RootDelay
		decoded["dispersion"] = packet.Dispersion
		decoded["reference_id"] = packet.ReferenceID
		decoded["reference_timestamp"] = packet.ReferenceTimestamp
		decoded["receive_timestamp"] = packet.ReceiveTimestamp
		decoded["origin_timestamp"] = packet.OriginTimestamp
		decoded["transmit_timestamp"] = packet.TransmitTimestamp

		packet_as_str = ''
		for value in decoded.values():
			packet_as_str = packet_as_str + str(value)
		
		str_bytes= packet_as_str.encode('utf-8')
		sha256hex = hashlib.sha256(str_bytes).hexdigest()
		assert(sha256hex ==packet.SHA2Checksum)
		return True

	def decode_client_packet(self, packet):
		integrity = self.check_packet_integrity(packet)
		client_version = packet.Header>>24 & 0x000000FF
		mode = packet.Header>>16 & 0x000000FF
		poll = packet.Header>>8 & 0x000000FF
		precision = packet.Header & 0x000000FF
		sha2hash = packet.SHA2Checksum
		print(f"Client packet header: {client_version} | {mode} | {poll} | {precision}")
		print(f"Client packet checksum: {sha2hash}")
		return (packet.TransmitTimestamp, packet.Header)

	def form_server_packet(self):
		packet = {}
		packet["header"] = self.version_info<<24 | self.mode<<16 | self.poll<<8 | self.precision
		packet["root_delay"] = 0
		packet["dispersion"] = 0
		packet["reference_id"] = 1
		packet["reference_timestamp"] = self.ref_timestamp
		packet["origin_timestamp"] =  0
		packet["receive_timestamp"] = mars_datetime_now(format="ms")
		packet["transmit_timestamp"] = 0
		packet["sha2checksum"] = '0'
		return packet

	def ProcessTimeSyncRequest(self, request, context):
		packet = self.form_server_packet()
		result, header = self.decode_client_packet(request)
		print("Client packet received: " + str(header))
		return mntp_pb2.MNTP_Packet(
			Header = packet["header"], 
			RootDelay = packet["root_delay"], 
			Dispersion = packet["dispersion"], 
			ReferenceID = packet["reference_id"],
            ReferenceTimestamp = packet["reference_timestamp"], 
            OriginTimestamp = result, 
            ReceiveTimestamp = packet["receive_timestamp"],
            TransmitTimestamp = mars_datetime_now(format="ms"), 
            SHA2Checksum = 'B'
        )


def serve():
	port = f"{PORT}"
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
	args = parser.parse_args()

	if args.server:
		serve()
	
	if args.client:
		client = MNTP_Client()
		client.client_call()
		return

	parser.print_help()

main()
