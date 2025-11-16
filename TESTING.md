# TruChain Testing Guide

Complete testing guide for the TruChain video authenticity verification system.

## Prerequisites

### Required Software
- Node.js (v16 or higher)
- npm or yarn
- Phantom wallet browser extension
- Chrome/Firefox/Brave browser

### Blockchain Setup
1. Install Phantom wallet extension
2. Create/import a wallet
3. Switch network to **Devnet** in Phantom settings
4. Get devnet SOL from faucet: https://faucet.solana.com/

### Test Wallets Needed
You'll need at least 3 wallets for complete testing:
1. **Admin wallet** - For registering officials
2. **Official wallet** - For uploading videos
3. **Endorser wallet(s)** - For voting on videos (ideally 3)

Tip: Create multiple Phantom wallet accounts or use different browsers with different wallets.

## Initial Setup

### 1. Backend Setup

Navigate to backend directory:
```bash
cd /Users/srinivasib/Developer/truchain/.worktrees/frontend-backend-implementation/backend
```

Install dependencies:
```bash
npm install
```

Verify `.env` file exists with correct configuration:
```env
PORT=3001
IPFS_HOST=ipfs.infura.io
IPFS_PORT=5001
IPFS_PROTOCOL=https
MAX_FILE_SIZE=524288000
```

Start backend server:
```bash
npm run dev
```

Expected output:
```
Backend server running on port 3001
```

Verify backend is running:
```bash
curl http://localhost:3001/health
```

Expected response: `{"status":"ok"}`

### 2. Frontend Setup

Navigate to frontend directory:
```bash
cd /Users/srinivasib/Developer/truchain/.worktrees/frontend-backend-implementation/frontend
```

Install dependencies:
```bash
npm install
```

Verify `.env` file exists and configure with your admin wallet:
```env
VITE_SOLANA_NETWORK=devnet
VITE_PROGRAM_ID=FGkp4CpRBNDQz2h5idbhbX7cHkbggpsUsF7enLiQE2nT
VITE_ADMIN_WALLET=<YOUR_ADMIN_WALLET_PUBLIC_KEY>
VITE_BACKEND_URL=http://localhost:3001
```

Replace `<YOUR_ADMIN_WALLET_PUBLIC_KEY>` with your Phantom wallet's public key.

Start frontend server:
```bash
npm run dev
```

Expected output:
```
VITE v... ready in ...ms

  ➜  Local:   http://localhost:5173/
```

Open browser to http://localhost:5173/

## End-to-End Testing Flow

### Test 1: Admin Registration of Official

**Goal:** Register a new official account on-chain

**Wallet:** Connect with admin wallet (matching VITE_ADMIN_WALLET)

**Steps:**

1. Open http://localhost:5173/ in browser
2. Click "Select Wallet" button
3. Select Phantom and approve connection
4. You should see **"Role: admin"** and **"Admin Panel - Register Official"**

5. Fill in the registration form:
   - **Official ID:** `1`
   - **Name:** `Test Official` (max 32 characters)
   - **Authority Wallet:** `<PUBLIC_KEY_OF_OFFICIAL_WALLET>`
   - **Endorser 1:** `<PUBLIC_KEY_1>`
   - **Endorser 2:** `<PUBLIC_KEY_2>`
   - **Endorser 3:** `<PUBLIC_KEY_3>`

   Note: Use actual wallet public keys. Endorsers must be unique.

6. Click **"Register Official"**
7. Phantom will prompt for transaction approval - click **Approve**
8. Wait for confirmation

**Expected Results:**
- Success message: "Official registered! Transaction: [signature]"
- Official appears in "Registered Officials" table
- Shows ID: 1, Name: "Test Official", Authority: [wallet address]

**Troubleshooting:**
- "Program not initialized": Check VITE_PROGRAM_ID matches deployed program
- "Transaction failed": Ensure you have enough SOL for fees (airdrop more)
- "Not authorized": Verify connected wallet matches VITE_ADMIN_WALLET exactly

---

### Test 2: Official Video Upload

**Goal:** Upload video as official and register on blockchain

**Wallet:** Connect with official's authority wallet

**Steps:**

1. Disconnect current wallet in Phantom
2. Switch to the official's authority wallet
3. Refresh the page and reconnect wallet
4. You should see **"Role: official"** and **"Official Panel - Upload Videos"**
5. Shows: "Official: Test Official"

6. Prepare a test video file (any video format, recommended: small MP4 < 10MB for testing)

7. Click **"Choose File"** and select your test video
8. Click **"Upload Video"**

