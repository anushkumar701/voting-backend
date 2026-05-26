from web3 import Web3
import json
import os

class BlockchainManager:
    def __init__(self):
        # ── Connection ─────────────────────────────────────────────────────────
        # Priority:
        #   1. WEB3_PROVIDER_URL env var  →  any RPC (Infura Sepolia, Alchemy, etc.)
        #   2. Ganache local fallback      →  http://127.0.0.1:7545
        provider_url = os.getenv('WEB3_PROVIDER_URL', 'http://127.0.0.1:7545')

        self.web3 = Web3(Web3.HTTPProvider(provider_url))
        self.contract_address = None
        self.contract_abi = None
        self.contract = None
        self.admin_account = None
        self.voter_accounts = []

        if not self.web3.is_connected():
            print(f"[Blockchain] WARNING: Provider not reachable → {provider_url}")
            return

        # ── Account setup ──────────────────────────────────────────────────────
        # For Sepolia: use ADMIN_PRIVATE_KEY env var (no unlocked accounts)
        admin_key = os.getenv('ADMIN_PRIVATE_KEY')
        if admin_key:
            try:
                acct = self.web3.eth.account.from_key(admin_key)
                self.admin_account = acct.address
                print(f"[Blockchain] Connected to Sepolia/RPC")
                print(f"[Blockchain] Admin: {self.admin_account}")
                self._private_key = admin_key  # stored for signing
            except Exception as e:
                print(f"[Blockchain] Key error: {e}")
        else:
            # Ganache path — accounts are pre-unlocked
            accounts = self.web3.eth.accounts
            if accounts:
                self.admin_account = accounts[0]
                self.voter_accounts = accounts[1:]
                self._private_key = None
                print(f"[Blockchain] Connected to Ganache")
                print(f"[Blockchain] Admin: {self.admin_account}")
                print(f"[Blockchain] Available accounts: {len(self.voter_accounts)}")

    # ── Helper: send a transaction (works for both Ganache & Sepolia) ──────────
    def _send_tx(self, fn, gas=500000):
        """Build, sign (if needed) and send a contract transaction."""
        if self._private_key:
            nonce = self.web3.eth.get_transaction_count(self.admin_account)
            tx = fn.build_transaction({
                'from': self.admin_account,
                'gas': gas,
                'nonce': nonce,
                'gasPrice': self.web3.eth.gas_price,
            })
            signed = self.web3.eth.account.sign_transaction(tx, self._private_key)
            tx_hash = self.web3.eth.send_raw_transaction(signed.rawTransaction)
        else:
            tx_hash = fn.transact({'from': self.admin_account, 'gas': gas})
        return self.web3.eth.wait_for_transaction_receipt(tx_hash)

    def load_contract(self, contract_address, abi_path='contracts/SecureVoting_ABI.json'):
        try:
            if not os.path.exists(abi_path):
                return False
            with open(abi_path, 'r') as f:
                self.contract_abi = json.load(f)
            self.contract_address = Web3.to_checksum_address(contract_address)
            self.contract = self.web3.eth.contract(
                address=self.contract_address, abi=self.contract_abi
            )
            print(f"[Blockchain] Contract loaded: {self.contract_address[:12]}...")
            return True
        except Exception as e:
            print(f"[Blockchain] Load error: {e}")
            return False

    def create_election(self, election_id, candidates):
        if not self.contract:
            return {"success": False, "message": "Contract not loaded"}
        try:
            receipt = self._send_tx(
                self.contract.functions.createElection(election_id, candidates),
                gas=5000000
            )
            print(f"[Blockchain] Election {election_id} created")
            return {"success": True, "tx_hash": receipt.transactionHash.hex()}
        except Exception as e:
            print(f"[Blockchain] Create error: {e}")
            return {"success": False, "message": str(e)}

    def activate_election(self, election_id):
        if not self.contract:
            return {"success": False, "message": "Contract not loaded"}
        try:
            receipt = self._send_tx(
                self.contract.functions.activateElection(election_id)
            )
            print(f"[Blockchain] Election {election_id} activated")
            return {"success": True, "tx_hash": receipt.transactionHash.hex()}
        except Exception as e:
            print(f"[Blockchain] Activate error: {e}")
            return {"success": False, "message": str(e)}

    def close_election(self, election_id):
        if not self.contract:
            return {"success": False, "message": "Contract not loaded"}
        try:
            receipt = self._send_tx(
                self.contract.functions.closeElection(election_id)
            )
            print(f"[Blockchain] Election {election_id} closed")
            return {"success": True, "tx_hash": receipt.transactionHash.hex()}
        except Exception as e:
            print(f"[Blockchain] Close error: {e}")
            return {"success": False, "message": str(e)}

    def cast_vote(self, election_id, candidate_index, voter_address):
        if not self.contract:
            return {"success": False, "message": "Contract not loaded"}
        try:
            voter_address = Web3.to_checksum_address(voter_address)

            # For Sepolia: voter must supply their private key via X-Voter-Key header
            # (handled in app.py) — for Ganache, check local accounts
            voter_key = getattr(self, '_current_voter_key', None)
            if voter_key:
                nonce = self.web3.eth.get_transaction_count(voter_address)
                tx = self.contract.functions.castVote(
                    election_id, candidate_index
                ).build_transaction({
                    'from': voter_address,
                    'gas': 500000,
                    'nonce': nonce,
                    'gasPrice': self.web3.eth.gas_price,
                })
                signed = self.web3.eth.account.sign_transaction(tx, voter_key)
                tx_hash = self.web3.eth.send_raw_transaction(signed.rawTransaction)
            else:
                if voter_address not in self.web3.eth.accounts:
                    return {"success": False, "message": "Address not in local accounts"}
                tx_hash = self.contract.functions.castVote(
                    election_id, candidate_index
                ).transact({'from': voter_address, 'gas': 500000})

            receipt = self.web3.eth.wait_for_transaction_receipt(tx_hash)
            print(f"[Blockchain] Vote cast: Election {election_id}, Candidate {candidate_index}")
            return {"success": True, "tx_hash": receipt.transactionHash.hex()}

        except Exception as e:
            msg = str(e).lower()
            if "already voted" in msg:
                msg = "Already voted"
            elif "not active" in msg:
                msg = "Election not active"
            elif "invalid candidate" in msg:
                msg = "Invalid candidate"
            else:
                msg = str(e)
            print(f"[Blockchain] Vote error: {msg}")
            return {"success": False, "message": msg}

    def get_results(self, election_id):
        if not self.contract:
            return {"success": False, "votes": [], "total_votes": 0}
        try:
            result = self.contract.functions.getResults(election_id).call()
            candidates = list(result[0])
            votes = list(result[1])
            if len(candidates) == 0:
                return {"success": False, "votes": [], "total_votes": 0}
            return {
                "success": True,
                "candidates": candidates,
                "votes": votes,
                "total_votes": sum(votes),
                "is_active": result[2],
            }
        except Exception as e:
            print(f"[Blockchain] Get results error for election {election_id}: {e}")
            return {"success": False, "votes": [], "total_votes": 0}

blockchain = BlockchainManager()
