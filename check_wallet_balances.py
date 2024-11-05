import requests
import pandas as pd
from web3 import Web3
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve API keys from environment variables
ETHERSCAN_API_KEY = os.getenv('ETHERSCAN_API_KEY')
POLYGONSCAN_API_KEY = os.getenv('POLYGONSCAN_API_KEY')
BSCSCAN_API_KEY = os.getenv('BSCSCAN_API_KEY')
ARBISCAN_API_KEY = os.getenv('ARBISCAN_API_KEY')
OPTIMISMSCAN_API_KEY = os.getenv('OPTIMISMSCAN_API_KEY')
INFURA_PROJECT_ID = os.getenv('INFURA_PROJECT_ID')

# Define the APIs and their respective URLs
API_URLS = {
    'ethereum': f'https://api.etherscan.io/api?module=account&action=balance&tag=latest&apikey={ETHERSCAN_API_KEY}',
    'polygon': f'https://api.polygonscan.com/api?module=account&action=balance&tag=latest&apikey={POLYGONSCAN_API_KEY}',
    'binance': f'https://api.bscscan.com/api?module=account&action=balance&tag=latest&apikey={BSCSCAN_API_KEY}',
    'arbitrum': f'https://api.arbiscan.io/api?module=account&action=balance&tag=latest&apikey={ARBISCAN_API_KEY}',
    'optimism': f'https://api-optimistic.etherscan.io/api?module=account&action=balance&tag=latest&apikey={OPTIMISMSCAN_API_KEY}',
}

# Define native tokens and their conversion rate APIs
NATIVE_TOKENS = {
    'ethereum': ('ETH', 'https://api.coinbase.com/v2/prices/ETH-USD/spot'),
    'polygon': ('MATIC', 'https://api.coinbase.com/v2/prices/MATIC-USD/spot'),
    'binance': ('BNB', 'https://api.coinbase.com/v2/prices/BNB-USD/spot'),
    'arbitrum': ('ETH', 'https://api.coinbase.com/v2/prices/ETH-USD/spot'),
    'optimism': ('ETH', 'https://api.coinbase.com/v2/prices/ETH-USD/spot'),
}

# Define token contract addresses for USDT and USDC
TOKEN_CONTRACTS = {
    'USDT': {
        'ethereum': '0xdAC17F958D2ee523a2206206994597C13D831ec7',
        'polygon': '0xc2132D05D31c914a87C6611C10748AEb04B58e8F',
        'binance': '0x55d398326f99059fF775485246999027B3197955',
        'arbitrum': '0xfd086bc7cd5c481dcc9c85eb53a24cc94d29f104',
        'optimism': '0x4200000000000000000000000000000000000042',
    },
    'USDC': {
        'ethereum': '0xA0b86991c6218B36c1d19D4a2e9Eb0cE3606EB48',
        'polygon': '0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174',
        'binance': '0x8ac76a51cc950d9822d68b83fe1ad97b32cd580d',
        'arbitrum': '0xff970a61a04b1ca14834a43f5de4533ebddb5cc8',
        'optimism': '0x7F5c764cBc14f9669B88837ca1490cCa17c31607',
    }
}

# Web3 providers (replace with your Infura project ID)
WEB3_PROVIDERS = {
    'ethereum': Web3(Web3.HTTPProvider(f'https://mainnet.infura.io/v3/{INFURA_PROJECT_ID}')),
    'polygon': Web3(Web3.HTTPProvider(f'https://polygon-mainnet.infura.io/v3/{INFURA_PROJECT_ID}')),
    'binance': Web3(Web3.HTTPProvider('https://bsc-dataseed.binance.org/')),
    'arbitrum': Web3(Web3.HTTPProvider(f'https://arbitrum-mainnet.infura.io/v3/{INFURA_PROJECT_ID}')),
    'optimism': Web3(Web3.HTTPProvider(f'https://optimism-mainnet.infura.io/v3/{INFURA_PROJECT_ID}')),
}

# Create a session with retries
session = requests.Session()
retry = Retry(
    total=5,
    backoff_factor=0.1,
    status_forcelist=[500, 502, 503, 504]
)
adapter = HTTPAdapter(max_retries=retry)
session.mount('http://', adapter)
session.mount('https://', adapter)

