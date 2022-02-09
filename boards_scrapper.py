#!/usr/bin/env python3
# coding: utf-8

from __future__ import (absolute_import, division, print_function,
                        unicode_literals)

import copy
from email.mime import image
import random
import socket
import os
import time
import re
import unicodedata
from pathlib import Path
from subprocess import call

from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.common.keys import Keys

try:
    from config import PINTEREST_PASSWORD, PINTEREST_USERNAME, PINTEREST_URL, EXPORT_DIR, BOARDS
except Exception as e:
    print(e)


def randdelay(a, b):
    time.sleep(random.uniform(a, b))


def u_to_s(uni):
    return unicodedata.normalize('NFKD', uni).encode('ascii', 'ignore')


class PinterestHelper(object):
    
    def __init__(self, login, pw, pinterest_url, download=True):
        self.download = download
        self.browser  = webdriver.Chrome()

        # Load pinterest webpage
        self.browser.get(pinterest_url)
        
        # Locate the login button and perform an automated click
        self.browser.find_element_by_xpath('//*[@id="__PWS_ROOT__"]/div[1]/div/div/div/div[1]/div[1]/div[2]/div[2]/button').click()

        # Login
        email_elem = self.browser.find_element_by_name('id')
        email_elem.send_keys(login)
        password_elem = self.browser.find_element_by_name('password')
        password_elem.send_keys(pw)
        password_elem.send_keys(Keys.RETURN)
        randdelay(2, 4)
        
    def runme(self, url, threshold=500):
        final_results = []
        previmages    = []
        tries         = 0
        try:
            self.browser.get(url)
            if self.browser.current_url.endswith("show_error=true"):
                print(f"URL {url} not found")
                threshold = -1
            while threshold > 0:
                try:
                    results = []
                    images = self.browser.find_elements_by_tag_name("img")
                    if images == previmages:
                        tries += 1
                    else:
                        tries = 0
                    if tries > 20:
                        return(final_results)
                    for i in images:
                        src = i.get_attribute("src")
                        if src:
                            if src.find("/236x/") != -1 or src.find("/474x/") != 1:
                                # TODO : check if there's more than 736x as resolution
                                src = src.replace("/236x/", "/736x/")
                                src = src.replace("/474x/", "/736x/")
                                results.append(u_to_s(src))
                                
                    previmages    = copy.copy(images)
                    final_results = list(set(final_results + results))
                    dummy         = self.browser.find_element_by_tag_name('a')
                    dummy.send_keys(Keys.PAGE_DOWN)
                    randdelay(0, 1)
                    threshold -= 1
                except StaleElementReferenceException:
                    threshold -= 1
        except(socket.error, socket.timeout):
            pass
        return(final_results)
    
    def close(self):
        """ Closes the browser """
        self.browser.close()



def main():
    """ Main function of pinterest parser """
    # Opening a pinterest session
    ph = PinterestHelper(PINTEREST_USERNAME, PINTEREST_PASSWORD, PINTEREST_URL)

    for term in BOARDS:
        destination = re.split("http.*\.fr\/\w+/", term)[-1]
        logs_file   = destination.replace("/", "_") + "pins.txt"

        # Scanning
        images = ph.runme(term)

        if len(images) == 0:
            print(f"Board {destination} : no pins found")
            continue
        
        # Create output folder if not existing
        Path(f"{EXPORT_DIR}/{destination}").mkdir(parents=True, exist_ok=True)

        # Check all filenames to only DL new pins
        images_string  = [i.decode('UTF-8') for i in images]
        already_dl_pin = os.listdir(f"{EXPORT_DIR}/{destination}")
        pin_to_dl      = [i for i in images_string if i.split("/")[-1] not in already_dl_pin]

        if len(pin_to_dl) == 0:
            print(f"Board {destination} : no new pins to download, skipping")
            continue
        
        with open(f"logs/{logs_file}", "w") as file:
            file.write('\n'.join(pin_to_dl))

        call(f'aria2c -i logs/{logs_file} -d {EXPORT_DIR}/{destination} --continue --auto-file-renaming false',
             shell=True)
    
    # Close at the end only
    ph.close()

if __name__ == '__main__':
    main()