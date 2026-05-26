# E-VOTING SYSTEM - COMPLETE TESTING GUIDE

## SYSTEM OVERVIEW
- **Backend**: Flask (Python) with blockchain integration
- **Frontend**: React with modern UI
- **Blockchain**: Ganache (Ethereum) on port 7545
- **Authentication**: OTP for voters, Email/Password for admin/officer
- **Security**: Face recognition, rate limiting, SQL injection protection

---

## PREREQUISITES

### 1. Install Dependencies (recommended: use project venv)
```powershell
# Create & activate virtual environment (PowerShell, Windows)
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install -U pip setuptools wheel
python -m pip install -r requirements.txt

# Or (CMD)
python -m venv venv
venv\Scripts\activate.bat
python -m pip install -U pip setuptools wheel
python -m pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

> **Note:** On Windows, `face-recognition` relies on `dlib` which may need native build tools. If installation of `dlib` or `face-recognition` fails, install **CMake** and the **Visual C++ Build Tools (Build Tools for Visual Studio)**, then re-run the install. As an alternative, run the helper scripts below which will attempt the standard install and print guidance on failures.

### 1.a Automated setup scripts (Windows)
- CMD (recommended for quick setup):

```
cd <project-root>
\.\scripts\setup_env.bat
```

- PowerShell (recommended for interactive sessions):

```
cd <project-root>
powershell -ExecutionPolicy Bypass -File .\scripts\setup_env.ps1
```

These scripts will create `venv`, upgrade pip & setuptools, and install the packages from `requirements.txt`.

### 1.b Run backend (after setup)
- Run directly with venv Python (preferred):

```
.\venv\Scripts\python app.py
```

- Or use helper script (CMD):

```
.\scripts\run_server.bat
```

---

### 2. Start Ganache
- Open Ganache application
- Create/Open workspace
- Ensure port: 7545
- Network ID: 5777 (default)

### 3. Deploy Smart Contract
- Open Remix IDE: https://remix.ethereum.org
- Upload `contracts/SecureVoting.sol`
- Compile (Solidity 0.8.x)
- Deploy to Ganache (Web3 Provider: http://127.0.0.1:7545)
- **Copy contract address**

### 4. Load Contract in Backend
The backend must know the deployed contract address before you can create elections
or cast votes. The server now attempts to load this address automatically on
startup if it can find it in one of the following locations:

1. `CONTRACT_ADDRESS` environment variable
2. file `contract_address.txt` in the project root (created automatically if you
   load via the API)

You can still load the contract manually using the API:
```bash
curl -X POST http://localhost:5000/api/load-contract \
  -H "Content-Type: application/json" \
  -d '{"contract_address": "0xYOUR_CONTRACT_ADDRESS"}'
```
After a successful call the address will be persisted to `contract_address.txt`
so you do not need to repeat this step on subsequent restarts.

Alternatively set the `CONTRACT_ADDRESS` env var before running `python app.py`:
```bash
set CONTRACT_ADDRESS=0xYOUR_CONTRACT_ADDRESS   # Windows
# or
export CONTRACT_ADDRESS=0xYOUR_CONTRACT_ADDRESS  # macOS/Linux
python app.py
```

---

## STARTING THE SYSTEM

### Terminal 1 - Backend
```bash
python app.py
```
**Expected Output:**
```
============================================================
SECURE E-VOTING SYSTEM - COMPLETE VERSION
============================================================
✓ Database: Initialized with RBAC
✓ OTP Authentication: Enabled
✓ Face Recognition: Active
✓ Blockchain: Connected to Ganache
✓ Admin: admin@admin.com / admin123
✓ Officer: officer@admin.com / officer123
============================================================

