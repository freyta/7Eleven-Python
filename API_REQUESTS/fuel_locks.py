'''
    7-Eleven Python implementation.
    An example of how to login with the API and show your current fuel lock.

    Copyright (C) 2019  Freyta
    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.
    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.
    You should have received a copy of the GNU General Public License
    along with this program. If not, see <https://www.gnu.org/licenses/>.
'''

import api.account    as account
import api.fuellock   as fuellock
import json

if __name__ == '__main__' :
    # We need to save the login details into a variable. When you login there are 3 details that 7-Eleven responds
    # with. They are your device secret token, access token and your account id.
    # Device secret and access token are used for almost every request to identify the user as you.
    myaccount = account.login("your@email.com","password")

    # Get your last fuel lock(s) into a JSON array.
    get_fuel_locks = json.loads(fuellock.listFuellock(myaccount[0],myaccount[1]))

    # Status codes:
    # 0 = ACTIVE
    # 1 = EXPIRED
    # 2 = REDEEMED
    if(get_fuel_locks[0]['Status'] == 2):
        # Get the details of the last fuel lock.
        get_last_lock_details = json.loads(fuellock.refreshFplData(myaccount[0], myaccount[1], get_fuel_locks[0]['Id']))

        print("You saved $" + str(get_last_lock_details['RewardAmount']) + ", while paying " + str(get_last_lock_details['CentsPerLitre']) + "cents per litre.")
        print("You filled up " + str(get_last_lock_details['RewardLitres'])[0:5] + " litres.")

    # And for good measure, logout.
    account.logout(myaccount[0],myaccount[1])
