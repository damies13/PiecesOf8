#	Pieces Of 8 Server
#
# 	v0.0.1
#

import configparser
import argparse
import threading

import time
from datetime import datetime

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer, HTTPServer
import urllib.parse
import json

from sqlite3worker import Sqlite3Worker
import uuid

class PO8_WebServer(BaseHTTPRequestHandler):
	def do_HEAD(self):
		core.debugmsg(7, " ")
		return

class PiecesOf8Server:

	version="0.0.1"
	debuglvl = 0

	po8_ini = None
	save_ini = True

	dbcleanup = None
	webserver = None
	httpserver = None
	db = None

	appstarted = False
	keeprunning = True


	def __init__(self, arg):

		self.debugmsg(0, "Pieces Of 8 Server")
		self.debugmsg(0, "	Version", self.version)

		self.debugmsg(9, "ArgumentParser")
		# Check for command line args
		parser = argparse.ArgumentParser()
		parser.add_argument('-g', '--debug', help='Set debug level, default level is 0')
		parser.add_argument('-v', '--version', help='Display the version and exit', action='store_true')
		parser.add_argument('-i', '--ini', help='path to alternate ini file')
		parser.add_argument('-d', '--dir', help='Data directory')
		parser.add_argument('-e', '--ipaddress', help='IP Address to bind the server to')
		parser.add_argument('-p', '--port', help='Port number to bind the server to')
		self.args = parser.parse_args()

		self.debugmsg(6, "self.args: ", self.args)

		if self.args.debug:
			self.debuglvl = int(self.args.debug)

		if self.args.version:
			exit()

		self.debugmsg(6, "ConfigParser")
		self.config = configparser.ConfigParser()
		scrdir = os.path.abspath(os.path.dirname(__file__))
		self.debugmsg(6, "scrdir: ", scrdir)

		self.tdt_ini = os.path.join(scrdir, "PiecesOf8Server.ini")
		if self.args.ini:
			self.save_ini = False
			self.debugmsg(5, "self.args.ini: ", self.args.ini)
			self.tdt_ini = self.args.ini

		if os.path.isfile(self.tdt_ini):
			self.debugmsg(9, "tdt_ini: ", self.tdt_ini)
			self.config.read(self.tdt_ini)
		else:
			self.saveini()
		self.debugmsg(0, "Configuration File: ", self.tdt_ini)

		if 'Server' not in self.config:
			self.config['Server'] = {}
			self.saveini()

		if 'BindIP' not in self.config['Server']:
			self.config['Server']['BindIP'] = ''
			self.saveini()

		if 'BindPort' not in self.config['Server']:
			self.config['Server']['BindPort'] = "3888"
			self.saveini()

		if 'DataDir' not in self.config['Server']:
			self.config['Server']['DataDir'] = scrdir
			self.saveini()

		if 'DBFile' not in self.config['Server']:
			self.config['Server']['DBFile'] = "TestDataTable.sqlite3"
			self.saveini()


		if 'Resources' not in self.config:
			self.config['Resources'] = {}
			self.saveini()

		if 'js_jquery' not in self.config['Resources']:
			self.config['Resources']['js_jquery'] = 'https://unpkg.com/jquery@latest/dist/jquery.min.js'
			self.saveini()

		if 'js_jqueryui' not in self.config['Resources']:
			self.config['Resources']['js_jqueryui'] = 'https://code.jquery.com/ui/1.12.1/jquery-ui.min.js'
			self.saveini()

		if 'css_jqueryui' not in self.config['Resources']:
			self.config['Resources']['css_jqueryui'] = 'https://code.jquery.com/ui/1.12.1/themes/base/jquery-ui.css'
			self.saveini()

		if 'js_papaparse' not in self.config['Resources']:
			self.config['Resources']['js_papaparse'] = 'https://unpkg.com/papaparse@latest/papaparse.min.js'
			self.saveini()


		if self.args.dir:
			self.save_ini = False
			self.debugmsg(5, "self.args.dir: ", self.args.dir)
			DataDir = os.path.abspath(self.args.dir)
			self.debugmsg(5, "DataDir: ", DataDir)
			self.config['Server']['DataDir'] = DataDir

		if self.args.ipaddress:
			self.save_ini = False
			self.debugmsg(5, "self.args.ipaddress: ", self.args.ipaddress)
			self.config['Server']['BindIP'] = self.args.ipaddress

		if self.args.port:
			self.save_ini = False
			self.debugmsg(5, "self.args.port: ", self.args.port)
			self.config['Server']['BindPort'] = self.args.port


		# https://pypi.org/project/sqlite3worker/
		#
		# Connect db
		#
		if self.db is None:
			createschema = False
			if not os.path.exists(self.config['Server']['DataDir']):
				os.mkdir(self.config['Server']['DataDir'])
			dbfile = os.path.join(self.config['Server']['DataDir'], self.config['Server']['DBFile'])
			if not os.path.exists(dbfile):
				createschema = True
			# chaning this setting did help to speed up bulk inserts a little, but it
			# 	also slowed individual inserts, selects, deletes etc a lot!
			# I'll leave this here as we may want to try tuning this later, maybe a value of 200 or 500
			# 	might be optimal, 1000 is definatly too big, I think 500 might be too big as well.
			# 	But 200 might not be enought to make an appreciable speed up in bulk inserts. will need some testing
			queue_size = 100 # use default value
			# queue_size = 1000 # default is 100
			self.db = Sqlite3Worker(dbfile, queue_size)
			if createschema:

				result = self.db.execute("CREATE TABLE po8_data (ID TEXT, type TEXT, value TEXT, created DATETIME, deleted DATETIME, PRIMARY KEY(ID))")
				self.debugmsg(6, "CREATE TABLE po8_data", result)


				# result = self.db.execute("CREATE TABLE tdt_tables (ID TEXT, table_name TEXT, deleted DATETIME, PRIMARY KEY(ID))")
				# self.debugmsg(6, "CREATE TABLE tdt_tables", result)

				# result = self.db.execute("CREATE TABLE tdt_columns (ID TEXT, table_id NUMBER, column_name TEXT, deleted DATETIME, PRIMARY KEY(ID))")
				# self.debugmsg(6, "CREATE TABLE tdt_columns", result)

				# result = self.db.execute("CREATE TABLE tdt_data (ID TEXT, column_id NUMBER, value TEXT, deleted DATETIME, PRIMARY KEY(ID))")
				# self.debugmsg(6, "CREATE TABLE tdt_data", result)


				result = self.db.execute("CREATE INDEX \"data_value\" ON \"po8_data\" (\"value\");")
				result = self.db.execute("CREATE INDEX \"data_type\" ON \"po8_data\" (\"type\");")
				result = self.db.execute("CREATE INDEX \"data_del\" ON \"po8_data\" (\"deleted\");")

				#  create indexes

				# result = self.db.execute("CREATE INDEX \"tables_name\" ON \"tdt_tables\" (\"table_name\");")
				# result = self.db.execute("CREATE INDEX \"tables_del\" ON \"tdt_tables\" (\"deleted\");")
				#
				# result = self.db.execute("CREATE INDEX \"columns_name\" ON \"tdt_columns\" (\"column_name\");")
				# result = self.db.execute("CREATE INDEX \"columns_tbl_id\" ON \"tdt_columns\" (\"table_id\");")
				# result = self.db.execute("CREATE INDEX \"columns_del\" ON \"tdt_columns\" (\"deleted\");")
				#
				# result = self.db.execute("CREATE INDEX \"data_value\" ON \"tdt_data\" (\"value\");")
				# result = self.db.execute("CREATE INDEX \"data_col_id\" ON \"tdt_data\" (\"column_id\");")
				# result = self.db.execute("CREATE INDEX \"data_del\" ON \"tdt_data\" (\"deleted\");")

				createschema = False
			# Never do this it changes the row id's and breaks the data
			else:
				# VACUUM frees up space and defragments the file, especially after large deletes
				results = self.db.execute("VACUUM")
				self.debugmsg(9, "VACUUM: results:", results)
				self.db.close()
				self.db = None
				self.db = Sqlite3Worker(dbfile)



		self.debugmsg(5, "run_web_server")
		self.webserver = threading.Thread(target=self.run_web_server)
		self.webserver.start()

		self.debugmsg(9, "end __init__")



	def mainloop(self):
		self.debugmsg(7, " ")
		self.debugmsg(5, "appstarted:", self.appstarted)
		while not self.appstarted:
			self.debugmsg(9, "sleep(1)")
			time.sleep(1)
			self.debugmsg(9, "appstarted:", self.appstarted)

		self.debugmsg(5, "keeprunning:", self.keeprunning)
		i = 0
		while self.keeprunning:
			time.sleep(1)
			if i > 9:
				self.debugmsg(9, "keeprunning:", self.keeprunning)
				i = 0
				# run_db_cleanup
				self.dbcleanup = threading.Thread(target=self.run_db_cleanup)
				self.dbcleanup.start()
			i +=1

		self.debugmsg(5, "mainloop ended")

	def run_web_server(self):
		self.debugmsg(7, " ")

		srvip = self.config['Server']['BindIP']
		srvport = int(self.config['Server']['BindPort'])
		if len(srvip)>0:
			srvdisphost = srvip
			ip = ipaddress.ip_address(srvip)
			self.debugmsg(5, "ip.version:", ip.version)
			if ip.version == 6 and sys.version_info < (3, 8):
				self.debugmsg(0, "Python 3.8 or higher required to bind to IPv6 Addresses")
				pyver = "{}.{}.{}".format(sys.version_info[0], sys.version_info[1], sys.version_info[2])
				self.debugmsg(0, "Python Version:",pyver,"	IP Version:", ip.version, "	IP Address:", srvip)
				srvip = ''
				srvdisphost = socket.gethostname()
		else:
			srvdisphost = socket.gethostname()

		server_address = (srvip, srvport)
		try:
			self.httpserver = ThreadingHTTPServer(server_address, PO8_WebServer)
		except PermissionError:
			self.debugmsg(0, "Permission denied when trying :",server_address)
			self.on_closing()
			return False
		except Exception as e:
			self.debugmsg(5, "e:", e)
			self.on_closing()
			return False


		self.appstarted = True
		self.debugmsg(5, "appstarted:", self.appstarted)
		self.debugmsg(0, "Starting Test Data Table Server", "http://{}:{}/".format(srvdisphost, srvport))
		self.httpserver.serve_forever()


	def run_db_cleanup(self):
		self.debugmsg(7, " ")


	def on_closing(self, *others):
		self.debugmsg(7, others)
		if self.appstarted:
			self.keeprunning = False

			self.debugmsg(5, "Close Web Server")
			try:
				# self.debugmsg(0, "Shutdown Agent Server")
				self.httpserver.shutdown()
				self.appstarted = False
			except Exception as e:
				self.debugmsg(9, "Exception:", e)
				pass

			if self.db is not None:
				self.debugmsg(5, "Close DB")
				try:
					self.db.close()
					self.db = None
				except Exception as e:
					self.debugmsg(9, "Exception:", e)
					pass

	def saveini(self):
		self.debugmsg(7, " ")
		if self.save_ini:
			with open(self.tdt_ini, 'w') as configfile:    # save
			    self.config.write(configfile)

	def debugmsg(self, lvl, *msg):
		msglst = []
		prefix = ""

		# print("debugmsg: debuglvl:", self.debuglvl," >= lvl:",lvl,"	msg:", msg)

		if self.debuglvl >= lvl:
			try:
				if self.debuglvl >= 4:
					stack = inspect.stack()
					the_class = stack[1][0].f_locals["self"].__class__.__name__
					the_method = stack[1][0].f_code.co_name
					the_line = stack[1][0].f_lineno
					# print("RFSwarmBase: debugmsg: I was called by {}.{}()".format(str(the_class), the_method))
					prefix = "{} | {}: {}({}): [{}:{}]	".format(datetime.now().isoformat(sep=' ',timespec='seconds'), str(the_class), the_method, the_line, self.debuglvl, lvl)
					# <36 + 1 tab
					# if len(prefix.strip())<36:
					# 	prefix = "{}	".format(prefix)
					# <32 + 1 tab
					if len(prefix.strip())<32:
						prefix = "{}	".format(prefix)
					# <28 + 1 tab
					# if len(prefix.strip())<28:
					# 	prefix = "{}	".format(prefix)
					# <24 + 1 tab
					if len(prefix.strip())<24:
						prefix = "{}	".format(prefix)

					msglst.append(str(prefix))

				for itm in msg:
					msglst.append(str(itm))
				print(" ".join(msglst))
			except Exception as e:
				# print("debugmsg: Exception:", e)
				pass

	#
	#	reusable table, column and vlaue functions
	#





core = PiecesOf8Server()
# core = TDT_Core()

try:
	core.mainloop()
except KeyboardInterrupt:
	core.on_closing()
except Exception as e:
	core.debugmsg(1, "self.Exception:", e)
	core.on_closing()
