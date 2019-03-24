'''
    7-Eleven Python implementation.
    An example of how to login with the API and add credit to your account via credit card.

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
import api.creditcard   as creditcard
import json

if __name__ == '__main__' :
    # We need to save the login details into a variable. When you login there are 3 details that 7-Eleven responds
    # with. They are your device secret token, access token and your account id.
    # Device secret and access token are used for almost every request to identify the user as you.
    myaccount = account.login("your@email.com","password")


    # Get your credit card details
    ccdetails = creditcard.getCreditCards(myaccount[0], myaccount[1])

    # The amount you want to add must be either of the following options:
    # 10.00 , 20.00 , 30.00 , 40.00 , 50.00 , 60.00 , 70.00 , 80.00
    #
    # begin_transaction returns 2 variables. The first is TraceId which is used throughout the transaction
    # which acts as a session. The second is the URL which we need to go to to upload credit
    begin_transaction = creditcard.beginCCTransaction(ccdetails[0], "10.00", myaccount[0], myaccount[1])

    # Now we need to verify the transaction. Replace 123 with your CVV
    creditcard.verifyCcTransaction('123', begin_transaction[0], begin_transaction[1], myaccount[0], myaccount[1])

    # After we have loaded the pay URL, we then just need to load the confirmation page and our account is topped up!
    creditcard.confirmCreditCardTransaction(begin_transaction[0], begin_transaction[1], myaccount[0], myaccount[1])

    # And for good measure, logout.
    account.logout(myaccount[0],myaccount[1])
