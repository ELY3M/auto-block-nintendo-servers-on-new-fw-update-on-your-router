from nintendo.switch import sun, atumn
from nintendo import switch
import anyio
import os
import re
import struct
import subprocess
import requests
from anynet import tls



SYSTEM_VERSION = 2015 # 20.1.5

# You can dump prod.keys with Lockpick_RCM and
# PRODINFO from hekate (decrypt it if necessary)
PATH_KEYS = "/root/nintendoupdate/prod.keys"
PATH_PRODINFO = "/root/nintendoupdate/PRODINFO.bin"
VERSION = "/root/nintendoupdate/version.txt"


async def main():
	
    if not os.path.exists(VERSION):
        with open(VERSION, 'w') as f:
            f.write("0000")

    keys = switch.load_keys(PATH_KEYS)
    	
    prodinfo = switch.ProdInfo(keys, PATH_PRODINFO)
    device_cert = prodinfo.get_tls_cert()
    device_cert_key = prodinfo.get_tls_key()
    device_id = prodinfo.get_device_id()
		
		
    cert = prodinfo.get_tls_cert()
    pkey = prodinfo.get_tls_key()
    cert.save("device_cert.pem",tls.TYPE_PEM)
    pkey.save("device_cert.key",tls.TYPE_PEM)

	
    print("    device_cert: ")
    print(device_cert)
    print("    device_cert_key: ")	
    print(device_cert_key)	
    print("    device_id: ")
    print(device_id)
	
    
    sun_client = sun.SunClient(device_id)
    sun_client.set_system_version(SYSTEM_VERSION)
    sun_client.set_certificate(device_cert, device_cert_key)
    
    atumn_client = atumn.AtumnClient(device_id)
    atumn_client.set_system_version(SYSTEM_VERSION)
    atumn_client.set_certificate(device_cert, device_cert_key)
	
   
    # Request latest system update info
    response = await sun_client.system_update_meta()
    
    print(response)
    
    title_id = int(response["system_update_metas"][0]["title_id"], 16)
    title_version = response["system_update_metas"][0]["title_version"]
	
	# read version.txt and compare update version numbers
    with open(VERSION, "r") as file:
        saved_title_version = file.read()
        print("saved update version: %s" %saved_title_version)
      
    if str(title_version) == saved_title_version:
        print("still same update version: %i" %title_version)
    else:
	    print("new update version!!! %i" %title_version)
	    ###requests.get("https://xxxxxxxxxxxxxxxxxxxxxx/nintendo.php") #my custom script to alert me
	    os.system("/bin/cp /root/nintendoupdate/dnsmasq-nintendoblock.conf /etc/dnsmasq.conf")
	    os.system("/etc/init.d/dnsmasq restart")
	   	    
    print("Latest system update:")
    print("    Title id: %016x" %title_id)
    print("    Title version: %i" %title_version)
    print()

    with open(VERSION, "w") as file:
        file.write("%i" %title_version)
		
anyio.run(main)

