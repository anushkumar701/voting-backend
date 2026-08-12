"""
Blockchain Simulator
────────────────────
In-memory ledger that replicates the SecureVoting Solidity contract.
All election creation, voting, and result tallying happen server-side
with no external blockchain dependency (Ganache / Infura not required).

State is rebuilt from the SQLite database on every server restart
via the ``sync_from_db`` method, ensuring full persistence.
"""

import hashlib
import secrets
import time


class BlockchainSimulator:
    """
    Drop-in replacement for the Web3-based BlockchainManager.
    Maintains an in-memory ledger of elections, votes, and voter
    participation that mirrors the Solidity SecureVoting contract.
    """

    def __init__(self):
        self._elections = {}
        self.contract_address = self._make_address()
        self.contract = True  # Always "loaded" — keeps app.py checks passing
        print("[Blockchain] Simulator initialized")
        print(f"[Blockchain] Contract: {self.contract_address[:12]}...")

    # ── Helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def _make_address():
        """Generate a realistic Ethereum-style address (0x + 40 hex chars)."""
        raw = secrets.token_hex(20)
        digest = hashlib.sha256(raw.encode()).hexdigest()
        addr = "0x"
        for i, ch in enumerate(raw):
            if ch in "abcdef" and int(digest[i % len(digest)], 16) >= 8:
                addr += ch.upper()
            else:
                addr += ch
        return addr

    @staticmethod
    def _tx_hash():
        """Generate a realistic transaction hash."""
        raw = f"{time.time_ns()}{secrets.token_hex(16)}".encode()
        return "0x" + hashlib.sha256(raw).hexdigest()

    # ── Public: address generation ──────────────────────────────────────

    def generate_address(self):
        """Return a new unique simulated Ethereum address."""
        return self._make_address()

    def load_contract(self, contract_address=None):
        """Compatibility stub — simulator is always ready."""
        if contract_address:
            self.contract_address = contract_address
        return True

    # ── Sync from database (called once at startup) ─────────────────────

    def sync_from_db(self, elections, vote_records):
        """
        Rebuild the in-memory ledger from existing database records.

        Args:
            elections:    list of dicts with keys
                          ``election_id``, ``candidates`` (list), ``status``
            vote_records: list of dicts with keys
                          ``election_id``, ``voter_address``, ``candidate_index``
        """
        for e in elections:
            eid = e["election_id"]
            cands = e["candidates"]
            self._elections[eid] = {
                "candidates": list(cands),
                "votes": [0] * len(cands),
                "has_voted": set(),
                "is_active": e["status"] == "ACTIVE",
            }

        for v in vote_records:
            eid = v["election_id"]
            if eid not in self._elections:
                continue
            el = self._elections[eid]
            ci = v.get("candidate_index")
            if ci is not None and 0 <= ci < len(el["candidates"]):
                el["votes"][ci] += 1
            el["has_voted"].add(v["voter_address"])

        print(f"[Blockchain] Synced {len(elections)} elections from database")

    # ── Election lifecycle ──────────────────────────────────────────────

    def create_election(self, election_id, candidates):
        if election_id in self._elections:
            return {"success": False, "message": "Election already exists on chain"}
        self._elections[election_id] = {
            "candidates": list(candidates),
            "votes": [0] * len(candidates),
            "has_voted": set(),
            "is_active": False,
        }
        print(f"[Blockchain] Election {election_id} created")
        return {"success": True, "tx_hash": self._tx_hash()}

    def activate_election(self, election_id):
        if election_id not in self._elections:
            return {"success": False, "message": "Election not found on chain"}
        self._elections[election_id]["is_active"] = True
        print(f"[Blockchain] Election {election_id} activated")
        return {"success": True, "tx_hash": self._tx_hash()}

    def close_election(self, election_id):
        if election_id not in self._elections:
            return {"success": False, "message": "Election not found on chain"}
        self._elections[election_id]["is_active"] = False
        print(f"[Blockchain] Election {election_id} closed")
        return {"success": True, "tx_hash": self._tx_hash()}

    def delete_election(self, election_id):
        if election_id in self._elections:
            del self._elections[election_id]
            print(f"[Blockchain] Election {election_id} deleted")
            return {"success": True}
        return {"success": False, "message": "Election not found on chain"}

    # ── Voting ──────────────────────────────────────────────────────────

    def cast_vote(self, election_id, candidate_index, voter_address):
        if election_id not in self._elections:
            return {"success": False, "message": "Election not found on chain"}

        el = self._elections[election_id]

        if not el["is_active"]:
            return {"success": False, "message": "Election not active"}
        if voter_address.lower() in {a.lower() for a in el["has_voted"]}:
            return {"success": False, "message": "Already voted"}
        if candidate_index < 0 or candidate_index >= len(el["candidates"]):
            return {"success": False, "message": "Invalid candidate"}

        el["votes"][candidate_index] += 1
        el["has_voted"].add(voter_address)

        print(f"[Blockchain] Vote: Election {election_id}, Candidate {candidate_index}")
        return {"success": True, "tx_hash": self._tx_hash()}

    # ── Results ─────────────────────────────────────────────────────────

    def get_results(self, election_id):
        if election_id not in self._elections:
            return {"success": False, "votes": [], "total_votes": 0}
        el = self._elections[election_id]
        return {
            "success": True,
            "candidates": el["candidates"],
            "votes": list(el["votes"]),
            "total_votes": sum(el["votes"]),
            "is_active": el["is_active"],
        }


blockchain = BlockchainSimulator()
