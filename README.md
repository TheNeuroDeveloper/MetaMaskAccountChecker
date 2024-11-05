# Install dependencies
npm install

# Install http-server globally
npm install -g http-server

# Start the server
http-server .

This setup will serve your index.html file, allowing you to interact with the MetaMask extension

Visit the provided address e.g. http://127.0.0.1:8080

Press the button "Get Accounts" and "Select All" within MetaMask. 

This exports all wallet addresses from the plugin. 

You can now copy and paste this list into the "wallet_addresses.csv" - I will be automating this in the future. 

Once this is done, feel free to close off the server.

Run "python3 check_wallet_balances.py".