**Expected Process:**
- Message: "Uploading to IPFS..."
- Message: "Registering on blockchain..."
- Phantom prompts for approval - click **Approve**
- Success message: "Video registered! Transaction: [signature]"

9. Verify video appears in "Registered Videos" table:
   - Shows IPFS CID (clickable link)
   - Status badge: **"Unverified"** (yellow/orange)
   - Votes: ✓ 0 / ✗ 0
   - Timestamp: current time

**Expected Results:**
- Video file successfully uploaded to IPFS
- SHA-256 hash computed
- Video registered on Solana blockchain
- Initial status: Unverified

**Troubleshooting:**
- "No file uploaded": Ensure file is selected
- "Invalid file type": Use video formats (mp4, webm, mov)
- "Failed to upload video": Check backend is running on port 3001
- "File too large": Use smaller file or increase MAX_FILE_SIZE
- Backend error: Check backend console logs

---

### Test 3: Endorser Voting (First Vote)

**Goal:** Endorser verifies and votes on pending video

**Wallet:** Connect with endorser wallet (one of the 3 registered)

**Steps:**

1. Disconnect current wallet
2. Switch to endorser wallet (must match one of the 3 endorser public keys)
3. Refresh and reconnect
4. You should see **"Role: endorser"** and **"Endorser Panel"**
5. Shows: "You are an endorser for 1 official(s)"

6. Check **"Pending Videos (Need Your Vote)"** section
7. Should show the video uploaded by official
8. Displays:
   - Official name: "Test Official"
   - IPFS CID (clickable)
   - Current Status: "Unverified"
   - Current Votes: ✓ 0 / ✗ 0

9. Click **"Vote Authentic"**
10. Approve transaction in Phantom

**Expected Results:**
- Success message: "Vote submitted! Transaction: [signature]"
- Video moves out of "Pending Videos" section (you already voted)
- Status may still show "Unverified" (needs 2-of-3 votes to become "Authentic")

**Check from Official's View:**
1. Switch back to official wallet
2. Refresh page
3. Video should now show: Votes: ✓ 1 / ✗ 0

**Troubleshooting:**
- "Not authorized": Wallet must exactly match one of the 3 endorser addresses
- No pending videos shown: Either video doesn't exist or you already voted

---

### Test 4: Endorser Voting (Second Vote - Status Change)

**Goal:** Second endorser vote triggers status update to "Authentic"

**Wallet:** Connect with second endorser wallet

**Steps:**

1. Switch to second endorser wallet (different from first)
2. Reconnect to app
3. See "Endorser Panel" with pending video
4. Click **"Vote Authentic"**
5. Approve transaction

**Expected Results:**
- Vote submitted successfully
- Status updates to **"Authentic"** (green badge)
- Requires 2-of-3 votes, so this vote triggers the status change

**Verify from Official's View:**
1. Switch back to official wallet
2. Refresh page
3. Video status: **"Authentic"** (green)
4. Votes: ✓ 2 / ✗ 0

---

### Test 5: Endorser File Verification (Hash Matching)

**Goal:** Verify file hash matches on-chain registration

**Wallet:** Use any endorser wallet (even one who already voted)

**Steps:**

1. Connect with endorser wallet
2. Scroll to **"Verify Uploaded File"** section
3. Upload the **same video file** that the official uploaded
4. Click **"Verify File"**

**Expected Results:**
- Message: "Match found! You can vote below."
- Shows match details:
  - Official: "Test Official"
  - Status: "Authentic" (or current status)
- Displays vote buttons

**Test with Different File:**
1. Upload a **different video file**
2. Click "Verify File"
3. Expected: "No matching video found on-chain."

**How It Works:**
- Backend computes SHA-256 hash of uploaded file
- Frontend searches all on-chain videos for matching hash
- If found, shows the matching video details

---

### Test 6: Endorser Negative Vote (Disputed Status)

**Goal:** Test disputed status when endorsers disagree

**Setup:** Register a new official with new endorsers, upload a new video

**Steps:**

1. As admin, register another official (ID: 2)
2. As that official, upload a new video
3. As first endorser, vote **"Vote Authentic"**
4. As second endorser, vote **"Vote Fake"**
5. As third endorser, vote **"Vote Fake"**

**Expected Results:**
- After majority votes for "fake": Status becomes **"Disputed"** (red)
- Votes: ✓ 1 / ✗ 2

---

### Test 7: User Role (No Privileges)

**Goal:** Verify users without roles see appropriate message

