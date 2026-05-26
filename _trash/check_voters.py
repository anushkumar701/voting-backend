from database.db_setup import get_all_voters
voters = get_all_voters()
print('Current voters in database:')
for voter in voters:
    eth = voter.get('ethereum_address', 'None')
    print(f'  {voter["user_id"]} | {voter["name"]} | {voter["phone"]} | ETH: {eth} | Active: {voter["is_active"]}')