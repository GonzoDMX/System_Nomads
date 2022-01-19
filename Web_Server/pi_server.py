#!/usr/bin/env python3

"""
	Python-Based HTTTP Server
	Créé par: Andrew O'Shei

	Il s'agit d'un simple serveur http pour une application
	de création et de connexion d'utilisateurs.
	Un serveur Web basé sur Python a été choisi pour rendre
	le projet plus portable, il peut donc être exécuté sans
	installer quelque chose comme un serveur Apache.

	Instructions:
	1. Lancez le serveur Web à partir de la ligne de commande avec python3
	2. Ouvrez un navigateur Web et accédez à l'URL: http://localhost:9001
	   (Testé sur Ubuntu 20.04 avec Python 3.8.8 et Firefox 92.0)
"""

import urllib.parse as up
from pathlib import Path
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
import db_helper as db
from subprocess import check_output

a = ""
p = 9001

""" Simple HTTP Server that handles GET and POST """
class WebServer(BaseHTTPRequestHandler):

	# Set HTML Doc type headers
	def _set_headers(self):
		self.send_response(200)
		self.send_header("Content-type", "text/html")
		self.end_headers()

	# Push GET Request to Clients
	def do_GET(self):
		# Check path, if none send to home page
		if self.path == '/':
			self.path = "/index.html"
		self.do_KICK(self.path)


	def do_HEAD(self):
		self._set_headers()

	# Retrieve POST Data
	def do_POST(self):
		content_len = int(self.headers['Content-Length'])
		# Get POST data as decoded byte string
		post_data = self.rfile.read(content_len).decode('utf-8')
		# Convert POST data to dictionary of lists
		parsed_data = up.parse_qs(post_data)
		print(parsed_data)


	# Feed Client the target page
	def do_KICK(self, target):
		self._set_headers()
		# for handling images
		if target[-4:] == ".jpg" or target[-4:] == ".ico":
			html = open(target[1:], "rb").read()
			# Push image to client
			self.wfile.write(html)
		elif target[-4:] == "html":
			# Read HTML doc as String
			html = open(target[1:], "r").read()

			data = db.select_from()

			html = html.replace("<option></option>\n", data)

			# Push web page to client
			self.wfile.write(html.encode('utf-8'))


def run(server_class=HTTPServer, handler_class=WebServer, addr=a, port=p):
	server_address = (addr, port)
	httpd = server_class(server_address, handler_class)

	print(f"Starting http server on {a}:{p}")
	try:
		httpd.serve_forever()
	except KeyboardInterrupt:
		pass
	httpd.server_close()



if __name__ == "__main__":
	# Get current IP Address of wlan0
	a = check_output(['hostname'. '-I']).decode('utf-8').replace(' ', '').replace('\n', '')
	run()

