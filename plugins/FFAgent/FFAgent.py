#!/usr/bin/python
# -*- coding: cp1252 -*-

"""
FFAgent-Plugin to send FMS-, ZVEI- and POCSAG - messages to FF-Agent

@author: Ricardo Krippner

@requires: FFAgent-Configuration has to be set in the config.ini
"""

import time
import logging # Global logger
import hmac, hashlib
import json, requests
import string

from includes import globals  # Global variables

from includes.helper import timeHandler
from includes.helper import configHandler

##
#
# onLoad (init) function of plugin
# will be called one time by the pluginLoader on start
#
def onLoad():
	"""
	While loading the plugins by pluginLoader.loadPlugins()
	this onLoad() routine is called one time for initialize the plugin

	@requires:  nothing

	@return:    nothing
	"""
	# nothing to do for this plugin
	return


##
#
# Main function of FFAgent-plugin
# will be called by the alarmHandler
#
def run(typ,freq,data):
	"""
	This function is the implementation of the FFAgent-Plugin.
	It will send the data to FFAgent Webservice API

	Documentation here:
	http://free.ff-agent.com/app/public/docs/Dokumentation_WebAPI.pdf

	@type    typ:  string (FMS|ZVEI|POC)
	@param   typ:  Typ of the dataset
	@type    data: map of data (structure see readme.md in plugin folder)
	@param   data: Contains the parameter
	@type    freq: string
	@keyword freq: frequency of the SDR Stick

	@requires:  FFAgent-Configuration has to be set in the config.ini

	@return:    nothing
	"""
	try:
		if configHandler.checkConfig("FFAgent"): #read and debug the config

			try:
				#
				# FFAgent-Request
				#
				logging.debug("send FFAgent %s", typ)

				if globals.config.get("FFAgent", "live") == "1":
					url = "https://api.service.ff-agent.com/v1/WebService/triggerAlarm"
				else:
					url = "https://free.api.service.ff-agent.com/v1/WebService/triggerAlarm"

				serverCertFile = globals.config.get("FFAgent", "serverCertFile")
				clientCertFile = globals.config.get("FFAgent", "clientCertFile")
				clientCertPass = globals.config.get("FFAgent", "clientCertPass")
				webApiToken = globals.config.get("FFAgent", "webApiToken")
				webApiKey = globals.config.get("FFAgent", "webApiKey")
				accessToken = globals.config.get("FFAgent", "accessToken")
				selectiveCallCode = globals.config.get("FFAgent", "selectiveCallCode")

				# data["description"]
				msg_split = data["msg"].split(';')

				alarmData = {
					"alarmDate" : "",
					"keyword" : msg_split[0],
					"type" : "",
					"message" : data["msg"],
					"note" : msg_split[5],
					"operationResources" : "",
					"operationSchedule" : "",
					"object" : msg_split[2],
					"location" : msg_split[3] + " " + msg_split[4],
					"district" : msg_split[1],
					"lat" : "",
					"lng" : "",
					"easting" : "",
					"northing" : "",
					"alarmMessage" : ""
				}

				if globals.config.get("FFAgent", "test") == "1":
					alarmData = {
						"alarmDate" : "",
						"keyword" : "Test",
						"type" : "Test",
                                        	"message" : data["msg"],
                                	        "note" : msg_split[5],
                        	                "operationResources" : "",
                	                        "operationSchedule" : "",
        	                                "object" : msg_split[2],
	                                        "location" : msg_split[3] + " " + msg_split[4],
                                        	"district" : msg_split[1],
                                	        "lat" : "",
                        	                "lng" : "",
                	                        "easting" : "",
        	                                "northing" : "",
	                                        "alarmMessage" : ""
					}

				alarmData = json.dumps(alarmData)
				logging.debug(alarmData)

				alarmHeaders = {
					"Content-Type": "application/json",
					"webApiToken": webApiToken,
					"accessToken": accessToken,
					"selectiveCallCode": selectiveCallCode,
					"hmac": hmac.new(webApiKey, webApiToken + selectiveCallCode + accessToken + alarmData, digestmod=hashlib.sha256).hexdigest()
				}

				if globals.config.get("FFAgent", "live") == "1":
					r = requests.post(url, data=alarmData, headers=headers, verify=serverCertFile, cert=(clientCertFile, clientCertPass))
				else:
					r = requests.post(url, data=alarmData, headers=alarmHeaders, verify=serverCertFile)

			except:
				logging.error("cannot send FFAgent request")
				logging.debug("cannot send FFAgent request", exc_info=True)
				return

			else:
				try:
					#
					# check FFAgent-Response
					#
					if r.status_code == requests.codes.ok: #Check FFAgent Response and print a Log or Error
						logging.debug("FFAgent response: %s" , str(r.status_code))
					else:
						logging.warning("FFAgent response: %s" , str(r.status_code))
				except: #otherwise
					logging.error("cannot get FFAgent response")
					logging.debug("cannot get FFAgent response", exc_info=True)
					return

			finally:
				logging.debug("close FFAgent-Connection")
				try:
					r.close()
				except:
					pass

	except:
		logging.error("unknown error")
		logging.debug("unknown error", exc_info=True)