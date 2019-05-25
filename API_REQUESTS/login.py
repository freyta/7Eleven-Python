'''
    7-Eleven Python implementation.
    An example of how to login with the API and print the accounts name.

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

import api.creditcard as creditcard
import api.account    as account
import api.fuellock   as fuellock
import api.giftcard   as giftcard
import json

if __name__ == '__main__' :
    # We need to save the login details into a variable. When you login there are 3 details that 7-Eleven responds
    # with. They are your device secret token, access token and your account id.
    # Device secret and access token are used for almost every request to identify the user as you.
    myaccount = account.login("your@email.com","password")

    # Get your account details. The response is a JSON array.
    get_account_details = json.loads(account.getAccountDetails(myaccount[0],myaccount[1]))
    # Print the users first name
    print(get_account_details['PersonalDetails']['Name']['Firstname'])

    account.logout(myaccount[0],myaccount[1])