🚀 Server: http://localhost:5000
```

### Terminal 2 - Frontend
```bash
cd frontend
npm start
```
**Expected Output:**
```
Compiled successfully!
Local: http://localhost:3000
```

---

## TEST CREDENTIALS

### Admin
- **URL**: http://localhost:3000/admin-login
- **Email**: admin@admin.com
- **Password**: admin123

### Election Officer
- **URL**: http://localhost:3000/officer-login
- **Email**: officer@admin.com
- **Password**: officer123

### Test Voter (must be added by officer first)
- **URL**: http://localhost:3000/voter-login
- **Voter ID**: V001
- **Phone**: 1234567890
- **OTP**: (displayed on screen after request)

---

## FUNCTIONAL TESTING

### TEST 1: Admin - Create Election
**Steps:**
1. Login as admin
2. Click "CREATE NEW"
3. Fill form:
   - Name: "2024 General Election"
   - Description: "Annual election for representatives"
   - Candidates: "Alice Johnson, Bob Smith, Carol Williams"
4. Click "DEPLOY ELECTION"

**Expected Result:**
- Success message: "Election created and deployed to blockchain"
- Election appears with status "CREATED"
- Transaction visible in Ganache
- Stats updated: Total Elections +1

**Verify:**
- Admin dashboard shows election card
- Candidates listed correctly
- Election ID generated (4-6 digits)

---

### TEST 2: Admin - Activate Election
**Steps:**
1. Find election with status "CREATED"
2. Click "ACTIVATE" button
3. Wait for blockchain transaction

**Expected Result:**
- Status changes to "ACTIVE"
- Success message displayed
- Transaction in Ganache
- Stats updated: Active Elections +1

**Verify:**
- Election visible to voters
- Cannot activate twice

---

### TEST 3: Officer - Add Voter
**Steps:**
1. Login as officer
2. Click "ADD VOTER"
3. Fill form:
   - Voter ID: V001
   - Name: Test Voter
   - Email: voter@test.com
   - Phone: 1234567890
   - Ethereum Address: (copy from Ganache account index 1)
4. Click "ADD VOTER"

**Expected Result:**
- Success message: "Voter added successfully"
- Voter appears in table
- Status: Active (green badge)
- Stats updated: Total Voters +1, Active Voters +1

**Verify:**
- Voter can login
- All fields saved correctly
- Ethereum address validated

---

### TEST 4: Officer - Edit Voter
**Steps:**
1. Click edit icon (pencil) on voter row
2. Modify name: "Test Voter Updated"
3. Click "UPDATE VOTER"

**Expected Result:**
- Success message: "Voter updated successfully"
- Name updated in table

**Verify:**
- Changes persist after refresh
- Email/phone editable
- Ethereum address NOT editable (security)

---

### TEST 5: Officer - Deactivate Voter
**Steps:**
1. Click deactivate icon (X) on active voter
2. Confirm action

**Expected Result:**
- Status badge changes to "Inactive" (red)
- Stats: Active Voters -1, Inactive Voters +1
- Voter cannot login

**Test Login:**
- Try voter login → "Account deactivated"

---

### TEST 6: Voter - OTP Login (Step 1)
**Steps:**
1. Go to voter login
2. Enter:
   - Voter ID: V001
   - Mobile: 1234567890
3. Click "REQUEST OTP"

**Expected Result:**
- Success message: "OTP sent to 1234567890"
- OTP displayed on screen (6 digits)
- OTP input field appears
- Timer: 5 minutes expiry

**Verify Backend:**
- Check terminal: `[OTP] Generated for V001: ######`
- Database: otp_sessions table has entry

---

### TEST 7: Voter - OTP Verification (Step 2)
**Steps:**
1. Enter OTP from previous step
2. Click "VERIFY & LOGIN"

**Expected Result:**
- Success message: "Login successful"
- Redirects to voter dashboard
- Session stored

**Verify:**
- Dashboard shows voter name
- Active elections visible
- User role displays "VOTER"

---

### TEST 8: Voter - Failed OTP Attempts
**Steps:**
1. Request OTP for V001
2. Enter wrong OTP (e.g., 000000)
3. Submit 3 times

**Expected Result:**
- Attempt 1: "Invalid OTP. 2 attempts remaining"
- Attempt 2: "Invalid OTP. 1 attempts remaining"
- Attempt 3: "Too many failed attempts. Locked for 60 minutes"

**Verify:**
- Further OTP requests blocked
- Database: locked_until timestamp set
- After 60 mins: can request OTP again

---

### TEST 9: Voter - View Active Election
**Steps:**
1. Login as voter
2. Click on active election card

**Expected Result:**
- Election details displayed
- Candidates listed (not "Candidate 0")
- Real candidate names shown
- "Back to Elections" button visible

**Verify:**
- Only ACTIVE elections visible
- CREATED elections hidden
- CLOSED elections hidden (unless admin)

---

### TEST 10: Voter - Cast Vote with Face Verification
**Steps:**
1. Select election
2. Click candidate card
3. Confirmation screen appears
4. Click "VERIFY FACE"
5. Simulated face verification (click OK in alert)
6. Click "CONFIRM & CAST VOTE"

**Expected Result:**
- Face verification success message
- Vote confirmation details shown
- Success: "Vote recorded successfully on blockchain!"
- Transaction hash displayed
- Redirects to elections list

