# Slack Bot 新手入門
使用 python & Flask 來實作一個簡單的 Slack bot


## :ballot_box_with_check:環境準備
* Python3
* pip3
* virtualenv
* Flask
* [slackclient](https://github.com/slackapi/python-slackclient)
* [ngrok](https://tenten.co/blog/how-to-use-ngrok-to-connect-your-localhost/) `brew cask install ngrok`
```shell=zsh
# create a new virtual envirnment for this project
virtualenv slackbot.env --python=python3
# active the virtual envirnment
source slackbot.env/bin/active
```
```shell=zsh
git clone XXXX
cd XXXX
pip3 install -r requirements.txt
```
## :ballot_box_with_check:Get started 
### Step1: 建立==Slack App==與==Bot user==
* https://api.slack.com/apps

![](https://i.imgur.com/UaNfxjN.png)

![](https://i.imgur.com/MoTnd37.png)

![](https://i.imgur.com/9l2Nfzh.png)

![](https://i.imgur.com/GYyciOP.png)

### Step2: 訂閱events
* 需事前訂閱需要用到的 events，當這些 events 被觸發，Slack 會送 http request 到指定的 URL（**Step4**會再提到）

![](https://i.imgur.com/I4rDNNy.png)

![](https://i.imgur.com/6ZEpJLW.png)

### Step3: 設定驗證資訊
* 目的是為了取得 bot token，讓我們能以 bot 的身份來進行後續的動作（例如：發送訊息、查詢user資訊、查詢channel資訊等）

![](https://i.imgur.com/iLpJJmU.png)

![](https://i.imgur.com/p81DZyi.png)

先將==Client ID==、==Client Secret==和==Verification Token==儲存至環境變數中（in your virtual envirnment）。
之後進行驗證程序時會用到，程式會從這些環境變數取得對應的金鑰。
```shell=zsh
export SLACK_CLIENT_ID='XXXXXXXXXXXXXXXX'
export SLACK_CLIENT_SECRET='XXXXXXXXXXXXXXXX'
export SLACK_VERIFICATION_TOKEN='XXXXXXXXXXXXXXXX'
```

### Step4: GO :dash::dash::dash:
首先，啟動你的flask app～
```
python3 app.py
```
接者使用 ngrok，在 terminal 輸入``ngrok http 5000``後會自動產生一個網址給你，讓 localhost 也能被外網的其他人連上。
（Flask 的 localhost 預設 port 為5000）
```
ngrok http 5000
```
![](https://i.imgur.com/icrJtxG.png)

==複製 **https** 開頭的那段網址！==

接下來回到[Slack App的管理介面](https://api.slack.com/apps)，這邊需要自行指定四個不同的URL，分別處理**驗證**、**Slack Events**、**Slash Commands**，以及**Interactive Messages**
![](https://i.imgur.com/V2NBBYl.png)

* **OAuth & Permissions**
 ![](https://i.imgur.com/iGOy9IP.png)
 
     這是驗證流程中的一個步驟，簡單來說我們需要拿到一組 ==code + Clien ID + Client Secret== 去交換 Slack 的 API access token。
當完成驗證流程前面的步驟後，Slack 會送出 http get request 到我們指定的 Redirect URL（`https://011bd378.ngrok.io/finish_auth?code=XXXXXXXXXXX&state=`），有了code，我們就可以去交換token。

* **Event Subscriptions**
 ![](https://i.imgur.com/7BunWIX.png)

    對應到 **Step2** 所訂閱的 events，例如 channel 中有人傳訊息，當 event 被觸發時，Slack 會發出 http post request 到我們指定的Request URL。
    
* **Slash Commands**
 ![](https://i.imgur.com/DLEjndj.png)

    建立屬於自己 App 的 Slash Command，跟前面的運作原理一樣，當有人使用`/truth`，則 Slack 會發出 http post request 到指定的 Request URL。

* **Interactive Messages**
 ![](https://i.imgur.com/Q0RxIhY.png)

    [Interactive Messages](https://api.slack.com/docs/message-buttons) 指的是 **button** 和 **menu**，這兩個物件讓使用者可以透過點擊的動作達到互動的效果。
    跟前面一模模一樣樣，當 button 或是 meau 的選項被點擊，則 Slack 會發出 http post request 到指定的 Request URL。

以上都設定完成後，請先連上`https://011bd378.ngrok.io/begin_auth`進行驗證的動作～（要用自己拿到的ngrok網址！）
驗證完成後，就可以打開你的 Slack 跟 simplebot 互動啦～ :tada: 

## 相關資訊
* [OAuth flow](https://api.slack.com/docs/oauth)
* [Types of tokens](https://api.slack.com/docs/token-types#legacy)
* [Slack APIs 筆記](https://hackmd.io/KYNgLAHCBGULQEMAMB2AZnMToBM4QGYFg4BGAThwGMIk1hyAmJUoA===)
* [pythOnBoarding Bot](https://github.com/slackapi/Slack-Python-Onboarding-Tutorial)（大部分是參考這篇的教學 :+1: )