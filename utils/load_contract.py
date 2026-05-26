from utils.blockchain_utils import blockchain
import sys

if len(sys.argv) < 2:
    print("Usage: python load_contract.py <contract_address>")
    sys.exit(1)

contract_address = sys.argv[1]
if blockchain.load_contract(contract_address):
    with open('contract_address.txt', 'w') as f:
        f.write(contract_address)
    print(f"Contract loaded and saved: {contract_address}")
else:
    print("Failed to load contract")
    sys.exit(1)