**Wallet:** Use wallet not registered as admin/official/endorser

**Steps:**

1. Connect with unregistered wallet
2. Observe role detection

**Expected Results:**
- Role: "user"
- Shows message: "You don't have admin, official, or endorser privileges."
- "Social feed functionality coming soon!"

---

## Build Verification

### Backend Build Test

```bash
cd backend
npm run build
```

**Expected:**
- Creates `dist/` directory
- No TypeScript compilation errors
- Files created: `dist/index.js`, `dist/config.js`, etc.

**Run Production Build:**
```bash
npm start
```

Should start server from compiled code.

---

### Frontend Build Test

```bash
cd frontend
npm run build
```

**Expected:**
- Creates `dist/` directory
- No build errors
- Output shows bundle sizes

**Preview Production Build:**
```bash
npm run preview
```

Opens production build on http://localhost:4173/

---

## Common Issues and Solutions

### Backend Issues

**Port 3001 already in use:**
```bash
lsof -ti:3001 | xargs kill
# Or change PORT in .env
```

**IPFS upload timeout:**
- Check internet connection
- Infura IPFS may have rate limits
- Consider using local IPFS node

**File upload fails:**
- Check file format (must be video/mp4, video/webm, video/quicktime)
- Check file size under 500MB
- Check uploads/ directory exists and is writable

---

### Frontend Issues

**"Program not initialized":**
- Verify VITE_PROGRAM_ID in .env
- Check program is deployed to devnet
- Verify wallet is connected

**Role shows as "null":**
- Check wallet has devnet SOL
- Verify on-chain accounts exist (officials registered)
- Check browser console for errors

**Transaction fails:**
- Ensure enough SOL for fees
- Check RPC endpoint is reachable
- Try different RPC endpoint if rate limited

**Wallet won't connect:**
- Ensure Phantom is installed
- Switch to Devnet in Phantom settings
- Clear browser cache/cookies

---

### Solana Program Issues

**"Account does not exist":**
- Official must be registered first by admin
- Use correct official ID and authority

**"Not authorized":**
- Wallet must exactly match registered authority/endorser
- Check public keys match character-for-character

**"Invalid endorser":**
- Endorser must be in official's endorser list
- Check official account has correct endorsers

---

## Testing Checklist

Use this checklist to verify complete functionality:

- [ ] Backend starts without errors
- [ ] Frontend starts without errors
- [ ] Backend health endpoint responds
- [ ] Admin wallet shows Admin Panel
- [ ] Admin can register official successfully
- [ ] Official appears in admin's table
- [ ] Official wallet shows Official Panel
- [ ] Official can upload video to IPFS
- [ ] Video registers on blockchain
- [ ] Video shows in official's table with "Unverified" status
- [ ] Endorser wallet shows Endorser Panel
- [ ] Endorser sees pending video
- [ ] Endorser can vote "Authentic"
- [ ] Vote increments on-chain
- [ ] Second endorser vote changes status to "Authentic"
- [ ] Endorser can verify file by upload (hash matching)
- [ ] Correct file shows "Match found"
- [ ] Different file shows "No match"
- [ ] Third endorser voting "Fake" creates disputed status (test separately)
- [ ] Unregistered wallet shows User role
- [ ] Backend builds successfully
- [ ] Frontend builds successfully

---

## Performance Testing

### Video Upload Performance

Test with different file sizes:
- Small (< 10MB): Should complete in 5-15 seconds
- Medium (50MB): Should complete in 30-60 seconds
- Large (200MB): May take 2-5 minutes

### Role Detection Performance

- Should complete in < 2 seconds on devnet
- May be slower on mainnet-beta due to more data

### Transaction Confirmation

- Devnet: Usually 1-2 seconds
- Check Solana Explorer for transaction details

---

## Next Steps After Testing

1. **Deploy to Mainnet:**
   - Change VITE_SOLANA_NETWORK to mainnet-beta
   - Update VITE_PROGRAM_ID to mainnet program
   - Get mainnet SOL

2. **Add Features:**
   - Social feed for regular users
   - Video preview/playback
   - AI clip matching
   - Database for social flags

3. **Improve UX:**
   - Better loading states
   - Progress bars for uploads
   - Toast notifications
   - Better styling/themes

4. **Security Hardening:**
   - Add authentication
   - Rate limiting
   - Input validation
   - CORS configuration

---

## Getting Help

- Check browser console for errors (F12)
- Check backend console for server errors
- View transaction details in Solana Explorer
- Verify on-chain accounts using Solana CLI or Explorer