# Helper function to get balance from an API
def get_balance(api_url, address):
    try:
        response = session.get(f"{api_url}&address={address}", timeout=10)
        data = response.json()
        return int(data['result']) / 10**18 if data['status'] == '1' else 0
    except Exception as e:
        print(f"Error fetching native balance for address {address} on {api_url}: {e}")
        return 0

# Helper function to get the current token to USD conversion rate
def get_token_usd(token_url):
    try:
        response = session.get(token_url, timeout=10)
        data = response.json()
        return float(data['data']['amount'])
    except Exception as e:
        print(f"Error fetching USD conversion rate from {token_url}: {e}")
        return 0

# Helper function to get ERC-20 token balance
def get_token_balance(web3, contract_address, address):
    try:
        contract_address_checksum = Web3.to_checksum_address(contract_address)
        address_checksum = Web3.to_checksum_address(address)
        print(f"Checking balance for contract {contract_address_checksum} and address {address_checksum} on network {web3}")

        if not web3.is_connected():
            print(f"Error: Not connected to {web3}. Check your Web3 provider.")
            return 0
        
        contract = web3.eth.contract(address=contract_address_checksum, abi=[
            {
                'constant': True,
                'inputs': [{'name': '_owner', 'type': 'address'}],
                'name': 'balanceOf',
                'outputs': [{'name': 'balance', 'type': 'uint256'}],
                'type': 'function'
            }
        ])
        balance = contract.functions.balanceOf(address_checksum).call()
        return balance / 10**18
    except Exception as e:
        print(f"Error fetching balance for contract {contract_address} and address {address}: {e}")
        return 0

# Main function to read CSV and get balances
def check_balances(csv_file):
    df = pd.read_csv(csv_file)
    
    # Debug print statement
    print("CSV Columns:", df.columns)
    
    if 'wallet_address' not in df.columns:
        print("The CSV file does not contain a 'wallet_address' column.")
        return
    
    addresses = df['wallet_address']

    # Get the USD conversion rates for native tokens
    native_usd_rates = {network: get_token_usd(url) for network, (_, url) in NATIVE_TOKENS.items()}

    results = []
    for index, address in enumerate(addresses):
        print(f"Checking balance for address {index + 1}/{len(addresses)}: {address}")
        address_balances = {'wallet_address': address}
        total_usd_value = 0

        for network, api_url in API_URLS.items():
            native_token, native_usd_url = NATIVE_TOKENS.get(network, (None, None))
            if native_token:
                balance = get_balance(api_url, address)
                usd_value = balance * native_usd_rates[network]
                address_balances[f'{network}_{native_token}_balance'] = balance
                address_balances[f'{network}_{native_token}_usd_value'] = usd_value
                total_usd_value += usd_value

            # Check ERC-20 token balances (USDT and USDC assumed to be $1 each)
            for token, contracts in TOKEN_CONTRACTS.items():
                token_contract = contracts.get(network)
                if token_contract:
                    token_balance = get_token_balance(WEB3_PROVIDERS[network], token_contract, address)
                    token_usd_value = token_balance  # USDT and USDC are assumed to be $1 each
                    address_balances[f'{network}_{token}_balance'] = token_balance
                    address_balances[f'{network}_{token}_usd_value'] = token_usd_value

                        # Check ERC-20 token balances (USDT and USDC assumed to be $1 each)
            for token, contracts in TOKEN_CONTRACTS.items():
                token_contract = contracts.get(network)
                if token_contract:
                    token_balance = get_token_balance(WEB3_PROVIDERS[network], token_contract, address)
                    token_usd_value = token_balance  # USDT and USDC are assumed to be $1 each
                    address_balances[f'{network}_{token}_balance'] = token_balance
                    address_balances[f'{network}_{token}_usd_value'] = token_usd_value
                    total_usd_value += token_usd_value

        address_balances['total_usd_value'] = total_usd_value
        results.append(address_balances)
        
        # Save progress to CSV file after each address
        result_df = pd.DataFrame(results)
        result_df.to_csv('wallet_balances.csv', index=False)
        print(f"Updated wallet_balances.csv with results for address {address}")

    print("Balance checking completed for all addresses.")

if __name__ == '__main__':
    check_balances('wallet_addresses.csv')

