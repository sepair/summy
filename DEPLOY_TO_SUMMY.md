# 🚀 Deploy to Your Existing Summy App

## ✅ Real Credentials Set on Summy!

Your existing `summy` app now has **real Instagram API credentials**:
- ✅ **Access Token**: Set with real token
- ✅ **App Secret**: Set with real secret  
- ✅ **Business ID**: Set to `17841473964575374`

## 🚀 Deploy via Heroku Dashboard

### Step 1: Go to Your Existing App
1. Visit: https://dashboard.heroku.com/
2. Login with: `sepeario@gmail.com`
3. Find your existing app: `summy`

### Step 2: Connect GitHub (if not already)
1. Go to **Deploy** tab
2. Under **Deployment method**, select **GitHub**
3. Connect your GitHub account if not already connected
4. Search for repository: `sepair/summy`
5. Click **Connect**

### Step 3: Deploy Now!
1. In **Deploy** tab, scroll to **Manual deploy**
2. Select **main** branch
3. Click **Deploy Branch**
4. Wait for deployment to complete

## 🌐 Your Bot Will Be Live At:

**Main Interface**: https://summy-9f6d7e440dad.herokuapp.com/

**Test URLs**:
- API: https://summy-9f6d7e440dad.herokuapp.com/api/messages
- Health: https://summy-9f6d7e440dad.herokuapp.com/health
- Test: https://summy-9f6d7e440dad.herokuapp.com/test-message

## 🎯 What Your Bot Will Do:

1. **Receive Instagram DMs** via webhook
2. **Auto-reply** with friendly message
3. **Show messages** on clean web interface
4. **Log conversations** to `messages.txt`

## 📱 After Deployment:

1. **Test the interface** by visiting: https://summy-9f6d7e440dad.herokuapp.com/
2. **Configure Instagram webhook** in Facebook Developer Console:
   - Webhook URL: `https://summy-9f6d7e440dad.herokuapp.com/webhook`
   - Verify Token: `summy_webhook_verify_token_2025`
3. **Send a DM** to your Instagram account to test

## 🔧 Monitor Deployment:

1. Check **Activity** tab for deployment status
2. Check **Logs** tab for any errors
3. Visit the main URL to see your bot live

## 🗑️ Clean Up:

You can delete the unused app `hidden-bayou-48402` if you want:
```bash
heroku apps:destroy hidden-bayou-48402 --confirm hidden-bayou-48402
```

---

**Status**: ✅ Ready to deploy to existing summy app!
**App**: `summy` (existing)
**URL**: https://summy-9f6d7e440dad.herokuapp.com/
**Credentials**: ✅ Real Instagram API credentials set 