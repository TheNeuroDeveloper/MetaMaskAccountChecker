# Overview
This small project was created due to MetaMask's portfolio limit of 25 addresses as once... I for one have ~50 addresses with dribs and drabs of funds from running countless tests on smart contracts, so I built this to quickly see if I have any significant funds remaining in my wallets. This way I don't need to manually check 50+ wallets.

# Set up .env variables
Set up your API keys in a .env file for each of the blockchain explorers and setup an Infura project (or a Web3 Provider of your choice) to receive a project ID.

# Install dependencies
npm install

# Install http-server globally
npm install -g http-server

# Start the server
http-server .

This setup will serve your index.html file, allowing you to interact with the MetaMask extension

# Next Steps
Visit the provided address e.g. http://127.0.0.1:8080

Press the button "Get Accounts" and "Select All" within MetaMask. 

This exports all wallet addresses from the plugin. 

You can now copy and paste this list into the "wallet_addresses.csv" - I will be automating this in the future. 

Once this is done, feel free to close off the server.

# Run Python Script
python3 check_wallet_balances.py

The script will begin checking the balances of your wallets across multiples chains and coins. 