**Verify Blockchain:**
- Open Ganache → Transactions tab
- Latest transaction from voter's address
- Gas used: ~200,000-300,000
- Contract method: castVote

**Verify Database:**
- votes table has entry
- election_id, voter_address, tx_hash recorded

---

### TEST 11: Voter - Duplicate Vote Prevention
**Steps:**
1. Try voting again in same election
2. Click candidate

**Expected Result:**
- Error: "You have already voted in this election"
- Cannot proceed
- Vote button disabled OR error shown immediately

**Verify:**
- Blockchain prevents duplicate
- Database check prevents attempt
- User informed clearly

---

### TEST 12: Admin - Close Election
**Steps:**
1. Login as admin
2. Find ACTIVE election
3. Click "CLOSE" button

**Expected Result:**
- Status changes to "CLOSED"
- Success message displayed
- Transaction in Ganache
- Voting disabled for voters

**Verify:**
- Voters cannot vote (error message)
- Results become visible
- Vote counts displayed

---

### TEST 13: Admin - View Results
**Steps:**
1. Login as admin
2. View closed election card

**Expected Result:**
- Candidate names with vote counts
- Progress bars showing percentages
- Total votes displayed
- Accurate vote distribution

**Verify Blockchain:**
```javascript
// In browser console or Remix
contract.methods.getResults(ELECTION_ID).call()
// Should match admin dashboard
```

---

### TEST 14: Admin - Archive Election
**Steps:**
1. Find CLOSED election
2. Click "ARCHIVE"

**Expected Result:**
- Status changes to "ARCHIVED"
- Election moves to archived section
- Results still visible
- No further state changes allowed

---

### TEST 15: Dashboard Statistics Accuracy
**Admin Stats:**
1. Create 3 elections
2. Activate 2
3. Close 1

**Expected:**
- Total Elections: 3
- Active Elections: 1
- Total Votes: (actual vote count)

**Officer Stats:**
1. Add 5 voters
2. Deactivate 2

**Expected:**
- Total Voters: 5
- Active Voters: 3
- Inactive Voters: 2

**Verify:**
- Stats update immediately
- Refresh maintains accuracy
- Backend `/api/admin/stats` matches UI
- Backend `/api/officer/stats` matches UI

---

## SECURITY TESTING

### TEST 16: SQL Injection Prevention
**Attempt:**
```
Voter ID: V001' OR '1'='1
OTP: 123456' OR '1'='1
```

**Expected Result:**
- Input sanitized
- Invalid voter ID error OR login fails
- No database compromise
- No SQL errors in console

---

### TEST 17: Rate Limiting - OTP
**Steps:**
1. Request OTP for V001
2. Immediately request again (before expiry)

**Expected Result:**
- Allow 2nd request (replaces 1st OTP)
- But prevent spam (server-side limiting)
- Database: old OTP marked invalid

---

### TEST 18: Cross-Role Access Prevention
**Test 1: Voter accessing admin endpoint**
```bash
curl -X GET http://localhost:5000/api/admin/stats \
-H "X-User-ID: V001"
```
**Expected:** 403 Forbidden "Access denied"

**Test 2: Admin accessing officer-only endpoint**
```bash
curl -X POST http://localhost:5000/api/officer/add-voter \
-H "X-User-ID: ADMIN001" \
-H "Content-Type: application/json" \
-d '{"user_id": "V999", ...}'
```
**Expected:** 403 Forbidden

---

### TEST 19: Inactive Account Prevention
**Steps:**
1. Officer deactivates V001
2. Try login as V001 (OTP succeeds)
3. Try casting vote

**Expected Result:**
- OTP login initially succeeds (session created)
- But vote attempt fails: "Account deactivated. Cannot vote"
- Or better: login itself fails at verification stage

---

### TEST 20: Blockchain Consistency
**Test:**
1. Create election
2. Cast 5 votes from different voters
3. Close election
4. Check results in 3 places:
   - Admin dashboard
   - Direct blockchain query (Remix)
   - Backend API `/api/election/{id}`

**Expected Result:**
- All 3 sources show identical vote counts
- No discrepancies
- Total votes match

---

## FACE RECOGNITION TESTING

### TEST 21: Face Registration (Officer)
**Using Python Script:**
```bash
python face_recognition_system.py register
```

**Steps:**
1. Webcam opens
2. Position face in frame
3. Press SPACE to capture
4. System validates:
   - Exactly 1 face detected
   - Face size adequate
   - Image not blurry
   - Lighting sufficient

