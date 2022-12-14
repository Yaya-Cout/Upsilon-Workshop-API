#!/usr/bin/env bash
# Upsilon Workshop API
# Copyright (C) 2022 Upsilon
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# Script to test the API

EMAIL="email@example.org"
PASSWORD="password"
PSEUDO="pseudo"
API_URL="http://localhost:3000"
VERBOSE="0"

# Request the API (with headers)
# $1: URL
# Others arguments: headers
request() {
    curl -s -H "Accept: application/json" -H "Content-Type: application/json" "$@"
}

# Test the API (with or without headers), it uses cURL to make the request
# $1: URL
# $2: expected status code
# Others arguments: headers (if first header is "DELETE", it will use the DELETE method)
test() {
    local url="${API_URL}$1"
    local status="$2"
    shift 2
    local headers="$@"
    # Generate the cURL command
    local cmd="curl '${url}'"
    # Add the headers
    if [[ -n "${headers}" ]]; then
        # Iterate over the headers
        for header in ${headers}; do
            # If the header is "DELETE", use the DELETE method
            if [[ "${header}" == "DELETE" ]]; then
                cmd="${cmd} -X DELETE"
            else
                cmd="${cmd} -d '${header}'"
            fi
        done
    fi
    # Add the cookie input/output
    cmd="${cmd} --cookie-jar /tmp/cookies.txt --cookie /tmp/cookies.txt"
    # Don't show the progress bar
    cmd="${cmd} -s"
    # Get the status code
    local code=$(eval "${cmd}" -o /tmp/output.txt -w "%{http_code}")
    # Check the status code
    echo -n "Testing ${url}... "
    # Check the status code
    if [[ "${code}" = "${status}" ]]; then
        echo "OK"
    else
        echo "KO: expected ${status}, got ${code}"
    fi
    # Show the output if verbose and if the status code is not 000 (cURL error, not output to /tmp/output.txt)
    if [[ "${VERBOSE}" = "1" && "${code}" != "000" ]]; then
        echo "Output:"
        cat /tmp/output.txt
        echo
    fi
}

# TODO: Make proper tests

# Remove the cookies
rm -f /tmp/cookies.txt
# Test the API
# This line may crash, because the account can already exist
test "/register" "400"  "email=${EMAIL}" "password=${PASSWORD}"
test "/register" "201" "email=${EMAIL}" "password=${PASSWORD}" "pseudo=${PSEUDO}" "firstName=John" "lastName=Doe"
test "/register" "400" "email=${EMAIL}" "password=${PASSWORD}" "pseudo=${PSEUDO}" "firstName=John" "lastName=Doe"
test "/login" "200" "email=${EMAIL}" "password=${PASSWORD}"
test "/logout" "200"
test "/logout" "401"
test "/login" "401" "email=${EMAIL}" "password=wrong"
test "/login" "401" "email=wrong" "password=${PASSWORD}"
test "/login" "401" "email=wrong" "password=wrong"
test "/login" "200" "email=${EMAIL}" "password=${PASSWORD}"
test "/delete-account" "401" "use_post_request=true" # use_post_request=true is used to avoid the test command to interpret the command as a GET request
# # Next lines crashes, because the first created account isn't an admin (TODO: create an admin account from the command line)
# test "/delete-account" "401" "password=${PASSWORD}" # It will fail because the admin account can't be deleted
# test "/logout" "200" # It will fail because the admin account has been deleted (should be fixed)
# # Create a new account (not admin to avoid the test to fail)
test "/register" "201" "email=${EMAIL}.1" "password=${PASSWORD}" "pseudo=${PSEUDO}.1"
test "/login" "200" "email=${EMAIL}.1" "password=${PASSWORD}"
test "/delete-account" "200" "password=${PASSWORD}"
# We recreate the account, because we need it for the next tests, but we log out
test "/register" "201" "email=${EMAIL}.1" "password=${PASSWORD}" "pseudo=${PSEUDO}.1"
test "/logout" "200"
# test "/login" "401" "email=${EMAIL}.1" "password=${PASSWORD}"
# test "/logout" "401"


# We have to remove the account to avoid the test to fail, but we can't do it with the API : we cannot remove an admin account
# So we have to do it manually
# test "/delete-account" "200" "password=$PASSWORD"
# test "/register" "401" "email=$EMAIL"
# test "/register" "401" "password=$PASSWORD"
# test "/register" "401" "email=$EMAIL" "password=$PASSWORD"
# test "/register" "401" "password=$PASSWORD" "pseudo=$PSEUDO"
# test "/register" "401" "email=$EMAIL" "pseudo=$PSEUDO"
# test "/register" "401" "pseudo=$PSEUDO"
# test "/register" "201" "email=${EMAIL}" "password=${PASSWORD}" "pseudo=${PSEUDO}"

test "/userinfo" "401"
test "/delete-account" "401" "password=${PASSWORD}"
test "/login" "200" "email=${EMAIL}" "password=${PASSWORD}"
test "/userinfo" "200"

# Get public user information
# test "/user/by-id/1" "200"
# test "/user/by-id/0" "404"
# test "/user/by-id/f" "401"
test "/user/${PSEUDO}" "200"
test "/user/unknown" "404"
test "/user/f" "404"

# Create a script
test "/scripts/new" "200" "name=script1.py" "code=from time import sleep\nsleep(1)" "description=description" "language=python"
test "/scripts/new" "200" "name=script1.py" "code=from time import sleep\nsleep(1)"
test "/scripts/new" "200" "name=script1.py" "code=from time import sleep\nsleep(1)" "isPublic=true"
test "/scripts/new" "400" "name=script1.py"
test "/scripts/new" "400" "code=from time import sleep\nsleep(1)"
test "/scripts/delete/1" "200" "DELETE"
test "/scripts/delete/1" "404"
test "/scripts/delete/f" "400" "DELETE"
# Login as the other user and try to delete the script
test "/logout" "200"
test "/login" "200" "email=${EMAIL}.1" "password=${PASSWORD}"
test "/scripts/delete/1" "400" "DELETE"

# Get a script
test "/logout" "200"
test "/scripts/get/2" "400"
test "/scripts/get/3" "200"
test "/login" "200" "email=${EMAIL}" "password=${PASSWORD}"
test "/scripts/get/2" "200"
test "/logout" "200"
test "/login" "200" "email=${EMAIL}.1" "password=${PASSWORD}"
test "/scripts/get/2" "400"
test "/scripts/get/f" "400"
test "/scripts/get/0" "400"
test "/scripts/list" "200"
