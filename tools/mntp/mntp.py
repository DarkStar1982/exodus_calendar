#!/usr/bin/env python3
import argparse
import os
import sys
from concurrent import futures
from math import modf

sys.path.append(os.path.join(os.path.dirname(__file__), '../..', 'src'))

from exodus_calendar.utils import mars_datetime_now
import grpc
import mntp_pb2
import mntp_pb2_grpc

class MNTP_Client():
	version_info = 1
	mode = 0
	poll = 1
	precision = 1

	def form_client_packet(self):
		packet = {}
		packet["header"] = self.version_info<<24 | self.mode<<16 | self.poll<<8 | self.precision
		packet["root_delay"] = 0
		packet["dispersion"] = 0
		packet["reference_id"] = 0
		packet["reference_timestamp"] = 0
		packet["origin_timestamp"] =  0
		packet["receive_timestamp"] = 0
		packet["transmit_timestamp"] = mars_datetime_now(format="ms")
		packet["sha2checksum"] = '0'
		return packet

	def client_call(self):
		print("Will try to request timestamp ...")
		with grpc.insecure_channel("localhost:1955") as channel:
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
	
	def decode_client_packet(self, packet):
		client_version = packet.Header>>24 & 0x000000FF
		mode = packet.Header>>16 & 0x000000FF
		poll = packet.Header>>8 & 0x000000FF
		precision = packet.Header & 0x000000FF
		print(f"Client header: {client_version} | {mode} | {poll} | {precision}")
		return (packet.TransmitTimestamp, packet.Header)

	def form_server_packet(self):
		packet = {}
		packet["header"] = self.version_info<<24 | self.mode<<16 | self.poll<<8 | self.precision
		packet["root_delay"] = 0
		packet["dispersion"] = 0
		packet["reference_id"] = 1
		packet["reference_timestamp"] = REF_TIMESTAMP
		packet["origin_timestamp"] =  0
		packet["receive_timestamp"] = mars_datetime_now(format="ms")
		packet["transmit_timestamp"] = 0
		packet["sha2checksum"] = '0'
		return packet

	def ProcessTimeSyncRequest(self, request, context):
		packet = self.form_server_packet()
		result, header = self.decode_client_packet(request)
		print("Client packed received: " + str(header))
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
	port = "1955"
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
		print("Are we there?")
		client = MNTP_Client()
		client.client_call()
		return

	parser.print_help()

main()