**Expected Result:**
- Success: "Face registered successfully"
- Encoding saved to `face_data/TEST_VOTER_encoding.pkl`
- Info file created

**Failure Cases (intentional):**
- No face: "No face detected in image"
- 2 faces: "Multiple faces detected"
- Too dark: "Image too dark"
- Blurry: "Image too blurry"

---

### TEST 22: Face Verification (Voter)
**Using Python Script:**
```bash
python face_recognition_system.py verify
```

**Steps:**
1. Webcam opens (10 seconds)
2. Position face (same person as registration)
3. System performs continuous verification
4. Live accuracy percentage shown
5. Progress bar advances

**Expected Result:**
- Accuracy: 70-95% (same person)
- Status: "VERIFIED"
- Green rectangle around face
- Final result: Success

**Verify Terminal:**
```
============================================================
VERIFICATION RESULTS
============================================================
Attempts: 15-30
Best accuracy: 85.34%
Average accuracy: 78.12%
Final accuracy: 85.34%
Threshold: 60.0%
Status: ✓ VERIFIED
============================================================
```

---

### TEST 23: Face Verification - Wrong Person
**Steps:**
1. Register face (Person A)
2. Verify with different person (Person B)

**Expected Result:**
- Accuracy: 10-40% (different person)
- Status: "FAILED"
- Error: "Verification failed. Accuracy X% < 60%"

---

### TEST 24: Face Verification - Quality Checks
**Test various conditions:**

**No Face:**
- Look away from camera
- Expected: "No face detected" (orange text)

**Multiple Faces:**
- Two people in frame
- Expected: "Multiple faces detected" (red text)

**Poor Lighting:**
- Cover camera partially
- Expected: "Image too dark" (red text)

**Face Too Small:**
- Sit far from camera
- Expected: "Face too small" (orange text)

---

## EDGE CASE TESTING

### TEST 25: Expired OTP
**Steps:**
1. Request OTP
2. Wait 5+ minutes
3. Try verify

**Expected Result:**
- Error: "OTP expired. Request new OTP"
- Must request fresh OTP

---

### TEST 26: Voter Without Ethereum Address
**Steps:**
1. Officer adds voter WITHOUT ethereum address
2. Voter logs in
3. Tries to vote

**Expected Result:**
- Error: "Voter ethereum address not configured"
- Cannot proceed with voting

---

### TEST 27: Election Status Transition Validation
**Invalid Transitions:**
- CREATED → CLOSED (skip ACTIVE)
- ACTIVE → ARCHIVED (skip CLOSED)
- CLOSED → ACTIVE (reopen)

**Expected Result:**
- Error messages for each
- Status remains unchanged
- Blockchain state consistent

---

### TEST 28: Contract Not Loaded
**Steps:**
1. Stop Ganache
2. Restart backend
3. Try create election

**Expected Result:**
- Error: "Blockchain contract not loaded"
- Status code: 503
- Clear error message

---

### TEST 29: Blockchain Transaction Failures
**Simulate:**
1. Create election
2. Disconnect Ganache mid-transaction

**Expected Result:**
- Error caught gracefully
- User informed of failure
- Database NOT updated (consistency)
- Can retry

---

### TEST 30: Frontend-Backend Sync
**Test:**
1. Admin dashboard open
2. Create election via API (Postman)
3. Refresh dashboard

**Expected Result:**
- New election appears
- Stats updated
- No manual reload needed (websocket would be better, but refresh acceptable)

---

## PERFORMANCE TESTING

### TEST 31: Multiple Concurrent Voters
**Setup:**
- Add 10 voters
- All login simultaneously (different browsers/incognito)

**Expected Result:**
- All can login
- No database locks
- No session conflicts
- Each sees own session

---

### TEST 32: High Vote Volume
**Steps:**
1. Create election
2. Activate
3. 50 voters cast votes quickly

**Expected Result:**
- All votes recorded
- No duplicate votes
- Blockchain handles load
- Results accurate

---

### TEST 33: Large Candidate List
**Test:**
- Create election with 20 candidates

**Expected Result:**
- UI renders properly
- Scrollable if needed
- Vote buttons accessible
- Results display correctly

---

## USABILITY TESTING

### TEST 34: Mobile Responsiveness
**Test on:**
- Phone (320px - 480px)
- Tablet (768px - 1024px)
- Desktop (1920px+)

**Expected:**
- All elements visible
- No horizontal scroll
- Buttons clickable
- Text readable

