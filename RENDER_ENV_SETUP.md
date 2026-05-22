# 🔧 HOW TO SET ENVIRONMENT VARIABLES IN RENDER

## ⚠️ YOUR APP IS FAILING BECAUSE THESE ARE NOT SET!

---

## 📋 STEP-BY-STEP INSTRUCTIONS

### Step 1: Go to Render Dashboard
1. Open: https://dashboard.render.com
2. Login if needed
3. You should see your services listed

### Step 2: Find Your Web Service
1. Look for **"pawfect-finds"** or your web service name
2. Click on it to open the service details

### Step 3: Go to Environment Tab
1. On the left sidebar, click **"Environment"**
2. You'll see a list of environment variables (if any are set)

### Step 4: Add SUPABASE_URL
1. Click the **"Add Environment Variable"** button
2. In the **Key** field, type exactly: `SUPABASE_URL`
3. In the **Value** field, paste: `https://pplprkapzevcuelsqcfv.supabase.co`
4. Click **"Save"** or **"Add"**

### Step 5: Add SUPABASE_SERVICE_KEY
1. Click **"Add Environment Variable"** button again
2. In the **Key** field, type exactly: `SUPABASE_SERVICE_KEY`
3. In the **Value** field, paste your NEW service key:
   ```
   eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InBwbHBya2FwemV2Y3VlbHNxY2Z2Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NzQ1NjAxOSwiZXhwIjoyMDkzMDMyMDE5fQ.durkbpEyVgJftk3FWXusiBviTCRBk9fCZAciPzLwHJo
   ```
4. Click **"Save"** or **"Add"**

### Step 6: Save Changes
1. After adding both variables, click **"Save Changes"** button at the bottom
2. Render will automatically redeploy your service
3. Wait 2-3 minutes for deployment to complete

---

## ✅ VERIFICATION

After deployment completes, your environment should have:

```
SUPABASE_URL = https://pplprkapzevcuelsqcfv.supabase.co
SUPABASE_SERVICE_KEY = eyJhbGci... (long JWT token)
```

---

## 🎯 WHAT YOU SHOULD SEE

### In Render Environment Tab:
```
Key                      | Value
-------------------------|----------------------------------
SUPABASE_URL            | https://pplprkapzevcuelsqcfv...
SUPABASE_SERVICE_KEY    | eyJhbGciOiJIUzI1NiIsInR5cCI6...
SECRET_KEY              | (your Flask secret key)
```

---

## 🚨 COMMON MISTAKES

❌ **Don't do this:**
- Typing the variable name wrong (case matters!)
- Adding spaces before/after the value
- Using the OLD service key
- Forgetting to click "Save Changes"

✅ **Do this:**
- Copy-paste the exact variable names
- Copy-paste the exact values
- Use the NEW service key from Supabase
- Click "Save Changes" after adding both

---

## 📞 IF STILL NOT WORKING

1. Check the Render logs for "SUPABASE_URL" or "SUPABASE_SERVICE_KEY"
2. Make sure you clicked "Save Changes"
3. Make sure the service redeployed (check Logs tab)
4. Try manually triggering a redeploy (click "Manual Deploy" → "Deploy latest commit")

---

## 🎓 WHY THIS IS NEEDED

Your app code reads these variables like this:
```python
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_KEY')
```

If they're not set in Render's environment, `os.getenv()` returns `None`, and the database client fails to initialize.

---

**IMPORTANT:** You MUST set these in Render's dashboard. They cannot be set in code or .env files for production.
