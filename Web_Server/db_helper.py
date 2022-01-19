#!/usr/bin/env python3

"""
	Created by: Andrew O'Shei
	
	Helper function for writing data to the SQLite DB
	This file is imported as a module and not executed directly
"""


import sqlite3


# Receives date, time, count, andrew and file path to image as arguments
def insert_entry(d, t, c, a, fp):
	try:
		sqliteConnection = sqlite3.connect('Detector.db')
		cursor = sqliteConnection.cursor()
		
		insert = """INSERT INTO detector_log
				(date, time, count, andrew, path)
				VALUES (?, ?, ?, ?, ?);"""
								
		data = (d, t, c, a, fp)
		cursor.execute(insert, data)
		sqliteConnection.commit()
		
		cursor.close()
		
	except:
		print("Failed to update log database.", error)
		
	finally:
		if sqliteConnection:
			sqliteConnection.close()
			
			
def format_number(val):
	if val > 9999:
		return str(val)
	if val > 999:
		return ("." + str(val))
	if val > 99:
		return (".." + str(val))
	if val > 9:
		return ("..." + str(val))
	return ("...." + str(val))
			
# Returns the contents of the database
def select_from():
	data = []
	data_string = ""
	try:
		sqliteConnection = sqlite3.connect('Detector.db')
		cursor = sqliteConnection.cursor()
		
		cursor.execute("SELECT * FROM detector_log;")
		
		rows = cursor.fetchall()
		cursor.close()
		
		# Fill list with data
		for row in rows:
			data.append(row)
		
		# Flip list so most recent entry is first
		data.reverse()
		
		data_count = 1
		for d in data:
			data_string += "<option value=\"photo_log/" + d[4] + "\">"
			data_string += format_number(data_count)
			data_string += " | Timestamp: " + d[0] + "  " + d[1] + " | "
			data_string += "Face Count: " + str(d[2]) + " | "
			data_string += "ID: "
			if d[3]:
				data_string += "Andrew"
			else:
				data_string += "Intruder"
			data_string += "</option>\n"
			data_count += 1
		print(data_string)
	except:
		print("Failed to connect to database.", error)
		
	finally:
		if sqliteConnection:
			sqliteConnection.close()
		return data_string
		