---

### TEST 35: Browser Compatibility
**Test browsers:**
- Chrome
- Firefox
- Edge
- Safari (if available)

**Expected:**
- Consistent appearance
- All features functional
- WebRTC camera access works

---

### TEST 36: Error Message Clarity
**Review all error messages:**
- Use clear language
- No technical jargon
- Actionable (tell user what to do)
- Consistent tone

**Examples:**
- Good: "Voter ID not found. Please check and try again."
- Bad: "SQL error: user_id not in DB"

---

## INTEGRATION TESTING

### TEST 37: End-to-End Voting Flow
**Full workflow:**
1. Officer adds voter (V002)
2. Admin creates election
3. Admin activates election
4. Voter V002 requests OTP
5. Voter V002 verifies OTP
6. Voter V002 views election
7. Voter V002 verifies face
8. Voter V002 casts vote
9. Admin closes election
10. Admin views results

**Expected Result:**
- Complete flow succeeds
- Each step works
- Data consistent across system
- Vote recorded correctly

---

### TEST 38: Multi-Election Scenario
**Setup:**
1. Create 3 elections
2. Activate all 3
3. Voter votes in Election 1
4. Voter votes in Election 2
5. Voter tries revoting in Election 1

**Expected Result:**
- Can vote once per election
- Cannot vote twice in same election
- Can vote in multiple elections
- Results separate and accurate

---

## TESTING CHECKLIST

### Pre-Testing
- [ ] Ganache running (port 7545)
- [ ] Contract deployed and address copied
- [ ] Backend started successfully
- [ ] Frontend started successfully
- [ ] Test credentials available

### Core Features
- [ ] Admin can login
- [ ] Officer can login
- [ ] Voter can login via OTP
- [ ] Admin can create election
- [ ] Admin can activate election
- [ ] Officer can add voter
- [ ] Voter can cast vote
- [ ] Face verification works
- [ ] Admin can close election
- [ ] Results display correctly

### Data Consistency
- [ ] Dashboard stats accurate
- [ ] Election count correct
- [ ] Vote count correct
- [ ] Blockchain matches database
- [ ] Results sum equals total votes

### Security
- [ ] SQL injection prevented
- [ ] Cross-role access blocked
- [ ] Inactive accounts rejected
- [ ] Duplicate votes prevented
- [ ] OTP rate limiting works

### Edge Cases
- [ ] Expired OTP rejected
- [ ] Invalid voter ID rejected
- [ ] Wrong OTP locked after 3 attempts
- [ ] Missing ethereum address caught
- [ ] Invalid election status transitions blocked

### UI/UX
- [ ] All pages load
- [ ] Forms validate input
- [ ] Error messages clear
- [ ] Success messages shown
- [ ] Navigation works
- [ ] Logout works
- [ ] Mobile responsive

---

## TROUBLESHOOTING

### Issue: "Cannot access webcam"
**Solution:**
- Check browser permissions
- Allow camera access
- Try different browser
- On Windows: Settings → Privacy → Camera

### Issue: "Blockchain contract not loaded"
**Solution:**
```bash
curl -X POST http://localhost:5000/api/load-contract \
-H "Content-Type: application/json" \
-d '{"contract_address": "0xYOUR_ADDRESS"}'
```

### Issue: OTP not generating
**Solution:**
- Check backend terminal for errors
- Verify database initialized
- Check otp_sessions table exists
```bash
python database/db_setup.py
```

### Issue: Voter not found
**Solution:**
- Officer must add voter first
- Check exact voter ID (case sensitive)
- Verify voter is active

### Issue: Transaction fails
**Solution:**
- Check Ganache is running
- Verify contract address correct
- Ensure voter has ethereum address
- Check gas limit sufficient

---

## SUCCESS CRITERIA

### System is production-ready when:
1. All 38 tests pass
2. No console errors
3. No database inconsistencies
4. Blockchain transactions succeed
5. Face recognition works reliably
6. OTP flow secure
7. UI responsive and accessible
8. Error handling comprehensive
9. Data persistence across restarts
10. Multi-user concurrent access stable

---

## FINAL VERIFICATION

Run complete test sequence:
1. Fresh database
2. Deploy contract
3. Add 5 voters
4. Create 3 elections
5. Activate 2
6. All 5 voters vote
7. Close elections
8. Verify results

**Expected:**
- 15 total votes (5 voters × 3 elections)
- Results accurate
- No errors
- System stable

---

**Testing Complete. System Ready for Demo/Deployment.**
